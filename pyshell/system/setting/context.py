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

from pyshell.arg.argchecker import DefaultInstanceArgChecker
from pyshell.arg.argchecker import ListArgChecker
from pyshell.system.environment import EnvironmentSettings
from pyshell.system.setting.parameter import ParameterGlobalSettings
from pyshell.system.setting.parameter import ParameterLocalSettings
from pyshell.utils.exception import ParameterException


_defaultArgChecker = DefaultInstanceArgChecker.getArgCheckerInstance()
CONTEXT_DEFAULT_CHECKER = ListArgChecker(_defaultArgChecker)
CONTEXT_DEFAULT_CHECKER.setSize(1, None)


class ContextSettings(EnvironmentSettings):
    def __init__(self, checker=None):
        EnvironmentSettings.__init__(self, checker)
        self.default_index = 0
        self.index = 0

        # temp var
        self.values_size = 0

    def _setValuesSize(self, size):
        self.values_size = size

    def _isValidIndex(self, value):
        if type(value) is not int:
            return False

        if value < 0:
            value += self.values_size

        if value < 0:
            return False

        if value >= self.values_size:
            return False

        return True

    def setIndex(self, index):
        if not self._isValidIndex(index):
            raise ParameterException("(ContextSettings) setIndex, invalid "
                                     "index value, a value between 0 and " +
                                     str(self.values_size)+" was "
                                     "expected, got "+str(index))

        self.index = index

    def tryToSetIndex(self, index):
        # try new index
        if self._isValidIndex(index):
            self.index = index
            return

        # try old index, is it still valid?
        if self._isValidIndex(self.index):
            return  # no update on the object

        # old index is no more valid, try defaultIndex
        # default index is still valid ?
        if self._isValidIndex(self.default_index):
            self.index = self.default_index
            return

        # no other choice, set indexes to 0
        self.index = 0
        self.default_index = 0

    def getIndex(self):
        return self.index

    def setDefaultIndex(self, default_index):
        self._raiseIfReadOnly(self.__class__.__name__, "setDefaultIndex")

        if not self._isValidIndex(default_index):
            raise ParameterException("(ContextSettings) setDefaultIndex, "
                                     "invalid index value, a value between 0 "
                                     "and "+str(self.values_size)+" was"
                                     " expected, got "+str(default_index))

        self.default_index = default_index

    def tryToSetDefaultIndex(self, default_index):
        self._raiseIfReadOnly(self.__class__.__name__, "tryToSetDefaultIndex")

        # try new default index
        if self._isValidIndex(default_index):
            self.default_index = default_index
            return

        # try old default index, is it still valid ?
        if self._isValidIndex(self.default_index):
            return  # no update on the object

        # if old default index is invalid, set default as 0, there is always
        # at least one element in context, index 0 will always be valid
        self.default_index = 0

    def getDefaultIndex(self):
        return self.default_index

    def reset(self):
        self.index = self.default_index

    def setTransientIndex(self, state):
        pass

    def isTransientIndex(self):
        return True

    def setChecker(self, checker=None):
        # check arg checker
        if checker is None:
            checker = CONTEXT_DEFAULT_CHECKER
        else:
            if not isinstance(checker, ListArgChecker):
                if checker.maximum_size != 1:
                    exc_msg = ("(ContextParameter) __init__, inner checker "
                               "must have a maximum length of 1, got '" +
                               str(checker.maximum_size)+"'")
                    raise ParameterException(exc_msg)

                # minimal size = 1, because we need at least one element
                # to have a context
                checker = ListArgChecker(checker,
                                         minimum_size=1,
                                         maximum_size=None)
            else:
                if checker.checker.maximum_size != 1:
                    exc_msg = ("(ContextParameter) __init__, inner checker "
                               "must have a maximum length of 1, got '" +
                               str(checker.checker.maximum_size)+"'")
                    raise ParameterException(exc_msg)

                checker.setSize(1, checker.maximum_size)

        EnvironmentSettings.setChecker(self, checker)

    def setListChecker(self, state):
        pass  # do nothing, checker must always be a list type

    def getProperties(self):
        prop = list(EnvironmentSettings.getProperties(self))
        prop.append(("transientIndex", self.isTransientIndex()))
        prop.append(("defaultIndex", self.getDefaultIndex()))

        if not self.isTransientIndex():
            prop.append(("index", self.getIndex()))

        return tuple(prop)

    def _buildOpposite(self):
        clazz = self._getOppositeSettingClass()

        default_index = self.getDefaultIndex()
        index = self.getIndex()
        read_only = self.isReadOnly()
        removable = self.isRemovable()
        checker = self.getChecker()
        settings = clazz(read_only=False, removable=removable, checker=checker)

        settings._setValuesSize(self.values_size)
        settings.tryToSetDefaultIndex(default_index)
        settings.tryToSetIndex(index)

        if read_only:
            settings.setReadOnly(True)

        return settings

    def clone(self, parent=None):
        if parent is None:
            parent = ContextSettings(checker=self.getChecker())

        # index are not cloned because the settings object do no know yet
        # which will be the related context object.  And maybe it does not
        # hold the same amount of items

        return EnvironmentSettings.clone(self, parent)


class ContextLocalSettings(ParameterLocalSettings, ContextSettings):
    getProperties = ContextSettings.getProperties

    @staticmethod
    def _getOppositeSettingClass():
        return ContextGlobalSettings

    def __init__(self, read_only=False, removable=True, checker=None):
        ParameterLocalSettings.__init__(self, read_only, removable)
        ContextSettings.__init__(self, checker)

    def clone(self, parent=None):
        if parent is None:
            parent = ContextLocalSettings(self.isReadOnly(),
                                          self.isRemovable())

        ContextSettings.clone(self, parent)

        return ParameterLocalSettings.clone(self, parent)


class ContextGlobalSettings(ParameterGlobalSettings, ContextSettings):
    getProperties = ContextSettings.getProperties

    @staticmethod
    def _getOppositeSettingClass():
        return ContextLocalSettings

    def __init__(self,
                 read_only=False,
                 removable=True,
                 transient=False,
                 transient_index=False,
                 checker=None):
        ParameterGlobalSettings.__init__(self, False, removable, transient)
        ContextSettings.__init__(self, checker)
        self.setTransientIndex(transient_index)

        if read_only:
            self.setReadOnly(True)

    def setTransientIndex(self, state):
        self._raiseIfReadOnly(self.__class__.__name__, "setTransientIndex")

        if type(state) != bool:
            raise ParameterException("(ContextGlobalSettings) "
                                     "setTransientIndex, expected a bool type "
                                     "as state, got '"+str(type(state))+"'")

        self.transient_index = state

    def isTransientIndex(self):
        return self.transient_index

    def clone(self, parent=None):
        if parent is None:
            parent = ContextGlobalSettings(self.isReadOnly(),
                                           self.isRemovable(),
                                           self.isTransient(),
                                           self.isTransientIndex())
        else:
            read_only = self.isReadOnly()
            parent.setReadOnly(False)
            parent.setTransientIndex(self.isTransientIndex())
            parent.setReadOnly(read_only)

        ContextSettings.clone(self, parent)

        return ParameterGlobalSettings.clone(self, parent)
