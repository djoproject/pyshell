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

from pyshell.arg.checker.argchecker import ArgChecker
from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.list import ListArgChecker
from pyshell.system.setting.parameter import ParameterGlobalSettings
from pyshell.system.setting.parameter import ParameterLocalSettings
from pyshell.system.setting.parameter import ParameterSettings
from pyshell.utils.constants import SETTING_PROPERTY_CHECKER
from pyshell.utils.constants import SETTING_PROPERTY_CHECKERLIST
from pyshell.utils.exception import ParameterException


DEFAULT_CHECKER = ListArgChecker(DefaultChecker.getArg())


class EnvironmentSettings(ParameterSettings):

    def __init__(self, checker=None):
        ParameterSettings.__init__(self)

        self.checker = None
        readonly = self.isReadOnly()
        self.setReadOnly(False)

        self.setChecker(checker)

        if readonly:
            self.setReadOnly(True)

    def getChecker(self):
        return self.checker

    def setChecker(self, checker=None):
        self._raiseIfReadOnly(self.__class__.__name__, "setChecker")

        if checker is None:
            self.checker = DEFAULT_CHECKER
            return

        if not isinstance(checker, ArgChecker):  # typ must be argChecker
            raise ParameterException("(EnvironmentParameter) __init__, an "
                                     "ArgChecker instance was expected for "
                                     "argument typ, got '"+str(type(checker)) +
                                     "'")

        # if the check was previously a listchecker, it must stay a listchecker
        # use setListChecker to convert to not a listchecker
        if (self.checker is not None and
           self.isListChecker() and
           not isinstance(checker, ListArgChecker)):
            self.checker = ListArgChecker(checker)
        else:
            self.checker = checker

    # TODO (issue #105) this method is not a method defined in the mother class
    # setting and so it should never be used outside of the class
    # system/Environment
    def isListChecker(self):
        return isinstance(self.getChecker(), ListArgChecker)

    def setListChecker(self, state):
        self._raiseIfReadOnly(self.__class__.__name__, "setListChecker")

        if state:
            if isinstance(self.getChecker(), ListArgChecker):
                return
            self.checker = ListArgChecker(self.getChecker())
        else:
            if not isinstance(self.getChecker(), ListArgChecker):
                return
            self.checker = self.getChecker().checker

    def getProperties(self):
        prop = list(ParameterSettings.getProperties(self))

        if self.isListChecker():
            prop.append((SETTING_PROPERTY_CHECKER,
                         self.getChecker().checker.getTypeName()))
        else:
            prop.append((SETTING_PROPERTY_CHECKER,
                         self.getChecker().getTypeName()))

        prop.append((SETTING_PROPERTY_CHECKERLIST, self.isListChecker()))
        return tuple(prop)

    def _buildOpposite(self):
        clazz = self._getOppositeSettingClass()
        read_only = self.isReadOnly()
        removable = self.isRemovable()
        checker = self.getChecker()

        return clazz(read_only=read_only,
                     removable=removable,
                     checker=checker)

    def clone(self, parent=None):
        if parent is None:
            parent = EnvironmentSettings(checker=self.getChecker())
        else:
            readonly = parent.isReadOnly()
            parent.setReadOnly(False)

            parent.setChecker(self.getChecker())
            parent.setListChecker(self.isListChecker())

            if readonly:
                parent.setReadOnly(True)

        return ParameterSettings.clone(self, parent)


class EnvironmentLocalSettings(ParameterLocalSettings, EnvironmentSettings):
    getProperties = EnvironmentSettings.getProperties

    @staticmethod
    def _getOppositeSettingClass():
        return EnvironmentGlobalSettings

    def __init__(self, read_only=False, removable=True, checker=None):
        ParameterLocalSettings.__init__(self, read_only, removable)
        EnvironmentSettings.__init__(self, checker)

    def clone(self, parent=None):
        if parent is None:
            parent = EnvironmentLocalSettings(self.isReadOnly(),
                                              self.isRemovable(),
                                              self.getChecker())

        EnvironmentSettings.clone(self, parent)

        return ParameterLocalSettings.clone(self, parent)


class EnvironmentGlobalSettings(ParameterGlobalSettings, EnvironmentSettings):
    getProperties = EnvironmentSettings.getProperties

    @staticmethod
    def _getOppositeSettingClass():
        return EnvironmentLocalSettings

    def __init__(self,
                 read_only=False,
                 removable=True,
                 transient=False,
                 checker=None):
        ParameterGlobalSettings.__init__(self, read_only, removable, transient)
        EnvironmentSettings.__init__(self, checker)

    def clone(self, parent=None):
        if parent is None:
            parent = EnvironmentGlobalSettings(self.isReadOnly(),
                                               self.isRemovable(),
                                               self.isTransient(),
                                               self.getChecker())

        EnvironmentSettings.clone(self, parent)

        return ParameterGlobalSettings.clone(self, parent)
