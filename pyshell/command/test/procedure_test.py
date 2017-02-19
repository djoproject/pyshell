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

import os

import pytest

from pyshell.command.exception import EngineInterruptionException
import pyshell.command.procedure as procedure_module
from pyshell.command.procedure import AbstractLevelHandler
from pyshell.command.procedure import FileProcedure
from pyshell.system.manager.parent import ParentManager
from pyshell.system.parameter.variable import VariableParameter
from pyshell.utils.constants import ENABLE_ON_POST_PROCESS
from pyshell.utils.constants import ENABLE_ON_PRE_PROCESS
from pyshell.utils.constants import ENABLE_ON_PROCESS
from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.exception import ERROR
from pyshell.utils.exception import NOTICE
from pyshell.utils.exception import WARNING


def getScriptPath(script_name):
    current_file_path = os.path.realpath(__file__)
    current_directory_path = os.path.dirname(current_file_path)
    return os.path.join(current_directory_path, 'resources', script_name)


class FakeContainer(AbstractLevelHandler, ParentManager):
    def __init__(self):
        ParentManager.__init__(self)
        self.level = 0

    def decrementLevel(self):
        self.level -= 1

    def incrementLevel(self):
        self.level += 1

    def getCurrentLevel(self):
        return self.level


class FakeEngine(object):

    def __init__(self, result):
        self.result = result

    def getLastResult(self):
        return self.result


class TestProcedure(object):
    def test_preProcessMode(self, monkeypatch):
        self.executed = False

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):
            self.executed = True
            return None, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        fp = FileProcedure(file_path=getScriptPath('not_empty_script'),
                           execute_on=ENABLE_ON_PRE_PROCESS)
        parameter_container = FakeContainer()

        assert len(fp) is 1
        command, use_args, enabled = fp[0]

        command.process(args=None)
        assert not self.executed

        command.postProcess(args=None)
        assert not self.executed

        command.preProcess(args=None, parameters=parameter_container)
        assert self.executed

    def test_processMode(self, monkeypatch):
        self.executed = False

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):
            self.executed = True
            return None, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        fp = FileProcedure(file_path=getScriptPath('not_empty_script'),
                           execute_on=ENABLE_ON_PROCESS)
        parameter_container = FakeContainer()

        assert len(fp) is 1
        command, use_args, enabled = fp[0]

        command.preProcess(args=None)
        assert not self.executed

        command.postProcess(args=None)
        assert not self.executed

        command.process(args=None, parameters=parameter_container)
        assert self.executed

    def test_postProcessMode(self, monkeypatch):
        self.executed = False

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):
            self.executed = True
            return None, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        fp = FileProcedure(file_path=getScriptPath('not_empty_script'),
                           execute_on=ENABLE_ON_POST_PROCESS)
        parameter_container = FakeContainer()

        assert len(fp) is 1
        command, use_args, enabled = fp[0]

        command.preProcess(args=None)
        assert not self.executed

        command.process(args=None)
        assert not self.executed

        command.postProcess(args=None, parameters=parameter_container)
        assert self.executed

    def test_createALocalVariableWithoutError(self, monkeypatch):
        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):
            variables = parameter_container.getVariableManager()
            var = VariableParameter('plo plop plop')
            variables.setParameter("plop", var, local_param=True)
            return None, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        parameter_container = FakeContainer()
        variable_manager = parameter_container.getVariableManager()
        fp = FileProcedure(file_path=getScriptPath('not_empty_script'))
        fp.execute(parameter_container=parameter_container, args=None)

        parameter_container.incrementLevel()  # go into procedure level
        assert not variable_manager.hasParameter(
            string_path="plop",
            raise_if_ambiguous=True,
            perfect_match=True,
            local_param=True,
            explore_other_scope=True)

    def test_createALocalVariableWithSevereError(self, monkeypatch):
        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):
            variables = parameter_container.getVariableManager()
            var = VariableParameter('plo plop plop')
            variables.setParameter("plop", var, local_param=True)
            raise Exception('unexpected')

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        parameter_container = FakeContainer()
        variable_manager = parameter_container.getVariableManager()
        fp = FileProcedure(file_path=getScriptPath('not_empty_script'))

        try:
            fp.execute(parameter_container=parameter_container, args=None)
        except Exception:
            pass

        parameter_container.incrementLevel()  # go into procedure level
        assert not variable_manager.hasParameter(
            string_path="plop",
            raise_if_ambiguous=True,
            perfect_match=True,
            local_param=True,
            explore_other_scope=True)

    def test_checkLevelBeforeAfterDuringTheExecution(self, monkeypatch):
        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):
            level_id = parameter_container.getCurrentLevel()
            assert level_id == 1
            return None, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        parameter_container = FakeContainer()

        fp = FileProcedure(file_path=getScriptPath('not_empty_script'))

        level_id = parameter_container.getCurrentLevel()
        assert level_id == 0
        fp.execute(parameter_container=parameter_container, args=None)
        level_id = parameter_container.getCurrentLevel()
        assert level_id == 0

    def test_interruptInTheMiddleOfTheProcedureExecutionWithReason(
            self, monkeypatch):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'))
        self.counter = 0

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):

            if self.counter == 1:
                fp.interrupt()

            self.counter += 1
            return None, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        with pytest.raises(EngineInterruptionException) as ex:
            fp.execute(parameter_container=FakeContainer(), args=None)

        assert 'reason' not in str(ex)
        assert self.counter == 2

    def test_interruptInTheMiddleOfTheProcedureExecutionWithoutReason(
            self, monkeypatch):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'))
        self.counter = 0

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):

            if self.counter == 1:
                fp.interrupt(reason='tytito')

            self.counter += 1
            return None, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        with pytest.raises(EngineInterruptionException) as ex:
            fp.execute(parameter_container=FakeContainer(), args=None)

        assert 'reason' in str(ex)
        assert 'tytito' in str(ex)
        assert self.counter == 2

    def test_checkCommandResult(self, monkeypatch):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'))
        self.counter = 0

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):

            last_exce, engine = None, None
            if self.counter == 0:
                last_exce, engine = None, FakeEngine([42, 55, 69])
            elif self.counter == 1:
                variable_manager = parameter_container.getVariableManager()

                assert variable_manager.hasParameter(
                    string_path="?",
                    raise_if_ambiguous=True,
                    perfect_match=True,
                    local_param=True,
                    explore_other_scope=False)

                var = variable_manager.getParameter(
                    string_path="?",
                    perfect_match=True,
                    local_param=True,
                    explore_other_scope=True)

                assert var.getValue() == [42, 55, 69]

            self.counter += 1
            return last_exce, engine

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        fp.execute(parameter_container=FakeContainer(), args=None)

    def test_checkCommandResultWithNoEngine(self, monkeypatch):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'))

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):

            variable_manager = parameter_container.getVariableManager()

            assert variable_manager.hasParameter(
                string_path="?",
                raise_if_ambiguous=True,
                perfect_match=True,
                local_param=True,
                explore_other_scope=False)

            var = variable_manager.getParameter(
                string_path="?",
                perfect_match=True,
                local_param=True,
                explore_other_scope=True)

            assert len(var.getValue()) == 0
            return None, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)
        fp.execute(parameter_container=FakeContainer(), args=None)

    def test_checkLastCommandResult(self, monkeypatch):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'))
        self.counter = 0

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):
            self.counter += 1
            return None, FakeEngine([self.counter])

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        result = fp.execute(parameter_container=FakeContainer(), args=None)
        assert [self.counter] == result

    def test_checkLastCommandResultWithNoEngine(self, monkeypatch):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'))

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):
            return None, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        result = fp.execute(parameter_container=FakeContainer(), args=None)
        assert len(result) == 0

    def test_removeResultParameterThenCheck(self, monkeypatch):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'))

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):

            variable_manager = parameter_container.getVariableManager()

            assert variable_manager.hasParameter(
                string_path="?",
                raise_if_ambiguous=True,
                perfect_match=True,
                local_param=True,
                explore_other_scope=False)

            variable_manager.unsetParameter(
                string_path="?",
                local_param=True,
                explore_other_scope=False)

            return None, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        result = fp.execute(parameter_container=FakeContainer(), args=None)
        assert len(result) == 0

    def test_exceptionInProcedureWithAllowedGranularity(self, monkeypatch):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'),
                           granularity=WARNING)
        self.counter = 0

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):

            exc = None
            if self.counter == 1:
                exc = DefaultPyshellException(value="plop", severity=NOTICE)

            self.counter += 1
            return exc, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        result = fp.execute(parameter_container=FakeContainer(), args=None)
        assert len(result) == 0

    def test_exceptionInProcedureWithNotAllowedGranularity(self, monkeypatch):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'),
                           granularity=WARNING)
        self.counter = 0

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):

            exc = None
            if self.counter == 1:
                exc = DefaultPyshellException(value="plop", severity=ERROR)

            self.counter += 1
            return exc, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        with pytest.raises(EngineInterruptionException):
            fp.execute(parameter_container=FakeContainer(), args=None)

    def test_exceptionInProcedureWithNoGranularity(self, monkeypatch):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'))
        self.counter = 0

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):

            exc = None
            if self.counter == 1:
                exc = Exception("plop")

            self.counter += 1
            return exc, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        with pytest.raises(EngineInterruptionException):
            fp.execute(parameter_container=FakeContainer(), args=None)
