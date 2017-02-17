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

from pyshell.register.file import enableConfigSaving
from pyshell.register.loader.file import FileLoader
from pyshell.register.utils.addon import AddonLoader
from pyshell.register.utils.module import getNearestModule


class TestFileRegister(object):

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
        assert _loaders.isLoaderBindedToProfile(FileLoader, profile)
        profile_object = _loaders.getLoaderProfile(FileLoader, profile)
        return profile_object

    def test_enableConfigSavingDefaultProfile(self):
        self.preTest()
        enableConfigSaving()
        self.postTest()

    def test_enableConfigSavingCustomProfile(self):
        self.preTest()
        enableConfigSaving(profile="toto")
        self.postTest(profile="toto")
