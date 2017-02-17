#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2017  Jonathan Delvaux <pyshell@djoproject.net>

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
from pyshell.register.profile.globale import GlobalProfile
from pyshell.register.result.abstractresult import AbstractResult


class FakeResult(AbstractResult):
    pass


class FakeLoader(AbstractLoader):
    pass


class TestGlobalProfile(object):

    def test_getName(self):
        p_name = "profile name"
        p = GlobalProfile(p_name, None)
        assert p.getName() is p_name

    def test_getAddonInformations(self):
        o = object()
        p = GlobalProfile("profile name", o)
        p.getAddonInformations() is o

    def test_postResultNotAClassDefinition(self):
        p = GlobalProfile("profile name", object())
        with pytest.raises(LoaderException):
            p.postResult(42, FakeResult())

    def test_postResultNotALoaderClassDefinition(self):
        p = GlobalProfile("profile name", object())
        with pytest.raises(LoaderException):
            p.postResult(FakeResult, FakeResult())

    def test_postResultNotAResult(self):
        p = GlobalProfile("profile name", object())
        with pytest.raises(LoaderException):
            p.postResult(FakeLoader, object)

    def test_postResult(self):
        p = GlobalProfile("profile name", object())
        result = FakeResult()
        p.postResult(FakeLoader, result)
        results = p.getResult(FakeResult)
        assert len(results) == 1
        assert FakeLoader in results
        assert results[FakeLoader] is result

    def test_postResultAlreadyExist(self):
        p = GlobalProfile("profile name", object())
        p.postResult(FakeLoader, FakeResult())
        with pytest.raises(LoaderException):
            p.postResult(FakeLoader, FakeResult())

    def test_getResultNotExistingKey(self):
        p = GlobalProfile("profile name", object())
        assert isinstance(p.getResult("toto"), dict)

    def test_flushResult(self):
        p = GlobalProfile("profile name", object())
        result = FakeResult()
        p.postResult(FakeLoader, result)
        results = p.getResult(FakeResult)
        assert len(results) == 1
        p.flushResult()
        results = p.getResult(FakeResult)
        assert len(results) == 0
