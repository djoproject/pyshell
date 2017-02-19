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

from pyshell.arg.checker.integer import BinaryArgChecker
from pyshell.arg.checker.integer import HexaArgChecker
from pyshell.arg.checker.integer import IntegerArgChecker
from pyshell.arg.checker.integer import LimitedInteger
from pyshell.arg.exception import ArgException
from pyshell.arg.exception import ArgInitializationException


class TestIntegerArgChecker(object):

    def setup_method(self, method):
        self.checker = IntegerArgChecker()

    def test_init(self):
        with pytest.raises(ArgInitializationException):
            IntegerArgChecker("plop")
        with pytest.raises(ArgInitializationException):
            IntegerArgChecker(1, "plop")
        with pytest.raises(ArgInitializationException):
            IntegerArgChecker(None, "plop")
        with pytest.raises(ArgInitializationException):
            IntegerArgChecker(5, 1)
        with pytest.raises(ArgInitializationException):
            IntegerArgChecker(5.5, 1.0)

        assert IntegerArgChecker(None) is not None
        assert IntegerArgChecker(1, None) is not None
        assert IntegerArgChecker(None, 1) is not None

    def test_check(self):
        with pytest.raises(ArgException):
            self.checker.getValue(None, 1)
        with pytest.raises(ArgException):
            self.checker.getValue("toto")
        with pytest.raises(ArgException):
            self.checker.getValue(u"toto")
        # self.assertRaises(ArgException, self.checker.getValue, 43.5, 4)
        # self.assertRaises(ArgException, self.checker.getValue, True)
        # self.assertRaises(ArgException, self.checker.getValue, False, 9)

    def test_get(self):
        assert 43 == self.checker.getValue("43")
        assert 52 == self.checker.getValue(52, 23)
        assert 0x52 == self.checker.getValue(0x52, 23)
        assert 52 == self.checker.getValue(52.33, 23)
        assert 1 == self.checker.getValue(True, 23)
        assert 0 == self.checker.getValue(False, 23)
        assert 0b0101001 == self.checker.getValue(0b0101001, 23)

    def test_usage(self):
        assert self.checker.getUsage() == "<int>"
        c = IntegerArgChecker(None, 1)
        assert c.getUsage() == "<int *-1>"
        c = IntegerArgChecker(1)
        assert c.getUsage() == "<int 1-*>"

    def test_limit(self):
        self.checker = IntegerArgChecker(5)
        with pytest.raises(ArgException):
            self.checker.getValue(3)
        with pytest.raises(ArgException):
            self.checker.getValue(-5)
        assert 52 == self.checker.getValue(52, 23)

        self.checker = IntegerArgChecker(None, 5)
        with pytest.raises(ArgException):
            self.checker.getValue(52)
        assert 3 == self.checker.getValue(3, 23)
        assert -5 == self.checker.getValue(-5, 23)

        self.checker = IntegerArgChecker(-5, 5)
        with pytest.raises(ArgException):
            self.checker.getValue(52)
        with pytest.raises(ArgException):
            self.checker.getValue(-52)
        assert 3 == self.checker.getValue(3, 23)
        assert -5 == self.checker.getValue(-5, 23)


class TestLimitedInteger(object):

    def test_init(self):
        with pytest.raises(ArgInitializationException):
            LimitedInteger(5)
        with pytest.raises(ArgInitializationException):
            LimitedInteger(23)

        l = LimitedInteger(8, True)
        assert l.minimum == -0x80
        assert l.maximum == 0x7f
        l = LimitedInteger(8)
        assert l.minimum == 0
        assert l.maximum == 0xff

        l = LimitedInteger(16, True)
        assert l.minimum == -0x8000
        assert l.maximum == 0x7fff
        l = LimitedInteger(16)
        assert l.minimum == 0
        assert l.maximum == 0xffff

        l = LimitedInteger(32, True)
        assert l.minimum == -0x80000000
        assert l.maximum == 0x7fffffff
        l = LimitedInteger(32)
        assert l.minimum == 0
        assert l.maximum == 0xffffffff


class TestHexaArgChecker(object):

    def setup_method(self, method):
        self.checker = HexaArgChecker()

    def test_check(self):
        with pytest.raises(ArgException):
            self.checker.getValue(None, 1)
        with pytest.raises(ArgException):
            self.checker.getValue("toto")
        with pytest.raises(ArgException):
            self.checker.getValue(u"toto")
        # self.assertRaises(ArgException, self.checker.getValue, 43.5, 4)
        # self.assertRaises(ArgException, self.checker.getValue, True)
        # self.assertRaises(ArgException, self.checker.getValue, False, 9)

    def test_get(self):
        assert 0x43 == self.checker.getValue("43")
        assert 0x34 == self.checker.getValue(52, 23)
        assert 0x34 == self.checker.getValue(52.33, 23)
        assert 0x52 == self.checker.getValue(0x52, 23)
        assert 1 == self.checker.getValue(True, 23)
        assert 0 == self.checker.getValue(False, 23)

    def test_usage(self):
        assert self.checker.getUsage() == "<hex>"


class TestBinaryArgChecker(object):

    def setup_method(self, method):
        self.checker = BinaryArgChecker()

    def test_check(self):
        with pytest.raises(ArgException):
            self.checker.getValue(None, 1)
        with pytest.raises(ArgException):
            self.checker.getValue("toto")
        with pytest.raises(ArgException):
            self.checker.getValue(u"toto")
        # self.assertRaises(ArgException, self.checker.getValue, 43.5, 4)
        # self.assertRaises(ArgException, self.checker.getValue, True)
        # self.assertRaises(ArgException, self.checker.getValue, False, 9)

    def test_get(self):
        assert 0b10 == self.checker.getValue("10")
        assert 0b10010101 == self.checker.getValue(0b10010101, 23)
        assert 52 == self.checker.getValue(52.33, 23)
        # self.assertTrue(0x52 == self.checker.getValue(0x52, 23))
        assert 1 == self.checker.getValue(True, 23)
        assert 0 == self.checker.getValue(False, 23)

    def test_usage(self):
        assert self.checker.getUsage() == "<bin>"
