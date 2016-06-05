#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.arg.argchecker import ArgChecker
from pyshell.arg.argchecker import DefaultInstanceArgChecker
from pyshell.arg.argchecker import ListArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.command.command import UniCommand
from pyshell.command.exception import EngineInterruptionException
from pyshell.system.container import AbstractParameterContainer
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.setting.procedure import ProcedureLocalSettings
from pyshell.system.setting.procedure import ProcedureSettings
from pyshell.system.variable import VariableParameter
from pyshell.system.variable import VariableParameterManager
from pyshell.utils.constants import VARIABLE_ATTRIBUTE_NAME
from pyshell.utils.exception import ERROR
from pyshell.utils.exception import ParameterException
from pyshell.utils.exception import PyshellException
from pyshell.utils.executing import execute


def setArgs(container, args=None):
    if not isinstance(container, AbstractParameterContainer):
        excmsg = ("(setArgs) an AbstractParameterContainer instance was"
                  " expected for the argument container, got'" +
                  str(type(container))+"'")
        raise ParameterException(excmsg)

    if not hasattr(container, VARIABLE_ATTRIBUTE_NAME):
        excmsg = ("(setArgs) no variable manager is present in the "
                  "provided container")
        raise ParameterException(excmsg)

    variables = getattr(container, VARIABLE_ATTRIBUTE_NAME)

    if not isinstance(variables, VariableParameterManager):
        excmsg = ("(setArgs) a VariableParameterManager instance was expected"
                  " for the argument variables, got '" +
                  str(type(variables))+"'")
        raise ParameterException(excmsg)

    if args is None:
        args = ()

    if not hasattr(args, "__iter__"):
        raise ParameterException("(setArgs) args argument is not iterable")

    # all in one string
    var = VariableParameter(' '.join(str(x) for x in args))
    variables.setParameter("*", var, local_param=True)

    # arg count
    var = VariableParameter(len(args))
    variables.setParameter("#", var, local_param=True)

    # all args
    var = VariableParameter(args)
    variables.setParameter("@", var, local_param=True)

    # value from last command
    var = VariableParameter(())
    variables.setParameter("?", var, local_param=True)

    # last pid started in background
    var = VariableParameter("")
    variables.setParameter("!", var, local_param=True)

    # current process id
    var = VariableParameter(container.getCurrentId())
    variables.setParameter("$", var, local_param=True)


class FileProcedure(EnvironmentParameter, UniCommand):
    @staticmethod
    def getInitSettings():
        return ProcedureLocalSettings()

    @staticmethod
    def getAllowedParentSettingClass():
        return ProcedureSettings

    def __init__(self, file_path, settings=None):
        UniCommand.__init__(self,
                            self._internalPre,
                            self._internalPro,
                            self._internalPost)

        EnvironmentParameter.__init__(self, file_path, settings=settings)

        # transient var
        self.interrupted = False
        self.interruptReason = None

    @shellMethod(
        args=ListArgChecker(ArgChecker()),
        parameters=DefaultInstanceArgChecker.getCompleteEnvironmentChecker())
    def _internalPre(self, args, parameters):
        if not self.settings.isEnabledOnPreProcess():
            return args

        return self.execute(parameters, args)

    @shellMethod(
        args=ListArgChecker(ArgChecker()),
        parameters=DefaultInstanceArgChecker.getCompleteEnvironmentChecker())
    def _internalPro(self, args, parameters):
        if not self.settings.isEnabledOnProcess():
            return args

        return self.execute(parameters, args)

    @shellMethod(
        args=ListArgChecker(ArgChecker()),
        parameters=DefaultInstanceArgChecker.getCompleteEnvironmentChecker())
    def _internalPost(self, args, parameters):
        if not self.settings.isEnabledOnPostProcess():
            return args

        return self.execute(parameters, args)

    def interrupt(self, reason=None):
        self.interruptReason = reason

        # ALWAYS keep interrupt at the end, because it will maybe interrupt
        # another thread, and the other thread could be interrupt before
        # the end of this method if interrupt is not set at the end.
        # And so interruptReason could be empty
        self.interrupted = True

    def execute(self, parameter_container, args):
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
        execution_name = "execute "+str(self.getValue())+" (line: "

        with open(self.getValue()) as f:
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
        variable_manager = getattr(parameter_container,
                                   VARIABLE_ATTRIBUTE_NAME)

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
            if severity <= self.settings.getErrorGranularity():
                self.interrupt('the exception granularity of the last '
                               'executed command was to low.')
        else:
            if (engine is not None and
               engine.getLastResult() is not None and
               len(engine.getLastResult()) > 0):
                result_param.setValue(engine.getLastResult())
            else:
                result_param.setValue(())

    def clone(self, parent=None):
        if parent is None:
            parent = FileProcedure(self.getValue(),
                                   self.settings.clone())

        UniCommand.clone(self, parent)

        return EnvironmentParameter.clone(self, parent)
