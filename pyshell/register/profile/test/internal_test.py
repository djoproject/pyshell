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
from pyshell.register.profile.internal import InternalLoaderProfile
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_UNLOADED


class FakeLoader(AbstractLoader):
    @staticmethod
    def createProfileInstance():
        return object()


class TestInternalLoaderProfile(object):
    def setup_method(self, method):
        self.p = InternalLoaderProfile()

    def test_notRoot(self):
        assert not self.p.isRoot()

    def test_setRoot(self):
        self.p.setRoot()
        assert self.p.isRoot()

    def test_setUnknownState(self):
        with pytest.raises(LoaderException):
            self.p.setState("toto")
        assert self.p.getState() is None

    def test_setNotAllowedUnloadedState(self):
        with pytest.raises(LoaderException):
            self.p.setState(STATE_UNLOADED)
        assert self.p.getState() is None

    def test_setAllowedKnownState(self):
        self.p.setState(STATE_LOADED)
        assert self.p.getState() is STATE_LOADED

    def test_setAllowedUnloadedState(self):
        self.p.setState(STATE_LOADED)
        self.p.setState(STATE_UNLOADED)
        assert self.p.getState() is STATE_UNLOADED

    def test_setUnallowedLoadedState(self):
        self.p.setState(STATE_LOADED)
        with pytest.raises(LoaderException):
            self.p.setState(STATE_LOADED)
        assert self.p.getState() is STATE_LOADED

    def test_addChildNotAValidLoader1(self):
        with pytest.raises(LoaderException):
            self.p.addChild(42)

    def test_addChildNotAValidLoader2(self):
        with pytest.raises(LoaderException):
            self.p.addChild(object)

    def test_addChild(self):
        self.p.addChild(FakeLoader)
        assert self.p.hasChild(FakeLoader)
        assert self.p.getChild(FakeLoader) is not None
        assert len(self.p.getChildKeys()) == 1
        assert FakeLoader in self.p.getChildKeys()

    def test_addExistingChild(self):
        self.p.addChild(FakeLoader)
        with pytest.raises(LoaderException):
            self.p.addChild(FakeLoader)

    def test_hasChildNotAValidLoader1(self):
        with pytest.raises(LoaderException):
            self.p.hasChild(42)

    def test_hasChildNotAValidLoader2(self):
        with pytest.raises(LoaderException):
            self.p.hasChild(object)

    def test_hasChildDoesNotExist(self):
        assert not self.p.hasChild(FakeLoader)

    def test_getChildNotAValidLoader1(self):
        with pytest.raises(LoaderException):
            self.p.getChild(42)

    def test_getChildNotAValidLoader2(self):
        with pytest.raises(LoaderException):
            self.p.getChild(object)

    def test_getChildDoesNotExist(self):
        with pytest.raises(LoaderException):
            self.p.getChild(FakeLoader)

    def test_getChildKeysEmpty(self):
        assert len(self.p.getChildKeys()) == 0
