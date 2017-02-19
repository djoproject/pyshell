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

from pyshell.arg.checker.default import DefaultChecker
from pyshell.register.dependency import _localGetAndInitCallerModule
from pyshell.register.dependency import registerDependOnAddon
from pyshell.register.dependency import setDependencyLoadPriority
from pyshell.register.dependency import setDependencyUnloadPriority
from pyshell.register.loader.dependency import DependencyLoader
from pyshell.register.profile.dependency import DependencyLoaderProfile
from pyshell.register.profile.exception import RegisterException
from pyshell.register.utils.module import getNearestModule
from pyshell.utils.constants import DEFAULT_PROFILE_NAME


DEFAULT_CHECKER = DefaultChecker.getArg()


def loader(profile=None):
    return _localGetAndInitCallerModule(profile)


class TestDependency(object):

    def teardown_method(self, method):
        mod = getNearestModule()
        if hasattr(mod, "_loaders"):
            delattr(mod, "_loaders")

    def preChecks(self):
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")
        return mod

    def postChecks(self, profile=DEFAULT_PROFILE_NAME):
        mod = getNearestModule()
        assert hasattr(mod, "_loaders")
        _loaders = mod._loaders
        assert _loaders.hasProfile(profile)
        assert _loaders.isLoaderBindedToProfile(DependencyLoader, profile)
        profile_object = _loaders.getLoaderProfile(DependencyLoader, profile)
        assert isinstance(profile_object, DependencyLoaderProfile)
        return profile_object

    def test_setDependencyLoadPriorityDefaultProfile(self):
        self.preChecks()
        setDependencyLoadPriority(66)
        profile = self.postChecks()
        assert profile.getLoadPriority() == 66

    def test_setDependencyUnloadPriorityDefaultProfile(self):
        self.preChecks()
        setDependencyUnloadPriority(77)
        profile = self.postChecks()
        assert profile.getUnloadPriority() == 77

    def test_setDependencyLoadPriorityCustomProfile(self):
        self.preChecks()
        setDependencyLoadPriority(44, profile="plop")
        profile = self.postChecks("plop")
        assert profile.getLoadPriority() == 44

    def test_setDependencyUnloadPriorityCustomProfile(self):
        self.preChecks()
        setDependencyUnloadPriority(55, profile="plop")
        profile = self.postChecks("plop")
        assert profile.getUnloadPriority() == 55

    # # registerDependOnAddon # #

    # registerDependOnAddon with invalid dependancy_name, profile None
    def testRegisterDependOnAddon1(self):
        with pytest.raises(RegisterException):
            registerDependOnAddon(dependancy_name=object(),
                                  dependancy_profile=None,
                                  profile=None)

    # registerDependOnAddon with str dependancy_name, profile None
    def testRegisterDependOnAddon2(self):
        self.preChecks()
        registerDependOnAddon(dependancy_name="plop",
                              dependancy_profile=None,
                              profile=None)
        l = self.postChecks()
        assert "plop" in l.dep
        assert l.dep["plop"] is None

    # registerDependOnAddon with unicode dependancy_name, profile None
    def testRegisterDependOnAddon3(self):
        self.preChecks()
        registerDependOnAddon(dependancy_name=u"plop",
                              dependancy_profile=None,
                              profile=None)
        l = self.postChecks()
        assert u"plop" in l.dep
        assert l.dep[u"plop"] is None

    # registerDependOnAddon with invalid dependancy_profile, profile None
    def testRegisterDependOnAddon4(self):
        with pytest.raises(RegisterException):
            registerDependOnAddon(dependancy_name="plop",
                                  dependancy_profile=object(),
                                  profile=None)

    # registerDependOnAddon with str dependancy_profile, profile None
    def testRegisterDependOnAddon5(self):
        self.preChecks()
        registerDependOnAddon(dependancy_name="plop",
                              dependancy_profile="tutu",
                              profile=None)
        l = self.postChecks()
        assert "plop" in l.dep
        assert l.dep["plop"] is "tutu"

    # registerDependOnAddon with unicode dependancy_profile, profile None
    def testRegisterDependOnAddon6(self):
        self.preChecks()
        registerDependOnAddon(dependancy_name=u"plop",
                              dependancy_profile=u"tutu",
                              profile=None)
        l = self.postChecks()
        assert u"plop" in l.dep
        assert l.dep[u"plop"] is u"tutu"

    # registerDependOnAddon with invalid dependancy_name, profile not None
    def testRegisterDependOnAddon7(self):
        with pytest.raises(RegisterException):
            registerDependOnAddon(dependancy_name=object(),
                                  dependancy_profile=None,
                                  profile="ahah")

    # registerDependOnAddon with str dependancy_name, profile not None
    def testRegisterDependOnAddon8(self):
        self.preChecks()
        registerDependOnAddon(dependancy_name="plop",
                              dependancy_profile=None,
                              profile="ahah")
        l = self.postChecks("ahah")
        assert "plop" in l.dep
        assert l.dep["plop"] is None

    # registerDependOnAddon with unicode dependancy_name, profile not None
    def testRegisterDependOnAddon9(self):
        self.preChecks()
        registerDependOnAddon(dependancy_name=u"plop",
                              dependancy_profile=None,
                              profile="ahah")
        l = self.postChecks("ahah")
        assert u"plop" in l.dep
        assert l.dep[u"plop"] is None

    # registerDependOnAddon with invalid dependancy_profile, profile not None
    def testRegisterDependOnAddon10(self):
        with pytest.raises(RegisterException):
            registerDependOnAddon(dependancy_name="plop",
                                  dependancy_profile=object(),
                                  profile="uhuh")

    # registerDependOnAddon with str dependancy_profile, profile not None
    def testRegisterDependOnAddon11(self):
        self.preChecks()
        registerDependOnAddon(dependancy_name="plop",
                              dependancy_profile="tutu",
                              profile="uhuh")
        l = self.postChecks("uhuh")
        assert u"plop" in l.dep
        assert l.dep["plop"] == "tutu"

    # registerDependOnAddon with unicode dependancy_profile, profile not None
    def testRegisterDependOnAddon12(self):
        self.preChecks()
        registerDependOnAddon(dependancy_name=u"plop",
                              dependancy_profile=u"tutu",
                              profile="uhuh")
        l = self.postChecks("uhuh")
        assert u"plop" in l.dep
        assert l.dep[u"plop"] == u"tutu"
