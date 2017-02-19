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

from pyshell.arg.checker.integer import IntegerArgChecker
from pyshell.utils.key import CryptographicKey

TYPENAME = "key"


class KeyArgChecker(IntegerArgChecker):
    "create a key from the input"
    def __init__(self):
        self.bases = [2, 16]
        self.shortType = "key"
        IntegerArgChecker.__init__(self, 0, None, True)

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        if isinstance(value, CryptographicKey):
            return value

        IntegerArgChecker.getValue(self, value, arg_number, arg_name_to_bind)

        try:
            return CryptographicKey(value)
        except Exception as e:
            excmsg = "Fail to resolve key: %s" % str(e)
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

    def getUsage(self):
        return "<key>"

    @classmethod
    def getTypeName(cls):
        return TYPENAME
