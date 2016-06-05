#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.system.manager import ParameterManager
from pyshell.system.parameter import Parameter
from pyshell.system.setting.environment import EnvironmentGlobalSettings
from pyshell.system.setting.environment import EnvironmentLocalSettings
from pyshell.system.setting.environment import EnvironmentSettings
from pyshell.utils.exception import ParameterException


class EnvironmentParameterManager(ParameterManager):
    def getAllowedType(self):
        return EnvironmentParameter


def _lockKey(parameter):
    return parameter.getLockId()


class ParametersLocker(object):
    def __init__(self, parameters_list):
        self.parameters_list = sorted(parameters_list, key=_lockKey)

    def __enter__(self):
        for param in self.parameters_list:
            param.getLock().acquire(True)  # blocking=True

        return self

    def __exit__(self, type, value, traceback):
        for param in self.parameters_list:
            param.getLock().release()


class EnvironmentParameter(Parameter):
    @staticmethod
    def getInitSettings():
        return EnvironmentLocalSettings()

    @staticmethod
    def getAllowedParentSettingClass():
        return EnvironmentSettings

    _internalLock = Lock()
    _internalLockCounter = 0

    def __init__(self, value, settings=None):
        Parameter.__init__(self, value, settings)
        self.lock = None
        self.lockID = -1

    def _initLock(self):
        if not self.isLockEnable():
            return

        if self.lock is None:
            with EnvironmentParameter._internalLock:
                if self.lock is None:
                    self.lockID = EnvironmentParameter._internalLockCounter
                    EnvironmentParameter._internalLockCounter += 1
                    self.lock = Lock()

    def getLock(self):
        self._initLock()
        return self.lock

    def getLockId(self):
        self._initLock()
        return self.lockID

    def isLockEnable(self):
        return isinstance(self.settings, EnvironmentGlobalSettings)

    def addValues(self, values):
        # must be "not readonly"
        self.settings._raiseIfReadOnly(self.__class__.__name__, "addValues")

        # typ must be list
        if not self.settings.isListChecker():
            raise ParameterException("(EnvironmentParameter) addValues, can "
                                     "only add value to a list parameter")

        # values must be iterable
        if not hasattr(values, "__iter__"):
            values = (values, )

        # each value must be a valid element from checker
        values = self.settings.getChecker().getValue(values)

        # append values
        self.value.extend(values)

    def removeValues(self, values):
        # must be "not readonly"
        self.settings._raiseIfReadOnly(self.__class__.__name__, "removeValues")

        # typ must be list
        if not self.settings.isListChecker():
            raise ParameterException("(EnvironmentParameter) removeValues, "
                                     "can only remove value to a list "
                                     "parameter")

        # values must be iterable
        if not hasattr(values, "__iter__"):
            values = (values,)

        # remove first occurence of each value
        values = self.settings.getChecker().getValue(values)
        for v in values:
            if v in self.value:
                self.value.remove(v)

    def setValue(self, value):
        self.settings._raiseIfReadOnly(self.__class__.__name__, "setValue")
        self.value = self.settings.getChecker().getValue(value)

    def __repr__(self):
        return "Environment, value:"+str(self.value)

    def __str__(self):
        return str(self.value)
