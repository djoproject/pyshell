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

from pyshell.arg.checker.argchecker import ArgChecker
from pyshell.utils.string65 import isString

TYPENAME = "string"


class StringArgChecker(ArgChecker):
    def __init__(self, minimum_string_size=0, maximum_string_size=None):
        ArgChecker.__init__(self, 1, 1, True)

        if type(minimum_string_size) != int:
            excmsg = ("Minimum string size must be an integer, got type '%s' "
                      "with the following value <%s>")
            excmsg %= (str(type(minimum_string_size)),
                       str(minimum_string_size),)
            self._raiseArgInitializationException(excmsg)

        if minimum_string_size < 0:
            excmsg = ("Minimum string size must be a positive value bigger or "
                      "equal to 0, got <%s>")
            excmsg %= str(minimum_string_size)
            self._raiseArgInitializationException(excmsg)

        if maximum_string_size is not None:
            if type(maximum_string_size) != int:
                excmsg = ("Maximum string size must be an integer, got type "
                          "'%s' with the following value <%s>")
                excmsg %= (str(type(maximum_string_size)),
                           str(maximum_string_size),)
                self._raiseArgInitializationException(excmsg)

            if maximum_string_size < 1:
                excmsg = ("Maximum string size must be a positive value bigger"
                          " than 0, got <%s>")
                excmsg %= str(maximum_string_size)
                self._raiseArgInitializationException(excmsg)

        if (minimum_string_size is not None and
           maximum_string_size is not None and
           maximum_string_size < minimum_string_size):
            excmsg = ("Maximum string size <%s> can not be smaller than "
                      "Minimum string size <%s>")
            excmsg %= (str(maximum_string_size), str(minimum_string_size),)
            self._raiseArgInitializationException(excmsg)

        self.minimum_string_size = minimum_string_size
        self.maximum_string_size = maximum_string_size

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        value = ArgChecker.getValue(self, value, arg_number, arg_name_to_bind)

        if value is None:
            excmsg = "the string arg can't be None"
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        if not isString(value):
            if not hasattr(value, "__str__"):
                excmsg = "this value '%s' is not a valid string, got type '%s'"
                excmsg %= (str(value), str(type(value)),)
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

            value = str(value)

        if len(value) < self.minimum_string_size:
            excmsg = ("this value '%s' is a too small string, got size '%s' "
                      "with value '%s', minimal allowed size is '%s'")
            excmsg %= (str(value),
                       str(len(value)),
                       str(value),
                       str(self.minimum_string_size),)
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        if (self.maximum_string_size is not None and
           len(value) > self.maximum_string_size):
            excmsg = ("this value '%s' is a too big string, got size '%s' with"
                      " value '%s', maximal allowed size is '%s'")
            excmsg %= (str(value),
                       str(len(value)),
                       str(value),
                       str(self.maximum_string_size),)
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        return value

    def getUsage(self):
        return "<string>"

    @classmethod
    def getTypeName(cls):
        return TYPENAME
