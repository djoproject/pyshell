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

from pyshell.arg.checker.default import DefaultChecker
from pyshell.register.exception import LoaderException
from pyshell.register.loader.dependency import DependencyLoader
from pyshell.register.loader.exception import LoadException
from pyshell.register.profile.dependency import DependencyLoaderProfile
from pyshell.register.profile.root import RootProfile
from pyshell.register.utils.addon import AddonLoader
from pyshell.register.utils.parent import ParentAddon
from pyshell.utils.constants import DEFAULT_PROFILE_NAME
from pyshell.utils.exception import ListOfException


DEFAULT_CHECKER = DefaultChecker.getArg()


class TestDependencyLoader(object):
    def setup_method(self, method):
        self.root_profile = RootProfile()
        self.root_profile.setName("profile_name")
        self.profile = DependencyLoaderProfile(self.root_profile)
        self.pc = ParentAddon()

    def test_createProfileInstance(self):
        profile = DependencyLoader.createProfileInstance(self.root_profile)
        assert isinstance(profile, DependencyLoaderProfile)

    def test_noneContainer(self):
        dl = DependencyLoader
        self.profile.addDependency("addons.plop", None)

        with pytest.raises(LoadException):
            dl.load(profile_object=self.profile, parameter_container=None)

    # __init__
    def testDependencyLoaderInit(self):
        assert hasattr(DependencyLoader, "__init__")
        assert hasattr(DependencyLoader.__init__, "__call__")
        with pytest.raises(LoaderException):
            DependencyLoader()

    # load with zero dep
    def testDependencyLoaderLoad1(self):
        dl = DependencyLoader
        dl.load(profile_object=self.profile, parameter_container=self.pc)

    # load with dep with dependancy_name not satisfied
    def testDependencyLoaderLoad3(self):
        dl = DependencyLoader
        self.profile.addDependency("addons.plop", None)
        with pytest.raises(ListOfException) as loe:
            dl.load(profile_object=self.profile, parameter_container=self.pc)

        assert len(loe.value.exceptions) is 1
        assert isinstance(loe.value.exceptions[0], LoadException)

    # load with dep, with dependancy_name satisfied, dependancy_profile not
    # satisfied
    def testDependencyLoaderLoad4(self):
        dl = DependencyLoader
        self.profile.addDependency("addons.plop", "profile.plap")
        loader = AddonLoader("test.loader.dependency")
        loader.createProfile(DEFAULT_PROFILE_NAME)
        loader.load(profile_name=DEFAULT_PROFILE_NAME, container=self.pc)

        self.pc.getAddonManager()["addons.plop"] = loader
        with pytest.raises(ListOfException) as loe:
            dl.load(profile_object=self.profile, parameter_container=self.pc)

        assert len(loe.value.exceptions) is 1
        assert isinstance(loe.value.exceptions[0], LoadException)

    # load with dep, with dependancy_name satisfied, dependancy_profile
    # satisfied, loaded
    def testDependencyLoaderLoad5(self):
        dl = DependencyLoader
        self.profile.addDependency("addons.plop", "profile.plap")
        loader = AddonLoader("test.loader.dependency")
        loader.createProfile("profile.plap")
        loader.load(profile_name="profile.plap", container=self.pc)
        self.pc.getAddonManager()["addons.plop"] = loader
        dl.load(profile_object=self.profile, parameter_container=self.pc)

    def test_successCaseWithNoneProfile(self):
        dl = DependencyLoader
        self.profile.addDependency("addons.plop")
        loader = AddonLoader("test.loader.dependency")
        loader.createProfile(None)
        loader.load(profile_name=None, container=self.pc)
        self.pc.getAddonManager()["addons.plop"] = loader
        dl.load(profile_object=self.profile, parameter_container=self.pc)

    # load with dep with dependancy_name satisfied, dependancy_profile
    # satisfied, not loaded
    def testDependencyLoaderLoad6(self):
        dl = DependencyLoader
        self.profile.addDependency("addons.plop", "profile.plap")
        loader = AddonLoader("test.loader.dependency")
        loader.createProfile("profile.plap")
        loader.load(profile_name="profile.plap", container=self.pc)
        loader.unload(profile_name="profile.plap", container=self.pc)
        self.pc.getAddonManager()["addons.plop"] = loader
        with pytest.raises(ListOfException) as loe:
            dl.load(profile_object=self.profile, parameter_container=self.pc)

        assert len(loe.value.exceptions) is 1
        assert isinstance(loe.value.exceptions[0], LoadException)
