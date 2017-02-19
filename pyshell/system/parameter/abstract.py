# -*- coding: utf-8 -*-

# Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

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

# TODO (create an issue) BUG what if a not hashable value is stored in the
# parameter?
#   the list case is managed, but what about the others? e.g. the dict
#   SOL 1: forbide to have not hashable value into a parameter
#   SOL 2: forbid only if not transient
#   SOL 3:


from collections import Hashable
from copy import deepcopy

from pyshell.system.setting.parameter import ParameterGlobalSettings
from pyshell.system.setting.parameter import ParameterLocalSettings
from pyshell.system.setting.parameter import ParameterSettings
from pyshell.utils.abstract.cloneable import Cloneable
from pyshell.utils.abstract.valuable import Valuable
from pyshell.utils.exception import ParameterException


class Parameter(Valuable, Cloneable, Hashable):  # abstract

    @staticmethod
    def getInitSettings():
        return ParameterLocalSettings()

    @staticmethod
    def getAllowedParentSettingClass():
        return ParameterSettings

    def __init__(self, value, settings=None):
        if settings is not None:
            settings_parent_class = self.getAllowedParentSettingClass()
            if (not isinstance(settings, settings_parent_class) or
               type(settings) is settings_parent_class):
                exc_msg = ("("+self.__class__.__name__+") __init__, a child "
                           "class of "+settings_parent_class.__name__+" was "
                           "expected for settings, got '"+str(type(settings)) +
                           "'")
                raise ParameterException(exc_msg)

            self.settings = settings
        else:
            self.settings = self.getInitSettings()

        read_only = self.settings.isReadOnly()
        self.settings.setReadOnly(False)

        self.setValue(value)

        if read_only:
            self.settings.setReadOnly(True)

    def getValue(self):
        return self.value

    def setValue(self, value):
        self.settings._raiseIfReadOnly(self.__class__.__name__, "setValue")
        self.value = value

    def __str__(self):
        return str(self.getValue())

    def __repr__(self):
        return "Parameter: " + str(self.getValue())

    def enableGlobal(self):
        if isinstance(self.settings, ParameterGlobalSettings):
            return

        self.settings = self.settings.getGlobalFromLocal()

    def enableLocal(self):
        if not isinstance(self.settings, ParameterGlobalSettings):
            return

        self.settings = self.settings.getLocalFromGlobal()

    def clone(self, parent=None):
        # About deepcopy, why is it used ?
        #    If value is a litteral, deepcopy will just assign the litteral
        #    If value is a list of litteral, deepcopy will create a new list
        #        then copy every literal
        #    If value is an object, deepcopy will copy everything in the obj
        #    If value is a list of object, deepcopy will create a new list
        #        and copy everything in each obj

        if parent is None:
            return self.__class__(deepcopy(self.value),
                                  self.settings.clone())

        parent.settings.setReadOnly(False)
        parent.setValue(deepcopy(self.value))

        # XXX should not clone the settings, should copy them
        # it will be solved with the issue #102
        parent.settings = self.settings.clone()

        return parent

    def __hash__(self):
        value = self.getValue()
        if hasattr(value, "__iter__"):
            return hash(str(hash(tuple(value))) + str(hash(self.settings)))
        else:
            return hash(str(hash(value)) + str(hash(self.settings)))
