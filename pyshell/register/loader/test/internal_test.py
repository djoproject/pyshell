#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2016  Jonathan Delvaux <pyshell@djoproject.net>

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
from pyshell.register.loader.abstractloader import AbstractLoader
from pyshell.register.loader.exception import LoadException
from pyshell.register.loader.exception import UnloadException
from pyshell.register.loader.internal import InternalLoader
from pyshell.register.profile.default import DefaultProfile
from pyshell.register.profile.globale import GlobalProfile
from pyshell.register.profile.internal import InternalLoaderProfile
from pyshell.register.utils.addon import AddonInformation
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_LOADED_E
from pyshell.utils.constants import STATE_UNLOADED
from pyshell.utils.constants import STATE_UNLOADED_E
from pyshell.utils.exception import ListOfException


class SubAbstractLoader(AbstractLoader):

    @staticmethod
    def createProfileInstance():
        return DefaultProfile()

    @classmethod
    def load(cls, profile_object, parameter_container=None):
        pass

    @classmethod
    def unload(cls, profile_object, parameter_container=None):
        pass


class SubAbstractLoaderWithError(AbstractLoader):

    @staticmethod
    def createProfileInstance():
        return DefaultProfile()

    @classmethod
    def load(cls, profile_object, parameter_container=None):
        raise Exception("errroooorrr !")

    @classmethod
    def unload(cls, profile_object, parameter_container=None):
        pass


class SubAbstractUnloaderWithError(AbstractLoader):

    @staticmethod
    def createProfileInstance():
        return DefaultProfile()

    @classmethod
    def load(cls, profile_object, parameter_container=None):
        pass

    @classmethod
    def unload(cls, profile_object, parameter_container=None):
        raise Exception("errroooorrr !")


class TestInternalLoader(object):

    def setup_method(self, method):
        self.gl = InternalLoader
        self.profile = self.gl.createProfileInstance()
        self.profile.setRoot()

        self.addon_information = AddonInformation('test.loader.parameter')
        global_profile = GlobalProfile('profile_name', self.addon_information)
        self.profile.setGlobalProfile(global_profile)

    def test_createProfileInstance(self):
        assert isinstance(self.profile, InternalLoaderProfile)

    # InternalLoader, test init, subAddons must be empty, no constructor arg
    def test_internalLoaderInit(self):
        assert hasattr(InternalLoader, "__init__")
        assert hasattr(InternalLoader.__init__, "__call__")
        with pytest.raises(LoaderException):
            InternalLoader()

    # # _innerLoad # #
    # profile is not None, profile is not in profile_list
    def test_internalLoaderInnerLoad1(self):
        assert self.gl._innerLoad(method_name="kill",
                                  priority_method_name="getKillPriority",
                                  parameter_container=None,
                                  profile_object=self.profile,
                                  next_state=STATE_LOADED,
                                  next_state_if_error=STATE_LOADED_E) is None

    # profile is not None, profile is in profile_list,profile in valid state,
    # unknown method name
    def test_internalLoaderInnerLoad3(self):
        self.profile.addChild(SubAbstractLoader)
        with pytest.raises(AttributeError):
            self.gl._innerLoad(method_name="kill",
                               priority_method_name="getKillPriority",
                               parameter_container=None,
                               profile_object=self.profile,
                               next_state=STATE_LOADED,
                               next_state_if_error=STATE_LOADED_E)

    # profile is not None, profile is in profile_list,profile in valid state,
    # known method name, with error production
    def test_internalLoaderInnerLoad4(self):
        self.profile.addChild(SubAbstractLoaderWithError)
        with pytest.raises(ListOfException):
            self.gl._innerLoad(method_name="load",
                               priority_method_name="getLoadPriority",
                               parameter_container=None,
                               profile_object=self.profile,
                               next_state=STATE_LOADED,
                               next_state_if_error=STATE_LOADED_E)
        assert self.addon_information.getLoadedProfileName() is None
        assert self.profile.getState() == STATE_LOADED_E

    # profile is not None, profile is in profile_list,profile in valid state,
    # known method name, without error production
    def test_internalLoaderInnerLoad5(self):
        self.profile.addChild(SubAbstractLoader)
        self.gl._innerLoad(method_name="load",
                           priority_method_name="getLoadPriority",
                           parameter_container=None,
                           profile_object=self.profile,
                           next_state=STATE_LOADED,
                           next_state_if_error=STATE_LOADED_E)
        assert self.addon_information.getLoadedProfileName() is None
        assert self.profile.getState() == STATE_LOADED

    # profile is None, profile is not in profile_list
    def test_internalLoaderInnerLoad6(self):
        assert self.gl._innerLoad(method_name="kill",
                                  priority_method_name="getKillPriority",
                                  parameter_container=None,
                                  profile_object=self.profile,
                                  next_state=STATE_LOADED,
                                  next_state_if_error=STATE_LOADED_E) is None

    # profile is None, profile is in profile_list,profile in valid state,
    # unknown method name
    def test_internalLoaderInnerLoad8(self):
        self.profile.addChild(SubAbstractLoader)
        with pytest.raises(AttributeError):
            self.gl._innerLoad(method_name="kill",
                               priority_method_name="getKillPriority",
                               parameter_container=None,
                               profile_object=self.profile,
                               next_state=STATE_LOADED,
                               next_state_if_error=STATE_LOADED_E)

    # profile is None, profile is in profile_list,profile in valid state,
    # known method name, without error production
    def test_internalLoaderInnerLoad10(self):
        self.profile.addChild(SubAbstractLoader)
        self.gl._innerLoad(method_name="load",
                           priority_method_name="getLoadPriority",
                           parameter_container=None,
                           profile_object=self.profile,
                           next_state=STATE_LOADED,
                           next_state_if_error=STATE_LOADED_E)
        assert self.addon_information.getLoadedProfileName() is None
        assert self.profile.getState() == STATE_LOADED

    # # load # #
    # valid load
    def test_internalLoaderLoad1(self):
        self.profile.addChild(SubAbstractLoader)
        self.gl.load(profile_object=self.profile, parameter_container=None)
        assert self.addon_information.getLoadedProfileName() is 'profile_name'
        assert self.profile.getState() == STATE_LOADED

    # valid load with error
    def test_internalLoaderLoad2(self):
        self.profile.addChild(SubAbstractLoaderWithError)
        with pytest.raises(ListOfException):
            self.gl.load(profile_object=self.profile, parameter_container=None)
        assert self.addon_information.getLoadedProfileName() is 'profile_name'
        assert self.profile.getState() == STATE_LOADED_E

    # invalid load
    def test_internalLoaderLoad3(self):
        self.profile.addChild(SubAbstractLoader)
        self.gl.load(profile_object=self.profile, parameter_container=None)
        assert self.addon_information.getLoadedProfileName() is 'profile_name'
        assert self.profile.getState() == STATE_LOADED
        with pytest.raises(LoadException):
            self.gl.load(profile_object=self.profile, parameter_container=None)
        # gl.load(None)

    # invalid load, another profile is loaded
    def test_internalLoaderLoad3b(self):
        self.profile.addChild(SubAbstractLoader)
        self.gl.load(profile_object=self.profile, parameter_container=None)

        profile = self.gl.createProfileInstance()
        profile.setRoot()

        global_profile = GlobalProfile('profile_name2', self.addon_information)
        profile.setGlobalProfile(global_profile)

        with pytest.raises(LoadException):
            self.gl.load(profile_object=profile, parameter_container=None)
        # gl.load(None)

    # # unload # #
    # valid unload
    def test_internalLoaderUnload4(self):
        self.profile.addChild(SubAbstractLoader)
        self.gl.load(profile_object=self.profile, parameter_container=None)
        self.gl.unload(profile_object=self.profile, parameter_container=None)
        assert self.addon_information.getLoadedProfileName() is None
        assert self.profile.getState() == STATE_UNLOADED

    # valid unload with error
    def test_internalLoaderUnload5(self):
        self.profile.addChild(SubAbstractUnloaderWithError)
        self.gl.load(profile_object=self.profile, parameter_container=None)
        with pytest.raises(ListOfException):
            self.gl.unload(
                profile_object=self.profile,
                parameter_container=None)
        assert self.addon_information.getLoadedProfileName() is None
        assert self.profile.getState() == STATE_UNLOADED_E

    # invalid unload
    def test_internalLoaderUnload6(self):
        self.profile.addChild(SubAbstractLoader)
        self.gl.load(profile_object=self.profile, parameter_container=None)
        self.gl.unload(profile_object=self.profile, parameter_container=None)
        assert self.addon_information.getLoadedProfileName() is None
        assert self.profile.getState() == STATE_UNLOADED
        with pytest.raises(UnloadException):
            self.gl.unload(
                profile_object=self.profile,
                parameter_container=None)


class RecordLoadOrderAbstractLoader(AbstractLoader):
    CLASSID = 1
    load_list = []
    unload_list = []

    @staticmethod
    def createProfileInstance():
        return DefaultProfile()

    @classmethod
    def load(cls, profile_object, parameter_container):
        cls.load_list.append(cls.CLASSID)

    @classmethod
    def unload(cls, profile_object, parameter_container):
        cls.unload_list.append(cls.CLASSID)


class RecordLoadOrderAbstractLoader2(RecordLoadOrderAbstractLoader):
    CLASSID = 2


class TestInternalLoaderPriority(object):

    def setup_method(self, method):
        self.gl = InternalLoader
        self.profile = self.gl.createProfileInstance()
        self.profile.setRoot()

        self.addon_information = AddonInformation('test.loader.parameter')
        global_profile = GlobalProfile('profile_name', self.addon_information)
        self.profile.setGlobalProfile(global_profile)

        del RecordLoadOrderAbstractLoader.load_list[:]
        del RecordLoadOrderAbstractLoader.unload_list[:]

    def test_differentPriorityInsertionOrder1(self):
        child_profile = self.profile.addChild(RecordLoadOrderAbstractLoader)
        child_profile.setLoadPriority(50)
        child_profile.setUnloadPriority(50)

        self.profile.addChild(RecordLoadOrderAbstractLoader2)

        self.gl.load(profile_object=self.profile, parameter_container=None)

        load_list = RecordLoadOrderAbstractLoader.load_list
        unload_list = RecordLoadOrderAbstractLoader.unload_list

        assert len(load_list) == 2
        assert load_list[0] == 1
        assert load_list[1] == 2

        self.gl.unload(profile_object=self.profile, parameter_container=None)

        assert len(unload_list) == 2
        assert unload_list[0] == 1
        assert unload_list[1] == 2

    def test_differentPriorityInsertionOrder2(self):
        self.profile.addChild(RecordLoadOrderAbstractLoader2)

        child_profile = self.profile.addChild(RecordLoadOrderAbstractLoader)
        child_profile.setLoadPriority(50)
        child_profile.setUnloadPriority(50)

        self.gl.load(profile_object=self.profile, parameter_container=None)

        load_list = RecordLoadOrderAbstractLoader.load_list
        unload_list = RecordLoadOrderAbstractLoader.unload_list

        assert len(load_list) == 2
        assert load_list[0] == 1
        assert load_list[1] == 2

        self.gl.unload(profile_object=self.profile, parameter_container=None)

        assert len(unload_list) == 2
        assert unload_list[0] == 1
        assert unload_list[1] == 2

    def test_differentPriorityInsertionOrder3(self):
        child_profile = self.profile.addChild(RecordLoadOrderAbstractLoader)
        child_profile.setLoadPriority(50)
        child_profile.setUnloadPriority(200)

        self.profile.addChild(RecordLoadOrderAbstractLoader2)

        self.gl.load(profile_object=self.profile, parameter_container=None)

        load_list = RecordLoadOrderAbstractLoader.load_list
        unload_list = RecordLoadOrderAbstractLoader.unload_list

        assert len(load_list) == 2
        assert load_list[0] == 1
        assert load_list[1] == 2

        self.gl.unload(profile_object=self.profile, parameter_container=None)

        assert len(unload_list) == 2
        assert unload_list[0] == 2
        assert unload_list[1] == 1

    def test_differentPriorityInsertionOrder4(self):
        self.profile.addChild(RecordLoadOrderAbstractLoader2)

        child_profile = self.profile.addChild(RecordLoadOrderAbstractLoader)
        child_profile.setLoadPriority(50)
        child_profile.setUnloadPriority(200)

        self.gl.load(profile_object=self.profile, parameter_container=None)

        load_list = RecordLoadOrderAbstractLoader.load_list
        unload_list = RecordLoadOrderAbstractLoader.unload_list

        assert len(load_list) == 2
        assert load_list[0] == 1
        assert load_list[1] == 2

        self.gl.unload(profile_object=self.profile, parameter_container=None)

        assert len(unload_list) == 2
        assert unload_list[0] == 2
        assert unload_list[1] == 1

    def test_differentPriorityInsertionOrder5(self):
        child_profile = self.profile.addChild(RecordLoadOrderAbstractLoader)
        child_profile.setLoadPriority(200)
        child_profile.setUnloadPriority(50)

        self.profile.addChild(RecordLoadOrderAbstractLoader2)

        self.gl.load(profile_object=self.profile, parameter_container=None)

        load_list = RecordLoadOrderAbstractLoader.load_list
        unload_list = RecordLoadOrderAbstractLoader.unload_list

        assert len(load_list) == 2
        assert load_list[0] == 2
        assert load_list[1] == 1

        self.gl.unload(profile_object=self.profile, parameter_container=None)

        assert len(unload_list) == 2
        assert unload_list[0] == 1
        assert unload_list[1] == 2

    def test_differentPriorityInsertionOrder6(self):
        self.profile.addChild(RecordLoadOrderAbstractLoader2)

        child_profile = self.profile.addChild(RecordLoadOrderAbstractLoader)
        child_profile.setLoadPriority(200)
        child_profile.setUnloadPriority(50)

        self.gl.load(profile_object=self.profile, parameter_container=None)

        load_list = RecordLoadOrderAbstractLoader.load_list
        unload_list = RecordLoadOrderAbstractLoader.unload_list

        assert len(load_list) == 2
        assert load_list[0] == 2
        assert load_list[1] == 1

        self.gl.unload(profile_object=self.profile, parameter_container=None)

        assert len(unload_list) == 2
        assert unload_list[0] == 1
        assert unload_list[1] == 2
