#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.arg.abstract import AbstractArg
from pyshell.arg.exception import ArgException
from pyshell.arg.exception import ArgInitializationException

TYPENAME = "any"


class ArgChecker(AbstractArg):
    def __init__(self,
                 minimum_size=1,
                 maximum_size=1,
                 show_in_usage=True):
        self.setSize(minimum_size, maximum_size)
        self.defaultValueEnabled = True
        self.hasDefault = False
        self.default = None
        self._show_in_usage = show_in_usage

    def getMinimumSize(self):
        return self._minimum_size

    def getMaximumSize(self):
        return self._maximum_size

    def isShowInUsage(self):
        return self._show_in_usage

    def setSize(self, minimum_size=None, maximum_size=None):
        self.checkSize(minimum_size, maximum_size)
        self._minimum_size = minimum_size
        self._maximum_size = maximum_size

    def checkSize(self, minimum_size, maximum_size):
        if minimum_size is not None:
            if type(minimum_size) != int:
                excmsg = ("Minimum size must be an integer, got type '%s' "
                          "with the following value <%s>")
                excmsg %= (str(type(minimum_size)), str(minimum_size),)
                self._raiseArgInitializationException(excmsg)

            if minimum_size < 0:
                excmsg = "Minimum size must be a positive value, got <%s>"
                excmsg %= str(minimum_size)
                self._raiseArgInitializationException(excmsg)

        if maximum_size is not None:
            if type(maximum_size) != int:
                excmsg = ("Maximum size must be an integer, got type '%s' "
                          "with the following value <%s>")
                excmsg %= (str(type(maximum_size)), str(maximum_size), )
                self._raiseArgInitializationException(excmsg)

            if maximum_size < 0:
                excmsg = "Maximum size must be a positive value, got <%s>"
                excmsg %= str(maximum_size)
                self._raiseArgInitializationException(excmsg)

        if (minimum_size is not None and
           maximum_size is not None and
           maximum_size < minimum_size):
            excmsg = ("Maximum size <%s> can not be smaller than Minimum"
                      " size <%s>")
            excmsg %= (str(maximum_size), str(minimum_size),)
            self._raiseArgInitializationException(excmsg)

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        return value

    def getUsage(self):
        return "<any>"

    def getDefaultValue(self, arg_name_to_bind=None):
        if not self.hasDefaultValue(arg_name_to_bind):
            self._raiseArgException("there is no default value")

        return self.default

    def hasDefaultValue(self, arg_name_to_bind=None):
        if not self.defaultValueEnabled:
            return False

        return self.hasDefault

    def setDefaultValue(self, value, arg_name_to_bind=None):
        if not self.defaultValueEnabled:
            # TODO (issue #41)  use arg_name_to_bind (if not None)
            #   in the exc msg
            excmsg = ("default value is not allowed with this kind of checker,"
                      " probably because it is a default instance checker")
            self._raiseArgInitializationException(excmsg)

        self.hasDefault = True

        if value is None:
            self.default = None
            return

        # will convert the value if needed
        self.default = self.getValue(value, None, arg_name_to_bind)

    def setDefaultValueEnable(self, state):
        self.defaultValueEnabled = state

    def setEngine(self, engine):
        pass

    def _raiseArgException(self,
                           message,
                           arg_number=None,
                           arg_name_to_bind=None):
        prefix = ""

        if arg_number is not None:
            prefix += "Token <"+str(arg_number)+">"

        if arg_name_to_bind is not None:
            if len(prefix) > 0:
                prefix += " "

            prefix += "at argument '"+str(arg_name_to_bind)+"'"

        if len(prefix) > 0:
            prefix += ": "

        raise ArgException("("+self.getTypeName()+") "+prefix+message)

    def _raiseArgInitializationException(self, message):
        excmsg = "(%s) %s" % (self.getTypeName(), message)
        raise ArgInitializationException(excmsg)

    @classmethod
    def getTypeName(cls):
        return TYPENAME
