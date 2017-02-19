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

import sys

PY3 = sys.version_info[0] == 3


def isString(to_test):
    if PY3:
        return isinstance(to_test, str)
    else:
        # the following will check str and unicode string
        return isinstance(to_test, basestring)


def escapeString(string, wrapped=True):

    if len(string) == 0:
        return string

    string = string.replace("\\", "\\\\")
    string = string.replace("\"", "\\\"")

    if wrapped:
        if string[0] in ('$', '-',):
            string = "\\" + string

        return "\"" + string + "\""

    string = string.replace("$", "\\$")
    string = string.replace("&", "\\&")
    string = string.replace("|", "\\|")
    string = string.replace("-", "\\-")

    string = string.replace(" ", "\\ ")
    string = string.replace("\t", "\\\t")
    string = string.replace("\n", "\\\n")
    string = string.replace("\r", "\\\r")

    return string
