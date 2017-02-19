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

from pyshell.arg.checker.boolean import BooleanValueArgChecker
from pyshell.arg.exception import ArgException


class TestBooleanArgChecker(object):

    def setup_method(self, method):
        self.checker = BooleanValueArgChecker()

    def test_check(self):
        with pytest.raises(ArgException):
            self.checker.getValue(None, 1)
        with pytest.raises(ArgException):
            self.checker.getValue(42)
        with pytest.raises(ArgException):
            self.checker.getValue(43.5, 4)
        # self.assertRaises(ArgException, self.checker.getValue, True)
        # self.assertRaises(ArgException, self.checker.getValue, False, 9)

    def test_get(self):
        assert self.checker.getValue("true") is True
        assert self.checker.getValue(u"false", 23) is False
        assert self.checker.getValue(True) is True
        assert self.checker.getValue(False, 23) is False

    def test_usage(self):
        assert self.checker.getUsage() == "(true|false)"
