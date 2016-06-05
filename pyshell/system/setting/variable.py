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

from pyshell.system.setting.environment import DEFAULT_CHECKER
from pyshell.system.setting.environment import EnvironmentSettings
from pyshell.system.setting.parameter import ParameterGlobalSettings
from pyshell.system.setting.parameter import ParameterLocalSettings


class VariableSettings(EnvironmentSettings):
    def getProperties(self):
        return ()

    def getChecker(self):
        return DEFAULT_CHECKER

    def setChecker(self, checker=None):
        pass

    def setListChecker(self, state):
        pass  # do nothing, checker must always be a list type

    def clone(self, parent=None):
        if parent is None:
            parent = VariableSettings(checker=None)

        return EnvironmentSettings.clone(self, parent)

    def _buildOpposite(self):
        clazz = self._getOppositeSettingClass()
        return clazz()


class VariableLocalSettings(ParameterLocalSettings, VariableSettings):
    isReadOnly = VariableSettings.isReadOnly  # always return False
    isRemovable = VariableSettings.isRemovable  # always return True
    getProperties = VariableSettings.getProperties  # always return ()

    @staticmethod
    def _getOppositeSettingClass():
        return VariableGlobalSettings

    def __init__(self):
        ParameterLocalSettings.__init__(self, read_only=False, removable=True)
        VariableSettings.__init__(self, checker=None)

    def clone(self, parent=None):
        if parent is None:
            parent = VariableLocalSettings()

        VariableSettings.clone(self, parent)

        return ParameterLocalSettings.clone(self, parent)


class VariableGlobalSettings(ParameterGlobalSettings, VariableSettings):
    isReadOnly = VariableSettings.isReadOnly  # always return False
    isRemovable = VariableSettings.isRemovable  # always return True
    getProperties = VariableSettings.getProperties  # always return ()

    @staticmethod
    def _getOppositeSettingClass():
        return VariableLocalSettings

    def __init__(self, transient=False):
        ParameterGlobalSettings.__init__(self,
                                         read_only=False,
                                         removable=True,
                                         transient=transient)
        VariableSettings.__init__(self, checker=None)

    def clone(self, parent=None):
        if parent is None:
            parent = VariableGlobalSettings(transient=self.isTransient())

        VariableSettings.clone(self, parent)

        return ParameterGlobalSettings.clone(self, parent)
