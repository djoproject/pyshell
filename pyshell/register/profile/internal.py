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
from pyshell.register.profile.default import DefaultProfile
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_LOADED_E
from pyshell.utils.constants import STATE_UNLOADED
from pyshell.utils.constants import STATE_UNLOADED_E
from pyshell.utils.raises import raiseIfNotSubclass

_loadAllowedState = (STATE_UNLOADED, STATE_UNLOADED_E,)
_unloadAllowedState = (STATE_LOADED, STATE_LOADED_E,)


class InternalLoaderProfile(DefaultProfile):
    def __init__(self):
        DefaultProfile.__init__(self)
        self.state = None
        self.children = {}
        self._is_root = False

    def setRoot(self):
        self._is_root = True

    def isRoot(self):
        return self._is_root

    def setState(self, state):
        if state not in _unloadAllowedState and state not in _loadAllowedState:
            class_name = self.__class__.__name__
            excmsg = ("("+class_name+") setState, invalid state: '" +
                      str(state)+"'")
            raise LoaderException(excmsg)

        if self.state is None or self.state in _loadAllowedState:
            expected_state = _unloadAllowedState
        else:
            expected_state = _loadAllowedState

        if state not in expected_state:
            class_name = self.__class__.__name__
            excmsg = ("("+class_name+") setState, state not allowed. Expected"
                      " a state in '"+str(expected_state)+"', got '" +
                      str(state)+"'")
            raise LoaderException(excmsg)

        self.state = state

    def getState(self):
        return self.state

    @classmethod
    def _raiseIfInvalidClassDefinition(cls, meth_name, class_definition):
        raiseIfNotSubclass(class_definition,
                           "loader_class_definition",
                           AbstractLoader,
                           LoaderException,
                           meth_name,
                           cls.__name__)

    def addChild(self, loader_class_definition):
        self._raiseIfInvalidClassDefinition("addChild",
                                            loader_class_definition)

        if loader_class_definition in self.children:
            class_name = self.__class__.__name__
            excmsg = ("("+class_name+") getChild, '" +
                      str(loader_class_definition)+"' already exists")
            raise LoaderException(excmsg)

        profile = loader_class_definition.createProfileInstance()
        self.children[loader_class_definition] = profile
        return profile

    def hasChild(self, loader_class_definition):
        self._raiseIfInvalidClassDefinition("hasChild",
                                            loader_class_definition)
        return loader_class_definition in self.children

    def getChild(self, loader_class_definition):
        self._raiseIfInvalidClassDefinition("getChild",
                                            loader_class_definition)

        if loader_class_definition not in self.children:
            class_name = self.__class__.__name__
            excmsg = ("("+class_name+") getChild, '" +
                      str(loader_class_definition)+"' does not exist")
            raise LoaderException(excmsg)

        return self.children[loader_class_definition]

    def getChildKeys(self):
        return self.children.keys()
