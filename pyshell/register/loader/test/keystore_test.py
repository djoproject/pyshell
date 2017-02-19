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

from pyshell.register.loader.keystore import KeyLoader
from pyshell.register.profile.parameter import ParameterLoaderProfile
from pyshell.register.profile.root import RootProfile
from pyshell.system.manager.key import CryptographicKeyParameterManager
from pyshell.system.manager.parent import ParentManager
from pyshell.system.parameter.key import CryptographicKeyParameter
from pyshell.utils.constants import KEY_ATTRIBUTE_NAME


class TestKeystore(object):
    def test_getManagerName(self):
        assert KeyLoader.getManagerName() is KEY_ATTRIBUTE_NAME

    def test_createProfileInstance(self):
        root_profile = RootProfile()
        root_profile.setName("profile_name")
        profile = KeyLoader.createProfileInstance(root_profile)
        assert isinstance(profile, ParameterLoaderProfile)
        assert profile.parameter_definition is CryptographicKeyParameter

    def test_getManager(self):
        parent_manager = ParentManager()
        manager1 = KeyLoader.getManager(parent_manager)
        assert isinstance(manager1, CryptographicKeyParameterManager)
        manager2 = KeyLoader.getManager(parent_manager)
        assert manager1 is manager2
