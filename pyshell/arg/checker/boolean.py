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

from pyshell.arg.checker.token43 import TokenValueArgChecker

try:
    from collections import OrderedDict
except:
    from pyshell.utils.ordereddict import OrderedDict

TYPENAME = "boolean"


class BooleanValueArgChecker(TokenValueArgChecker):
    def __init__(self, true_name=None, false_name=None):
        if true_name is None:
            true_name = "true"

        if false_name is None:
            false_name = "false"

        # the constructor of TokenValueArgChecker will check if every keys are
        ordered_items = OrderedDict([(true_name, True,), (false_name, False)])
        TokenValueArgChecker.__init__(self, ordered_items)
        self.true_name = true_name
        self.false_name = false_name

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        if type(value) == bool:
            if value:
                value = self.true_name
            else:
                value = self.false_name
        else:
            value = str(value).lower()

        return TokenValueArgChecker.getValue(self,
                                             value,
                                             arg_number,
                                             arg_name_to_bind)

    @classmethod
    def getTypeName(cls):
        return TYPENAME
