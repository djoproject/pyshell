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

from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.integer import IntegerArgChecker
from pyshell.arg.checker.list import ListArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.utils.printing import printShell
from pyshell.utils.printing import strLength
from pyshell.utils.string65 import isString


@shellMethod(result=ListArgChecker(DefaultChecker.getArg()))
def listResultHandler(result):
    if len(result) == 0:
        return result

    ret = ""
    for i in result:
        ret += str(i) + "\n"

    printShell(ret[:-1])
    return result


@shellMethod(result=ListArgChecker(DefaultChecker.getArg()))
def listFlatResultHandler(result):
    if len(result) == 0:
        printShell("")
        return result

    s = ""
    for i in result:
        s += str(i) + " "

    printShell(s[:-1])

    return result


@shellMethod(string=ListArgChecker(IntegerArgChecker(0, 255)))
def printStringCharResult(string):
    s = ""
    for char in string:
        s += chr(char)

    printShell(s)
    return string


@shellMethod(byte_list=ListArgChecker(IntegerArgChecker(0, 255)))
def printBytesAsString(byte_list):
    if len(byte_list) == 0:
        printShell("")
        return byte_list

    ret = ""
    for b in byte_list:
        ret += "%-0.2X" % b

    printShell(ret)

    return byte_list


_defaultArgCheckerInstance = DefaultChecker.getArg()


@shellMethod(list_of_line=ListArgChecker(_defaultArgCheckerInstance))
def printColumnWithouHeader(list_of_line):
    if len(list_of_line) == 0:
        return list_of_line

    # compute size
    column_size = {}
    space_to_add = 2  # at least two space column separator

    for row_index in range(0, len(list_of_line)):
        line = list_of_line[row_index]

        if isString(line) or not hasattr(line, "__getitem__"):
            if 0 not in column_size:
                column_size[0] = strLength(str(line)) + space_to_add
            else:
                column_size[0] = max(column_size[0],
                                     strLength(str(line)) + space_to_add)
        else:
            for column_index in range(0, len(line)):
                if column_index not in column_size:
                    column_size[column_index] = \
                        strLength(str(line[column_index])) + space_to_add
                else:
                    column_size[column_index] = max(
                        column_size[column_index],
                        strLength(str(line[column_index])) + space_to_add)

    to_print = ""
    # print table
    for row_index in range(0, len(list_of_line)):
        line = list_of_line[row_index]

        if isString(line) or not hasattr(line, "__getitem__"):
            to_print += str(line) + "\n"

            # no need of pading if the line has only the first column
        else:
            line_to_print = ""
            for column_index in range(0, len(line)):
                if column_index == len(column_size) - 1 or \
                 column_index == len(line) - 1:  # no padding on last column
                    line_to_print += str(line[column_index])
                else:
                    padding = column_size[column_index] - \
                              strLength(str(line[column_index]))
                    line_to_print += str(line[column_index]) + " "*padding

            to_print += line_to_print + "\n"

    printShell(to_print[:-1])
    return list_of_line


@shellMethod(list_of_line=ListArgChecker(_defaultArgCheckerInstance))
def printColumn(list_of_line):
    if len(list_of_line) == 0:
        return list_of_line

    # compute size
    column_size = {}
    space_to_add = 2  # at least two space column separator

    for row_index in range(0, len(list_of_line)):
        line = list_of_line[row_index]

        # space to add to have the data column slighty on the right
        if row_index == 1:
            space_to_add += 1

        if isString(line) or not hasattr(line, "__getitem__"):
            if 0 not in column_size:
                column_size[0] = strLength(str(line)) + space_to_add
            else:
                column_size[0] = max(column_size[0],
                                     strLength(str(line)) + space_to_add)
        else:
            for column_index in range(0, len(line)):
                if column_index not in column_size:
                    column_size[column_index] = \
                        strLength(str(line[column_index])) + space_to_add
                else:
                    column_size[column_index] = \
                        max(column_size[column_index],
                            strLength(str(line[column_index])) + space_to_add)

    to_print = ""
    # print table
    default_prefix = ""
    for row_index in range(0, len(list_of_line)):
        line = list_of_line[row_index]

        if row_index == 1:
            default_prefix = " "

        if isString(line) or not hasattr(line, "__getitem__"):
            to_print += default_prefix + str(line) + "\n"

            # no need of pading if the line has only one column
        else:
            line_to_print = ""
            for column_index in range(0, len(line)):
                # no padding on last column
                if column_index == len(column_size) - 1 or \
                   column_index == len(line) - 1:
                    line_to_print += default_prefix + str(line[column_index])
                else:
                    padding = column_size[column_index] - \
                              strLength(str(line[column_index])) - \
                              len(default_prefix)
                    line_to_print += default_prefix + \
                        str(line[column_index]) + " "*padding

            to_print += line_to_print + "\n"

    printShell(to_print[:-1])
    return list_of_line
