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

from tries import tries
from tries.exception import ambiguousPathException

from pyshell.arg.checker.string43 import StringArgChecker
from pyshell.utils.string65 import isString

TYPENAME = "token"


class TokenValueArgChecker(StringArgChecker):
    def __init__(self, token_dict):
        StringArgChecker.__init__(self, 1, None)
        if not isinstance(token_dict, dict):
            excmsg = "token_dict must be a dictionary, got '%s'"
            excmsg %= str(type(token_dict))
            self._raiseArgInitializationException(excmsg)

        self.localtries = tries()
        for k, v in token_dict.items():
            # key must be non empty string, value can be anything
            if not isString(k):
                excmsg = ("a key in the dictionary is  not a string: '%s', "
                          "type: '%s'")
                excmsg %= (str(k), str(type(k)),)
                self._raiseArgInitializationException(excmsg)

            self.localtries.insert(k, v)

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        value = StringArgChecker.getValue(self,
                                          value,
                                          arg_number,
                                          arg_name_to_bind)

        try:
            node = self.localtries.search(value)
            if node is None:
                excmsg = ("this arg '%s' is not an existing token, valid token"
                          " are (%s)")
                excmsg %= (str(value),
                           "|".join(self.localtries.getKeyList()),)
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)
            return node.value

        except ambiguousPathException:
            excmsg = "this arg '%s' is ambiguous, valid token are (%s)"
            excmsg %= (str(value), "|".join(self.localtries.getKeyList()),)
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

    def getUsage(self):
        return "("+("|".join(self.localtries.getKeyList()))+")"

    @classmethod
    def getTypeName(cls):
        return TYPENAME
