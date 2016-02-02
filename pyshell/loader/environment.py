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

from pyshell.loader.parameter import registerAddValues, \
                                     registerSet, ParameterAbstractLoader
from pyshell.system.environment import EnvironmentParameter
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME


def registerAddValuesToEnvironment(envKey, value, subLoaderName=None):
    registerAddValues(envKey, value, EnvironmentLoader, subLoaderName)


def registerSetEnvironment(envKey,
                           env,
                           noErrorIfKeyExist=False,
                           override=False,
                           subLoaderName=None):
    registerSet(envKey,
                env,
                EnvironmentLoader,
                EnvironmentParameter,
                noErrorIfKeyExist,
                override,
                subLoaderName)


class EnvironmentLoader(ParameterAbstractLoader):
    def __init__(self):
        ParameterAbstractLoader.__init__(self, ENVIRONMENT_ATTRIBUTE_NAME)
