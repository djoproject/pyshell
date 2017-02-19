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
from pyshell.utils.raises import raiseIfNotSubclass


class InternalLoaderProfile(DefaultProfile):
    def __init__(self, root_profile):
        DefaultProfile.__init__(self, root_profile)
        self.children = {}

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

        p = loader_class_definition.createProfileInstance(
            self.getRootProfile())
        self.children[loader_class_definition] = p
        return p

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
