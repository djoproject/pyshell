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

from pyshell.register.loader.abstractloader import AbstractLoader
from pyshell.register.loader.exception import LoadException
from pyshell.register.loader.exception import UnloadException
from pyshell.register.loader.root import RootLoader
from pyshell.register.profile.default import DefaultProfile
from pyshell.register.profile.root import RootProfile
from pyshell.register.utils.addon import AddonInformation
from pyshell.utils.exception import ListOfException


class SubAbstractLoader(AbstractLoader):

    @staticmethod
    def createProfileInstance(root_profile):
        return DefaultProfile(root_profile)

    @classmethod
    def load(cls, profile_object, parameter_container=None):
        pass

    @classmethod
    def unload(cls, profile_object, parameter_container=None):
        pass


class SubAbstractLoaderWithError(AbstractLoader):

    @staticmethod
    def createProfileInstance(root_profile):
        return DefaultProfile(root_profile)

    @classmethod
    def load(cls, profile_object, parameter_container=None):
        raise Exception("errroooorrr !")

    @classmethod
    def unload(cls, profile_object, parameter_container=None):
        pass


class SubAbstractUnloaderWithError(AbstractLoader):

    @staticmethod
    def createProfileInstance(root_profile):
        return DefaultProfile(root_profile)

    @classmethod
    def load(cls, profile_object, parameter_container=None):
        pass

    @classmethod
    def unload(cls, profile_object, parameter_container=None):
        raise Exception("errroooorrr !")


class TestRootLoader(object):
    def setup_method(self, method):
        self.gl = RootLoader
        self.addon_information = AddonInformation('test.loader.parameter')
        self.profile = self.gl.createProfileInstance(None)
        self.profile.setName("profile_name")
        self.profile.setAddonInformations(self.addon_information)

    def test_createProfileInstance(self):
        assert isinstance(self.profile, RootProfile)

    # # load # #
    # valid load
    def test_internalLoaderLoad1(self):
        self.profile.addChild(SubAbstractLoader)
        self.gl.load(profile_object=self.profile, parameter_container=None)
        assert self.addon_information.getLastProfileUsed() is self.profile
        assert self.profile.isLoaded() and not self.profile.hasError()

    # valid load with error
    def test_internalLoaderLoad2(self):
        self.profile.addChild(SubAbstractLoaderWithError)
        with pytest.raises(ListOfException):
            self.gl.load(profile_object=self.profile, parameter_container=None)
        assert self.addon_information.getLastProfileUsed() is self.profile
        assert self.profile.isLoaded() and self.profile.hasError()

    # invalid load
    def test_internalLoaderLoad3(self):
        self.profile.addChild(SubAbstractLoader)
        self.gl.load(profile_object=self.profile, parameter_container=None)
        assert self.addon_information.getLastProfileUsed() is self.profile
        assert self.profile.isLoaded() and not self.profile.hasError()
        with pytest.raises(LoadException):
            self.gl.load(profile_object=self.profile, parameter_container=None)

    # invalid load, another profile is loaded
    def test_internalLoaderLoad3b(self):
        self.profile.addChild(SubAbstractLoader)
        self.gl.load(profile_object=self.profile, parameter_container=None)

        profile = self.gl.createProfileInstance(None)
        profile.setName("profile_name2")
        profile.setAddonInformations(self.addon_information)

        with pytest.raises(LoadException):
            self.gl.load(profile_object=profile, parameter_container=None)
        # gl.load(None)

    # # unload # #
    # valid unload
    def test_internalLoaderUnload4(self):
        self.profile.addChild(SubAbstractLoader)
        self.gl.load(profile_object=self.profile, parameter_container=None)
        self.gl.unload(profile_object=self.profile, parameter_container=None)
        assert self.addon_information.getLastProfileUsed() is self.profile
        assert self.profile.isUnloaded() and not self.profile.hasError()

    # valid unload with error
    def test_internalLoaderUnload5(self):
        self.profile.addChild(SubAbstractUnloaderWithError)
        self.gl.load(profile_object=self.profile, parameter_container=None)
        with pytest.raises(ListOfException):
            self.gl.unload(
                profile_object=self.profile,
                parameter_container=None)
        assert self.addon_information.getLastProfileUsed() is self.profile
        assert self.profile.isUnloaded() and self.profile.hasError()

    # invalid unload
    def test_internalLoaderUnload6(self):
        self.profile.addChild(SubAbstractLoader)
        self.gl.load(profile_object=self.profile, parameter_container=None)
        self.gl.unload(profile_object=self.profile, parameter_container=None)
        assert self.addon_information.getLastProfileUsed() is self.profile
        assert self.profile.isUnloaded() and not self.profile.hasError()
        with pytest.raises(UnloadException):
            self.gl.unload(
                profile_object=self.profile,
                parameter_container=None)
