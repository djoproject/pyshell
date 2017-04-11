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

from pyshell.arg.checker.file import FilePathArgChecker
from pyshell.system.setting.environment import EnvironmentGlobalSettings
from pyshell.system.setting.environment import EnvironmentLocalSettings
from pyshell.system.setting.environment import EnvironmentSettings
from pyshell.utils.constants import ENABLE_ON_POST_PROCESS
from pyshell.utils.constants import ENABLE_ON_PRE_PROCESS
from pyshell.utils.constants import ENABLE_ON_PROCESS
from pyshell.utils.constants import SETTING_PROPERTY_CHECKER
from pyshell.utils.constants import SETTING_PROPERTY_CHECKERLIST
from pyshell.utils.constants import SETTING_PROPERTY_ENABLEON
from pyshell.utils.constants import SETTING_PROPERTY_GRANULARITY
from pyshell.utils.exception import ParameterException


DEFAULT_CHECKER = FilePathArgChecker(exist=True,
                                     readable=True,
                                     writtable=None,
                                     is_file=True)


class ProcedureSettings(EnvironmentSettings):
    def __init__(self, error_granularity=None, enable_on=None):
        EnvironmentSettings.__init__(self, checker=DEFAULT_CHECKER)
        self.error_granularity = float("inf")  # stop on any error

        readonly = self.isReadOnly()
        self.setReadOnly(False)

        if error_granularity is not None:
            self.setErrorGranularity(error_granularity)

        self.enable_on = ENABLE_ON_PRE_PROCESS
        if enable_on is not None:
            self.setEnableOn(enable_on)

        if readonly:
            self.setReadOnly(True)

    def enableOnPreProcess(self):
        self.setEnableOn(ENABLE_ON_PRE_PROCESS)

    def isEnabledOnPreProcess(self):
        return self.enable_on is ENABLE_ON_PRE_PROCESS

    def enableOnProcess(self):
        self.setEnableOn(ENABLE_ON_PROCESS)

    def isEnabledOnProcess(self):
        return self.enable_on is ENABLE_ON_PROCESS

    def enableOnPostProcess(self):
        self.setEnableOn(ENABLE_ON_POST_PROCESS)

    def isEnabledOnPostProcess(self):
        return self.enable_on is ENABLE_ON_POST_PROCESS

    def setEnableOn(self, value):
        self._raiseIfReadOnly(self.__class__.__name__, "setEnableOn")

        allowed_values = (ENABLE_ON_PRE_PROCESS,
                          ENABLE_ON_PROCESS,
                          ENABLE_ON_POST_PROCESS,)
        if value not in allowed_values:
            exc_msg = ("(ProcedureSettings) one of these three value was "
                       "expected: %s, %s, %s. got '%s'." %
                       (ENABLE_ON_PRE_PROCESS, ENABLE_ON_PROCESS,
                        ENABLE_ON_POST_PROCESS, str(value)))
            raise ParameterException(exc_msg)

        self.enable_on = value

    def getEnableOn(self):
        return self.enable_on

    def stopOnFirstError(self):
        self.setErrorGranularity(
            float("inf"))

    def neverStopIfErrorOccured(self):
        self.setErrorGranularity(-1)

    def setErrorGranularity(self, value):
        """
        Every error with a granularity bellow this limit will stop the
        execution of the current procedure.

        +inf means no error are allowed
        -1 means every error are allowed

        """

        self._raiseIfReadOnly(self.__class__.__name__, "setErrorGranularity")

        error = False
        try:
            value = float(value)
        except (TypeError, ValueError):
            error = True

        if error or value < -1.0:
            exc_msg = ("(ProcedureSettings) setErrorGranularity, expected a "
                       "float value bigger or equal than -1.0, got type='" +
                       str(type(value)) + "', value='"+str(value)+"'")
            raise ParameterException(exc_msg)

        self.error_granularity = value

    def getErrorGranularity(self):
        return self.error_granularity

    def getProperties(self):
        prop = {}
        prop[SETTING_PROPERTY_GRANULARITY] = self.getErrorGranularity()
        prop[SETTING_PROPERTY_ENABLEON] = self.getEnableOn()
        return prop

    def setChecker(self, checker=None):
        if self.getChecker() is not None:
            excmsg = "(%s) setChecker, not allowed on key settings"
            excmsg %= self.__class__.__name__
            raise ParameterException(excmsg)

        EnvironmentSettings.setChecker(self, checker)

    def setListChecker(self, state):
        excmsg = "(%s) setListChecker, not allowed on key settings"
        excmsg %= self.__class__.__name__
        raise ParameterException(excmsg)

    def _buildOpposite(self):
        clazz = self._getOppositeSettingClass()
        read_only = self.isReadOnly()
        removable = self.isRemovable()
        enable_on = self.getEnableOn()
        error_granularity = self.getErrorGranularity()

        return clazz(read_only=read_only,
                     removable=removable,
                     error_granularity=error_granularity,
                     enable_on=enable_on)

    def clone(self):
        return ProcedureSettings(error_granularity=self.getErrorGranularity(),
                                 enable_on=self.getEnableOn())


class ProcedureLocalSettings(EnvironmentLocalSettings, ProcedureSettings):
    @staticmethod
    def _getOppositeSettingClass():
        return ProcedureGlobalSettings

    def __init__(self,
                 read_only=False,
                 removable=True,
                 error_granularity=None,
                 enable_on=None):

        EnvironmentLocalSettings.__init__(self,
                                          read_only=read_only,
                                          removable=removable)
        ProcedureSettings.__init__(self,
                                   error_granularity=error_granularity,
                                   enable_on=enable_on)

    def getProperties(self):
        props = EnvironmentLocalSettings.getProperties(self)
        props.update(ProcedureSettings.getProperties(self))
        del props[SETTING_PROPERTY_CHECKER]
        del props[SETTING_PROPERTY_CHECKERLIST]
        return props

    def clone(self):
        return ProcedureLocalSettings(
            read_only=self.isReadOnly(),
            removable=self.isRemovable(),
            error_granularity=self.getErrorGranularity(),
            enable_on=self.getEnableOn())


class ProcedureGlobalSettings(EnvironmentGlobalSettings, ProcedureSettings):
    @staticmethod
    def _getOppositeSettingClass():
        return ProcedureLocalSettings

    def __init__(self,
                 read_only=False,
                 removable=True,
                 transient=False,
                 error_granularity=None,
                 enable_on=None):

        EnvironmentGlobalSettings.__init__(self,
                                           read_only=read_only,
                                           removable=removable,
                                           transient=transient)

        ProcedureSettings.__init__(self,
                                   error_granularity=error_granularity,
                                   enable_on=enable_on)

    def getProperties(self):
        props = EnvironmentGlobalSettings.getProperties(self)
        props.update(ProcedureSettings.getProperties(self))
        del props[SETTING_PROPERTY_CHECKER]
        del props[SETTING_PROPERTY_CHECKERLIST]
        return props

    def clone(self):
        return ProcedureGlobalSettings(
            read_only=self.isReadOnly(),
            removable=self.isRemovable(),
            transient=self.isTransient(),
            error_granularity=self.getErrorGranularity(),
            enable_on=self.getEnableOn())
