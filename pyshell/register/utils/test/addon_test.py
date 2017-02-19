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

import pytest

from pyshell.register.exception import LoaderException
from pyshell.register.loader.abstractloader import AbstractLoader
from pyshell.register.loader.root import RootLoader
from pyshell.register.profile.default import DefaultProfile
from pyshell.register.utils.addon import AddonInformation
from pyshell.register.utils.addon import AddonLoader
from pyshell.register.utils.addon import getOrCreateProfile
from pyshell.register.utils.module import getNearestModule


class TestAddonInformation(object):

    def test_init(self):
        i = AddonInformation("name")
        assert i.getName() == "name"
        assert i.getLoadedProfileName() is None

    def test_setLoadedProfileName(self):
        i = AddonInformation("name")
        assert i.getLoadedProfileName() is None
        i.setLoadedProfileName("toto")
        assert i.getLoadedProfileName() is "toto"

    def test_unsetLoadedProfileName(self):
        i = AddonInformation("name")
        i.setLoadedProfileName("toto")
        i.unsetLoadedProfileName()
        assert i.getLoadedProfileName() is None


class LoaderAa(AbstractLoader):

    @staticmethod
    def createProfileInstance(root_profile):
        return DefaultProfile(root_profile)


class LoaderBb(AbstractLoader):

    @staticmethod
    def createProfileInstance(root_profile):
        return DefaultProfile(root_profile)


class TestAddonLoader(object):

    def test_getRootLoaderClass(self):
        assert AddonLoader.getRootLoaderClass() is RootLoader

    def test_getInformations(self):
        a = AddonLoader("plop")
        assert a.getInformations().getName() == "plop"

    def test_hasProfileInvalidProfileName(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.hasProfile(object)

    def test_hasProfileDoesNotExist(self):
        a = AddonLoader("plop")
        assert not a.hasProfile("titi")

    def test_hasProfileExists(self):
        a = AddonLoader("plop")
        a.createProfile("titi")
        assert a.hasProfile("titi")

    def test_hasProfileNoneDoesNotExist(self):
        a = AddonLoader("plop")
        assert not a.hasProfile(None)

    def test_hasProfileNoneExists(self):
        a = AddonLoader("plop")
        a.createProfile(None)
        assert a.hasProfile(None)

    def test_createProfileInvalidProfileName(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.createProfile(object)

    def test_createProfileAlreadyExists(self):
        a = AddonLoader("plop")
        a.createProfile("titi")
        with pytest.raises(LoaderException):
            a.createProfile("titi")

    def test_createProfileValid(self):
        a = AddonLoader("plop")
        a.createProfile("titi")
        assert a.hasProfile("titi")

    def test_removeProfileIfEmptyInvalidProfileName(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.removeProfileIfEmpty(object)

    def test_removeProfileIfEmptyDoesNotExist(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.removeProfileIfEmpty("titi")

    def test_removeProfileIfEmptyNotEmpty(self):
        a = AddonLoader("plop")
        a.createProfile("titi")
        a.bindLoaderToProfile(LoaderAa, "titi")
        a.removeProfileIfEmpty("titi")
        assert a.hasProfile("titi")

    def test_removeProfileIfEmptyValid(self):
        a = AddonLoader("plop")
        a.createProfile("titi")
        a.removeProfileIfEmpty("titi")
        assert not a.hasProfile("titi")

    def test_isLoaderBindedToProfileInvalidLoaderClass(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.isLoaderBindedToProfile(42, "titi")

    def test_isLoaderBindedToProfileInvalidProfileName(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.isLoaderBindedToProfile(LoaderAa, object)

    def test_isLoaderBindedToProfileProfileNameDoesNotExist(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.isLoaderBindedToProfile(LoaderAa, "titi")

    def test_isLoaderBindedToProfileNotBinded(self):
        a = AddonLoader("plop")
        a.createProfile("titi")
        assert not a.isLoaderBindedToProfile(LoaderAa, "titi")

    def test_isLoaderBindedToProfileBinded(self):
        a = AddonLoader("plop")
        a.createProfile("titi")
        a.bindLoaderToProfile(LoaderAa, "titi")
        assert a.isLoaderBindedToProfile(LoaderAa, "titi")

    def test_bindLoaderToProfileInvalidLoaderClass(self):
        a = AddonLoader("plop")
        a.createProfile("titi")
        with pytest.raises(LoaderException):
            a.bindLoaderToProfile(42, "titi")

    def test_bindLoaderToProfileInvalidProfileName(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.bindLoaderToProfile(LoaderAa, object)

    def test_bindLoaderToProfileProfileNameDoesNotExist(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.bindLoaderToProfile(42, "titi")

    def test_bindLoaderToProfileAlreadyBinded(self):
        a = AddonLoader("plop")
        a.createProfile("titi")
        a.bindLoaderToProfile(LoaderAa, "titi")
        with pytest.raises(LoaderException):
            a.bindLoaderToProfile(LoaderAa, "titi")

    def test_bindLoaderToProfileValid(self):
        a = AddonLoader("plop")
        a.createProfile("titi")
        a.bindLoaderToProfile(LoaderAa, "titi")

    def test_getRootLoaderProfileInvalidProfileName(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.getRootLoaderProfile(object)

    def test_getRootLoaderProfileProfileNameDoesNotExist(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.getRootLoaderProfile("titi")

    def test_getRootLoaderProfileValid(self):
        a = AddonLoader("plop")
        a.createProfile("titi")
        a.getRootLoaderProfile("titi")

    def test_getLoaderProfileInvalidLoaderClass(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.getLoaderProfile(42, "titi")

    def test_getLoaderProfileInvalidProfileName(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.getLoaderProfile(LoaderAa, object)

    def test_getLoaderProfileProfileNameDoesNotExist(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.getLoaderProfile(LoaderAa, "titi")

    def test_getLoaderProfileNotBinded(self):
        a = AddonLoader("plop")
        a.createProfile("titi")
        with pytest.raises(LoaderException):
            a.getLoaderProfile(LoaderAa, "titi")

    def test_getLoaderProfileValid(self):
        a = AddonLoader("plop")
        a.createProfile("titi")
        p = a.bindLoaderToProfile(LoaderAa, "titi")
        assert p == a.getLoaderProfile(LoaderAa, "titi")

    def test_loadInvalidProfileName(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.load(None, object)

    def test_loadProfileNameDoesNotExist(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.load(None, "titi")

    def test_loadValid(self):
        a = AddonLoader("plop")
        a.createProfile("titi")
        a.load(None, "titi")

    def test_unloadInvalidProfileName(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.unload(None, object)

    def test_unloadProfileNameDoesNotExist(self):
        a = AddonLoader("plop")
        with pytest.raises(LoaderException):
            a.unload(None, "titi")

    def test_unloadValid(self):
        a = AddonLoader("plop")
        a.createProfile("titi")
        a.load(None, "titi")
        a.unload(None, "titi")


class TestAddonLoaderGetAddonLoader(object):

    def teardown_method(self, method):
        mod = getNearestModule()
        if hasattr(mod, "_loaders"):
            delattr(mod, "_loaders")

    def test_getAddonLoaderSomethingElseExists(self):
        mod = getNearestModule()
        setattr(mod, "_loaders", 42)
        with pytest.raises(LoaderException):
            AddonLoader.getAddonLoader()

    def test_getAddonLoaderDoesNotExist(self):
        a = AddonLoader.getAddonLoader()
        assert isinstance(a, AddonLoader)

    def test_getAddonLoaderAlreadyExists(self):
        a1 = AddonLoader.getAddonLoader()
        a2 = AddonLoader.getAddonLoader()
        assert a1 is a2


class LoaderError(AbstractLoader):

    @staticmethod
    def createProfileInstance(root_profile):
        raise Exception("Ooops")


class TestGetOrCreateProfile(object):

    def teardown_method(self, method):
        mod = getNearestModule()
        if hasattr(mod, "_loaders"):
            delattr(mod, "_loaders")

    def test_invalidProfileName(self):
        with pytest.raises(LoaderException):
            getOrCreateProfile(LoaderAa, object)

    def test_invalidLoaderClass(self):
        with pytest.raises(LoaderException):
            getOrCreateProfile(object, "titi")

    def test_profileCreationAndLoaderDoesNotExist(self):
        p = getOrCreateProfile(LoaderAa, "titi")
        assert isinstance(p, DefaultProfile)

    def test_profileCreationAndErrorAndEmpty(self):
        with pytest.raises(Exception):
            getOrCreateProfile(LoaderError, "titi")

        mod = getNearestModule()
        ap = getattr(mod, "_loaders")
        assert not ap.hasProfile("titi")

    def test_profileAlreadyExistsAndError(self):
        getOrCreateProfile(LoaderAa, "titi")

        with pytest.raises(Exception):
            getOrCreateProfile(LoaderError, "titi")

        mod = getNearestModule()
        ap = getattr(mod, "_loaders")
        assert ap.hasProfile("titi")

    def test_profileExistsAndLoaderExists(self):
        p1 = getOrCreateProfile(LoaderAa, "titi")
        p2 = getOrCreateProfile(LoaderAa, "titi")
        assert p1 is p2

    def test_profileExistsAndLoaderDoesNotExist(self):
        getOrCreateProfile(LoaderAa, "titi")
        p2 = getOrCreateProfile(LoaderBb, "titi")
        assert isinstance(p2, DefaultProfile)
