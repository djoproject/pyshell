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

from pyshell.arg.decorator import shellMethod
from pyshell.arg.argchecker import defaultInstanceArgChecker, listArgChecker, \
                                   IntegerArgChecker
from pyshell.utils.printing import printShell, strLength


@shellMethod(
    result=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def listResultHandler(result):
    if len(result) == 0:
        return result

    ret = ""
    for i in result:
        ret += str(i) + "\n"

    printShell(ret[:-1])
    return result


@shellMethod(
    result=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def listFlatResultHandler(result):
    if len(result) == 0:
        printShell("")
        return result

    s = ""
    for i in result:
        s += str(i) + " "

    printShell(s[:-1])

    return result


@shellMethod(string=listArgChecker(IntegerArgChecker(0, 255)))
def printStringCharResult(string):
    s = ""
    for char in string:
        s += chr(char)

    printShell(s)
    return string


@shellMethod(byteList=listArgChecker(IntegerArgChecker(0, 255)))
def printBytesAsString(byteList):
    if len(byteList) == 0:
        printShell("")
        return byteList

    ret = ""
    for b in byteList:
        ret += "%-0.2X" % b

    printShell(ret)

    return byteList


_defaultArgCheckerInstance = defaultInstanceArgChecker.getArgCheckerInstance()


@shellMethod(listOfLine=listArgChecker(_defaultArgCheckerInstance))
def printColumnWithouHeader(listOfLine):
    if len(listOfLine) == 0:
        return listOfLine

    # compute size
    column_size = {}
    spaceToAdd = 2  # at least two space column separator

    for row_index in range(0, len(listOfLine)):
        line = listOfLine[row_index]

        if type(line) == str or type(line) == unicode or \
           not hasattr(line, "__getitem__"):
            if 0 not in column_size:
                column_size[0] = strLength(str(line)) + spaceToAdd
            else:
                column_size[0] = max(column_size[0],
                                     strLength(str(line)) + spaceToAdd)
        else:
            for column_index in range(0, len(line)):
                if column_index not in column_size:
                    column_size[column_index] = \
                        strLength(str(line[column_index])) + spaceToAdd
                else:
                    column_size[column_index] = max(
                        column_size[column_index],
                        strLength(str(line[column_index])) + spaceToAdd)

    to_print = ""
    # print table
    for row_index in range(0, len(listOfLine)):
        line = listOfLine[row_index]

        if type(line) == str or type(line) == unicode or \
           not hasattr(line, "__getitem__"):
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
    return listOfLine


@shellMethod(listOfLine=listArgChecker(_defaultArgCheckerInstance))
def printColumn(listOfLine):
    if len(listOfLine) == 0:
        return listOfLine

    # compute size
    column_size = {}
    spaceToAdd = 2  # at least two space column separator

    for row_index in range(0, len(listOfLine)):
        line = listOfLine[row_index]

        # space to add to have the data column slighty on the right
        if row_index == 1:
            spaceToAdd += 1

        if type(line) == str or type(line) == unicode or \
           not hasattr(line, "__getitem__"):
            if 0 not in column_size:
                column_size[0] = strLength(str(line)) + spaceToAdd
            else:
                column_size[0] = max(column_size[0],
                                     strLength(str(line)) + spaceToAdd)
        else:
            for column_index in range(0, len(line)):
                if column_index not in column_size:
                    column_size[column_index] = \
                        strLength(str(line[column_index])) + spaceToAdd
                else:
                    column_size[column_index] = \
                        max(column_size[column_index],
                            strLength(str(line[column_index])) + spaceToAdd)

    to_print = ""
    # print table
    defaultPrefix = ""
    for row_index in range(0, len(listOfLine)):
        line = listOfLine[row_index]

        if row_index == 1:
            defaultPrefix = " "

        if type(line) == str or type(line) == unicode or \
           not hasattr(line, "__getitem__"):
            to_print += defaultPrefix + str(line) + "\n"

            # no need of pading if the line has only one column
        else:
            line_to_print = ""
            for column_index in range(0, len(line)):
                # no padding on last column
                if column_index == len(column_size) - 1 or \
                   column_index == len(line) - 1:
                    line_to_print += defaultPrefix + str(line[column_index])
                else:
                    padding = column_size[column_index] - \
                              strLength(str(line[column_index])) - \
                              len(defaultPrefix)
                    line_to_print += defaultPrefix + \
                        str(line[column_index]) + " "*padding

            to_print += line_to_print + "\n"

    printShell(to_print[:-1])
    return listOfLine
