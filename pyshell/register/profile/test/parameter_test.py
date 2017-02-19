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

from pyshell.register.profile.exception import RegisterException
from pyshell.register.profile.parameter import ParameterLoaderProfile
from pyshell.register.profile.root import RootProfile
from pyshell.system.parameter.abstract import Parameter


class FakeParameter(Parameter):
    pass


class FakeIntParameter(Parameter):

    def __init__(self, value, settings=None):
        if not isinstance(value, int):
            raise ValueError("not an int")


class TestParameterInit(object):
    def setup_method(self, method):
        self.root_profile = RootProfile()
        self.root_profile.setName("profile_name")

    def test_noClassDeclaration(self):
        with pytest.raises(RegisterException):
            ParameterLoaderProfile(parameter_definition=42,
                                   root_profile=self.root_profile)

    def test_notClassInheritingFromParameter(self):
        with pytest.raises(RegisterException):
            ParameterLoaderProfile(parameter_definition=object,
                                   root_profile=self.root_profile)

    def test_successInit(self):
        ParameterLoaderProfile(parameter_definition=FakeParameter,
                               root_profile=self.root_profile)


class TestParameterLoaderAddParameter(object):

    def setup_method(self, method):
        self.root_profile = RootProfile()
        self.root_profile.setName("profile_name")
        self.loader_profile = ParameterLoaderProfile(
            parameter_definition=FakeParameter,
            root_profile=self.root_profile)

    def test_invalidPath(self):
        with pytest.raises(RegisterException):
            self.loader_profile.addParameter(object, FakeParameter(42))

    def test_invalidParameterInstance(self):
        with pytest.raises(RegisterException):
            self.loader_profile.addParameter("tutu.tata", Parameter(42))

    def test_notAParameterAndCanNotBeUsedAsValue(self):
        profile = ParameterLoaderProfile(
            parameter_definition=FakeIntParameter,
            root_profile=self.root_profile)
        with pytest.raises(RegisterException):
            profile.addParameter("tutu.tata", "plop")

    def test_success(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))

    def test_success2(self):
        self.loader_profile.addParameter("tutu.tata", 42)
