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

from pyshell.arg.checker.string43 import StringArgChecker
from pyshell.arg.exception import ArgException


class TestStringArgChecker(object):

    def setup_method(self, method):
        self.checker = StringArgChecker()

    def test_check(self):
        with pytest.raises(ArgException):
            self.checker.getValue(None, 1)
        assert self.checker.getValue(42) == "42"
        assert self.checker.getValue(43.5, 4) == "43.5"
        assert self.checker.getValue(True) == "True"
        assert self.checker.getValue(False, 9) == "False"

    def test_get(self):
        assert "toto" == self.checker.getValue("toto")
        assert u"toto" == self.checker.getValue(u"toto", 23)

    def test_usage(self):
        assert self.checker.getUsage() == "<string>"
