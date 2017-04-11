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

import pytest

from pyshell.arg.checker.argchecker import ArgChecker
from pyshell.arg.exception import ArgException
from pyshell.arg.exception import ArgInitializationException


class TestArgChecker():

    def test_initLimitCase(self):
        with pytest.raises(ArgInitializationException):
            ArgChecker("plop")
        with pytest.raises(ArgInitializationException):
            ArgChecker(1, "plop")
        with pytest.raises(ArgInitializationException):
            ArgChecker(-1)
        with pytest.raises(ArgInitializationException):
            ArgChecker(1, -1)
        with pytest.raises(ArgInitializationException):
            ArgChecker(5, 1)
        assert ArgChecker() is not None

    def test_defaultValue(self):
        a = ArgChecker()
        assert not a.hasDefaultValue()
        with pytest.raises(ArgException):
            a.getDefaultValue()

        a.setDefaultValue("plop")
        assert a.hasDefaultValue()
        assert a.getDefaultValue() == "plop"

    def test_misc(self):
        a = ArgChecker()
        assert a.getUsage() == "<any>"
        assert a.getValue(28000) == 28000
