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

from pyshell.arg.checker.float import FloatArgChecker
from pyshell.arg.exception import ArgException
from pyshell.arg.exception import ArgInitializationException


class TestFloatArgChecker(object):

    def setup_method(self, method):
        self.checker = FloatArgChecker()

    def test_init(self):
        with pytest.raises(ArgInitializationException):
            FloatArgChecker("plop")
        with pytest.raises(ArgInitializationException):
            FloatArgChecker(1, "plop")
        with pytest.raises(ArgInitializationException):
            FloatArgChecker(None, "plop")
        with pytest.raises(ArgInitializationException):
            FloatArgChecker(5, 1)
        with pytest.raises(ArgInitializationException):
            FloatArgChecker(5.5, 1.0)

        assert FloatArgChecker(None) is not None
        assert FloatArgChecker(1.2, None) is not None
        assert FloatArgChecker(None, 1.5) is not None

    def test_check(self):
        with pytest.raises(ArgException):
            self.checker.getValue(None, 1)
        with pytest.raises(ArgException):
            self.checker.getValue("toto")
        with pytest.raises(ArgException):
            self.checker.getValue(u"toto")

    def test_get(self):
        assert 43 == self.checker.getValue("43")
        assert 52 == self.checker.getValue(52, 23)
        assert 0x52 == self.checker.getValue(0x52, 23)
        assert 1 == self.checker.getValue(True, 23)
        assert 0 == self.checker.getValue(False, 23)
        assert 43.542 == self.checker.getValue("43.542")
        assert 52.542 == self.checker.getValue(52.542, 23)
        assert 0x52 == self.checker.getValue(0x52, 23)
        assert 52.542 == self.checker.getValue(52.542, 23)

    def test_usage(self):
        assert self.checker.getUsage() == "<float>"

    def test_limit(self):
        self.checker = FloatArgChecker(5)
        with pytest.raises(ArgException):
            self.checker.getValue(3)
        with pytest.raises(ArgException):
            self.checker.getValue(-5)
        assert 52 == self.checker.getValue(52, 23)

        self.checker = FloatArgChecker(None, 5)
        with pytest.raises(ArgException):
            self.checker.getValue(52)
        assert 3 == self.checker.getValue(3, 23)
        assert -5 == self.checker.getValue(-5, 23)

        self.checker = FloatArgChecker(-5, 5)
        with pytest.raises(ArgException):
            self.checker.getValue(52)
        with pytest.raises(ArgException):
            self.checker.getValue(-52)
        assert 3 == self.checker.getValue(3, 23)
        assert -5 == self.checker.getValue(-5, 23)
