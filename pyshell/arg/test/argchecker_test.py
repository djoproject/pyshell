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

from pyshell.arg.argchecker import ArgChecker
from pyshell.arg.argchecker import BinaryArgChecker
from pyshell.arg.argchecker import BooleanValueArgChecker
from pyshell.arg.argchecker import DefaultValueChecker
from pyshell.arg.argchecker import FloatTokenArgChecker
from pyshell.arg.argchecker import HexaArgChecker
from pyshell.arg.argchecker import IntegerArgChecker
from pyshell.arg.argchecker import LimitedInteger
from pyshell.arg.argchecker import ListArgChecker
from pyshell.arg.argchecker import StringArgChecker
from pyshell.arg.argchecker import TokenValueArgChecker
from pyshell.arg.exception import ArgException
from pyshell.arg.exception import ArgInitializationException

try:
    from collections import OrderedDict
except:
    from pyshell.utils.ordereddict import OrderedDict


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

        a.erraseDefaultValue()
        assert not a.hasDefaultValue()
        with pytest.raises(ArgException):
            a.getDefaultValue()

    def test_misc(self):
        a = ArgChecker()
        assert a.getUsage() == "<any>"
        assert a.getValue(28000) == 28000


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


class TestFloatArgChecker(object):

    def setup_method(self, method):
        self.checker = FloatTokenArgChecker()

    def test_init(self):
        with pytest.raises(ArgInitializationException):
            FloatTokenArgChecker("plop")
        with pytest.raises(ArgInitializationException):
            FloatTokenArgChecker(1, "plop")
        with pytest.raises(ArgInitializationException):
            FloatTokenArgChecker(None, "plop")
        with pytest.raises(ArgInitializationException):
            FloatTokenArgChecker(5, 1)
        with pytest.raises(ArgInitializationException):
            FloatTokenArgChecker(5.5, 1.0)

        assert FloatTokenArgChecker(None) is not None
        assert FloatTokenArgChecker(1.2, None) is not None
        assert FloatTokenArgChecker(None, 1.5) is not None

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
        self.checker = FloatTokenArgChecker(5)
        with pytest.raises(ArgException):
            self.checker.getValue(3)
        with pytest.raises(ArgException):
            self.checker.getValue(-5)
        assert 52 == self.checker.getValue(52, 23)

        self.checker = FloatTokenArgChecker(None, 5)
        with pytest.raises(ArgException):
            self.checker.getValue(52)
        assert 3 == self.checker.getValue(3, 23)
        assert -5 == self.checker.getValue(-5, 23)

        self.checker = FloatTokenArgChecker(-5, 5)
        with pytest.raises(ArgException):
            self.checker.getValue(52)
        with pytest.raises(ArgException):
            self.checker.getValue(-52)
        assert 3 == self.checker.getValue(3, 23)
        assert -5 == self.checker.getValue(-5, 23)

"""class TestLittleEngine(object):
    def __init__(self, d):
        self.d = d

    def getEnv(self):
        return self.d

class TestEnvironmentArgChecker(object):
    def test_init(self):
        #self.assertRaises(ArgInitializationException,environmentChecker, None)
        self.assertRaises(ArgInitializationException,environmentChecker, {})

    # TODO test les conditions qui testent la validité du dictionnaire dans
    # getDefault, getValue, ...

    def test_key(self):
        checker = environmentChecker("plop")
        checker.setEngine(littleEngine({"toto":53, u"plip":"kkk"}))
        self.assertRaises(ArgException,checker.getValue, [])

        checker = environmentChecker("toto")
        checker.setEngine(littleEngine({"toto":53, u"plip":"kkk"}))
        self.assertTrue(checker.getValue([]) == 53)

        d = {"toto":53, u"plip":"kkk"}
        checker = environmentChecker("plop")
        checker.setEngine(littleEngine(d))
        d["plop"] = 33
        self.assertTrue(checker.getValue([]) == 33)

        #arg in the env
        #arg not in the env
        #..."""

"""class TestEnvironmentDynamicChecker(object):
    #def test_init(self):
    #    self.assertRaises(ArgInitializationException,
                           environmentDynamicChecker)

    # TODO test les conditions qui testent la validité du dictionnaire
    # dans getDefault, getValue, ...

    def test_key(self):
        checker = environmentDynamicChecker()
        checker.setEngine(littleEngine({"toto":53, u"plip":"kkk"}))
        self.assertRaises(ArgException,checker.getValue, [])

        checker = environmentDynamicChecker()
        checker.setEngine(littleEngine({"toto":53, u"plip":"kkk"}))
        self.assertTrue(checker.getValue("toto") == 53)

        d = {"toto":53, u"plip":"kkk"}
        checker = environmentDynamicChecker()
        checker.setEngine(littleEngine(d))
        d["plop"] = 33
        self.assertTrue(checker.getValue("plop") == 33)"""


class TestDefaultArgChecker(object):

    def setup_method(self, method):
        self.checker = DefaultValueChecker("53")

    def test_get(self):
        assert "53" == self.checker.getValue("43")
        assert "53" == self.checker.getValue(52, 23)
        assert "53" == self.checker.getValue(0x52, 23)
        assert "53" == self.checker.getValue(52.33, 23)
        assert "53" == self.checker.getValue(True, 23)
        assert "53" == self.checker.getValue(False, 23)

    def test_usage(self):
        assert self.checker.getUsage() == "<any>"


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


class TestArgFeeder(object):
    pass  # TODO
