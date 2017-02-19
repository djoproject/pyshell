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
from pyshell.system.setting.environment import EnvironmentSettings
from pyshell.system.setting.parameter import ParameterGlobalSettings
from pyshell.system.setting.parameter import ParameterLocalSettings
from pyshell.system.setting.parameter import ParameterSettings


class KeySettings(EnvironmentSettings):
    def getChecker(self):
        return DefaultChecker.getKey()

    def setChecker(self, checker=None):
        pass

    def setListChecker(self, state):
        pass  # do nothing, checker must never be a list type

    def getProperties(self):
        # use the getProperties method from the class Settings in place of
        # the getProperties from EnvironmentSettings because there is no need
        # to return the checker informations
        return ParameterSettings.getProperties(self)

    def _buildOpposite(self):
        clazz = self._getOppositeSettingClass()
        read_only = self.isReadOnly()
        removable = self.isRemovable()

        return clazz(read_only=read_only, removable=removable)

    def clone(self, parent=None):
        if parent is None:
            parent = KeySettings(checker=None)

        return EnvironmentSettings.clone(self, parent)


class KeyLocalSettings(ParameterLocalSettings, KeySettings):
    getProperties = KeySettings.getProperties

    @staticmethod
    def _getOppositeSettingClass():
        return KeyGlobalSettings

    def __init__(self, read_only=False, removable=True):
        ParameterLocalSettings.__init__(self,
                                        read_only=read_only,
                                        removable=removable)
        KeySettings.__init__(self, checker=None)

    def clone(self, parent=None):
        if parent is None:
            parent = KeyLocalSettings(read_only=self.isReadOnly(),
                                      removable=self.isRemovable())

        KeySettings.clone(self, parent)

        return ParameterLocalSettings.clone(self, parent)


class KeyGlobalSettings(ParameterGlobalSettings, KeySettings):
    getProperties = KeySettings.getProperties

    @staticmethod
    def _getOppositeSettingClass():
        return KeyLocalSettings

    def __init__(self, read_only=False, removable=True, transient=False):
        ParameterGlobalSettings.__init__(self,
                                         read_only=read_only,
                                         removable=removable,
                                         transient=transient)
        KeySettings.__init__(self, checker=None)

    def clone(self, parent=None):
        if parent is None:
            parent = KeyGlobalSettings(read_only=self.isReadOnly(),
                                       removable=self.isRemovable(),
                                       transient=self.isTransient())

        KeySettings.clone(self, parent)

        return ParameterGlobalSettings.clone(self, parent)
