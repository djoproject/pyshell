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

from pyshell.arg.checker.defaultvalue import DefaultValueChecker
from pyshell.arg.checker.integer import IntegerArgChecker
from pyshell.arg.checker.list import ListArgChecker
from pyshell.arg.checker.string43 import StringArgChecker
from pyshell.arg.exception import ArgException
from pyshell.arg.exception import ArgInitializationException


class TestListArgChecker(object):

    def test_init(self):
        with pytest.raises(ArgInitializationException):
            ListArgChecker(None)
        with pytest.raises(ArgInitializationException):
            ListArgChecker(ListArgChecker(IntegerArgChecker()))
        with pytest.raises(ArgInitializationException):
            ListArgChecker(23)
        with pytest.raises(ArgInitializationException):
            ListArgChecker(DefaultValueChecker(42))
        with pytest.raises(ArgInitializationException):
            ListArgChecker("plop")

        assert ListArgChecker(IntegerArgChecker()) is not None
        assert ListArgChecker(StringArgChecker()) is not None

    def test_get(self):
        # check/get, test special case with 1 item
        # c = ListArgChecker(IntegerArgChecker(), 1,1)
        # self.assertTrue(c.getValue("53") == 53)

        # check/get, test case without a list
        c = ListArgChecker(IntegerArgChecker())
        assert c.getValue("53") == [53]

        # check/get, test normal case
        assert c.getValue(["1", "2", "3"]) == [1, 2, 3]

    def test_default(self):
        # getDefault, test the 3 valid case and the error case
        c = ListArgChecker(IntegerArgChecker(), 1, 23)
        assert not c.hasDefaultValue()

        c = ListArgChecker(IntegerArgChecker())
        assert c.hasDefaultValue()

        c = ListArgChecker(IntegerArgChecker(), 1, 23)
        c.setDefaultValue([1, 2, 3])
        assert c.hasDefaultValue()

        i = IntegerArgChecker()
        i.setDefaultValue(42)
        c = ListArgChecker(i, 3, 23)
        assert c.hasDefaultValue()
        defv = c.getDefaultValue()
        assert len(defv) == c.minimum_size
        for v in defv:
            assert v == 42

        # test the completion of the list with default value
        defv = c.getValue(["42"])
        assert len(defv) == c.minimum_size
        for v in defv:
            assert v == 42

    def test_setDefault(self):
        # setDefaultValue, test special case with value, with empty list,
        # with normal list
        c = ListArgChecker(IntegerArgChecker(), 1, 1)

        assert c.setDefaultValue(["1", "2", "3"]) is None
        with pytest.raises(ArgException):
            c.setDefaultValue([])
        assert c.getValue("53") == [53]

        # setDefaultValue, test without special case, without list, with too
        # small list, with bigger list, with list between size
        c = ListArgChecker(IntegerArgChecker(), 5, 7)
        with pytest.raises(ArgException):
            c.setDefaultValue("plop")
        with pytest.raises(ArgException):
            c.setDefaultValue([1, 2, 3])
        assert c.setDefaultValue([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) is None
        assert len(c.getDefaultValue()) == 7
        assert c.setDefaultValue([1, 2, 3, 4, 5, 6]) is None

    def test_usage(self):
        c = ListArgChecker(IntegerArgChecker())
        assert c.getUsage() == "(<int> ... <int>)"

        c = ListArgChecker(IntegerArgChecker(), None, 5)
        assert c.getUsage() == "(<int>0 ... <int>4)"
        c = ListArgChecker(IntegerArgChecker(), None, 1)
        assert c.getUsage() == "(<int>)"
        c = ListArgChecker(IntegerArgChecker(), None, 2)
        assert c.getUsage() == "(<int>0 <int>1)"

        c = ListArgChecker(IntegerArgChecker(), 1)
        assert c.getUsage() == "<int>0 (... <int>)"
        c = ListArgChecker(IntegerArgChecker(), 2)
        assert c.getUsage() == "<int>0 <int>1 (... <int>)"
        c = ListArgChecker(IntegerArgChecker(), 23)
        assert c.getUsage() == "<int>0 ... <int>22 (... <int>)"

        c = ListArgChecker(IntegerArgChecker(), 1, 1)
        assert c.getUsage() == "<int>"

        c = ListArgChecker(IntegerArgChecker(), 1, 2)
        assert c.getUsage() == "<int>0 (<int>1)"
        c = ListArgChecker(IntegerArgChecker(), 2, 2)
        assert c.getUsage() == "<int>0 <int>1"

        c = ListArgChecker(IntegerArgChecker(), 1, 23)
        assert c.getUsage() == "<int>0 (<int>1 ... <int>22)"
        c = ListArgChecker(IntegerArgChecker(), 2, 23)
        assert c.getUsage() == "<int>0 <int>1 (<int>2 ... <int>22)"
        c = ListArgChecker(IntegerArgChecker(), 23, 23)
        assert c.getUsage() == "<int>0 ... <int>22"

        c = ListArgChecker(IntegerArgChecker(), 23, 56)
        assert c.getUsage() == "<int>0 ... <int>22 (<int>23 ... <int>55)"
