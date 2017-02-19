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
from pyshell.register.profile.root import RootProfile
from pyshell.register.result.abstractresult import AbstractResult
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_LOADED_E
from pyshell.utils.constants import STATE_LOADING
from pyshell.utils.constants import STATE_UNLOADED
from pyshell.utils.constants import STATE_UNLOADED_E
from pyshell.utils.constants import STATE_UNLOADING


class TestRootProfile(object):
    def setup_method(self, method):
        self.p = RootProfile()

    def test_setUnknownState(self):
        with pytest.raises(LoaderException):
            self.p.setState("toto")
        assert self.p.hasNoState()

    def test_setNotAllowedUnloadedState(self):
        with pytest.raises(LoaderException):
            self.p.setState(STATE_LOADED)
        assert self.p.hasNoState()

    def test_setAllowedKnownState(self):
        self.p.setState(STATE_LOADING)
        assert self.p.isLoading()
        assert not self.p.hasNoState()

    def test_setAllowedUnloadedState(self):
        self.p.setState(STATE_LOADING)
        self.p.setState(STATE_LOADED)
        assert self.p.isLoaded()
        assert not self.p.hasNoState()

    def test_setUnallowedLoadedState(self):
        self.p.setState(STATE_LOADING)
        with pytest.raises(LoaderException):
            self.p.setState(STATE_UNLOADED)
        assert self.p.isLoading()
        assert not self.p.hasNoState()


class FakeResult(AbstractResult):
    pass


class FakeLoader(AbstractLoader):
    pass


class TestRootProfilePart2(object):

    def test_getName(self):
        p_name = "profile name"
        p = RootProfile()
        p.setName(p_name)
        assert p.getName() is p_name

    def test_getAddonInformations(self):
        o = object()
        p = RootProfile()
        p.setAddonInformations(o)
        p.getAddonInformations() is o

    def test_postResultNotAClassDefinition(self):
        p = RootProfile()
        with pytest.raises(LoaderException):
            p.postResult(42, FakeResult())

    def test_postResultNotALoaderClassDefinition(self):
        p = RootProfile()
        with pytest.raises(LoaderException):
            p.postResult(FakeResult, FakeResult())

    def test_postResultNotAResult(self):
        p = RootProfile()
        with pytest.raises(LoaderException):
            p.postResult(FakeLoader, object)

    def test_postResult(self):
        p = RootProfile()
        result = FakeResult()
        p.postResult(FakeLoader, result)
        results = p.getResult(FakeResult)
        assert len(results) == 1
        assert FakeLoader in results
        assert results[FakeLoader] is result

    def test_postResultAlreadyExist(self):
        p = RootProfile()
        p.postResult(FakeLoader, FakeResult())
        with pytest.raises(LoaderException):
            p.postResult(FakeLoader, FakeResult())

    def test_getResultNotExistingKey(self):
        p = RootProfile()
        assert isinstance(p.getResult("toto"), dict)

    def test_flush(self):
        p = RootProfile()
        result = FakeResult()
        p.postResult(FakeLoader, result)
        results = p.getResult(FakeResult)
        assert len(results) == 1
        p.flush()
        results = p.getResult(FakeResult)
        assert len(results) == 0

    def test_isLoading(self):
        p = RootProfile()
        p.setState(STATE_LOADING)
        assert p.isLoading()

    def test_isLoaded(self):
        p = RootProfile()
        p.setState(STATE_LOADING)
        p.setState(STATE_LOADED)
        assert p.isLoaded()
        assert not p.hasError()

    def test_isLoadede(self):
        p = RootProfile()
        p.setState(STATE_LOADING)
        p.setState(STATE_LOADED_E)
        assert p.isLoaded()
        assert p.hasError()

    def test_isUnloading(self):
        p = RootProfile()
        p.setState(STATE_LOADING)
        p.setState(STATE_LOADED)
        p.setState(STATE_UNLOADING)
        assert p.isUnloading()
        assert not p.hasError()

    def test_isUnloaded(self):
        p = RootProfile()
        p.setState(STATE_LOADING)
        p.setState(STATE_LOADED)
        p.setState(STATE_UNLOADING)
        p.setState(STATE_UNLOADED)
        assert p.isUnloaded()
        assert not p.hasError()

    def test_isUnloadede(self):
        p = RootProfile()
        p.setState(STATE_LOADING)
        p.setState(STATE_LOADED)
        p.setState(STATE_UNLOADING)
        p.setState(STATE_UNLOADED_E)
        assert p.isUnloaded()
        assert p.hasError()
