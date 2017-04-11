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
from pyshell.arg.accessor.command import CommandAccessor
from pyshell.arg.accessor.container import ContainerAccessor
from pyshell.arg.accessor.context import ContextDynamicAccessor
from pyshell.arg.accessor.context import ContextManagerAccessor
from pyshell.arg.accessor.engine import EngineAccessor
from pyshell.arg.accessor.environment import EnvironmentDynamicAccessor
from pyshell.arg.accessor.environment import EnvironmentManagerAccessor
from pyshell.arg.accessor.exchange import ExchangeAccessor
from pyshell.arg.accessor.key import KeyDynamicAccessor
from pyshell.arg.accessor.key import KeyManagerAccessor
from pyshell.arg.accessor.procedure import ProcedureDynamicAccessor
from pyshell.arg.accessor.procedure import ProcedureManagerAccessor
from pyshell.arg.accessor.variable import VariableDynamicAccessor
from pyshell.arg.accessor.variable import VariableManagerAccessor


class DefaultAccessor(object):
    _lock = Lock()

    DEFAULTACCESSOR_DICO = {
        AddonAccessor.getTypeName(): None,
        CommandAccessor.getTypeName(): None,
        ContainerAccessor.getTypeName(): None,
        ContextDynamicAccessor.getTypeName(): None,
        ContextManagerAccessor.getTypeName(): None,
        EngineAccessor.getTypeName(): None,
        EnvironmentDynamicAccessor.getTypeName(): None,
        EnvironmentManagerAccessor.getTypeName(): None,
        ExchangeAccessor.getTypeName(): None,
        KeyDynamicAccessor.getTypeName(): None,
        KeyManagerAccessor.getTypeName(): None,
        ProcedureDynamicAccessor.getTypeName(): None,
        ProcedureManagerAccessor.getTypeName(): None,
        VariableDynamicAccessor.getTypeName(): None,
        VariableManagerAccessor.getTypeName(): None}

    @classmethod
    def _getAccessorInstance(cls, classdef):
        key = classdef.getTypeName()
        if cls.DEFAULTACCESSOR_DICO[key] is None:
            with cls._lock:
                if cls.DEFAULTACCESSOR_DICO[key] is None:
                    cls.DEFAULTACCESSOR_DICO[key] = classdef()

        return cls.DEFAULTACCESSOR_DICO[key]

    @classmethod
    def getAddon(cls):
        return cls._getAccessorInstance(AddonAccessor)

    @classmethod
    def getCommand(cls):
        return cls._getAccessorInstance(CommandAccessor)

    @classmethod
    def getContainer(cls):
        return cls._getAccessorInstance(ContainerAccessor)

    @classmethod
    def getEngine(cls):
        return cls._getAccessorInstance(EngineAccessor)

    @classmethod
    def getContext(cls):
        return cls._getAccessorInstance(ContextDynamicAccessor)

    @classmethod
    def getEnvironment(cls):
        return cls._getAccessorInstance(EnvironmentDynamicAccessor)

    @classmethod
    def getExchange(cls):
        return cls._getAccessorInstance(ExchangeAccessor)

    @classmethod
    def getKey(cls):
        return cls._getAccessorInstance(KeyDynamicAccessor)

    @classmethod
    def getVariable(cls):
        return cls._getAccessorInstance(VariableDynamicAccessor)

    @classmethod
    def getProcedure(cls):
        return cls._getAccessorInstance(ProcedureDynamicAccessor)

    @classmethod
    def getContextManager(cls):
        return cls._getAccessorInstance(ContextManagerAccessor)

    @classmethod
    def getEnvironmentManager(cls):
        return cls._getAccessorInstance(EnvironmentManagerAccessor)

    @classmethod
    def getKeyManager(cls):
        return cls._getAccessorInstance(KeyManagerAccessor)

    @classmethod
    def getVariableManager(cls):
        return cls._getAccessorInstance(VariableManagerAccessor)

    @classmethod
    def getProcedureManager(cls):
        return cls._getAccessorInstance(ProcedureManagerAccessor)
