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

from math import log

from pyshell.arg.checker.argchecker import ArgChecker
from pyshell.utils.string65 import isString

INTEGERCHECKER_TYPENAME = "integer"
LIMITEDINTEGERCHECKER_TYPENAME = "limited integer"
HEXACHECKER_TYPENAME = "hexadecimal"
BINARYCHECKER_TYPENAME = "binary"


class IntegerArgChecker(ArgChecker):
    def __init__(self, minimum=None, maximum=None, show_in_usage=True):
        ArgChecker.__init__(self, 1, 1, True)

        if not hasattr(self, "shortType"):
            self.shortType = "int"

        if not hasattr(self, "bases"):
            self.bases = [10, 16, 2]

        if (minimum is not None and
           type(minimum) != int and
           type(minimum) != float):
            excmsg = ("Minimum must be an integer or None, got <%s>")
            excmsg %= str(type(minimum))
            self._raiseArgInitializationException(excmsg)

        if (maximum is not None and
           type(maximum) != int and
           type(maximum) != float):
            excmsg = ("Maximum must be an integer or None, got <%s>")
            excmsg %= str(type(maximum))
            self._raiseArgInitializationException(excmsg)

        if minimum is not None and maximum is not None and maximum < minimum:
            excmsg = ("Maximum size <%s> can not be smaller than Minimum size"
                      " <%s>")
            excmsg %= (str(maximum), str(minimum),)
            self._raiseArgInitializationException(excmsg)

        self.minimum = minimum
        self.maximum = maximum

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        value = ArgChecker.getValue(self, value, arg_number, arg_name_to_bind)

        if value is None:
            excmsg = "the '%s' arg can't be None" % self.getTypeName().lower()
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        casted_value = None
        if type(value) == int or type(value) == float or type(value) == bool:
            casted_value = int(value)
        elif isString(value):
            for b in self.bases:
                try:
                    casted_value = int(value, b)
                    break
                except ValueError:
                    continue

        if casted_value is None:

            if len(self.bases) == 1:
                message = ("Only a number in base <"+str(self.bases[0])+"> is "
                           "allowed")
            else:
                message = ("Only a number in bases <" +
                           ", ".join(str(x) for x in self.bases) +
                           "> is allowed")

            excmsg = "this arg is not a valid '%s', got <%s>. %s"
            excmsg %= (self.getTypeName().lower(), str(value), message,)
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        if self.minimum is not None:
            if casted_value < self.minimum:
                excmsg = ("the lowest value must be bigger or equal than <%s>,"
                          " got <%s>")
                excmsg %= (str(self.minimum), str(value),)
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        if self.maximum is not None:
            if casted_value > self.maximum:
                excmsg = ("the biggest value must be lower or equal than <%s>,"
                          " got <%s>")
                excmsg %= (str(self.maximum), str(value),)
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        return casted_value

    def getUsage(self):
        if self.minimum is not None:
            if self.maximum is not None:
                return ("<"+self.shortType+" "+str(self.minimum)+"-" +
                        str(self.maximum)+">")
            return "<"+self.shortType+" "+str(self.minimum)+"-*>"
        else:
            if self.maximum is not None:
                return "<"+self.shortType+" *-"+str(self.maximum)+">"
        return "<"+self.shortType+">"

    @classmethod
    def getTypeName(cls):
        return INTEGERCHECKER_TYPENAME


class LimitedInteger(IntegerArgChecker):
    def __init__(self, amount_of_bit=8, signed=False):
        if amount_of_bit < 8:
            excmsg = "the amount of bit must at least be 8, got <%s>"
            excmsg %= str(amount_of_bit)
            self._raiseArgInitializationException(excmsg)

        if log(amount_of_bit, 2) % 1 != 0:
            excmsg = ("only powers of 2 are allowed, 8, 16, 32, 64, ..., got"
                      " <%s>")
            excmsg %= str(amount_of_bit)
            self._raiseArgInitializationException(excmsg)

        if signed:
            minimum = -(2**(amount_of_bit-1))
            maximum = (2**(amount_of_bit-1))-1
        else:
            minimum = 0
            maximum = (2**amount_of_bit)-1

        IntegerArgChecker.__init__(self, minimum, maximum, True)

    @classmethod
    def getTypeName(cls):
        return LIMITEDINTEGERCHECKER_TYPENAME


class HexaArgChecker(IntegerArgChecker):
    def __init__(self, minimum=None, maximum=None):
        self.bases = [16]
        self.shortType = "hex"
        IntegerArgChecker.__init__(self, minimum, maximum, True)

    @classmethod
    def getTypeName(cls):
        return HEXACHECKER_TYPENAME


class BinaryArgChecker(IntegerArgChecker):
    def __init__(self, minimum=None, maximum=None):
        self.bases = [2]
        self.shortType = "bin"
        IntegerArgChecker.__init__(self, minimum, maximum, True)

    @classmethod
    def getTypeName(cls):
        return BINARYCHECKER_TYPENAME
