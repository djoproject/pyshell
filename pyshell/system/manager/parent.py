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

import threading

from pyshell.system.manager.abstract import AbstractParentManager
from pyshell.system.manager.context import ContextParameterManager
from pyshell.system.manager.environment import EnvironmentParameterManager
from pyshell.system.manager.key import CryptographicKeyParameterManager
from pyshell.system.manager.procedure import ProcedureParameterManager
from pyshell.system.manager.variable import VariableParameterManager
from pyshell.utils.abstract.flushable import Flushable
from pyshell.utils.constants import DEFAULT_GROUP_NAME
from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.raises import raiseIfNotString


class ParentManager(AbstractParentManager, Flushable):
    def __init__(self):
        self._environement = EnvironmentParameterManager(self)
        self._context = ContextParameterManager(self)
        self._key = CryptographicKeyParameterManager(self)
        self._procedure = ProcedureParameterManager(self)
        self._variable = VariableParameterManager(self)

        self._managers = (self._environement,
                          self._context,
                          self._key,
                          self._procedure,
                          self._variable)

        self._group_name = DEFAULT_GROUP_NAME

    def getEnvironmentManager(self):
        return self._environement

    def getContextManager(self):
        return self._context

    def getKeyManager(self):
        return self._key

    def getProcedureManager(self):
        return self._procedure

    def getVariableManager(self):
        return self._variable

    def flush(self):
        for m in self._managers:
            m.flush()

    def getCurrentId(self):
        return threading.current_thread().ident

    def setDefaultGroupName(self, group_name):
        raiseIfNotString(group_name,
                         "group_name",
                         DefaultPyshellException,
                         "setDefaultGroupName",
                         self.__class__.__name__)

        self._group_name = group_name

    def getDefaultGroupName(self):
        return self._group_name

    def checkForSetGlobalParameter(self, group_name, loader_name):
        pass  # do nothing

    def checkForUnsetGlobalParameter(self, group_name, loader_name):
        pass  # do nothing
