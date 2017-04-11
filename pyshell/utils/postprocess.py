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

from pyshell.arg.accessor.context import ContextAccessor
from pyshell.arg.accessor.environment import EnvironmentAccessor
from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.integer import IntegerArgChecker
from pyshell.arg.checker.list import ListArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.utils.constants import CONTEXT_EXECUTION_KEY
from pyshell.utils.constants import CONTEXT_EXECUTION_SHELL
from pyshell.utils.constants import ENVIRONMENT_TAB_SIZE_KEY
from pyshell.utils.constants import TAB_SIZE
from pyshell.utils.misc import getTerminalSize
from pyshell.utils.printing import printShell
from pyshell.utils.printing import reduceFormatedString
from pyshell.utils.printing import strLength
from pyshell.utils.string65 import isString


# TODO should also limit the single column size
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


def _computeSize(list_of_line, padding=2, extra_padding=0):
    sizes = [0]  # at least one line

    increase_padding = True
    prefix_padding = 0
    for line in list_of_line:
        if isString(line) or not hasattr(line, "__iter__"):
            sizes[0] = max(sizes[0], strLength(str(line)) + padding)
        else:
            if len(line) > len(sizes):
                sizes.extend([0] * (len(line) - len(sizes)))

            for cindex in range(0, len(line)):
                if cindex < len(line)-1:
                    new_value = prefix_padding + strLength(str(line[cindex]))
                    new_value += padding
                else:
                    new_value = prefix_padding + strLength(str(line[cindex]))
                sizes[cindex] = max(sizes[cindex], new_value)

        # space to add to have the data column slighty on the right in front
        # of the title line
        if increase_padding:
            prefix_padding = extra_padding
            increase_padding = False

    return sizes


def _printUntilColumn(column_size, con_execution, tab_size):
    if tab_size is None:
        tab_size = TAB_SIZE
    else:
        tab_size = tab_size.getValue()

    if (con_execution is not None and
       con_execution.getSelectedValue() == CONTEXT_EXECUTION_SHELL):
        # get sizes (tab, terminal, ...)
        width, height = getTerminalSize()

        # remove the tab size added by printShell
        width -= tab_size

        for i in range(0, len(column_size)):
            if column_size[i] >= width:
                return i, width
            width -= column_size[i]

    # there is room for every columns
    return len(column_size)-1, column_size[-1]


@shellMethod(list_of_line=ListArgChecker(_defaultArgCheckerInstance),
             tab_size=EnvironmentAccessor(ENVIRONMENT_TAB_SIZE_KEY),
             con_execution=ContextAccessor(CONTEXT_EXECUTION_KEY))
def printColumnWithouHeader(list_of_line, tab_size=None, con_execution=None):
    if len(list_of_line) == 0:
        return list_of_line

    column_size = _computeSize(list_of_line)
    last_col, space_last_col = _printUntilColumn(column_size,
                                                 con_execution,
                                                 tab_size)

    to_print = ""
    for row_index in range(0, len(list_of_line)):
        line = list_of_line[row_index]

        if isString(line) or not hasattr(line, "__iter__"):
            to_print += str(line) + "\n"
            # TODO must be reduce to IFF last column
        else:  # no need of pading if the line has only the first column
            line_to_print = ""
            latest_column = min(len(line)-1, last_col)
            for column_index in range(0, latest_column+1):
                column = str(line[column_index])
                if column_index < latest_column:
                    # no padding on last column
                    padding = 0
                    padding = column_size[column_index]
                    padding -= strLength(str(line[column_index]))
                    column += " "*padding
                else:
                    column = reduceFormatedString(column, space_last_col)

                line_to_print += column
            to_print += line_to_print + "\n"

    printShell(to_print[:-1])
    return list_of_line


@shellMethod(list_of_line=ListArgChecker(_defaultArgCheckerInstance),
             tab_size=EnvironmentAccessor(ENVIRONMENT_TAB_SIZE_KEY),
             con_execution=ContextAccessor(CONTEXT_EXECUTION_KEY))
def printColumn(list_of_line, tab_size=None, con_execution=None):
    if len(list_of_line) == 0:
        return list_of_line

    column_size = _computeSize(list_of_line, extra_padding=1)
    last_col, space_last_col = _printUntilColumn(column_size,
                                                 con_execution,
                                                 tab_size)

    to_print = ""
    default_prefix = ""
    for row_index in range(0, len(list_of_line)):
        line = list_of_line[row_index]

        if row_index == 1:
            default_prefix = " "

        if isString(line) or not hasattr(line, "__iter__"):
            to_print += default_prefix + str(line) + "\n"
            # TODO must be reduce to IFF last column
        else:  # no need of pading if the line has only one column
            line_to_print = ""
            latest_column = min(len(line)-1, last_col)
            for column_index in range(0, latest_column+1):
                padding = 0
                column = default_prefix + str(line[column_index])
                if column_index < latest_column:
                    # no padding on last column
                    padding = column_size[column_index]
                    padding -= strLength(str(line[column_index]))
                    padding -= len(default_prefix)
                    column += " "*padding
                else:
                    column = reduceFormatedString(column, space_last_col)

                line_to_print += column
            to_print += line_to_print + "\n"

    printShell(to_print[:-1])
    return list_of_line
