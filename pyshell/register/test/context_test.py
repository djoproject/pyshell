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

from pyshell.register.context import registerContext
from pyshell.register.context import setContextLoadPriority
from pyshell.register.context import setContextUnloadPriority
from pyshell.register.loader.context import ContextLoader
from pyshell.register.utils.addon import AddonLoader
from pyshell.register.utils.module import getNearestModule
from pyshell.system.parameter.context import ContextParameter


class TestContextRegister(object):

    def teardown_method(self, method):
        mod = getNearestModule()
        if hasattr(mod, "_loaders"):
            delattr(mod, "_loaders")

    def preTest(self):
        mod = getNearestModule()
        assert not hasattr(mod, "_loaders")
        return mod

    def postTest(self, profile=None):
        mod = getNearestModule()
        assert hasattr(mod, "_loaders")
        _loaders = mod._loaders
        assert isinstance(_loaders, AddonLoader)
        assert _loaders.hasProfile(profile)
        assert _loaders.isLoaderBindedToProfile(ContextLoader, profile)
        profile_object = _loaders.getLoaderProfile(ContextLoader, profile)
        return profile_object

    def test_setContextLoadPriorityDefaultProfile(self):
        self.preTest()
        setContextLoadPriority(66)
        profile = self.postTest()
        assert profile.getLoadPriority() == 66

    def test_setContextUnloadPriorityDefaultProfile(self):
        self.preTest()
        setContextUnloadPriority(77)
        profile = self.postTest()
        assert profile.getUnloadPriority() == 77

    def test_registerContextDefaultProfile(self):
        self.preTest()
        c = ContextParameter(['aa', 'bb'])
        registerContext("toto.context", c)
        profile = self.postTest()
        assert "toto.context" in profile.parameter_to_set
        assert profile.parameter_to_set["toto.context"] is c

    def test_setContextLoadPriorityCustomProfile(self):
        self.preTest()
        setContextLoadPriority(44, profile="plop")
        profile = self.postTest("plop")
        assert profile.getLoadPriority() == 44

    def test_setContextUnloadPriorityCustomProfile(self):
        self.preTest()
        setContextUnloadPriority(55, profile="plop")
        profile = self.postTest("plop")
        assert profile.getUnloadPriority() == 55

    def test_registerContextCustomProfile(self):
        self.preTest()
        c = ContextParameter(['aa', 'bb'])
        registerContext("titi.context", c, profile="plop")
        profile = self.postTest("plop")
        assert "titi.context" in profile.parameter_to_set
        assert profile.parameter_to_set["titi.context"] is c
