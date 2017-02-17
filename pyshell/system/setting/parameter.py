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

from pyshell.utils.abstract.cloneable import Cloneable
from pyshell.utils.constants import EMPTY_STRING
from pyshell.utils.constants import SETTING_PROPERTY_READONLY
from pyshell.utils.constants import SETTING_PROPERTY_REMOVABLE
from pyshell.utils.constants import SETTING_PROPERTY_TRANSIENT
from pyshell.utils.exception import ParameterException


class ParameterSettings(Cloneable):
    def __init__(self, read_only=False, removable=True):
        pass

    def setTransient(self, state):
        pass

    def isTransient(self):
        return True

    def setReadOnly(self, state):
        pass

    def isReadOnly(self):
        return False

    def setRemovable(self, state):
        pass

    def isRemovable(self):
        return True

    # TODO should be a dict...
    def getProperties(self):
        return ((SETTING_PROPERTY_REMOVABLE, self.isRemovable(),),
                (SETTING_PROPERTY_READONLY, self.isReadOnly(),),
                (SETTING_PROPERTY_TRANSIENT, self.isTransient(),))

    def __hash__(self):
        return hash(self.getProperties())

    def clone(self, parent=None):
        if parent is None:
            return self.__class__()

        return parent

    def _raiseIfReadOnly(self, class_name=None, meth_name=None):
        if self.isReadOnly():
            if meth_name is not None:
                meth_name = str(meth_name) + ", "
            else:
                meth_name = EMPTY_STRING

            if class_name is not None:
                class_name = "(" + str(class_name) + ") "
            else:
                class_name = EMPTY_STRING

            excmsg = class_name + meth_name + "read only parameter"
            raise ParameterException(excmsg)

    @staticmethod
    def _getOppositeSettingClass():
        return None

    def _buildOpposite(self):
        clazz = self._getOppositeSettingClass()
        read_only = self.isReadOnly()
        removable = self.isRemovable()

        return clazz(read_only=read_only, removable=removable)


class ParameterLocalSettings(ParameterSettings):
    @staticmethod
    def _getOppositeSettingClass():
        return ParameterGlobalSettings

    def __init__(self, read_only=False, removable=True):
        self.read_only = False
        self.setRemovable(removable)
        self.setReadOnly(read_only)

    def setReadOnly(self, state):
        if not isinstance(state, bool):
            excmsg = ("(ParameterLocalSettings) setReadOnly, expected a bool "
                      "type as state, got '"+str(type(state)) + "'")
            raise ParameterException(excmsg)

        self.read_only = state

    def isReadOnly(self):
        return self.read_only

    def setRemovable(self, state):
        self._raiseIfReadOnly(self.__class__.__name__, "setRemovable")

        if not isinstance(state, bool):
            excmsg = ("(ParameterLocalSettings) setRemovable, expected a bool "
                      "type as state, got '"+str(type(state)) + "'")
            raise ParameterException(excmsg)

        self.removable = state

    def isRemovable(self):
        return self.removable

    def getGlobalFromLocal(self):
        return self._buildOpposite()

    def getLocalFromGlobal(self):
        return self

    def clone(self, parent=None):
        if parent is None:
            return ParameterLocalSettings(self.isReadOnly(),
                                          self.isRemovable())
        else:
            read_only = self.isReadOnly()
            parent.setReadOnly(False)
            parent.setRemovable(self.isRemovable())
            parent.setReadOnly(read_only)

        return ParameterSettings.clone(self, parent)


class ParameterGlobalSettings(ParameterLocalSettings):

    @staticmethod
    def _getOppositeSettingClass():
        return ParameterLocalSettings

    def __init__(self, read_only=False, removable=True, transient=False):
        ParameterLocalSettings.__init__(self, False, removable)

        self.setTransient(transient)
        self.startingHash = None
        self.setReadOnly(read_only)

    def setTransient(self, state):
        self._raiseIfReadOnly(self.__class__.__name__, "setTransient")

        if not isinstance(state, bool):
            excmsg = ("(ParameterGlobalSettings) setTransient, expected a bool"
                      " type as state, got '"+str(type(state)) + "'")
            raise ParameterException(excmsg)

        self.transient = state

    def isTransient(self):
        return self.transient

    def setStartingPoint(self, hashi):
        if self.startingHash is not None:
            excmsg = ("(ParameterGlobalSettings) setStartingPoint, a starting "
                      "point was already defined for this parameter")
            raise ParameterException(excmsg)

        self.startingHash = hashi

    def isEqualToStartingHash(self, hashi):
        return hashi == self.startingHash

    def getGlobalFromLocal(self):
        return self

    def getLocalFromGlobal(self):
        return self._buildOpposite()

    def clone(self, parent=None):
        if parent is None:
            parent = ParameterGlobalSettings(self.isReadOnly(),
                                             self.isRemovable(),
                                             self.isTransient())
        else:
            read_only = self.isReadOnly()
            parent.setReadOnly(False)
            parent.setTransient(self.isTransient())
            parent.setReadOnly(read_only)

        # starting hash is not copied because it comes from something outside
        # of this class, and it won't be relevant to copy it.

        return ParameterLocalSettings.clone(self, parent)
