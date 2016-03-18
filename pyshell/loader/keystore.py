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

from pyshell.loader.parameter import ParameterAbstractLoader
from pyshell.loader.parameter import registerSet
from pyshell.loader.parameter import setLoaderPriority
from pyshell.system.key import CryptographicKeyParameter
from pyshell.utils.constants import KEY_ATTRIBUTE_NAME


def setKeyLoaderPriority(value, sub_loader_name=None):
    setLoaderPriority(value, KeyLoader, sub_loader_name)


def registerSetKey(key,
                   obj,
                   no_error_if_key_exist=False,
                   override=False,
                   sub_loader_name=None):
    registerSet(key,
                obj,
                KeyLoader,
                CryptographicKeyParameter,
                no_error_if_key_exist,
                override,
                sub_loader_name)


class KeyLoader(ParameterAbstractLoader):
    def __init__(self):
        ParameterAbstractLoader.__init__(self, KEY_ATTRIBUTE_NAME)
