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
from pyshell.utils.exception import ProcedureStackableException
from pyshell.utils.exception import PyshellException
from pyshell.utils.executing import execute
from pyshell.utils.parsing import Parser
from pyshell.utils.printing import getPrinterFromExceptionSeverity
from pyshell.utils.printing import printShell
from pyshell.utils.printing import warning


# TODO will be deleted with procedureInList class
def getAbsoluteIndex(index, list_size):
    "convert any positive or negative index into an absolute positive one"

    if index >= 0:
        return index

    index = list_size + index

    # because python list.insert works like that, a value can be inserted with
    # a negativ value out of bound but some other function like update does not
    # manage negativ out of bound value, and that's why it is set to 0
    if index < 0:
        return 0

    return index


# TODO merge with ProcedureFromFile as soon as ProcedureFromList is removed
class Procedure(UniCommand):
    def __init__(self, name, settings=None):
        # by default, enable on pre process #TODO this information should be
        # stored
        UniCommand.__init__(self, self._internalProcess, None, None)

        self.name = name
        # default error policy  #TODO should be in settings
        self.stopOnFirstError()

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
        parameters.pushVariableLevelForThisThread(self)

        thread_id, level = parameters.getCurrentId()

        if level == 0 and self.errorGranularity is not None:
            warning("WARN: execution of the procedure " + str(self.name) +
                    " at level 0 with an error granularity equal to '" +
                    str(self.errorGranularity) + "'.  Any error with a " +
                    "granularity equal or lower will interrupt the " +
                    "application.")

        self._setArgs(parameters, args)
        try:
            return self.execute(parameters)
        finally:
            parameters.popVariableLevelForThisThread()

    def interrupt(self, reason=None):
        self.interruptReason = reason

        # ALWAYS keep interrupt at last, because it will interrupt another
        # thread, and the other thread could be interrupt before the end of
        # this method if interrupt is not set at the end
        self.interrupt = True

    def execute(self, parameters):
        pass  # XXX TO OVERRIDE AND USE _innerExecute

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

            if self.errorGranularity is not None and \
               severity <= self.errorGranularity:
                if isinstance(last_exception, ProcedureStackableException):
                    last_exception.append((cmd, name,))
                    raise last_exception

                exception = ProcedureStackableException(
                    severity, last_exception)
                exception.procedureStack.append((cmd, name,))

                thread_id, level = param.getCurrentId()
                if level == 0:
                    self._printProcedureStack(exception, thread_id, 0)

                raise exception

            if isinstance(last_exception, ProcedureStackableException):
                thread_id, level = param.getCurrentId()
                last_exception.procedureStack.append((cmd, name,))
                self._printProcedureStack(last_exception, thread_id, level)

        else:
            if engine is not None and engine.getLastResult(
            ) is not None and len(engine.getLastResult()) > 0:
                param.setValue(engine.getLastResult())
            else:
                param.setValue(())

        return last_exception, engine

    def _printProcedureStack(self, stack_exception, thread_id, current_level):
        # TODO no usage of thread_id ?

        if len(stack_exception.procedureStack) == 0:
            return

        to_print = ""
        for i in range(0, len(stack_exception.procedureStack)):
            cmd, name = stack_exception.procedureStack[
                len(stack_exception.procedureStack) - i - 1]
            to_print += (i * " ") + str(name) + " : " + str(cmd) + \
                "(level=" + str(current_level + i) + ")\n"

        to_print = to_print[:-1]
        color_fun = getPrinterFromExceptionSeverity(stack_exception.severity)
        printShell(color_fun(to_print))

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
            parent = Procedure(self.name, settings=self.settings.clone())

        parent.errorGranularity = self.errorGranularity
        return UniCommand.clone(self, parent)

    def __hash__(self):
        return hash(self.settings)


class ProcedureFromList(Procedure):

    def __init__(self, name, settings=None):
        Procedure.__init__(self, name, settings)

        # specific command system
        self.stringCmdList = []
        self.lockedTo = -1  # TODO should be a properties of settings
        self.nextCommandIndex = None

    def setLockedTo(self, value):
        try:
            value = int(value)
        except ValueError as va:
            raise ParameterException("(Procedure) setLockedTo, expected an "
                                     "integer value as parameter: " + str(va))

        if value < -1 or value >= len(self.stringCmdList):
            if len(self.stringCmdList) == 0:
                raise ParameterException("(Procedure) setLockedTo, only -1 is "
                                         "allowed because procedure list is "
                                         "empty, got '" + str(value) + "'")
            else:
                raise ParameterException("(Procedure) setLockedTo, only a " +
                                         "value from -1 to '" +
                                         str(len(self.stringCmdList) - 1) +
                                         "' is allowed, got '" + str(value) +
                                         "'")

        self.lockedTo = value

    def getLockedTo(self):
        return self.lockedTo

    def getStringCmdList(self):
        return self.stringCmdList

    def execute(self, parameters):
        # e = self.clone() #make a copy of the current procedure
        engine = None

        # for cmd in self.stringCmdList:
        i = 0
        while i < len(self.stringCmdList):
            execution_name = self.name+" (index: "+str(i)+")"
            last_exception, engine = self._innerExecute(self.stringCmdList[i],
                                                        execution_name,
                                                        parameters)

            if self.nextCommandIndex is not None:
                i = self.nextCommandIndex
                self.nextCommandIndex = None
            else:
                i += 1

        # return the result of last command in the procedure
        if engine is None:
            return ()

        return engine.getLastResult()

    # business method

    def setNextCommandIndex(self, index):
        try:
            value = int(index)
        except ValueError as va:
            raise ParameterException("(Procedure) setNextCommandIndex, "
                                     "expected an integer index as parameter, "
                                     "got '" + str(type(va)) + "'")

        if value < 0:
            raise ParameterException("(Procedure) setNextCommandIndex, "
                                     "negativ value not allowed, got '" +
                                     str(value) + "'")

        self.nextCommandIndex = value

    def setCommand(self, index, command_string_list):
        self._checkAccess("setCommand", (index,), False)

        parser = Parser(command_string_list)
        parser.parse()

        if len(parser) == 0:
            raise ParameterException("(Procedure) addCommand, try to add a "
                                     "command string that does not hold any "
                                     "command")

        index = getAbsoluteIndex(index, len(self.stringCmdList))

        if index >= len(self.stringCmdList):
            self.stringCmdList.append([command_string_list])
            return len(self.stringCmdList) - 1
        else:
            self.stringCmdList[index] = [command_string_list]

        return index

    def addCommand(self, command_string):
        self._checkAccess("addCommand")
        parser = Parser(command_string)
        parser.parse()

        if len(parser) == 0:
            raise ParameterException("(Procedure) addCommand, try to add a "
                                     "command string that does not hold any "
                                     "command")

        # TODO mark the command if loader, origin information should be
        # available through settings

        self.stringCmdList.append(parser)
        return len(self.stringCmdList) - 1

    def removeCommand(self, index):
        self._checkAccess("removeCommand", (index,))

        try:
            del self.stringCmdList[index]
        except IndexError:
            pass  # do nothing

    def moveCommand(self, from_index, to_index):
        self._checkAccess("moveCommand", (from_index, to_index,))
        from_index = getAbsoluteIndex(from_index, len(self.stringCmdList))
        to_index = getAbsoluteIndex(to_index, len(self.stringCmdList))

        if from_index == to_index:
            return

        # manage the case when we try to insert after the existing index
        if from_index < to_index:
            to_index -= 1

        self.stringCmdList.insert(to_index, self.stringCmdList.pop(from_index))

    def _checkAccess(self, meth_name, index_to_check=(),
                     raise_if_out_of_bound=True):
        if self.settings.isReadOnly():
            raise ParameterException("(Procedure) " + meth_name + ", this "
                                     "procedure is readonly, can not do any "
                                     "update on its content")

        for index in index_to_check:
            # check validity
            try:
                self.stringCmdList[index]
            except IndexError:
                if raise_if_out_of_bound:
                    if len(self.stringCmdList) == 0:
                        message = "Command list is empty"
                    elif len(self.stringCmdList) == 1:
                        message = "Only index 0 is available"
                    else:
                        message = "A value between 0 and " + \
                            str(len(self.stringCmdList) - 1) + " was expected"

                    raise ParameterException(
                        "(Procedure) " +
                        meth_name +
                        ", index out of bound. " +
                        message +
                        ", got '" +
                        str(index) +
                        "'")
            except TypeError as te:
                raise ParameterException(
                    "(Procedure) " + meth_name + ", invalid index: " + str(te))

            # make absolute index
            index = getAbsoluteIndex(index, len(self.stringCmdList))

            # check access
            if index <= self.lockedTo:
                if len(self.stringCmdList) == 0:
                    message = "Command list is empty"
                elif len(self.stringCmdList) == 1:
                    message = "Only index 0 is available"
                else:
                    message = "A value between 0 and " + \
                        str(len(self.stringCmdList) - 1) + " was expected"

                raise ParameterException(
                    "(Procedure) " +
                    meth_name +
                    ", invalid index. " +
                    message +
                    ", got '" +
                    str(index) +
                    "'")

    def upCommand(self, index):
        self.moveCommand(index, index - 1)

    def downCommand(self, index):
        self.moveCommand(index, index + 1)

    def clone(self, parent=None):
        if parent is None:
            parent = ProcedureFromList(self.name)

        parent.stringCmdList = self.stringCmdList[:]
        parent.lockedTo = self.lockedTo

        return Procedure.clone(self, parent)

    def __hash__(self):
        pass  # TODO

    def getListOfCommandsToSave(self):
        pass  # TODO


class ProcedureFromFile(Procedure):

    def __init__(self, file_path, settings=None):
        Procedure.__init__(self, "execute " + str(file_path), settings)
        self.file_path = None
        self.setFilePath(file_path)

    def getFilePath(self):
        return self.file_path

    def setFilePath(self, file_path):
        # TODO readOnly, path validity, ...
        self.file_path = file_path

    def execute(self, parameters):
        # make a copy of the current procedure
        engine = None

        # for cmd in self.stringCmdList:
        index = 1
        with open(self.file_path) as f:
            for line in f:
                execution_name = self.name+" (line: "+str(index)+")"
                last_exception, engine = self._innerExecute(line,
                                                            execution_name,
                                                            parameters)
                index += 1

        # return the result of last command in the procedure
        if engine is None:
            return ()

        return engine.getLastResult()

    def clone(self, parent=None):
        if parent is None:
            parent = ProcedureFromFile(self.file_path)

        return Procedure.clone(self, parent)

    def __hash__(self):
        procedure_string_hash = str(hash(Procedure.__hash__(self)))
        file_path_string_hash = str(hash(self.file_path))
        return hash(procedure_string_hash + file_path_string_hash)
