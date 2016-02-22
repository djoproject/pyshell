#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

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

import threading
from time import sleep

import pytest

from tries import multiLevelTries

from pyshell.arg.argchecker import DefaultInstanceArgChecker as DefaultArg
from pyshell.arg.argchecker import IntegerArgChecker
from pyshell.arg.argchecker import ListArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.arg.exception import ArgException
from pyshell.command.command import Command
from pyshell.command.command import MultiCommand
from pyshell.command.command import UniCommand
from pyshell.command.engine import EngineV3
from pyshell.command.exception import CommandException
from pyshell.command.exception import EngineInterruptionException
from pyshell.command.exception import ExecutionException
from pyshell.command.exception import ExecutionInitException
from pyshell.system.container import ParameterContainer
from pyshell.system.context import ContextParameter
from pyshell.system.context import ContextParameterManager
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.environment import EnvironmentParameterManager
from pyshell.system.variable import VariableParameterManager
from pyshell.utils.constants import CONTEXT_COLORATION_DARK
from pyshell.utils.constants import CONTEXT_COLORATION_KEY
from pyshell.utils.constants import CONTEXT_COLORATION_LIGHT
from pyshell.utils.constants import CONTEXT_COLORATION_NONE
from pyshell.utils.constants import CONTEXT_EXECUTION_DAEMON
from pyshell.utils.constants import CONTEXT_EXECUTION_KEY
from pyshell.utils.constants import CONTEXT_EXECUTION_SCRIPT
from pyshell.utils.constants import CONTEXT_EXECUTION_SHELL
from pyshell.utils.constants import DEBUG_ENVIRONMENT_NAME
from pyshell.utils.constants import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.constants import ENVIRONMENT_TAB_SIZE_KEY
from pyshell.utils.exception import ListOfException
from pyshell.utils.executing import _generateSuffix
from pyshell.utils.executing import execute
from pyshell.utils.parsing import Parser


RESULT = None
RESULT_BIS = None


@shellMethod(param=ListArgChecker(DefaultArg.getArgCheckerInstance()))
def plopMeth(param):
    global RESULT
    param.append(threading.current_thread().ident)
    RESULT = param
    return param


@shellMethod(param=ListArgChecker(DefaultArg.getArgCheckerInstance()))
def tutuMeth(param):
    global RESULT_BIS
    param.append(threading.current_thread().ident)
    RESULT_BIS = param
    return param


@shellMethod(param=ListArgChecker(DefaultArg.getArgCheckerInstance()))
def raiseExc1(param):
    raise ExecutionInitException("test 1")


@shellMethod(param=ListArgChecker(DefaultArg.getArgCheckerInstance()))
def raiseExc2(param):
    raise ExecutionException("test 2")


@shellMethod(param=ListArgChecker(DefaultArg.getArgCheckerInstance()))
def raiseExc3(param):
    raise CommandException("test 3")


@shellMethod(param=ListArgChecker(DefaultArg.getArgCheckerInstance()))
def raiseExc4(param):
    e = EngineInterruptionException("test 4")
    e.abnormal = True
    raise e


@shellMethod(param=ListArgChecker(DefaultArg.getArgCheckerInstance()))
def raiseExc5(param):
    e = EngineInterruptionException("test 5")
    e.abnormal = False
    raise e


@shellMethod(param=ListArgChecker(DefaultArg.getArgCheckerInstance()))
def raiseExc6(param):
    raise ArgException("test 6")


@shellMethod(param=ListArgChecker(DefaultArg.getArgCheckerInstance()))
def raiseExc7(param):
    l = ListOfException()
    l.addException(Exception("test 7"))
    raise l


@shellMethod(param=ListArgChecker(DefaultArg.getArgCheckerInstance()))
def raiseExc8(param):
    raise Exception("test 8")


class TestExecuting(object):

    def setup_method(self, method):
        global RESULT, RESULT_BIS

        self.params = ParameterContainer()

        manager = EnvironmentParameterManager(self.params)
        self.params.registerParameterManager("environment", manager)
        manager = ContextParameterManager(self.params)
        self.params.registerParameterManager("context", manager)
        manager = VariableParameterManager(self.params)
        self.params.registerParameterManager("variable", manager)

        self.debugContext = ContextParameter(
            value=tuple(range(0, 91)),
            typ=DefaultArg.getIntegerArgCheckerInstance())
        self.params.context.setParameter(DEBUG_ENVIRONMENT_NAME,
                                         self.debugContext,
                                         local_param=False)
        self.debugContext.settings.setTransient(False)
        self.debugContext.settings.setTransientIndex(False)
        self.debugContext.settings.setRemovable(False)
        self.debugContext.settings.setReadOnly(True)

        self.shellContext = ContextParameter(
            value=(CONTEXT_EXECUTION_SHELL,
                   CONTEXT_EXECUTION_SCRIPT,
                   CONTEXT_EXECUTION_DAEMON,),
            typ=DefaultArg.getStringArgCheckerInstance())
        self.params.context.setParameter(CONTEXT_EXECUTION_KEY,
                                         self.shellContext,
                                         local_param=False)
        self.shellContext.settings.setTransient(True)
        self.shellContext.settings.setTransientIndex(True)
        self.shellContext.settings.setRemovable(False)
        self.shellContext.settings.setReadOnly(True)

        self.backgroundContext = ContextParameter(
            value=(CONTEXT_COLORATION_LIGHT,
                   CONTEXT_COLORATION_DARK,
                   CONTEXT_COLORATION_NONE,),
            typ=DefaultArg.getStringArgCheckerInstance())
        self.params.context.setParameter(CONTEXT_COLORATION_KEY,
                                         self.backgroundContext,
                                         local_param=False)
        self.backgroundContext.settings.setTransient(False)
        self.backgroundContext.settings.setTransientIndex(False)
        self.backgroundContext.settings.setRemovable(False)
        self.backgroundContext.settings.setReadOnly(True)

        self.spacingContext = EnvironmentParameter(value=5,
                                                   typ=IntegerArgChecker(0))
        self.params.environment.setParameter(ENVIRONMENT_TAB_SIZE_KEY,
                                             self.spacingContext,
                                             local_param=False)
        self.spacingContext.settings.setTransient(False)
        self.spacingContext.settings.setRemovable(False)
        self.spacingContext.settings.setReadOnly(False)

        self.mltries = multiLevelTries()

        m = UniCommand(plopMeth)
        self.mltries.insert(("plop",), m)

        param = self.params.environment.setParameter(
            ENVIRONMENT_LEVEL_TRIES_KEY,
            EnvironmentParameter(value=self.mltries,
                                 typ=DefaultArg.getArgCheckerInstance()),
            local_param=False)
        param.settings.setTransient(True)
        param.settings.setRemovable(False)
        param.settings.setReadOnly(True)

        RESULT = None
        RESULT_BIS = None

        self.m = MultiCommand()
        self.mltries.insert(("plap",), self.m)

    # ## execute test ## #
    def test_execute1(self):  # with process_arg iterable
        assert RESULT is None
        last_exception, engine = execute("plop",
                                         self.params,
                                         process_arg=(1, 2, 3,))
        assert last_exception is None
        assert engine is not None
        assert RESULT == ["1", "2", "3", threading.current_thread().ident]
        expected = [["1", "2", "3", threading.current_thread().ident]]
        assert engine.getLastResult() == expected

    def test_execute2(self):  # with process_arg as string
        assert RESULT is None
        last_exception, engine = execute("plop",
                                         self.params,
                                         process_arg="1 2 3")
        assert last_exception is None
        assert engine is not None
        assert RESULT == ["1", "2", "3", threading.current_thread().ident]
        expected = [["1", "2", "3", threading.current_thread().ident]]
        assert engine.getLastResult() == expected

    def test_execute3(self):  # with process_arg as something else
        assert RESULT is None
        with pytest.raises(Exception):
            execute("plop", self.params, process_arg=object())
        assert RESULT is None

    def test_execute4(self):  # with parser parsed
        p = Parser("plop 1 2 3")
        assert RESULT is None
        last_exception, engine = execute(p, self.params)
        assert last_exception is None
        assert engine is not None
        assert RESULT == ["1", "2", "3", threading.current_thread().ident]
        expected = [["1", "2", "3", threading.current_thread().ident]]
        assert engine.getLastResult() == expected

    def test_execute5(self):  # with parser not parsed
        p = Parser("plop 1 2 3")
        p.parse()
        assert RESULT is None
        last_exception, engine = execute(p, self.params)
        assert last_exception is None
        assert engine is not None
        assert RESULT == ["1", "2", "3", threading.current_thread().ident]
        expected = [["1", "2", "3", threading.current_thread().ident]]
        assert engine.getLastResult() == expected

    def test_execute6(self):  # with string as parser
        assert RESULT is None
        last_exception, engine = execute("plop 1 2 3", self.params)
        assert last_exception is None
        assert engine is not None
        assert RESULT == ["1", "2", "3", threading.current_thread().ident]
        expected = [["1", "2", "3", threading.current_thread().ident]]
        assert engine.getLastResult() == expected

    def test_execute7(self):  # with empty parser
        p = Parser("")
        p.parse()
        assert RESULT is None
        last_exception, engine = execute(p, self.params)
        assert last_exception is None
        assert engine is None
        assert RESULT is None

    def test_execute8(self):  # try in thread
        assert RESULT is None
        last_exception, engine = execute("plop 1 2 3 &", self.params)
        assert last_exception is None
        assert engine is None

        thread_id = self.params.variable.getParameter("!").getValue()

        for t in threading.enumerate():
            if t.ident == thread_id[0]:
                t.join(4)
                break
        sleep(0.1)

        assert RESULT is not None
        assert len(RESULT) == 4
        assert RESULT[3] != threading.current_thread().ident

    def test_execute9(self):  # test with an empty command
        assert RESULT is None
        with pytest.raises(Exception):
            execute("plap", self.params, process_arg=object())
        assert RESULT is None

    def test_execute10(self):  # check if commands are correctly cloned
        m = MultiCommand()
        m.addProcess(process=plopMeth)

        c = Command()
        c.process = tutuMeth
        m.addDynamicCommand(c)

        self.mltries.insert(("tutu",), m)

        assert RESULT is None
        assert RESULT_BIS is None

        last_exception, engine = execute("tutu aa bb cc", self.params)

        assert last_exception is None
        assert engine is not None
        assert RESULT == ["aa", "bb", "cc", threading.current_thread().ident]
        assert RESULT_BIS is None

    def test_execute11(self, capsys):  # raise every exception
        # IDEA create a command that raise a defined exception, and call it

        m = MultiCommand()
        m.addProcess(process=raiseExc1)

        self.mltries.insert(("test_1",), m)

        last_exception, engine = execute("test_1 aa bb cc", self.params)
        out, err = capsys.readouterr()
        assert isinstance(last_exception, ExecutionInitException)
        assert engine is not None
        assert out == "Fail to init an execution object: test 1\n"

        ##

        m = MultiCommand()
        m.addProcess(process=raiseExc2)

        self.mltries.insert(("test_2",), m)

        last_exception, engine = execute("test_2 aa bb cc", self.params)
        out, err = capsys.readouterr()
        assert isinstance(last_exception, ExecutionException)
        assert engine is not None
        assert out == "Fail to execute: test 2\n"

        ##

        m = MultiCommand()
        m.addProcess(process=raiseExc3)

        self.mltries.insert(("test_3",), m)

        last_exception, engine = execute("test_3 aa bb cc", self.params)
        out, err = capsys.readouterr()
        assert isinstance(last_exception, CommandException)
        assert engine is not None
        assert out == "Error in command method: test 3\n"

        ##

        m = MultiCommand()
        m.addProcess(process=raiseExc4)

        self.mltries.insert(("test_4",), m)

        last_exception, engine = execute("test_4 aa bb cc", self.params)
        out, err = capsys.readouterr()
        assert isinstance(last_exception, EngineInterruptionException)
        assert engine is not None
        assert out == "Abnormal execution abort, reason: test 4\n"

        ##

        m = MultiCommand()
        m.addProcess(process=raiseExc5)

        self.mltries.insert(("test_5",), m)

        last_exception, engine = execute("test_5 aa bb cc", self.params)
        out, err = capsys.readouterr()
        assert isinstance(last_exception, EngineInterruptionException)
        assert engine is not None
        assert out == "Normal execution abort, reason: test 5\n"

        ##

        m = MultiCommand()
        m.addProcess(process=raiseExc6)

        self.mltries.insert(("test_6",), m)

        last_exception, engine = execute("test_6 aa bb cc", self.params)
        out, err = capsys.readouterr()
        assert isinstance(last_exception, ArgException)
        assert engine is not None
        assert out == "Error while parsing argument: test 6\n"

        ##

        m = MultiCommand()
        m.addProcess(process=raiseExc7)

        self.mltries.insert(("test_7",), m)

        last_exception, engine = execute("test_7 aa bb cc", self.params)
        out, err = capsys.readouterr()
        assert isinstance(last_exception, ListOfException)
        assert engine is not None
        assert out == "List of exception(s): \ntest 7\n"

        ##

        m = MultiCommand()
        m.addProcess(process=raiseExc8)

        self.mltries.insert(("test_8",), m)

        last_exception, engine = execute("test_8 aa bb cc", self.params)
        out, err = capsys.readouterr()
        assert isinstance(last_exception, Exception)
        assert engine is not None
        assert out == "test 8\n"

    # ## _generateSuffix test ## #
    def test_generateSuffix0(self):  # no suffix production
        assert _generateSuffix(self.params,
                               (("plop",),),
                               None,
                               "__process__") is None

    def test_generateSuffix1(self):  # test with debug
        self.debugContext.settings.setIndexValue(1)
        expected = (" (threadId="+str(threading.current_thread().ident)+", "
                    "level=-1, process='__process__')")
        assert _generateSuffix(self.params,
                               (("plop",),),
                               None,
                               "__process__") == expected
        self.debugContext.settings.setIndexValue(0)
        assert _generateSuffix(self.params,
                               (("plop",),),
                               None,
                               "__process__") is None

    def test_generateSuffix2(self):  # test outside shell context
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        assert _generateSuffix(self.params,
                               (("plop",),),
                               None,
                               "__process__") is None
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        expected = (" (threadId="+str(threading.current_thread().ident)+", "
                    "level=-1, process='__process__')")
        assert _generateSuffix(self.params,
                               (("plop",),),
                               None,
                               "__process__") == expected

    def test_generateSuffix3(self):  # test with processName provided or not
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        expected = (" (threadId="+str(threading.current_thread().ident)+", "
                    "level=-1, process='__process__')")
        assert _generateSuffix(self.params,
                               (("plop",),),
                               None,
                               "__process__") == expected
        expected = (" (threadId="+str(threading.current_thread().ident)+", "
                    "level=-1)")
        assert _generateSuffix(
            self.params, (("plop",),), None, None) == expected

    def test_generateSuffix5(self):  # test without commandNameList
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        e = EngineV3([UniCommand(plopMeth)], [["titi"]], ["titi"])
        expected = (" (threadId="+str(threading.current_thread().ident)+", "
                    "level=-1, process='__process__')")
        assert _generateSuffix(self.params, None, e, "__process__") == expected

    def test_generateSuffix6(self):  # test with None engine
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        expected = (" (threadId="+str(threading.current_thread().ident)+", "
                    "level=-1, process='__process__')")
        assert _generateSuffix(self.params,
                               (("plop",),),
                               None,
                               "__process__") == expected

    def test_generateSuffix7(self):  # test with empty engine
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        e = EngineV3([UniCommand(plopMeth)], [["titi"]], ["titi"])
        del e.stack[:]
        expected = (" (threadId="+str(threading.current_thread().ident)+", "
                    "level=-1, process='__process__')")
        assert _generateSuffix(self.params,
                               (("plop",),),
                               e,
                               "__process__") == expected

    # test with valid engine and commandNameList
    def test_generateSuffix8(self):
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        e = EngineV3([UniCommand(plopMeth)], [["titi"]], ["titi"])
        expected = (" (threadId="+str(threading.current_thread().ident)+", "
                    "level=-1, process='__process__', command='plop')")
        assert _generateSuffix(self.params,
                               (("plop",),),
                               e,
                               "__process__") == expected
