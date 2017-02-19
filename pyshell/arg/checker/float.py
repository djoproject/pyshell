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

TYPENAME = "float"


class FloatArgChecker(ArgChecker):
    def __init__(self, minimum=None, maximum=None):
        ArgChecker.__init__(self, 1, 1, True)

        if (minimum is not None and
           type(minimum) != float and
           type(minimum) != int):
            excmsg = "Minimum must be a float or None, got '%s'"
            excmsg %= str(type(minimum))
            self._raiseArgInitializationException(excmsg)

        if (maximum is not None and
           type(maximum) != float and
           type(maximum) != int):
            excmsg = "Maximum must be a float or None, got '%s'"
            excmsg %= str(type(maximum))
            self._raiseArgInitializationException(excmsg)

        if minimum is not None and maximum is not None and maximum < minimum:
            excmsg = "Maximum <%s> can not be smaller than Minimum <%s>"
            excmsg %= (str(maximum), str(minimum),)
            self._raiseArgInitializationException(excmsg)

        self.minimum = minimum
        self.maximum = maximum

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        value = ArgChecker.getValue(self, value, arg_number, arg_name_to_bind)

        if value is None:
            excmsg = "the float arg can't be None"
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        try:
            casted_value = float(value)
        except ValueError:
            excmsg = "this arg is not a valid float or hexadecimal, got <%s>"
            excmsg %= str(value)
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        if self.minimum is not None:
            if casted_value < self.minimum:
                excmsg = ("the lowest value must be bigger or equal than <%s>"
                          ", got <%s>")
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
                return "<float "+str(self.minimum)+"-"+str(self.maximum)+">"
            return "<float "+str(self.minimum)+"-*.*>"
        else:
            if self.maximum is not None:
                return "<float *.*-"+str(self.maximum)+">"
        return "<float>"

    @classmethod
    def getTypeName(cls):
        return TYPENAME
