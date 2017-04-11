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

from pyshell.arg.checker.default import DefaultChecker
from pyshell.system.setting.environment import EnvironmentGlobalSettings
from pyshell.system.setting.environment import EnvironmentLocalSettings
from pyshell.system.setting.environment import EnvironmentSettings
from pyshell.utils.constants import SETTING_PROPERTY_CHECKER
from pyshell.utils.constants import SETTING_PROPERTY_CHECKERLIST
from pyshell.utils.exception import ParameterException


class KeySettings(EnvironmentSettings):
    def __init__(self):
        EnvironmentSettings.__init__(self, checker=DefaultChecker.getKey())

    def setChecker(self, checker=None):
        if self.getChecker() is not None:
            excmsg = "(%s) setChecker, not allowed on key settings"
            excmsg %= self.__class__.__name__
            raise ParameterException(excmsg)

        EnvironmentSettings.setChecker(self, checker)

    def setListChecker(self, state):
        if state:
            excmsg = "(%s) setListChecker, not allowed on key settings"
            excmsg %= self.__class__.__name__
            raise ParameterException(excmsg)

    def _buildOpposite(self):
        clazz = self._getOppositeSettingClass()
        read_only = self.isReadOnly()
        removable = self.isRemovable()

        return clazz(read_only=read_only, removable=removable)

    def getProperties(self):
        return {}

    def clone(self):
        return KeySettings()


class KeyLocalSettings(EnvironmentLocalSettings, KeySettings):
    @staticmethod
    def _getOppositeSettingClass():
        return KeyGlobalSettings

    def __init__(self, read_only=False, removable=True):
        EnvironmentLocalSettings.__init__(self,
                                          read_only=read_only,
                                          removable=removable)
        KeySettings.__init__(self)

    def getProperties(self):
        props = EnvironmentLocalSettings.getProperties(self)
        props.update(KeySettings.getProperties(self))
        del props[SETTING_PROPERTY_CHECKER]
        del props[SETTING_PROPERTY_CHECKERLIST]
        return props

    def clone(self):
        return KeyLocalSettings(read_only=self.isReadOnly(),
                                removable=self.isRemovable())


class KeyGlobalSettings(EnvironmentGlobalSettings, KeySettings):
    @staticmethod
    def _getOppositeSettingClass():
        return KeyLocalSettings

    def __init__(self, read_only=False, removable=True, transient=False):
        EnvironmentGlobalSettings.__init__(self,
                                           read_only=read_only,
                                           removable=removable,
                                           transient=transient)
        KeySettings.__init__(self)

    def getProperties(self):
        props = EnvironmentGlobalSettings.getProperties(self)
        props.update(KeySettings.getProperties(self))
        del props[SETTING_PROPERTY_CHECKER]
        del props[SETTING_PROPERTY_CHECKERLIST]
        return props

    def clone(self):
        return KeyGlobalSettings(read_only=self.isReadOnly(),
                                 removable=self.isRemovable(),
                                 transient=self.isTransient())
