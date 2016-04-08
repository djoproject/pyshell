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

import sys

from pyshell.arg.argchecker import ArgChecker
from pyshell.arg.argchecker import DefaultInstanceArgChecker
from pyshell.arg.argchecker import ListArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.command.command import MultiCommand
from pyshell.command.command import UniCommand
from pyshell.command.exception import EngineInterruptionException
from pyshell.system.settings import GlobalSettings
from pyshell.system.variable import VarParameter
from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.exception import ERROR
from pyshell.utils.exception import ParameterException
from pyshell.utils.exception import PyshellException
from pyshell.utils.executing import execute
from pyshell.utils.printing import printException


class ProcedureFromFile(UniCommand):
    def __init__(self, file_path, settings=None):
        # by default, enable on pre process #TODO this information should be
        # stored
        UniCommand.__init__(self, self._internalProcess, None, None)

        self.name = "execute " + str(file_path)
        # default error policy  #TODO should be in settings
        self.stopOnFirstError()
        self.setFilePath(file_path)

        if settings is not None:
            if not isinstance(settings, GlobalSettings):
                raise ParameterException("(EnvironmentParameter) __init__, "
                                         "a GlobalSettings was expected for "
                                         "settings, got '" +
                                         str(type(settings))+"'")

            self.settings = settings
        else:
            self.settings = GlobalSettings()

        # transient var
        self.interrupt = False
        self.interruptReason = None

    # ## PRE/POST process ## #

    def _setArgs(self, parameters, args):
        parameters.variable.setParameter(
            "*",  # all in one string
            VarParameter(' '.join(str(x) for x in args)),
            local_param=True)
        parameters.variable.setParameter(
            "#",  # arg count
            VarParameter(len(args)), local_param=True)
        parameters.variable.setParameter(
            "@", VarParameter(args), local_param=True)  # all args
        parameters.variable.setParameter(
            "?",  # value from last command
            VarParameter(()), local_param=True)
        parameters.variable.setParameter(
            "!",  # last pid started in background
            VarParameter(()), local_param=True)
        parameters.variable.setParameter(
            "$",  # current process id
            VarParameter(parameters.getCurrentId()),
            local_param=True)

    def enableOnPreProcess(self):
        del self[:]
        MultiCommand.addProcess(self, self._internalProcess, None, None)

    def enableOnProcess(self):
        del self[:]
        MultiCommand.addProcess(self, None, self._internalProcess, None)

    def enableOnPostProcess(self):
        del self[:]
        MultiCommand.addProcess(self, None, None, self._internalProcess)

    @shellMethod(
        args=ListArgChecker(
            ArgChecker()),
        parameters=DefaultInstanceArgChecker.getCompleteEnvironmentChecker())
    def _internalProcess(self, args, parameters):
        self._setArgs(parameters, args)
        return self.execute(parameters)

    def interrupt(self, reason=None):
        self.interruptReason = reason

        # ALWAYS keep interrupt at last, because it will interrupt another
        # thread, and the other thread could be interrupt before the end of
        # this method if interrupt is not set at the end
        self.interrupt = True

    def execute(self, parameters):
        # make a copy of the current procedure
        engine = None
        index = 1

        with open(self.file_path) as f:
            for line in f:
                execution_name = self.name+" (line: "+str(index)+")"
                # TODO no parsing ?
                last_exception, engine = self._innerExecute(line,
                                                            execution_name,
                                                            parameters)
                index += 1

        # return the result of last command in the procedure
        if engine is None:
            return ()

        return engine.getLastResult()

    def _innerExecute(self, cmd, name, parameters):
        if self.interrupt:
            if self.interruptReason is None:
                raise EngineInterruptionException(
                    "this process has been interrupted", abnormal=True)
            else:
                raise EngineInterruptionException(
                    "this process has been interrupted, reason: '" + str(
                        self.interruptReason) + "'", abnormal=True)

        last_exception, engine = execute(cmd, parameters, name)
        param = parameters.variable.getParameter("?",
                                                 perfect_match=True,
                                                 local_param=True,
                                                 explore_other_level=False)

        if last_exception is not None:
            # set empty the variable "?"
            param.setValue(())

            # manage exception
            if isinstance(last_exception, PyshellException):
                severity = last_exception.severity
            else:
                severity = ERROR

            printException(last_exception)

            # The last error was too severe, stop the procedure.
            if (self.errorGranularity is not None and
               severity <= self.errorGranularity):
                raise last_exception
        else:
            if engine is not None and engine.getLastResult(
            ) is not None and len(engine.getLastResult()) > 0:
                param.setValue(engine.getLastResult())
            else:
                param.setValue(())

        return last_exception, engine

    # get/set method

    def setNextCommandIndex(self, index):  # TODO remove me
        raise DefaultPyshellException("(Procedure) setNextCommandIndex, not "
                                      "possible to set next command index on "
                                      "this king of procedure")

    def stopOnFirstError(self):
        self.stopIfAnErrorOccuredWithAGranularityLowerOrEqualTo(
            sys.maxsize)

    def neverStopIfErrorOccured(self):
        self.stopIfAnErrorOccuredWithAGranularityLowerOrEqualTo(None)

    def stopIfAnErrorOccuredWithAGranularityLowerOrEqualTo(self, value):
        """
        Every error granularity bellow this limit will stop the execution of
        the current procedure.  A None value is equal to no limit.
        """

        if value is not None and (not isinstance(value, int) or value < 0):
            raise ParameterException("(Procedure) setStopProcedureIfAnErrorOcc"
                                     "uredWithAGranularityLowerOrEqualTo, "
                                     "expected a integer value bigger than 0, "
                                     "got '" + str(type(value)) + "'")

        self.errorGranularity = value

    def getErrorGranularity(self):
        return self.errorGranularity

    def clone(self, parent=None):
        if parent is None:
            parent = ProcedureFromFile(self.file_path,
                                       self.settings.clone())

        parent.errorGranularity = self.errorGranularity
        return UniCommand.clone(self, parent)

    def __hash__(self):
        settings_string_hash = str(hash(self.settings))
        file_path_string_hash = str(hash(self.file_path))
        return hash(settings_string_hash + file_path_string_hash)

    def getFilePath(self):
        return self.file_path

    def setFilePath(self, file_path):
        # TODO readOnly, path validity, ...
        self.file_path = file_path
