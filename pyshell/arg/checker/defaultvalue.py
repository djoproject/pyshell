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

TYPENAME = "default"


class DefaultValueChecker(ArgChecker):
    def __init__(self, value):
        ArgChecker.__init__(self, 0, 0, False)
        self.setDefaultValue(value)

    def setDefaultValue(self, value, arg_name_to_bind=None):
        self.hasDefault = True
        self.default = value  # no check on the value...

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        return self.getDefaultValue(arg_name_to_bind)

    @classmethod
    def getTypeName(cls):
        return TYPENAME
