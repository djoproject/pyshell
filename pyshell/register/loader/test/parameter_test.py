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
from pyshell.register.loader.parameter import ParameterAbstractLoader
from pyshell.register.profile.parameter import ParameterLoaderProfile
from pyshell.register.result.command import CommandResult
from pyshell.register.utils.addon import AddonLoader
from pyshell.register.utils.parent import ParentAddon
from pyshell.system.manager.abstract import AbstractParameterManager
from pyshell.system.manager.parent import ParentManager
from pyshell.system.parameter.abstract import Parameter
from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.exception import ListOfException
from pyshell.utils.exception import ParameterException


class FakeParent(ParentAddon, ParentManager):
    def __init__(self, *args, **kwargs):
        ParentAddon.__init__(self)
        ParentManager.__init__(self)

    def checkForSetGlobalParameter(self, addon_name, loader_name):
        pass

    def checkForUnsetGlobalParameter(self, addon_name, loader_name):
        pass


class FakeParameterManager(AbstractParameterManager):
    def getAllowedType(self):
        return FakeParameter

    @staticmethod
    def getLoaderName():
        return "parameter"


class FakeParameter(Parameter):
    pass


class FakeParameterLoader(ParameterAbstractLoader):
    MANAGER = None

    @staticmethod
    def getManagerName():
        return "parameter"

    @staticmethod
    def getManager(container):
        return FakeParameterLoader.MANAGER

    @staticmethod
    def createProfileInstance(root_profile):
        return ParameterLoaderProfile(FakeParameter, root_profile)


class FakeParameterLoader2(ParameterAbstractLoader):

    @staticmethod
    def getManagerName():
        return "parameter2"


class TestParameterLoaderLoad(object):

    def setup_method(self, method):
        self.container = FakeParent()
        self.fake_manager = FakeParameterManager(self.container)
        FakeParameterLoader.MANAGER = self.fake_manager

        self.addon_name = 'test.loader.parameter'
        self.addon_loader = AddonLoader(self.addon_name)
        self.addon_loader.createProfile(profile_name=None)
        self.container.getAddonManager()[self.addon_name] = self.addon_loader

        self.master_profile = self.addon_loader.getRootLoaderProfile(
            profile_name=None)

        self.loader_profile = self.addon_loader.bindLoaderToProfile(
            FakeParameterLoader,
            profile_name=None)

    def test_getManagerName(self):
        with pytest.raises(LoaderException):
            assert ParameterAbstractLoader.getManagerName()

    def test_containerIsNone(self):
        with pytest.raises(LoadException):
            FakeParameterLoader.load(
                profile_object=self.loader_profile,
                parameter_container=None)

    def test_managerIsNoneButCanBeCreated(self):
        FakeParameterLoader.load(
            profile_object=self.loader_profile,
            parameter_container=self.container)

    def test_managerIsNoneAndCanNotBeCreated(self):
        with pytest.raises(DefaultPyshellException):
            FakeParameterLoader2.load(profile_object=self.loader_profile,
                                      parameter_container=self.container)

    def test_parameterAlreadyExist(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))
        manager = self.fake_manager
        manager.setParameter("tutu.tata",
                             FakeParameter(42),
                             local_param=False,
                             origin_group='test.loader.parameter',
                             freeze=True)
        with pytest.raises(ListOfException):
            self.addon_loader.load(self.container)

    def test_errorWithParameterSet(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))
        manager = self.fake_manager
        manager.setParameter("tutu.tata",
                             FakeParameter(42),
                             local_param=False,
                             origin_group='test.loader.parameter',
                             freeze=True)

        manager.unsetParameter(string_path="tutu.tata",
                               local_param=False,
                               explore_other_scope=False,
                               force=False,
                               unfreeze=False)

        with pytest.raises(ListOfException):
            self.addon_loader.load(self.container)

    def test_nothingToDo(self):
        self.addon_loader.load(self.container)

    def test_success(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        assert manager.hasParameter("tutu.tata")


class RaisingManager(FakeParameterManager):

    def unsetParameter(self,
                       string_path,
                       local_param=True,
                       explore_other_scope=True,
                       force=False,
                       origin_group=None,
                       unfreeze=False):
        raise ParameterException("ERROR")


class TestParameterLoaderUnload(object):
    def setup_method(self, method):
        self.container = FakeParent()
        self.fake_manager = FakeParameterManager(self.container)
        FakeParameterLoader.MANAGER = self.fake_manager

        self.addon_name = 'test.loader.parameter'
        self.addon_loader = AddonLoader(self.addon_name)
        self.addon_loader.createProfile(profile_name=None)
        self.container.getAddonManager()[self.addon_name] = self.addon_loader

        self.master_profile = self.addon_loader.getRootLoaderProfile(
            profile_name=None)

        self.loader_profile = self.addon_loader.bindLoaderToProfile(
            FakeParameterLoader,
            profile_name=None)

    def _expectedResult(self, instruction_list):
        root_profile = self.loader_profile.getRootProfile()
        cmd_results = root_profile.getResult(CommandResult)
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

    def _expectedEmptyResult(self):
        root_profile = self.loader_profile.getRootProfile()
        cmd_results = root_profile.getResult(CommandResult)
        assert FakeParameterLoader not in cmd_results

    def test_containerIsNone(self):
        with pytest.raises(UnloadException):
            FakeParameterLoader.unload(
                profile_object=self.loader_profile,
                parameter_container=None)

    """def test_managerIsNone(self):
        with pytest.raises(UnloadException):
            FakeParameterLoader.unload(
                profile_object=self.loader_profile,
                parameter_container=self.container)"""

    def test_nothingToDo(self):
        FakeParameterLoader.load(
            profile_object=self.loader_profile,
            parameter_container=self.container)

        FakeParameterLoader.unload(
            profile_object=self.loader_profile,
            parameter_container=self.container)

    def test_notRegisteredParameterUnsetFail(self, monkeypatch):
        FakeParameterLoader.MANAGER = RaisingManager(self.container)
        self.addon_loader.load(self.container)
        manager = FakeParameterLoader.MANAGER
        manager.setParameter("tutu.tata",
                             FakeParameter(42),
                             local_param=False,
                             origin_group="test.loader.parameter")
        with pytest.raises(ListOfException):
            self.addon_loader.unload(self.container)

    def test_notRegisteredParameterNotReadOnly(self):
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        manager.setParameter("tutu.tata",
                             FakeParameter(42),
                             local_param=False,
                             origin_group="test.loader.parameter")
        self.addon_loader.unload(self.container)

        expected = ["parameter create tutu.tata \"42\" -local_param False"]
        self._expectedResult(expected)

    def test_notRegisteredParameterReadOnly(self):
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.setParameter("tutu.tata",
                                     FakeParameter(42),
                                     local_param=False,
                                     origin_group="test.loader.parameter")
        param.settings.setReadOnly(True)
        self.addon_loader.unload(self.container)

        expected = []
        expected.append("parameter create tutu.tata \"42\" -local_param False")
        expected.append("parameter properties set tutu.tata readOnly True")
        self._expectedResult(expected)

    def test_registeredParameterDeletedNotRemovable(self):
        param = self.loader_profile.addParameter(
            "tutu.tata", FakeParameter(42))
        param.settings.setRemovable(False)
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.unsetParameter("tutu.tata",
                                       local_param=False,
                                       explore_other_scope=False,
                                       force=True)
        self.addon_loader.unload(self.container)

        expected = []
        expected.append("parameter properties set tutu.tata removable True")
        expected.append("parameter unset tutu.tata -start_with_local False"
                        " -explore_other_scope False")
        self._expectedResult(expected)

    def test_notRegisteredListParameter(self):
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        manager.setParameter("tutu.tata",
                             FakeParameter([11, 22, 33, 44]),
                             local_param=False,
                             origin_group="test.loader.parameter")
        self.addon_loader.unload(self.container)

        expected = [("parameter create tutu.tata \"11\" \"22\" \"33\" \"44\" "
                     "-local_param False")]
        self._expectedResult(expected)

    def test_notRegisteredCreatedTransient(self):
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        p = manager.setParameter("tutu.tata",
                                 FakeParameter([11, 22, 33, 44]),
                                 local_param=False,
                                 origin_group="test.loader.parameter")
        p.settings.setTransient(True)
        self.addon_loader.unload(self.container)
        self._expectedEmptyResult()

    def test_registeredParameterDeletedNotRemovableReadonly(self):
        param = self.loader_profile.addParameter(
            "tutu.tata", FakeParameter(42))
        param.settings.setRemovable(False)
        param.settings.setReadOnly(True)
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.unsetParameter("tutu.tata",
                                       local_param=False,
                                       explore_other_scope=False,
                                       force=True)
        self.addon_loader.unload(self.container)

        expected = []
        expected.append("parameter properties set tutu.tata readOnly False")
        expected.append("parameter properties set tutu.tata removable True")
        expected.append("parameter unset tutu.tata -start_with_local False"
                        " -explore_other_scope False")
        self._expectedResult(expected)

    def test_registeredParameterDeletedTransient(self):
        param = self.loader_profile.addParameter(
            "tutu.tata", FakeParameter(42))
        param.settings.setTransient(True)
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.unsetParameter("tutu.tata",
                                       local_param=False,
                                       explore_other_scope=False,
                                       force=True)
        self.addon_loader.unload(self.container)
        self._expectedEmptyResult()

    def test_registeredParameterFailToUnsetInManager(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))
        self.addon_loader.load(self.container)
        origin_group = "test.loader.parameter"
        manager = self.fake_manager
        manager.unsetParameter("tutu.tata",
                               local_param=False,
                               explore_other_scope=False,
                               force=True,
                               origin_group=origin_group,
                               unfreeze=True)
        manager.setParameter("tutu.tata",
                             FakeParameter(42),
                             local_param=False,
                             origin_group="plop",
                             freeze=True)
        with pytest.raises(ListOfException):
            self.addon_loader.unload(self.container)

    def test_registeredParameterSetValue(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.getParameter("tutu.tata",
                                     local_param=False,
                                     explore_other_scope=False)
        param.setValue(50)
        self.addon_loader.unload(self.container)

        expected = ["parameter set tutu.tata \"50\""]
        self._expectedResult(expected)

    def test_registeredParameterSetValueReadonly(self):
        param = self.loader_profile.addParameter(
            "tutu.tata", FakeParameter(42))
        param.settings.setReadOnly(True)
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.getParameter("tutu.tata",
                                     local_param=False,
                                     explore_other_scope=False)
        param.settings.setReadOnly(False)
        param.setValue(55)
        param.settings.setReadOnly(True)
        self.addon_loader.unload(self.container)

        expected = []
        expected.append("parameter properties set tutu.tata readOnly False")
        expected.append("parameter set tutu.tata \"55\"")
        expected.append("parameter properties set tutu.tata readOnly True")
        self._expectedResult(expected)

    def test_registeredParameterSetValueTransient(self):
        param = self.loader_profile.addParameter(
            "tutu.tata", FakeParameter(42))
        param.settings.setTransient(True)
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.getParameter("tutu.tata",
                                     local_param=False,
                                     explore_other_scope=False)
        param.setValue(55)
        self.addon_loader.unload(self.container)
        self._expectedEmptyResult()

    def test_registeredOnlysettingsChanged(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.getParameter("tutu.tata",
                                     local_param=False,
                                     explore_other_scope=False)
        param.settings.setRemovable(False)

        self.addon_loader.unload(self.container)

        expected = ["parameter properties set tutu.tata removable False"]
        self._expectedResult(expected)

    def test_registeredOnlysettingsChangedReadOnly(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.getParameter("tutu.tata",
                                     local_param=False,
                                     explore_other_scope=False)
        param.settings.setRemovable(False)
        param.settings.setReadOnly(True)

        self.addon_loader.unload(self.container)

        expected = []
        expected.append("parameter properties set tutu.tata removable False")
        expected.append("parameter properties set tutu.tata readOnly True")
        self._expectedResult(expected)

    def test_registeredParameterRemoveAndAddValue(self):
        self.loader_profile.addParameter(
            "tutu.tata", FakeParameter([11, 22, 33, 44]))
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.getParameter("tutu.tata",
                                     local_param=False,
                                     explore_other_scope=False)

        param.setValue([11, 22, 33, 55])
        self.addon_loader.unload(self.container)

        expected = []
        expected.append("parameter subtract tutu.tata \"44\"")
        expected.append("parameter add tutu.tata \"55\"")
        self._expectedResult(expected)

    def test_registeredParameterRemoveValue(self):
        self.loader_profile.addParameter(
            "tutu.tata", FakeParameter([11, 22, 33, 44]))
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.getParameter("tutu.tata",
                                     local_param=False,
                                     explore_other_scope=False)

        param.setValue([11, 22, 33])
        self.addon_loader.unload(self.container)

        expected = ["parameter subtract tutu.tata \"44\""]
        self._expectedResult(expected)

    def test_registeredParameterAddValue(self):
        self.loader_profile.addParameter(
            "tutu.tata", FakeParameter([11, 22, 33, 44]))
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.getParameter("tutu.tata",
                                     local_param=False,
                                     explore_other_scope=False)

        param.setValue([11, 22, 33, 44, 55])
        self.addon_loader.unload(self.container)

        expected = ["parameter add tutu.tata \"55\""]
        self._expectedResult(expected)

    def test_registeredParameterSetListValue(self):
        self.loader_profile.addParameter(
            "tutu.tata", FakeParameter([11, 22, 33, 44]))
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.getParameter("tutu.tata",
                                     local_param=False,
                                     explore_other_scope=False)

        param.setValue([55, 66, 77, 88])
        self.addon_loader.unload(self.container)

        expected = ["parameter set tutu.tata \"55\" \"66\" \"77\" \"88\""]
        self._expectedResult(expected)

    def test_registeredParameterSetListValue2(self):
        self.loader_profile.addParameter(
            "tutu.tata", FakeParameter([11, 22, 33, 44]))
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.getParameter("tutu.tata",
                                     local_param=False,
                                     explore_other_scope=False)

        param.setValue([11, 66, 77, 88])
        self.addon_loader.unload(self.container)

        expected = ["parameter set tutu.tata \"11\" \"66\" \"77\" \"88\""]
        self._expectedResult(expected)

    def test_changeTypeFromListToSingleValue(self):
        self.loader_profile.addParameter(
            "tutu.tata", FakeParameter([11, 22, 33, 44]))
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.getParameter("tutu.tata",
                                     local_param=False,
                                     explore_other_scope=False)

        param.setValue(11)
        self.addon_loader.unload(self.container)

        expected = ["parameter set tutu.tata \"11\""]
        self._expectedResult(expected)

    def test_changeTypeFromSingleValueToList(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(11))
        self.addon_loader.load(self.container)
        manager = self.fake_manager
        param = manager.getParameter("tutu.tata",
                                     local_param=False,
                                     explore_other_scope=False)

        param.setValue([11, 66, 77, 88])
        self.addon_loader.unload(self.container)

        expected = ["parameter set tutu.tata \"11\" \"66\" \"77\" \"88\""]
        self._expectedResult(expected)
