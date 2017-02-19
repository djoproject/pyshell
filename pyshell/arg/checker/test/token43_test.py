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

from pyshell.arg.checker.token43 import TokenValueArgChecker
from pyshell.arg.exception import ArgException
from pyshell.arg.exception import ArgInitializationException

try:
    from collections import OrderedDict
except:
    from pyshell.utils.ordereddict import OrderedDict


class TestTokenArgChecker(object):

    def setup_method(self, method):
        ordered_items = OrderedDict([("toto", 53,), (u"plip", "kkk")])
        self.checker = TokenValueArgChecker(ordered_items)

    def test_init(self):
        with pytest.raises(ArgInitializationException):
            TokenValueArgChecker("toto")
        with pytest.raises(ArgInitializationException):
            TokenValueArgChecker({"toto": 53, 23: "kkk"})

    def test_check(self):
        with pytest.raises(ArgException):
            self.checker.getValue(None, 1)
        with pytest.raises(ArgException):
            self.checker.getValue(42)
        with pytest.raises(ArgException):
            self.checker.getValue(43.5, 4)
        with pytest.raises(ArgException):
            self.checker.getValue(True)
        with pytest.raises(ArgException):
            self.checker.getValue(False, 9)
        with pytest.raises(ArgException):
            self.checker.getValue("toti", 9)
        with pytest.raises(ArgException):
            self.checker.getValue("flofi", 9)

    def test_get(self):
        assert 53 == self.checker.getValue("t")
        assert 53 == self.checker.getValue("to")
        assert 53 == self.checker.getValue("tot")
        assert 53 == self.checker.getValue("toto")
        assert "kkk" == self.checker.getValue("plip")

    def test_ambiguous(self):
        checker = TokenValueArgChecker({"toto": 53, "tota": "kkk"})
        with pytest.raises(ArgException):
            checker.getValue("to", 1)

    def test_usage(self):
        assert self.checker.getUsage() == "(toto|plip)"
