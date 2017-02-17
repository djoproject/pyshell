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
from pyshell.system.parameter import Parameter


class FakeParameter(Parameter):
    pass


class FakeIntParameter(Parameter):

    def __init__(self, value, settings=None):
        if not isinstance(value, int):
            raise ValueError("not an int")


class TestParameterInit(object):

    def test_noClassDeclaration(self):
        with pytest.raises(RegisterException):
            ParameterLoaderProfile(parameter_definition=42)

    def test_notClassInheritingFromParameter(self):
        with pytest.raises(RegisterException):
            ParameterLoaderProfile(parameter_definition=object)

    def test_successInit(self):
        ParameterLoaderProfile(parameter_definition=FakeParameter)


class TestParameterLoaderAddParameter(object):

    def setup_method(self, method):
        self.loader_profile = ParameterLoaderProfile(
            parameter_definition=FakeParameter)

    def test_invalidPath(self):
        with pytest.raises(RegisterException):
            self.loader_profile.addParameter(object, FakeParameter(42))

    def test_invalidParameterInstance(self):
        with pytest.raises(RegisterException):
            self.loader_profile.addParameter("tutu.tata", Parameter(42))

    def test_notAParameterAndCanNotBeUsedAsValue(self):
        profile = ParameterLoaderProfile(
            parameter_definition=FakeIntParameter)
        with pytest.raises(RegisterException):
            profile.addParameter("tutu.tata", "plop")

    def test_success(self):
        self.loader_profile.addParameter("tutu.tata", FakeParameter(42))

    def test_success2(self):
        self.loader_profile.addParameter("tutu.tata", 42)
