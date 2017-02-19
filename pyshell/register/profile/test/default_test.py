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

from pyshell.register.profile.default import DefaultProfile
from pyshell.register.profile.exception import RegisterException
from pyshell.register.profile.root import RootProfile


class TestDefaultProfile(object):
    def setup_method(self, method):
        root_profile = RootProfile()
        root_profile.setName("profile_name")
        self.p = DefaultProfile(root_profile)

    def test_setRootProfileInvalid(self):
        with pytest.raises(RegisterException):
            DefaultProfile(object)

    def test_setRootProfileValid(self):
        root_profile = RootProfile()
        root_profile.setName("profile_name")
        p = DefaultProfile(root_profile)
        assert p.getRootProfile() is root_profile

    def test_setLoadPriorityInvalid(self):
        assert self.p.getLoadPriority() == 100.0
        with pytest.raises(RegisterException):
            self.p.setLoadPriority(object)
        assert self.p.getLoadPriority() == 100.0

    def test_setLoadPriorityValid(self):
        assert self.p.getLoadPriority() == 100.0
        self.p.setLoadPriority(45)
        assert self.p.getLoadPriority() == 45.0

    def test_setUnloadPriorityInvalid(self):
        assert self.p.getUnloadPriority() == 100.0
        with pytest.raises(RegisterException):
            self.p.setUnloadPriority(object)
        assert self.p.getUnloadPriority() == 100.0

    def test_setUnloadPriorityValid(self):
        assert self.p.getUnloadPriority() == 100.0
        self.p.setUnloadPriority(54)
        assert self.p.getUnloadPriority() == 54.0

    def test_setLastExceptionExistingOne(self):
        assert self.p.getLastException() is None
        o = Exception()
        self.p.setLastException(o, "stacktrace")
        assert self.p.getLastException() is o

    def test_setLastExceptionNone(self):
        assert self.p.getLastException() is None
        o = Exception()
        self.p.setLastException(o, "stacktrace")
        assert self.p.getLastException() is o
        self.p.setLastException(None)
        assert self.p.getLastException() is None
