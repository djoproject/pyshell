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

from pyshell.register.profile.dependency import DependencyLoaderProfile
from pyshell.register.profile.exception import RegisterException


class TestDependencyLoaderProfile(object):
    def setup_method(self, method):
        self.p = DependencyLoaderProfile()

    def test_addDependencyInvalidAddonName(self):
        with pytest.raises(RegisterException):
            self.p.addDependency(object)

    def test_addDependencyInvalidProfileName(self):
        with pytest.raises(RegisterException):
            self.p.addDependency("name", object)

    def test_addDependencyAddonAlreadyExist(self):
        self.p.addDependency("name", "profile")
        with pytest.raises(RegisterException):
            self.p.addDependency("name", "profile")

    def test_addDependencyValidAdd(self):
        self.p.addDependency("name", "profile")
