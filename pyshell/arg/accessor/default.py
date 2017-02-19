#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2017  Jonathan Delvaux <pyshell@djoproject.net>

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

from threading import Lock

from pyshell.arg.accessor.addon import AddonAccessor
from pyshell.arg.accessor.container import ContainerAccessor
from pyshell.arg.accessor.context import ContextDynamicAccessor
from pyshell.arg.accessor.engine import EngineAccessor
from pyshell.arg.accessor.environment import EnvironmentDynamicAccessor
from pyshell.arg.accessor.key import KeyDynamicAccessor
from pyshell.arg.accessor.variable import VariableDynamicAccessor


class DefaultAccessor(object):
    _lock = Lock()

    DEFAULTACCESSOR_DICO = {
        AddonAccessor.getTypeName(): None,
        ContainerAccessor.getTypeName(): None,
        ContextDynamicAccessor.getTypeName(): None,
        EngineAccessor.getTypeName(): None,
        EnvironmentDynamicAccessor.getTypeName(): None,
        KeyDynamicAccessor.getTypeName(): None,
        VariableDynamicAccessor.getTypeName(): None}

    @classmethod
    def _getAccessorInstance(cls, classdef):
        key = classdef.getTypeName()
        if cls.DEFAULTACCESSOR_DICO[key] is None:
            with cls._lock:
                if cls.DEFAULTACCESSOR_DICO[key] is None:
                    cls.DEFAULTACCESSOR_DICO[key] = classdef()
                    cls.DEFAULTACCESSOR_DICO[key].setDefaultValueEnable(False)

        return cls.DEFAULTACCESSOR_DICO[key]

    @classmethod
    def getAddon(cls):
        return cls._getAccessorInstance(AddonAccessor)

    @classmethod
    def getContainer(cls):
        return cls._getAccessorInstance(ContainerAccessor)

    @classmethod
    def getContext(cls):
        return cls._getAccessorInstance(ContextDynamicAccessor)

    @classmethod
    def getEngine(cls):
        return cls._getAccessorInstance(EngineAccessor)

    @classmethod
    def getEnvironment(cls):
        return cls._getAccessorInstance(EnvironmentDynamicAccessor)

    @classmethod
    def getKey(cls):
        return cls._getAccessorInstance(KeyDynamicAccessor)

    @classmethod
    def getVariable(cls):
        return cls._getAccessorInstance(VariableDynamicAccessor)
