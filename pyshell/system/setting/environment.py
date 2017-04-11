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


# TODO does really need to inherit from ParameterSettings?
#   for _buildOpposite, but is it a good idea to keep it in this class and not
#   in the local/global classes?
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
        # Why ?  Because once a parameter is created, settings set and value
        # sets, it is never suppose to become a list except voluntary.
        if (self.checker is not None and
           self.isListChecker() and
           not isinstance(checker, ListArgChecker)):
            self.checker = ListArgChecker(checker)
        else:
            self.checker = checker

    # TODO (issue #105) this method is not a method defined in the mother class
    # setting and so it should never be used outside of the class
    # system/Environment. So? as almost all the methods in this class...
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
        prop = {}

        if self.isListChecker():
            type_name = self.getChecker().checker.getTypeName()
        else:
            type_name = self.getChecker().getTypeName()

        prop[SETTING_PROPERTY_CHECKER] = type_name
        prop[SETTING_PROPERTY_CHECKERLIST] = self.isListChecker()
        return prop

    def _buildOpposite(self):
        clazz = self._getOppositeSettingClass()
        read_only = self.isReadOnly()
        removable = self.isRemovable()
        checker = self.getChecker()

        return clazz(read_only=read_only,
                     removable=removable,
                     checker=checker)

    def clone(self):
        return EnvironmentSettings(checker=self.getChecker())


class EnvironmentLocalSettings(ParameterLocalSettings, EnvironmentSettings):
    @staticmethod
    def _getOppositeSettingClass():
        return EnvironmentGlobalSettings

    def __init__(self, read_only=False, removable=True, checker=None):
        ParameterLocalSettings.__init__(self, read_only, removable)
        EnvironmentSettings.__init__(self, checker)

    def getProperties(self):
        props = ParameterLocalSettings.getProperties(self)
        props.update(EnvironmentSettings.getProperties(self))
        return props

    def clone(self):
        return EnvironmentLocalSettings(self.isReadOnly(),
                                        self.isRemovable(),
                                        self.getChecker())


class EnvironmentGlobalSettings(ParameterGlobalSettings, EnvironmentSettings):
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

    def getProperties(self):
        props = ParameterGlobalSettings.getProperties(self)
        props.update(EnvironmentSettings.getProperties(self))
        return props

    def clone(self, parent=None):
        return EnvironmentGlobalSettings(self.isReadOnly(),
                                         self.isRemovable(),
                                         self.isTransient(),
                                         self.getChecker())
