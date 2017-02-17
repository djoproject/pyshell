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

# TODO
#   - comparison between two byte list
#   - comparison on bit or byte
#   - look after pattern
#   - ...

from math import log

from pyshell.arg.argchecker import DefaultInstanceArgChecker
from pyshell.arg.argchecker import IntegerArgChecker
from pyshell.arg.argchecker import ListArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.register.command import registerCommand
from pyshell.register.command import registerSetGlobalPrefix
from pyshell.register.command import registerStopHelpTraversalAt
from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.printing import formatOrange
from pyshell.utils.printing import formatRed
from pyshell.utils.printing import printShell
from pyshell.utils.printing import strLength
from pyshell.utils.printing import warning


@shellMethod(
    var_lists=ListArgChecker(
        DefaultInstanceArgChecker.getStringArgCheckerInstance()),
    parameters=DefaultInstanceArgChecker.getCompleteEnvironmentChecker(),
    byte_per_line=IntegerArgChecker(4))
def compareByteList(var_lists, byte_per_line=4, parameters=None):
    # TODO
    #   it is possible to inject something else than byte in the list,
    #   check them
    #       DONE!
    #       test it

    #   make an easy way to convert to binary
    #       replace byte size from 3 to 9
    #       replace conversion from hex to bin
    #   replace empty string XX
    #       coloration must occured on bit not on whole byte
    #       convert each byte list to binary stream

    if len(var_lists) == 0:
        return

    byte_list_checker = ListArgChecker(IntegerArgChecker(0, 255))

    var_lists_values = {}
    for i in range(0, len(var_lists)):
        var_key = var_lists[i]
        var = parameters.getParameter(var_key).getValue()
        if var is None:
            raise DefaultPyshellException(
                "unknown variable '" + str(var_key) + "'", )

        var_lists_values[var_key] = byte_list_checker.getValue(var, i, var_key)

    # get the size of the bigger list of byte
    max_size = 0
    for var_name, var_list in var_lists_values.items():
        max_size = max(max_size, len(var_list))

    # get the number of line
    line_count = int(max_size / byte_per_line)

    if (max_size % byte_per_line) > 0:
        line_count += 1

    id_column_size = int(log(line_count, 10)) + 1
    id_line = 0

    # compute line width
    # an hexa number is printed with two number and one space
    # a first pipe
    # then a space
    # the final pipe is not in the calculus
    column_size = 3 * byte_per_line + 2
    line_parts = ["| "] * len(var_lists_values)

    title_column = " " * (id_column_size + 1)

    for var_name, var_list in var_lists_values.items():
        title_column += ("| "+var_name[0:column_size-2] +
                         " "*(column_size-len(var_name)-2))

    printShell(title_column + "|")
    for i in range(0, max_size):

        common_bytes_hight = {}
        max_key_high = None
        max_value_high = 0

        common_bytes_low = {}
        max_key_low = None
        max_value_low = 0

        for var_name, var_listValue in var_lists_values.items():
            if i >= len(var_listValue):
                continue

            hight = int(var_listValue[i]) & 0xF0
            low = int(var_listValue[i]) & 0x0F

            if hight not in common_bytes_hight:
                common_bytes_hight[hight] = 1

                if max_key_high is None:
                    max_key_high = hight
                    max_value_high = 1
            else:
                common_bytes_hight[hight] += 1

                if common_bytes_hight[hight] > max_value_high:
                    max_key_high = hight
                    max_value_high = common_bytes_hight[hight]

            if low not in common_bytes_low:
                common_bytes_low[low] = 1

                if max_key_low is None:
                    max_key_low = low
                    max_value_low = 1
            else:
                common_bytes_low[low] += 1

                if common_bytes_low[low] > max_value_low:
                    max_key_low = low
                    max_value_low = common_bytes_low[low]

        j = -1
        for var_name, var_listValue in var_lists_values.items():
            j += 1
            # high
            if len(common_bytes_hight) == 1:
                if i >= len(var_listValue):
                    line_parts[j] += formatOrange("xx ")
                    continue

                line_parts[j] += "%x" % ((int(var_listValue[i]) & 0xF0) >> 4)

            elif len(common_bytes_hight) == len(var_listValue):
                if i >= len(var_listValue):
                    line_parts[j] += formatOrange("xx ")
                    continue

                value = (int(var_listValue[i]) & 0xF0) >> 4
                line_parts[j] += formatRed("%x" % value)
            else:
                if i >= len(var_listValue):
                    line_parts[j] += formatOrange("xx ")
                    continue

                if var_listValue[i] == max_key_high:
                    value = (int(var_listValue[i]) & 0xF0) >> 4
                    line_parts[j] += "%x" % value
                else:
                    value = (int(var_listValue[i]) & 0xF0) >> 4
                    line_parts[j] += formatRed("%x" % value)

            # low
            if len(common_bytes_low) == 1:
                line_parts[j] += "%x " % (int(var_listValue[i]) & 0x0F)

            elif len(common_bytes_low) == len(var_listValue):
                value = int(var_listValue[i]) & 0x0F
                line_parts[j] += formatRed("%x " % value)
            else:
                if var_listValue[i] == max_key_low:
                    value = int(var_listValue[i]) & 0x0F
                    line_parts[j] += "%x " % value
                else:
                    value = int(var_listValue[i]) & 0x0F
                    line_parts[j] += formatRed("%x " % value)

        # new line
        if (i + 1) % (byte_per_line) == 0:
            final_line = ""
            for linePart in line_parts:
                final_line += linePart

            final_line += "|"

            id_line_str = str(id_line)
            id_line_str = " " * \
                (id_column_size - len(id_line_str) - 1) + id_line_str + " "
            printShell(id_line_str + final_line)
            id_line += 1
            line_parts = ["| "] * len(var_lists_values)

    # we do not finish on a complete line, add padding
    if (i + 1) % (byte_per_line) != 0:
        final_line = ""
        for linePart in line_parts:
            final_line += linePart + " " * (column_size - strLength(linePart))

        final_line += "|"

        id_line_str = str(id_line)
        id_line_str = (" "*(id_column_size - len(id_line_str) - 1) +
                       id_line_str+" ")
        printShell(id_line_str + final_line)


@shellMethod(bytelist=ListArgChecker(IntegerArgChecker(0, 255)),
             byte_per_line=IntegerArgChecker(4, 16))
def printByteTable(bytelist, byte_per_line=4):
    if len(bytelist) == 0:
        warning("empty list of byte")

    bytecolumn_size = 3 * byte_per_line
    asciicolumn_size = byte_per_line + 2
    decimalcolumn_size = 4 * byte_per_line + 1

    # print header line
    printShell("Hex"+" "*(bytecolumn_size-3)+"|"+" Char " +
               " "*(asciicolumn_size-6)+"|"+" Dec"+" "*(decimalcolumn_size-4) +
               "|"+" Bin")

    for i in range(0, len(bytelist), byte_per_line):
        hexa = ""
        ascii = ""
        int_string = ""
        bin_string = ""
        sub_byte_list = bytelist[i:i + byte_per_line]

        for h in sub_byte_list:

            tmp = "%x" % h
            while len(tmp) < 2:
                tmp = "0" + tmp

            hexa += tmp + " "

            if h < 33 or h > 126:
                ascii += formatOrange(".")
            else:
                ascii += chr(h)

            tmp = str(h)
            while len(tmp) < 3:
                tmp = "0" + tmp

            int_string += tmp + " "

            tmp = bin(h)[2:]
            while len(tmp) < 8:
                tmp = "0" + tmp
            bin_string += tmp + " "

        printShell(hexa+" "*(bytecolumn_size-len(hexa))+"| "+ascii +
                   " "*(asciicolumn_size-len(sub_byte_list)-1)+"| " +
                   int_string +
                   " "*(decimalcolumn_size-len(int_string)-1)+"| "+bin_string)

registerSetGlobalPrefix(("printing", ))
registerStopHelpTraversalAt()
registerCommand(("bytelist",), post=printByteTable)
registerCommand(("compareByte",), post=compareByteList)
