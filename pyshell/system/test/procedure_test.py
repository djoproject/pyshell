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

import os

import pytest

from pyshell.arg.exception import ArgException
from pyshell.command.exception import EngineInterruptionException
from pyshell.system.container import MAIN_LEVEL
from pyshell.system.container import PROCEDURE_LEVEL
from pyshell.system.container import ParameterContainer
import pyshell.system.procedure as procedure_module
from pyshell.system.procedure import FileProcedure
from pyshell.system.procedure import setArgs
from pyshell.system.setting.procedure import ProcedureGlobalSettings
from pyshell.system.variable import VariableParameter
from pyshell.system.variable import VariableParameterManager
from pyshell.utils.constants import VARIABLE_ATTRIBUTE_NAME
from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.exception import ERROR
from pyshell.utils.exception import NOTICE
from pyshell.utils.exception import ParameterException
from pyshell.utils.exception import WARNING


def convertAllItemInString(list):
    output = []

    for item in list:
        output.append(str(item))

    return output


def createContainer():
    container = ParameterContainer()
    manager = VariableParameterManager(container)
    container.registerParameterManager(VARIABLE_ATTRIBUTE_NAME, manager)
    return container


class TestSetArgs(object):

    def getParams(self, manager):
        assert manager.hasParameter("*",
                                    perfect_match=True,
                                    local_param=True,
                                    explore_other_scope=False)

        assert manager.hasParameter("#",
                                    perfect_match=True,
                                    local_param=True,
                                    explore_other_scope=False)

        assert manager.hasParameter("@",
                                    perfect_match=True,
                                    local_param=True,
                                    explore_other_scope=False)

        assert manager.hasParameter("?",
                                    perfect_match=True,
                                    local_param=True,
                                    explore_other_scope=False)

        assert manager.hasParameter("!",
                                    perfect_match=True,
                                    local_param=True,
                                    explore_other_scope=False)

        assert manager.hasParameter("$",
                                    perfect_match=True,
                                    local_param=True,
                                    explore_other_scope=False)

        dico = {}

        dico["*"] = manager.getParameter("*",
                                         perfect_match=True,
                                         local_param=True,
                                         explore_other_scope=False)

        dico["#"] = manager.getParameter("#",
                                         perfect_match=True,
                                         local_param=True,
                                         explore_other_scope=False)

        dico["@"] = manager.getParameter("@",
                                         perfect_match=True,
                                         local_param=True,
                                         explore_other_scope=False)

        dico["?"] = manager.getParameter("?",
                                         perfect_match=True,
                                         local_param=True,
                                         explore_other_scope=False)

        dico["!"] = manager.getParameter("!",
                                         perfect_match=True,
                                         local_param=True,
                                         explore_other_scope=False)

        dico["$"] = manager.getParameter("$",
                                         perfect_match=True,
                                         local_param=True,
                                         explore_other_scope=False)

        return dico

    def test_noneContainer(self):
        with pytest.raises(ParameterException):
            setArgs(container=None)

    def test_noVariableManagerInContainter(self):
        with pytest.raises(ParameterException):
            setArgs(container=ParameterContainer())

    def test_invalidVariableManagerInContainter(self):
        container = ParameterContainer()
        setattr(container, VARIABLE_ATTRIBUTE_NAME, "toto")

        with pytest.raises(ParameterException):
            setArgs(container=container)

    def test_notIterableArgs(self):
        container = createContainer()
        with pytest.raises(ParameterException):
            setArgs(container=container, args=52)

    def test_noneArgs(self):
        container = createContainer()
        setArgs(container=container, args=None)
        manager = getattr(container, VARIABLE_ATTRIBUTE_NAME)
        dico = self.getParams(manager)

        assert dico['*'].getValue() == ['']
        assert dico['#'].getValue() == ['0']
        assert dico['@'].getValue() == []
        assert dico['?'].getValue() == []
        assert dico['!'].getValue() == ['']
        curr_id = convertAllItemInString(container.getCurrentId())
        assert dico['$'].getValue() == curr_id

    def test_emptyArgs(self):
        container = createContainer()
        setArgs(container=container, args=())
        manager = getattr(container, VARIABLE_ATTRIBUTE_NAME)
        dico = self.getParams(manager)

        assert dico['*'].getValue() == ['']
        assert dico['#'].getValue() == ['0']
        assert dico['@'].getValue() == []
        assert dico['?'].getValue() == []
        assert dico['!'].getValue() == ['']
        curr_id = convertAllItemInString(container.getCurrentId())
        assert dico['$'].getValue() == curr_id

    def test_singleArg(self):
        container = createContainer()
        setArgs(container=container, args=('toto',))
        manager = getattr(container, VARIABLE_ATTRIBUTE_NAME)
        dico = self.getParams(manager)

        assert dico['*'].getValue() == ['toto']
        assert dico['#'].getValue() == ['1']
        assert dico['@'].getValue() == ['toto']
        assert dico['?'].getValue() == []
        assert dico['!'].getValue() == ['']
        curr_id = convertAllItemInString(container.getCurrentId())
        assert dico['$'].getValue() == curr_id

    def test_multipleArgs(self):
        container = createContainer()
        setArgs(container=container, args=('toto', 'titi', 'tata',))
        manager = getattr(container, VARIABLE_ATTRIBUTE_NAME)
        dico = self.getParams(manager)

        assert dico['*'].getValue() == ['toto titi tata']
        assert dico['#'].getValue() == ['3']
        assert dico['@'].getValue() == ['toto', 'titi', 'tata']
        assert dico['?'].getValue() == []
        assert dico['!'].getValue() == ['']
        curr_id = convertAllItemInString(container.getCurrentId())
        assert dico['$'].getValue() == curr_id

    def test_multipleArgsWithDifferentType(self):
        container = createContainer()
        setArgs(container=container, args=('toto', 23, True, 42.569,))
        manager = getattr(container, VARIABLE_ATTRIBUTE_NAME)
        dico = self.getParams(manager)

        assert dico['*'].getValue() == ['toto 23 True 42.569']
        assert dico['#'].getValue() == ['4']
        assert dico['@'].getValue() == ['toto', '23', 'True', '42.569']
        assert dico['?'].getValue() == []
        assert dico['!'].getValue() == ['']
        curr_id = convertAllItemInString(container.getCurrentId())
        assert dico['$'].getValue() == curr_id


def getScriptPath(script_name):
    current_file_path = os.path.realpath(__file__)
    current_directory_path = os.path.dirname(current_file_path)
    return os.path.join(current_directory_path, 'resources', script_name)


class FakeEngine(object):

    def __init__(self, result):
        self.result = result

    def getLastResult(self):
        return self.result


class TestFileProcedure(object):

    def test_innitInvalidFilePath(self):
        with pytest.raises(ArgException) as excinfo:
            FileProcedure(file_path=object())
        assert 'does not exist and must exist' in str(excinfo.value)

    def test_innitValidFilePath(self):
        path = getScriptPath('script')
        fp = FileProcedure(file_path=path)
        assert fp.getValue() is path

    def test_innitInvalidCustomSettings(self):
        with pytest.raises(ParameterException):
            FileProcedure(file_path=getScriptPath('script'),
                          settings=object())

    def test_innitCustomSettings(self):
        path = getScriptPath('script')
        settings = ProcedureGlobalSettings()
        fp = FileProcedure(file_path=path, settings=settings)
        assert fp.getValue() is path
        assert fp.settings is settings

    def test_preProcessMode(self, monkeypatch):
        self.executed = False

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):
            self.executed = True
            return None, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        fp = FileProcedure(file_path=getScriptPath('not_empty_script'))
        fp.settings.enableOnPreProcess()
        parameter_container = createContainer()

        fp._internalPro(args=None, parameters=parameter_container)
        assert not self.executed

        fp._internalPost(args=None, parameters=parameter_container)
        assert not self.executed

        fp._internalPre(args=None, parameters=parameter_container)
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

        fp = FileProcedure(file_path=getScriptPath('not_empty_script'))
        fp.settings.enableOnProcess()
        parameter_container = createContainer()

        fp._internalPre(args=None, parameters=parameter_container)
        assert not self.executed

        fp._internalPost(args=None, parameters=parameter_container)
        assert not self.executed

        fp._internalPro(args=None, parameters=parameter_container)
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

        fp = FileProcedure(file_path=getScriptPath('not_empty_script'))
        fp.settings.enableOnPostProcess()
        parameter_container = createContainer()

        fp._internalPre(args=None, parameters=parameter_container)
        assert not self.executed

        fp._internalPro(args=None, parameters=parameter_container)
        assert not self.executed

        fp._internalPost(args=None, parameters=parameter_container)
        assert self.executed

    def test_createALocalVariableWithoutError(self, monkeypatch):
        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):
            variables = getattr(parameter_container, VARIABLE_ATTRIBUTE_NAME)
            var = VariableParameter('plo plop plop')
            variables.setParameter("plop", var, local_param=True)
            return None, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        parameter_container = createContainer()
        variable_manager = getattr(
            parameter_container,
            VARIABLE_ATTRIBUTE_NAME)

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
            variables = getattr(parameter_container, VARIABLE_ATTRIBUTE_NAME)
            var = VariableParameter('plo plop plop')
            variables.setParameter("plop", var, local_param=True)
            raise Exception('unexpected')

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        parameter_container = createContainer()
        variable_manager = getattr(
            parameter_container,
            VARIABLE_ATTRIBUTE_NAME)

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
            tid, level_id = parameter_container.getCurrentId()
            assert level_id is PROCEDURE_LEVEL
            return None, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        parameter_container = createContainer()

        fp = FileProcedure(file_path=getScriptPath('not_empty_script'))

        tid, level_id = parameter_container.getCurrentId()
        assert level_id is MAIN_LEVEL
        fp.execute(parameter_container=parameter_container, args=None)
        tid, level_id = parameter_container.getCurrentId()
        assert level_id is MAIN_LEVEL

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
            fp.execute(parameter_container=createContainer(), args=None)

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
            fp.execute(parameter_container=createContainer(), args=None)

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
                variable_manager = getattr(
                    parameter_container, VARIABLE_ATTRIBUTE_NAME)

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

        fp.execute(parameter_container=createContainer(), args=None)

    def test_checkCommandResultWithNoEngine(self, monkeypatch):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'))

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):

            variable_manager = getattr(
                parameter_container, VARIABLE_ATTRIBUTE_NAME)

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
        fp.execute(parameter_container=createContainer(), args=None)

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

        result = fp.execute(parameter_container=createContainer(), args=None)
        assert [self.counter] == result

    def test_checkLastCommandResultWithNoEngine(self, monkeypatch):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'))

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):
            return None, None

        monkeypatch.setattr(procedure_module, 'execute', fakeExecute)

        result = fp.execute(parameter_container=createContainer(), args=None)
        assert len(result) == 0

    def test_removeResultParameterThenCheck(self, monkeypatch):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'))

        def fakeExecute(string,
                        parameter_container,
                        process_name=None,
                        process_arg=None):

            variable_manager = getattr(
                parameter_container, VARIABLE_ATTRIBUTE_NAME)

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

        result = fp.execute(parameter_container=createContainer(), args=None)
        assert len(result) == 0

    def test_exceptionInProcedureWithAllowedGranularity(self, monkeypatch):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'))
        fp.settings.setErrorGranularity(WARNING)
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

        result = fp.execute(parameter_container=createContainer(), args=None)
        assert len(result) == 0

    def test_exceptionInProcedureWithNotAllowedGranularity(self, monkeypatch):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'))
        fp.settings.setErrorGranularity(WARNING)
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
            fp.execute(parameter_container=createContainer(), args=None)

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
            fp.execute(parameter_container=createContainer(), args=None)

    def test_cloneWithParent(self):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'))
        fpc = FileProcedure(file_path=getScriptPath('script'))
        fpc.settings.setRemovable(False)

        fpc.clone(fp)

        assert fp is not fpc
        assert fp.settings is not fpc.settings
        assert fp.getValue() is fpc.getValue()
        assert fp.getValue() == fpc.getValue()
        assert hash(fp.settings) == hash(fpc.settings)
        assert hash(fp) == hash(fpc)

    def test_cloneWithoutParent(self):
        fp = FileProcedure(file_path=getScriptPath('several_actions_script'))
        fpc = fp.clone()

        assert fp is not fpc
        assert fp.settings is not fpc.settings
        assert fp.getValue() is fpc.getValue()
        assert fp.getValue() == fpc.getValue()
        assert hash(fp.settings) == hash(fpc.settings)
        assert hash(fp) == hash(fpc)
