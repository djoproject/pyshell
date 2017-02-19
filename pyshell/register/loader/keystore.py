#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.register.loader.parameter import ParameterAbstractLoader
from pyshell.register.profile.parameter import ParameterLoaderProfile
from pyshell.system.parameter.key import CryptographicKeyParameter
from pyshell.utils.constants import KEY_ATTRIBUTE_NAME


class KeyLoader(ParameterAbstractLoader):
    @staticmethod
    def getManagerName():
        return KEY_ATTRIBUTE_NAME

    @staticmethod
    def getManager(container):
        return container.getKeyManager()

    @staticmethod
    def createProfileInstance(root_profile):
        return ParameterLoaderProfile(CryptographicKeyParameter, root_profile)
