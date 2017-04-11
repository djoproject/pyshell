#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2017  Jonathan Delvaux <pyshell@djoproject.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from abc import ABCMeta, abstractmethod

from pyshell.arg.accessor.default import DefaultAccessor
from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.list import ListArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.command.command import UniCommand
from pyshell.command.exception import EngineInterruptionException
from pyshell.system.parameter.variable import VariableParameter
from pyshell.utils.constants import ENABLE_ON_POST_PROCESS
from pyshell.utils.constants import ENABLE_ON_PRE_PROCESS
from pyshell.utils.constants import ENABLE_ON_PROCESS
from pyshell.utils.exception import ERROR
from pyshell.utils.exception import PyshellException
from pyshell.utils.executing import execute
from pyshell.utils.setargs import setArgs


# TODO (issue #126) move into its own file
class AbstractLevelHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def decrementLevel(self):
        pass

    @abstractmethod
    def incrementLevel(self):
        pass

    @abstractmethod
    def getCurrentLevel(self):
        pass


class FileProcedure(UniCommand):
    def __init__(self,
                 file_path,
                 execute_on=ENABLE_ON_PRE_PROCESS,
                 granularity=float("inf")):
        # TODO (issue #126) check file_path
        self._file_path = file_path

        # TODO (issue #126) check granularity
        self._granularity = granularity

        if execute_on is ENABLE_ON_PRE_PROCESS:
            UniCommand.__init__(self, pre_process=self._internalExecute)
        elif execute_on is ENABLE_ON_PROCESS:
            UniCommand.__init__(self, process=self._internalExecute)
        elif execute_on is ENABLE_ON_POST_PROCESS:
            UniCommand.__init__(self, post_process=self._internalExecute)
        else:
            pass  # TODO (issue #126) unknown execute_on, raise

        # transient var
        self.interrupted = False
        self.interruptReason = None

    @shellMethod(
        args=ListArgChecker(DefaultChecker.getArg()),
        parameters=DefaultAccessor.getContainer())
    def _internalExecute(self, args, parameters):
        return self.execute(parameters, args)

    def interrupt(self, reason=None):
        self.interruptReason = reason

        # ALWAYS keep interrupt at the end, because it will maybe interrupt
        # another thread, and the other thread could be interrupt before
        # the end of this method if interrupt is not set at the end.
        # And so interruptReason could be empty
        self.interrupted = True

    def execute(self, parameter_container, args):
        # TODO (issue #126) check if parameter_container is an instance of
        # AbstractLevelHandler

        # incrementing the level will isolate the local parameters of the
        # procedure from the local parameters of the caller
        parameter_container.incrementLevel()

        try:
            setArgs(parameter_container, args)
            return self.innerExecute(parameter_container)
        finally:
            # remove every local parameters created in this procedure
            parameter_container.flush()
            parameter_container.decrementLevel()

    def innerExecute(self, parameter_container):
        engine = None
        index = 1
        self.interrupted = False
        self.interruptReason = None
        execution_name = "execute '%s' (line: " % self._file_path

        with open(self._file_path) as f:
            for cmd in f:
                self._raiseIfInterrupted()

                last_exception, engine = execute(
                    cmd,
                    parameter_container,
                    execution_name+str(index)+")")

                self._setResult(last_exception,
                                engine,
                                parameter_container)

                index += 1

        # return the result of last command in the procedure
        if engine is None:
            return ()

        return engine.getLastResult()

    def _raiseIfInterrupted(self):
        if self.interrupted:
            exc_msg = "this process has been interrupted"

            if self.interruptReason is not None:
                exc_msg += ", reason: '" + str(self.interruptReason)

            raise EngineInterruptionException(exc_msg, abnormal=True)

    def _setResult(self, last_exception, engine, parameter_container):
        variable_manager = parameter_container.getVariableManager()

        if variable_manager.hasParameter(string_path="?",
                                         raise_if_ambiguous=True,
                                         perfect_match=True,
                                         local_param=True,
                                         explore_other_scope=False):
            result_param = variable_manager.getParameter(
                string_path="?",
                perfect_match=True,
                local_param=True,
                explore_other_scope=False)
        else:
            result_param = VariableParameter(())
            variable_manager.setParameter("?", result_param, local_param=True)

        if last_exception is not None:
            # set empty the variable "?"
            result_param.setValue(())

            # manage exception
            if isinstance(last_exception, PyshellException):
                severity = last_exception.severity
            else:
                severity = ERROR

            # The last error was too severe, stop the procedure.
            if severity <= self._granularity:
                self.interrupt('the exception granularity of the last '
                               'executed command was to low.')
        else:
            if (engine is not None and
               engine.getLastResult() is not None and
               len(engine.getLastResult()) > 0):
                result_param.setValue(engine.getLastResult())
            else:
                result_param.setValue(())
