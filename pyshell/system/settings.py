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

import collections

from pyshell.utils.constants import EMPTY_STRING
from pyshell.utils.constants import SYSTEM_VIRTUAL_LOADER
from pyshell.utils.exception import ParameterException


class Settings(object):
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

    def isFantom(self):
        return False

    def addLoader(self, loader_signature):
        pass

    def mergeFromPreviousSettings(self, parameter):
        pass

    def getLoaderSet(self):
        return None

    def getProperties(self):
        return (("removable", self.isRemovable(),),
                ("readOnly", self.isReadOnly(),),
                ("transient", self.isTransient(),))

    def __hash__(self):
        return hash(self.getProperties())

    def clone(self, parent=None):
        if parent is None:
            return Settings()

        return parent


class LocalSettings(Settings):
    def __init__(self, read_only=False, removable=True):
        self.read_only = False
        self.setRemovable(removable)
        self.setReadOnly(read_only)

    def setReadOnly(self, state):
        if type(state) != bool:
            raise ParameterException("(LocalSettings) setReadOnly, expected a"
                                     " bool type as state, got '" +
                                     str(type(state))+"'")

        self.read_only = state

    def isReadOnly(self):
        return self.read_only

    def _raiseIfReadOnly(self, class_name=None, meth_name=None):
        if self.isReadOnly():
            if meth_name is not None:
                meth_name = str(meth_name)+", "
            else:
                meth_name = EMPTY_STRING

            if class_name is not None:
                class_name = "("+str(class_name)+") "
            else:
                class_name = EMPTY_STRING

            excmsg = class_name+meth_name+"read only parameter"
            raise ParameterException(excmsg)

    def setRemovable(self, state):
        self._raiseIfReadOnly(self.__class__.__name__, "setRemovable")

        if type(state) != bool:
            raise ParameterException("(LocalSettings) setRemovable, expected "
                                     "a bool type as state, got '" +
                                     str(type(state))+"'")

        self.removable = state

    def isRemovable(self):
        return self.removable

    def clone(self, parent=None):
        if parent is None:
            return LocalSettings(self.isReadOnly(), self.isRemovable())
        else:
            read_only = self.isReadOnly()
            parent.setReadOnly(False)
            parent.setRemovable(self.isRemovable())
            parent.setReadOnly(read_only)

        return Settings.clone(self, parent)


class GlobalSettings(LocalSettings):
    def __init__(self, read_only=False, removable=True, transient=False):
        LocalSettings.__init__(self, False, removable)

        self.setTransient(transient)
        self.loaderSet = {}
        self.startingHash = None
        self.setReadOnly(read_only)

    def setTransient(self, state):
        self._raiseIfReadOnly(self.__class__.__name__, "setTransient")

        if type(state) != bool:
            raise ParameterException("(GlobalSettings) setTransient, expected "
                                     "a bool type as state, got '" +
                                     str(type(state))+"'")

        self.transient = state

    def isTransient(self):
        return self.transient

    def setLoaderState(self, loader_signature, loader_state):
        # loaderState must be hashable
        if not isinstance(loader_signature, collections.Hashable):
            raise ParameterException("(GlobalSettings) setLoaderState, "
                                     "loader_signature has to be hashable")

        self.loaderSet[loader_signature] = loader_state
        return loader_state

    def getLoaderState(self, loader_signature):
        return self.loaderSet[loader_signature]

    def hasLoaderState(self, loader_signature):
        return loader_signature in self.loaderSet

    def hashForLoader(self, loader_signature=None):
        if loader_signature is None:
            SYSTEM_VIRTUAL_LOADER

        if loader_signature is not SYSTEM_VIRTUAL_LOADER:
            return hash(self.loaderSet[loader_signature])

        if SYSTEM_VIRTUAL_LOADER not in self.loaderSet:
            return hash(self)

        self_hash = str(hash(self))
        loader_set_hash = str(hash(self.loaderSet[loader_signature]))
        return hash(self_hash+loader_set_hash)

    def getLoaders(self):
        return self.loaderSet.keys()

    def isFantom(self):
        return len(self.loaderSet) == 0

    # #### TODO remove method below, and update parameter/container
    #   each loader will store two hash for each storable items
    #   (original hash, hash after file load)
    #   merge does not exist anymore
    #   create a method, setRegisteredHashForLoader, setFileHashForLoader
    #   (these methods will be called in loaders)
    #       these methods only take the loaders signature as argument,
    #       the hash occurs on the information stored in the settings

    def mergeFromPreviousSettings(self, settings):
        if settings is None:
            return

        if not isinstance(settings, GlobalSettings):
            raise ParameterException("(GlobalSettings) "
                                     "mergeFromPreviousSettings, a "
                                     "GlobalSettings object was expected, "
                                     "got '"+str(type(settings))+"'")

        # manage loader
        other_loaders = settings.getLoaderSet()
        if self.loaderSet is None:
            if other_loaders is not None:
                self.loaderSet = set(other_loaders)
        elif other_loaders is not None:
            self.loaderSet = self.loaderSet.union(other_loaders)

        # manage origin
        self.startingHash = settings.startingHash

    def setStartingPoint(self, hashi, origin, origin_profile=None):
        if self.startingHash is not None:
            raise ParameterException("(GlobalSettings) setStartingPoint, a "
                                     "starting point was already defined for "
                                     "this parameter")

        self.startingHash = hashi

    def isEqualToStartingHash(self, hashi):
        return hashi == self.startingHash

    # XXX stop removing here ###############################################

    def clone(self, parent=None):
        if parent is None:
            parent = GlobalSettings(self.isReadOnly(),
                                    self.isRemovable(),
                                    self.isTransient())
        else:
            read_only = self.isReadOnly()
            parent.setReadOnly(False)
            parent.setTransient(self.isTransient())
            parent.setReadOnly(read_only)

        # TODO clone loader state
        #   if no clone method, use copy tools
        #       simple or deep copy ?

        return LocalSettings.clone(self, parent)
