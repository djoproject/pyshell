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

from pyshell.register.exception import LoaderException
from pyshell.register.loader.abstractloader import AbstractLoader
from pyshell.register.profile.internal import InternalLoaderProfile
from pyshell.register.result.abstractresult import AbstractResult
from pyshell.utils.abstract.flushable import Flushable
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_LOADED_E
from pyshell.utils.constants import STATE_LOADING
from pyshell.utils.constants import STATE_UNLOADED
from pyshell.utils.constants import STATE_UNLOADED_E
from pyshell.utils.constants import STATE_UNLOADING
from pyshell.utils.raises import raiseIfNotInstance
from pyshell.utils.raises import raiseIfNotSubclass


_allowedState = (STATE_LOADED,
                 STATE_LOADED_E,
                 STATE_LOADING,
                 STATE_UNLOADED,
                 STATE_UNLOADED_E,
                 STATE_UNLOADING,)


_allowedNextSate = {}
_allowedNextSate[None] = (STATE_LOADING,)
_allowedNextSate[STATE_LOADING] = (STATE_LOADED, STATE_LOADED_E,)
_allowedNextSate[STATE_LOADED] = (STATE_UNLOADING,)
_allowedNextSate[STATE_LOADED_E] = (STATE_UNLOADING,)
_allowedNextSate[STATE_UNLOADING] = (STATE_UNLOADED, STATE_UNLOADED_E)
_allowedNextSate[STATE_UNLOADED] = (STATE_LOADING,)
_allowedNextSate[STATE_UNLOADED_E] = (STATE_LOADING,)


class RootProfile(InternalLoaderProfile, Flushable):
    def __init__(self):
        InternalLoaderProfile.__init__(self, self)
        self.state = None
        self._name = None
        self._informations = None
        self._result = {}

    def setName(self, name):
        self._name = name

    def getName(self):
        return self._name

    def setAddonInformations(self, informations):
        self._informations = informations

    def getAddonInformations(self):
        return self._informations

    def postResult(self, loader_class_def, result_instance):
        raiseIfNotSubclass(loader_class_def,
                           "loader_class_def",
                           AbstractLoader,
                           LoaderException,
                           "postResult",
                           self.__class__.__name__)

        raiseIfNotInstance(result_instance,
                           "result_instance",
                           AbstractResult,
                           LoaderException,
                           "postResult",
                           self.__class__.__name__)

        class_key = result_instance.__class__

        if (class_key in self._result and
                loader_class_def in self._result[class_key]):
            excmsg = ("(" + self.__class__.__name__ + ") postResult, a "
                      "result of type '" + str(type(result_instance)) + "'"
                      " already exists for the key '" +
                      str(type(loader_class_def)) + "'")
            raise LoaderException(excmsg)

        if class_key not in self._result:
            self._result[class_key] = {}

        self._result[class_key][loader_class_def] = result_instance

    def getResult(self, result_class_def):
        return self._result.get(result_class_def, {})

    def flush(self):
        self._result.clear()

    def setState(self, state):
        if state not in _allowedState:
            excmsg = "(%s) setState, invalid state: '%s'"
            excmsg %= (self.__class__.__name__, str(state),)
            raise LoaderException(excmsg)

        expected_state = _allowedNextSate[self.state]

        if state not in expected_state:
            excmsg = ("(%s) setState, state not allowed. Expected a state in "
                      "'%s', got '%s'")
            excmsg %= (self.__class__.__name__,
                       str(expected_state),
                       str(state),)
            raise LoaderException(excmsg)

        self.state = state

    def hasNoState(self):
        return self.state is None

    def isLoading(self):
        return self.state == STATE_LOADING

    def isLoaded(self):
        return self.state in (STATE_LOADED, STATE_LOADED_E,)

    def isUnloading(self):
        return self.state == STATE_UNLOADING

    def isUnloaded(self):
        return self.state in (STATE_UNLOADED, STATE_UNLOADED_E)

    def hasError(self):
        return self.state in (STATE_LOADED_E, STATE_UNLOADED_E)
