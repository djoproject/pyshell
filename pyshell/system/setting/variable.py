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

from pyshell.system.setting.environment import EnvironmentSettings
from pyshell.system.setting.parameter import ParameterGlobalSettings
from pyshell.system.setting.parameter import ParameterLocalSettings
from pyshell.utils.exception import ParameterException


class VariableSettings(EnvironmentSettings):
    def __init__(self):
        EnvironmentSettings.__init__(self, checker=None)

    def getProperties(self):
        return {}

    def setChecker(self, checker=None):
        if self.getChecker() is not None:
            excmsg = "(%s) setChecker, not allowed on key settings"
            excmsg %= self.__class__.__name__
            raise ParameterException(excmsg)

        EnvironmentSettings.setChecker(self, checker)

    def setListChecker(self, state):
        if not state:
            excmsg = "(%s) setListChecker, not allowed on variable settings"
            excmsg %= self.__class__.__name__
            raise ParameterException(excmsg)

    def clone(self):
        return VariableSettings()

    def _buildOpposite(self):
        clazz = self._getOppositeSettingClass()
        return clazz()


class VariableLocalSettings(ParameterLocalSettings, VariableSettings):
    isReadOnly = VariableSettings.isReadOnly  # always return False
    isRemovable = VariableSettings.isRemovable  # always return True
    getProperties = VariableSettings.getProperties  # always return {}

    @staticmethod
    def _getOppositeSettingClass():
        return VariableGlobalSettings

    def __init__(self):
        ParameterLocalSettings.__init__(self, read_only=False, removable=True)
        VariableSettings.__init__(self)

    def clone(self):
        return VariableLocalSettings()


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
        VariableSettings.__init__(self)

    def clone(self):
        return VariableGlobalSettings(transient=self.isTransient())
