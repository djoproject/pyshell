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

import pytest

from pyshell.register.exception import LoaderException
from pyshell.register.loader.exception import LoadException
from pyshell.register.loader.exception import UnloadException
from pyshell.register.loader.internal import InternalLoader
import pyshell.register.loader.parameter as monkey_parameter
from pyshell.register.loader.parameter import ParameterAbstractLoader
from pyshell.register.profile.globale import GlobalProfile
from pyshell.register.profile.parameter import ParameterLoaderProfile
from pyshell.register.result.command import CommandResult
from pyshell.register.utils.addon import AddonInformation
from pyshell.system.container import ParameterContainer
from pyshell.system.manager import ParameterManager
from pyshell.system.parameter import Parameter
from pyshell.utils.exception import ListOfException
from pyshell.utils.exception import ParameterException


class FakeParameter(Parameter):
    pass


class FakeParameterManager(ParameterManager):

    def getAllowedType(self):
        return FakeParameter


def fakeGetManager(manager_name):
    if manager_name == "parameter":
        return FakeParameterManager
    return None


class FakeParameterLoader(ParameterAbstractLoader):

    @staticmethod
    def getManagerName():
        return "parameter"

    @staticmethod
    def createProfileInstance():
        return ParameterLoaderProfile(FakeParameter)


class FakeParameterLoader2(ParameterAbstractLoader):

    @staticmethod
    def getManagerName():
        return "parameter2"


@pytest.fixture(autouse=True)
def patchGetManager(monkeypatch):
    monkeypatch.setattr(monkey_parameter, "getManager", fakeGetManager)


class TestParameterLoaderLoad(object):

    def setup_method(self, method):
        self.master = InternalLoader
        self.master_profile = self.master.createProfileInstance()
        self.master_profile.setRoot()

        addon_information = AddonInformation('test.loader.parameter')
        global_profile = GlobalProfile('profile_name', addon_information)
        self.master_profile.setGlobalProfile(global_profile)

        self.container = ParameterContainer()
        self.loader = FakeParameterLoader
        self.loader_profile = self.master_profile.addChild(
            FakeParameterLoader)
        self.loader_profile.setGlobalProfile(global_profile)
        self.manager = FakeParameterManager(self.container)
        self.container.registerParameterManager("parameter", self.manager)

    def test_getManagerName(self):
        with pytest.raises(LoaderException):
            assert ParameterAbstractLoader.getManagerName()

    def test_containerIsNone(self):
        with pytest.raises(LoadException):
            self.loader.load(
                profile_object=self.loader_profile,
                parameter_container=None)

    def test_managerIsNoneButCanBeCreated(self):
        delattr(self.container, "parameter")
        self.loader.load(
            profile_object=self.loader_profile,
            parameter_container=self.container)

    def test_managerIsNoneAndCanNotBeCreated(self):
        delattr(self.container, "parameter")
        with pytest.raises(LoadException):
            FakeParameterLoader2.load(profile_object=self.loader_profile,
                                      parameter_container=self.container)

    def test_parameterAlreadyExist(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))
        self.manager.setParameter("tutu.tata",
                                  FakeParameter(42),
                                  local_param=False,
                                  origin_addon="plop",
                                  freeze=True)
        with pytest.raises(ListOfException):
            self.loader.load(
                profile_object=self.loader_profile,
                parameter_container=self.container)

    def test_errorWithParameterSet(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))
        self.manager.setParameter("tutu.tata",
                                  FakeParameter(42),
                                  local_param=False,
                                  origin_addon="plop",
                                  freeze=True)

        self.manager.unsetParameter(string_path="tutu.tata",
                                    local_param=False,
                                    explore_other_scope=False,
                                    force=False,
                                    unfreeze=False)

        with pytest.raises(ListOfException):
            self.loader.load(
                profile_object=self.loader_profile,
                parameter_container=self.container)

    def test_nothingToDo(self):
        self.loader.load(
            profile_object=self.loader_profile,
            parameter_container=self.container)

    def test_success(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))
        self.loader.load(
            profile_object=self.loader_profile,
            parameter_container=self.container)
        assert self.manager.hasParameter("tutu.tata")


class RaisingManager(FakeParameterManager):

    def unsetParameter(self,
                       string_path,
                       local_param=True,
                       explore_other_scope=True,
                       force=False,
                       origin_addon=None,
                       unfreeze=False):
        raise ParameterException("ERROR")


class TestParameterLoaderUnload(object):

    def setup_method(self, method):
        self.master = InternalLoader
        self.master_profile = self.master.createProfileInstance()
        self.master_profile.setRoot()

        addon_information = AddonInformation('test.loader.parameter')
        global_profile = GlobalProfile('profile_name', addon_information)
        self.master_profile.setGlobalProfile(global_profile)

        self.container = ParameterContainer()
        self.loader = FakeParameterLoader
        self.loader_profile = self.master_profile.addChild(
            FakeParameterLoader)
        self.loader_profile.setGlobalProfile(global_profile)
        self.manager = FakeParameterManager(self.container)
        self.container.registerParameterManager("parameter", self.manager)

    def _expectedResult(self, instruction_list):
        global_profile = self.loader_profile.getGlobalProfile()
        cmd_results = global_profile.getResult(CommandResult)
        assert FakeParameterLoader in cmd_results
        cmd_result = cmd_results[FakeParameterLoader]

        last_section_name = cmd_result.section_name
        last_command_list = cmd_result.command_list
        last_addons_set = cmd_result.addons_set

        assert last_section_name == "SECTION ABOUT parameter"
        assert last_command_list is not None
        assert len(last_command_list) == len(instruction_list)

        for i in range(0, len(instruction_list)):
            assert last_command_list[i] == instruction_list[i]

        assert last_addons_set == set(["pyshell.addons.parameter"])

    def test_containerIsNone(self):
        with pytest.raises(UnloadException):
            self.loader.unload(
                profile_object=self.loader_profile,
                parameter_container=None)

    def test_managerIsNone(self):
        delattr(self.container, "parameter")
        with pytest.raises(UnloadException):
            self.loader.unload(
                profile_object=self.loader_profile,
                parameter_container=self.container)

    def test_nothingToDo(self):
        self.loader.unload(
            profile_object=self.loader_profile,
            parameter_container=self.container)

    def test_notRegisteredParameterUnsetFail(self):
        container = ParameterContainer()
        manager = RaisingManager(container)
        container.registerParameterManager("parameter", manager)
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=container)
        manager.setParameter("tutu.tata",
                             FakeParameter(42),
                             local_param=False,
                             origin_addon="test.loader.parameter")
        with pytest.raises(ListOfException):
            self.master.unload(
                profile_object=self.master_profile,
                parameter_container=container)

    def test_notRegisteredParameterNotReadOnly(self):
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)
        self.manager.setParameter("tutu.tata",
                                  FakeParameter(42),
                                  local_param=False,
                                  origin_addon="test.loader.parameter")
        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = ["parameter create tutu.tata \"42\" -local_var False"]
        self._expectedResult(expected)

    def test_notRegisteredParameterReadOnly(self):
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)
        param = self.manager.setParameter("tutu.tata",
                                          FakeParameter(42),
                                          local_param=False,
                                          origin_addon="test.loader.parameter")
        param.settings.setReadOnly(True)
        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = []
        expected.append("parameter create tutu.tata \"42\" -local_var False")
        expected.append("parameter properties set tutu.tata readOnly True")
        self._expectedResult(expected)

    def test_registeredParameterDeletedNotRemovable(self):
        param = self.loader_profile.addParameter(
            "tutu.tata", FakeParameter(42))
        param.settings.setRemovable(False)
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)
        param = self.manager.unsetParameter("tutu.tata",
                                            local_param=False,
                                            explore_other_scope=False,
                                            force=True)
        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = []
        expected.append("parameter properties set tutu.tata removable True")
        expected.append("parameter unset tutu.tata -start_with_local False"
                        " -explore_other_scope False")
        self._expectedResult(expected)

    def test_notRegisteredListParameter(self):
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)
        self.manager.setParameter("tutu.tata",
                                  FakeParameter([11, 22, 33, 44]),
                                  local_param=False,
                                  origin_addon="test.loader.parameter")
        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = [("parameter create tutu.tata \"11\" \"22\" \"33\" \"44\" "
                     "-local_var False")]
        self._expectedResult(expected)

    def test_registeredParameterDeletedNotRemovableReadonly(self):
        param = self.loader_profile.addParameter(
            "tutu.tata", FakeParameter(42))
        param.settings.setRemovable(False)
        param.settings.setReadOnly(True)
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)
        param = self.manager.unsetParameter("tutu.tata",
                                            local_param=False,
                                            explore_other_scope=False,
                                            force=True)
        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = []
        expected.append("parameter properties set tutu.tata readOnly False")
        expected.append("parameter properties set tutu.tata removable True")
        expected.append("parameter unset tutu.tata -start_with_local False"
                        " -explore_other_scope False")
        self._expectedResult(expected)

    def test_registeredParameterFailToUnsetInManager(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)
        origin_addon = "test.loader.parameter"
        self.manager.unsetParameter("tutu.tata",
                                    local_param=False,
                                    explore_other_scope=False,
                                    force=True,
                                    origin_addon=origin_addon,
                                    unfreeze=True)
        self.manager.setParameter("tutu.tata",
                                  FakeParameter(42),
                                  local_param=False,
                                  origin_addon="plop",
                                  freeze=True)
        with pytest.raises(ListOfException):
            self.master.unload(
                profile_object=self.master_profile,
                parameter_container=self.container)

    def test_registeredParameterSetValue(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)
        param = self.manager.getParameter("tutu.tata",
                                          local_param=False,
                                          explore_other_scope=False)
        param.setValue(50)
        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = ["parameter set tutu.tata \"50\""]
        self._expectedResult(expected)

    def test_registeredParameterSetValueReadonly(self):
        param = self.loader_profile.addParameter(
            "tutu.tata", FakeParameter(42))
        param.settings.setReadOnly(True)
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)
        param = self.manager.getParameter("tutu.tata",
                                          local_param=False,
                                          explore_other_scope=False)
        param.settings.setReadOnly(False)
        param.setValue(55)
        param.settings.setReadOnly(True)
        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = []
        expected.append("parameter properties set tutu.tata readOnly False")
        expected.append("parameter set tutu.tata \"55\"")
        expected.append("parameter properties set tutu.tata readOnly True")
        self._expectedResult(expected)

    def test_registeredOnlysettingsChanged(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)

        param = self.manager.getParameter("tutu.tata",
                                          local_param=False,
                                          explore_other_scope=False)
        param.settings.setRemovable(False)

        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = ["parameter properties set tutu.tata removable False"]
        self._expectedResult(expected)

    def test_registeredOnlysettingsChangedReadOnly(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)

        param = self.manager.getParameter("tutu.tata",
                                          local_param=False,
                                          explore_other_scope=False)
        param.settings.setRemovable(False)
        param.settings.setReadOnly(True)

        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = []
        expected.append("parameter properties set tutu.tata removable False")
        expected.append("parameter properties set tutu.tata readOnly True")
        self._expectedResult(expected)

    def test_registeredParameterRemoveAndAddValue(self):
        self.loader_profile.addParameter(
            "tutu.tata", FakeParameter([11, 22, 33, 44]))
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)

        param = self.manager.getParameter("tutu.tata",
                                          local_param=False,
                                          explore_other_scope=False)

        param.setValue([11, 22, 33, 55])
        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = []
        expected.append("parameter subtract tutu.tata \"44\"")
        expected.append("parameter add tutu.tata \"55\"")
        self._expectedResult(expected)

    def test_registeredParameterRemoveValue(self):
        self.loader_profile.addParameter(
            "tutu.tata", FakeParameter([11, 22, 33, 44]))
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)

        param = self.manager.getParameter("tutu.tata",
                                          local_param=False,
                                          explore_other_scope=False)

        param.setValue([11, 22, 33])
        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = ["parameter subtract tutu.tata \"44\""]
        self._expectedResult(expected)

    def test_registeredParameterAddValue(self):
        self.loader_profile.addParameter(
            "tutu.tata", FakeParameter([11, 22, 33, 44]))
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)

        param = self.manager.getParameter("tutu.tata",
                                          local_param=False,
                                          explore_other_scope=False)

        param.setValue([11, 22, 33, 44, 55])
        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = ["parameter add tutu.tata \"55\""]
        self._expectedResult(expected)

    def test_registeredParameterSetListValue(self):
        self.loader_profile.addParameter(
            "tutu.tata", FakeParameter([11, 22, 33, 44]))
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)

        param = self.manager.getParameter("tutu.tata",
                                          local_param=False,
                                          explore_other_scope=False)

        param.setValue([55, 66, 77, 88])
        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = ["parameter set tutu.tata \"55\" \"66\" \"77\" \"88\""]
        self._expectedResult(expected)

    def test_registeredParameterSetListValue2(self):
        self.loader_profile.addParameter(
            "tutu.tata", FakeParameter([11, 22, 33, 44]))
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)

        param = self.manager.getParameter("tutu.tata",
                                          local_param=False,
                                          explore_other_scope=False)

        param.setValue([11, 66, 77, 88])
        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = ["parameter set tutu.tata \"11\" \"66\" \"77\" \"88\""]
        self._expectedResult(expected)

    def test_changeTypeFromListToSingleValue(self):
        self.loader_profile.addParameter(
            "tutu.tata", FakeParameter([11, 22, 33, 44]))
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)

        param = self.manager.getParameter("tutu.tata",
                                          local_param=False,
                                          explore_other_scope=False)

        param.setValue(11)
        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = ["parameter set tutu.tata \"11\""]
        self._expectedResult(expected)

    def test_changeTypeFromSingleValueToList(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(11))
        self.master.load(
            profile_object=self.master_profile,
            parameter_container=self.container)

        param = self.manager.getParameter("tutu.tata",
                                          local_param=False,
                                          explore_other_scope=False)

        param.setValue([11, 66, 77, 88])
        self.master.unload(
            profile_object=self.master_profile,
            parameter_container=self.container)

        expected = ["parameter set tutu.tata \"11\" \"66\" \"77\" \"88\""]
        self._expectedResult(expected)
