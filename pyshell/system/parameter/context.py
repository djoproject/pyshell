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

from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.system.setting.context import ContextLocalSettings
from pyshell.system.setting.context import ContextSettings
from pyshell.utils.abstract.valuable import SelectableValuable
from pyshell.utils.exception import ParameterException


def _convertToSetList(orig):
    seen = set()
    seen_add = seen.add
    return [x for x in orig if not (x in seen or seen_add(x))]


class ContextParameter(EnvironmentParameter, SelectableValuable):
    @staticmethod
    def getInitSettings():
        return ContextLocalSettings()

    @staticmethod
    def getAllowedParentSettingClass():
        return ContextSettings

    def setValue(self, value):
        EnvironmentParameter.setValue(self, value)
        self.value = _convertToSetList(self.value)
        self.settings._setValuesSize(len(self.value))
        self.settings.tryToSetDefaultIndex(self.settings.getDefaultIndex())
        self.settings.tryToSetIndex(self.settings.getIndex())

    def addValues(self, values):
        EnvironmentParameter.addValues(self, values)
        self.value = _convertToSetList(self.value)
        self.settings._setValuesSize(len(self.value))

    def removeValues(self, values):
        self.settings._raiseIfReadOnly(self.__class__.__name__, "removeValues")

        values = _convertToSetList(values)

        # compute the list of values to remove, only the existing values
        # will be kept
        new_values = []
        for v in values:
            if v in self.value:
                new_values.append(v)

        # the remove will do nothing, abort
        if len(new_values) == 0:
            return

        # must stay at least one item in list
        if (len(self.value) - len(new_values)) == 0:
            excmsg = ("(%s) removeValues, can not remove all the value in this"
                      " context, at least one value must stay in the list")
            excmsg %= self.__class__.__name__
            raise ParameterException(excmsg)

        # remove
        EnvironmentParameter.removeValues(self, new_values)

        # recompute index if needed
        self.settings._setValuesSize(len(self.value))
        self.settings.tryToSetDefaultIndex(self.settings.getDefaultIndex())
        self.settings.tryToSetIndex(self.settings.getIndex())

    def setSelectedValue(self, value):
        checker = self.settings.getChecker().checker
        try:
            index = self.value.index(checker.getValue(value))
            self.settings.setIndex(index)
        except ValueError:
            excmsg = ("(%s) setSelectedValue, unexisting value '%s', the value"
                      " must exist in the context")
            excmsg %= (self.__class__.__name__, str(value),)
            raise ParameterException(excmsg)

    def getSelectedValue(self):
        return self.value[self.settings.getIndex()]

    def __repr__(self):
        return_value = ("Context, available values: %s, selected index: %s, "
                        "selected value: %s")
        return return_value % (str(self.value),
                               str(self.settings.getIndex()),
                               str(self.value[self.settings.getIndex()]),)

    def __str__(self):
        return str(self.value[self.settings.getIndex()])

    def clone(self, parent=None):
        if parent is None:
            # convert to set will copy the value
            # so there is no need to use a copy function here
            parent = ContextParameter(value=self.value,
                                      settings=self.settings.clone())
        else:
            parent = EnvironmentParameter.clone(self, parent)

        read_only = parent.settings.isReadOnly()
        if read_only:
            parent.settings.setReadOnly(False)

        parent.settings.tryToSetDefaultIndex(self.settings.getDefaultIndex())
        parent.settings.tryToSetIndex(self.settings.getIndex())

        if read_only:
            parent.settings.setReadOnly(True)

        return parent
