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

from pyshell.arg.argchecker import DefaultInstanceArgChecker
from pyshell.arg.argchecker import ListArgChecker
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.parameter import ParameterManager
from pyshell.system.settings import GlobalSettings
from pyshell.system.settings import LocalSettings
from pyshell.system.settings import Settings
from pyshell.utils.exception import ParameterException
from pyshell.utils.valuable import SelectableValuable

_defaultArgChecker = DefaultInstanceArgChecker.getArgCheckerInstance()
CONTEXT_DEFAULT_CHECKER = ListArgChecker(_defaultArgChecker)
CONTEXT_DEFAULT_CHECKER.setSize(1, None)


class ContextParameterManager(ParameterManager):
    def getAllowedType(self):
        return ContextParameter


def _convertToSetList(orig):
    seen = set()
    seen_add = seen.add
    return [x for x in orig if not (x in seen or seen_add(x))]


class ContextSettings(Settings):
    def __init__(self):
        self.default_index = 0
        self.index = 0
        self.context = None

    def setIndex(self, index):
        try:
            self.context.value[index]
        except IndexError:
            raise ParameterException("(ContextSettings) setIndex, invalid "
                                     "index value, a value between 0 and " +
                                     str(len(self.context.value))+" was "
                                     "expected, got "+str(index))
        except TypeError:
            raise ParameterException("(ContextSettings) setIndex, invalid "
                                     "index value, a value between 0 and " +
                                     str(len(self.context.value))+" was "
                                     "expected, got "+str(index))

        self.index = index

    def tryToSetIndex(self, index):
        # try new index
        try:
            self.context.value[index]
            self.index = index
            return
        except IndexError:
            pass
        except TypeError:
            pass

        # try old index, is it still valid?
        try:
            self.context.value[self.index]
            return  # no update on the object
        except IndexError:
            pass

        # old index is no more valid, try defaultIndex
        # default index is still valid ?
        self.tryToSetDefaultIndex(self.default_index)
        self.index = self.default_index

    def setIndexValue(self, value):
        checker = self.context.typ.checker
        try:
            self.index = self.context.value.index(checker.getValue(value))
        except ValueError:
            raise ParameterException("(ContextSettings) setIndexValue, "
                                     "unexisting value '"+str(value)+"', the "
                                     "value must exist in the context")

    def getIndex(self):
        return self.index

    def setDefaultIndex(self, default_index):
        self._raiseIfReadOnly(self.__class__.__name__, "setDefaultIndex")

        try:
            self.context.value[default_index]
        except IndexError:
            raise ParameterException("(ContextSettings) setDefaultIndex, "
                                     "invalid index value, a value between 0 "
                                     "and "+str(len(self.context.value))+" was"
                                     " expected, got "+str(default_index))
        except TypeError:
            raise ParameterException("(ContextSettings) setDefaultIndex, "
                                     "invalid index value, a value between 0 "
                                     "and "+str(len(self.context.value))+" was"
                                     " expected, got "+str(default_index))

        self.default_index = default_index

    def tryToSetDefaultIndex(self, default_index):
        self._raiseIfReadOnly(self.__class__.__name__, "tryToSetDefaultIndex")

        # try new default index
        try:
            self.context.value[default_index]
            self.default_index = default_index
            return
        except IndexError:
            pass
        except TypeError:
            pass

        # try old default index, is it still valid ?
        try:
            self.context.value[self.default_index]
            return  # no update on the object
        except IndexError:
            pass

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

    def getProperties(self):
        prop = list(Settings.getProperties(self))
        prop.append(("transientIndex", self.isTransientIndex()))
        prop.append(("defaultIndex", self.getDefaultIndex()))

        if not self.isTransientIndex():
            prop.append(("index", self.getIndex()))

        return tuple(prop)

    def clone(self, parent=None):
        if parent is None:
            parent = ContextSettings()

        return parent


class LocalContextSettings(LocalSettings, ContextSettings):
    getProperties = ContextSettings.getProperties

    def __init__(self, read_only=False, removable=True):
        ContextSettings.__init__(self)
        LocalSettings.__init__(self, read_only, removable)

    def clone(self, parent=None):
        if parent is None:
            parent = LocalContextSettings(self.isReadOnly(),
                                          self.isRemovable())

        ContextSettings.clone(self, parent)

        return LocalSettings.clone(self, parent)


class GlobalContextSettings(GlobalSettings, ContextSettings):
    getProperties = ContextSettings.getProperties

    def __init__(self,
                 read_only=False,
                 removable=True,
                 transient=False,
                 transient_index=False):
        ContextSettings.__init__(self)
        GlobalSettings.__init__(self, False, removable, transient)
        self.setTransientIndex(transient_index)

        if read_only:
            self.setReadOnly(True)

    def setTransientIndex(self, state):
        self._raiseIfReadOnly(self.__class__.__name__, "setTransientIndex")

        if type(state) != bool:
            raise ParameterException("(GlobalContextSettings) "
                                     "setTransientIndex, expected a bool type "
                                     "as state, got '"+str(type(state))+"'")

        self.transient_index = state

    def isTransientIndex(self):
        return self.transient_index

    def clone(self, parent=None):
        if parent is None:
            parent = GlobalContextSettings(self.isReadOnly(),
                                           self.isRemovable(),
                                           self.isTransient(),
                                           self.isTransientIndex())
        else:
            read_only = self.isReadOnly()
            parent.setReadOnly(False)
            parent.setTransientIndex(self.isTransientIndex())
            parent.setReadOnly(read_only)

        ContextSettings.clone(self, parent)

        return GlobalSettings.clone(self, parent)


class ContextParameter(EnvironmentParameter, SelectableValuable):
    @staticmethod
    def getInitSettings():
        return LocalContextSettings()

    def __init__(self,
                 value,
                 typ=None,
                 settings=None,
                 index=0,
                 default_index=0):

        # check arg checker
        if typ is None:
            typ = CONTEXT_DEFAULT_CHECKER
        else:
            if not isinstance(typ, ListArgChecker):
                # minimal size = 1, because we need at least one element
                # to have a context
                typ = ListArgChecker(typ, minimum_size=1, maximum_size=None)
            else:
                typ.setSize(1, typ.maximum_size)

            if typ.checker.maximum_size != 1:
                raise ParameterException("(ContextParameter) __init__, inner "
                                         "checker must have a maximum length "
                                         "of 1, got '" +
                                         str(typ.checker.maximum_size)+"'")

        # set and check settings
        if settings is not None:
            if not isinstance(settings, ContextSettings):
                raise ParameterException("(ContextParameter) __init__, a "
                                         "ContextSettings was expected for "
                                         "settings, got '" +
                                         str(type(settings))+"'")
        else:
            settings = self.getInitSettings()

        # init parent
        settings.context = self
        EnvironmentParameter.__init__(self, value, typ, settings)

        # set index and default_index
        if default_index != 0 or index != 0:
            read_only = self.settings.isReadOnly()
            self.settings.setReadOnly(False)
            self.settings.tryToSetDefaultIndex(default_index)
            self.settings.tryToSetIndex(index)
            self.settings.setReadOnly(read_only)

    def setValue(self, value):
        EnvironmentParameter.setValue(self, value)
        self.value = _convertToSetList(self.value)
        self.settings.tryToSetDefaultIndex(self.settings.getDefaultIndex())
        self.settings.tryToSetIndex(self.settings.getIndex())

    def addValues(self, values):
        EnvironmentParameter.addValues(self, values)
        self.value = _convertToSetList(self.value)

    def removeValues(self, values):
        self.settings._raiseIfReadOnly(self.__class__.__name__, "removeValues")

        values = _convertToSetList(values)

        new_values = []
        for v in values:
            if v in self.value:
                new_values.append(v)

        if len(new_values) == 0:
            return

        # must stay at least one item in list
        if (len(self.value) - len(new_values)) == 0:
            raise ParameterException("(ContextParameter) removeValues, can "
                                     "remove all the value in this context, "
                                     "at least one value must stay in the "
                                     "list")

        # remove
        EnvironmentParameter.removeValues(self, new_values)

        # recompute index if needed
        self.settings.tryToSetDefaultIndex(self.settings.getDefaultIndex())
        self.settings.tryToSetIndex(self.settings.getIndex())

    def getSelectedValue(self):
        return self.value[self.settings.getIndex()]

    def __repr__(self):
        return "Context, available values: "+str(self.value) + \
            ", selected index: "+str(self.settings.getIndex()) + \
            ", selected value: "+str(self.value[self.settings.getIndex()])

    def __str__(self):
        return str(self.value[self.settings.getIndex()])

    def enableGlobal(self):
        if type(self.settings) is GlobalContextSettings:
            return

        default_index = self.settings.getDefaultIndex()
        index = self.settings.getIndex()
        read_only = self.settings.isReadOnly()
        removable = self.settings.isRemovable()
        self.settings = GlobalContextSettings(read_only=False,
                                              removable=removable)
        self.settings.context = self
        self.settings.tryToSetDefaultIndex(default_index)
        self.settings.tryToSetIndex(index)

        if read_only:
            self.settings.setReadOnly(True)

    def enableLocal(self):
        if type(self.settings) is LocalContextSettings:
            return

        default_index = self.settings.getDefaultIndex()
        index = self.settings.getIndex()
        read_only = self.settings.isReadOnly()
        removable = self.settings.isRemovable()
        self.settings = LocalContextSettings(read_only=False,
                                             removable=removable)
        self.settings.context = self
        self.settings.tryToSetDefaultIndex(default_index)
        self.settings.tryToSetIndex(index)

        if read_only:
            self.settings.setReadOnly(True)
