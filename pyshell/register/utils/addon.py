#!/usr/bin/env python -t
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


from pyshell.register.exception import LoaderException
from pyshell.register.loader.abstractloader import AbstractLoader
from pyshell.register.loader.root import RootLoader
from pyshell.register.utils.module import getNearestModule
from pyshell.utils.constants import DEFAULT_PROFILE_NAME
from pyshell.utils.raises import raiseIfNotString
from pyshell.utils.raises import raiseIfNotSubclass


class AddonInformation(object):
    """
        the purpose of this class is to allowed loader and addon to exchange
        infomations whithout creating an access to the addon object from
        the loaders
    """

    def __init__(self, name):
        self._name = name
        self.loaded_profile_name = None

    def getName(self):
        return self._name

    def setLoadedProfileName(self, name):
        self.loaded_profile_name = name

    def getLoadedProfileName(self):
        return self.loaded_profile_name

    def unsetLoadedProfileName(self):
        self.loaded_profile_name = None


class AddonLoader(object):

    def __init__(self, addon_name):
        self._profiles = {}
        self._informations = AddonInformation(addon_name)

    @staticmethod
    def getRootLoaderClass():
        return RootLoader

    def getInformations(self):
        return self._informations

    def _checkProfileName(self, method_name, profile_name):
        if profile_name is None:
            return DEFAULT_PROFILE_NAME

        raiseIfNotString(profile_name,
                         "profile_name",
                         LoaderException,
                         method_name,
                         self.__class__.__name__)

        return profile_name

    def _checkLoaderClass(self, method_name, loader_class):
        raiseIfNotSubclass(loader_class,
                           "loader_class",
                           AbstractLoader,
                           LoaderException,
                           method_name,
                           self.__class__.__name__)

    def _checkIfProfileExist(self, method_name, profile_name):
        profile_name = self._checkProfileName(method_name, profile_name)

        if profile_name not in self._profiles:
            excmsg = "(%s) %s, the profile '%s' does not exist"
            raise LoaderException(excmsg % (self.__class__.__name__,
                                            method_name,
                                            profile_name))

        return profile_name

    def hasProfile(self, profile_name):
        profile_name = self._checkProfileName("hasProfile", profile_name)
        return profile_name in self._profiles

    def createProfile(self, profile_name):
        profile_name = self._checkProfileName("createProfile", profile_name)

        if profile_name in self._profiles:
            excmsg = "(%s) createProfile, the profile '%s' already exists"
            raise LoaderException(excmsg % (self.__class__.__name__,
                                            profile_name))

        rootp = self.getRootLoaderClass().createProfileInstance(None)
        rootp.setName(profile_name)
        rootp.setAddonInformations(self._informations)
        self._profiles[profile_name] = rootp

    def removeProfileIfEmpty(self, profile_name):
        profile_name = self._checkIfProfileExist("hasProfile", profile_name)
        internal_profile = self._profiles[profile_name]

        if len(internal_profile.getChildKeys()) > 0:
            return

        del self._profiles[profile_name]

    def isLoaderBindedToProfile(self, loader_class, profile_name):
        self._checkLoaderClass("isLoaderBindedToProfile", loader_class)
        profile_name = self._checkIfProfileExist(
            "isLoaderBindedToProfile", profile_name)
        internal_profile = self._profiles[profile_name]
        return internal_profile.hasChild(loader_class)

    def bindLoaderToProfile(self, loader_class, profile_name):
        self._checkLoaderClass("bindLoaderToProfile", loader_class)
        profile_name = self._checkIfProfileExist(
            "isLoaderBindedToProfile", profile_name)

        internal_profile = self._profiles[profile_name]

        if internal_profile.hasChild(loader_class):
            excmsg = ("(%s) bindLoaderToProfile, the loader '%s' is already "
                      "binded to the profile '%s'")
            raise LoaderException(excmsg % (self.__class__.__name__,
                                            loader_class.__name__,
                                            profile_name))

        return internal_profile.addChild(loader_class)

    def getRootLoaderProfile(self, profile_name):
        profile_name = self._checkIfProfileExist(
            "getLoaderProfile", profile_name)
        return self._profiles[profile_name]

    def getLoaderProfile(self, loader_class, profile_name):
        self._checkLoaderClass("getLoaderProfile", loader_class)
        profile_name = self._checkIfProfileExist(
            "getLoaderProfile", profile_name)

        internal_profile = self._profiles[profile_name]

        if not internal_profile.hasChild(loader_class):
            excmsg = ("(%s) bindLoaderToProfile, the loader '%s' is not "
                      "binded to the profile '%s'")
            raise LoaderException(excmsg % (self.__class__.__name__,
                                            loader_class.__name__,
                                            profile_name))

        return internal_profile.getChild(loader_class)

    def load(self, container, profile_name=None):
        profile_name = self._checkIfProfileExist('load', profile_name)
        root_profile = self._profiles[profile_name]
        return self.getRootLoaderClass().load(root_profile, container)

    def unload(self, container, profile_name=None):
        profile_name = self._checkIfProfileExist('unload', profile_name)
        root_profile = self._profiles[profile_name]
        return self.getRootLoaderClass().unload(root_profile, container)

    @classmethod
    def getAddonLoader(cls):
        mod = getNearestModule()

        if hasattr(mod, "_loaders"):
            if not isinstance(mod._loaders, cls):
                excmsg = ("(" + str(cls.__name__) + ") getRootLoader, the "
                          "stored loader in the module '" + str(mod) +
                          "' is not an instance of '" + cls.__name__ +
                          "', get '" + str(type(mod._loaders)) + "'")
                raise LoaderException(excmsg)

            return mod._loaders
        else:
            master = cls(mod.__name__)
            setattr(mod, "_loaders", master)
            return master


def getOrCreateProfile(loader_class,
                       profile_name=None,
                       addon_loader=AddonLoader):
    raiseIfNotSubclass(loader_class,
                       "loader_class",
                       AbstractLoader,
                       LoaderException,
                       "getOrCreateProfile",
                       "Addon")

    if profile_name is not None:
        raiseIfNotString(profile_name,
                         "profile_name",
                         LoaderException,
                         "getOrCreateProfile",
                         "Addon")

    master_loader = addon_loader.getAddonLoader()
    profile_created = False
    if not master_loader.hasProfile(profile_name):
        profile_created = True
        master_loader.createProfile(profile_name)

    try:
        if not master_loader.isLoaderBindedToProfile(
                loader_class, profile_name):
            return master_loader.bindLoaderToProfile(
                loader_class, profile_name)

        return master_loader.getLoaderProfile(loader_class, profile_name)
    except:
        if profile_created:
            master_loader.removeProfileIfEmpty(profile_name)
        raise
