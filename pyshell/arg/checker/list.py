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
from pyshell.utils.string65 import isString

TYPENAME = "list"


class ListArgChecker(ArgChecker):
    def __init__(self, checker, minimum_size=None, maximum_size=None):
        if (not isinstance(checker, ArgChecker) or
           isinstance(checker, ListArgChecker)):
            excmsg = ("checker must be an instance of ArgChecker but can not "
                      "be an instance of ListArgChecker, got '%s'")
            excmsg %= str(type(checker))
            self._raiseArgInitializationException(excmsg)

        # checker must have a fixed size
        checker_minimum_size = checker.getMinimumSize()
        checker_maximum_size = checker.getMaximumSize()
        if (checker_minimum_size != checker_maximum_size or
           checker_minimum_size is None or
           checker_minimum_size == 0):
            if checker_minimum_size is None:
                checker_size = "]-Inf,"
            else:
                checker_size = "["+str(checker_minimum_size)+","

            if checker_maximum_size is None:
                checker_size += "+Inf["
            else:
                checker_size += str(checker_maximum_size)+"]"

            excmsg = ("checker must have a fixed size bigger than zero, got "
                      "this size : '%s'")
            excmsg %= checker_size
            self._raiseArgInitializationException(excmsg)

        self.checker = checker
        ArgChecker.__init__(self, minimum_size, maximum_size, True)

    def checkSize(self, minimum_size, maximum_size):
        ArgChecker.checkSize(self, minimum_size, maximum_size)

        checker_minimum_size = self.checker.getMinimumSize()
        if (minimum_size is not None and
           (minimum_size % checker_minimum_size) != 0):
            excmsg = ("the minimum size of the list <%s> is not a multiple of"
                      " the checker size <%s>")
            excmsg %= (str(minimum_size), str(checker_minimum_size),)
            self._raiseArgInitializationException(excmsg)

        checker_maximum_size = self.checker.getMaximumSize()
        if (maximum_size is not None and
           (maximum_size % checker_maximum_size) != 0):
            excmsg = ("the maximum size of the list <%s> is not a multiple of"
                      " the checker size <%s>")
            excmsg %= (str(maximum_size), str(checker_maximum_size),)
            self._raiseArgInitializationException(excmsg)

    def getValue(self, values, arg_number=None, arg_name_to_bind=None):
        # check if it's a list
        if not hasattr(values, "__iter__") or isString(values):
            values = (values,)

        # len(values) must always be a multiple of self.checker.minimum_size
        #   even if there is to much data, it is a sign of anomalies
        checker_minimum_size = self.checker.getMinimumSize()
        if (len(values) % checker_minimum_size) != 0:
            excmsg = ("the size of the value list <%s> is not a multiple of "
                      "the checker size <%s>")
            excmsg %= (str(len(values)), str(checker_minimum_size),)
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        # check the minimal size
        add_at_end = []
        minimum_size = self.getMinimumSize()
        if minimum_size is not None and len(values) < minimum_size:
            # checker has default value ?
            if self.checker.hasDefaultValue(arg_name_to_bind):
                # build the missing part with the default value
                add_at_end = (int(minimum_size - len(values) /
                              checker_minimum_size) *
                              [self.checker.getDefaultValue(arg_name_to_bind)])
            else:
                excmsg = "need at least <%s> items, got <%s>"
                excmsg %= (str(minimum_size), str(len(values)),)
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        # build range limite and manage max size
        maximum_size = self.getMaximumSize()
        if maximum_size is not None:
            if len(values) < maximum_size:
                msize = len(values)
            else:
                msize = maximum_size
        else:
            msize = len(values)

        # check every args
        ret = []
        if arg_number is not None:
            for i in range(0, msize, checker_minimum_size):
                if checker_minimum_size == 1:
                    ret.append(self.checker.getValue(values[i],
                                                     arg_number,
                                                     arg_name_to_bind))
                else:
                    value_max_index = i+checker_minimum_size
                    ret.append(self.checker.getValue(values[i:value_max_index],
                                                     arg_number,
                                                     arg_name_to_bind))

                arg_number += 1
        else:
            for i in range(0, msize, checker_minimum_size):
                if checker_minimum_size == 1:
                    ret.append(self.checker.getValue(values[i],
                                                     None,
                                                     arg_name_to_bind))
                else:
                    value_max_index = i+checker_minimum_size
                    ret.append(self.checker.getValue(values[i:value_max_index],
                                                     None,
                                                     arg_name_to_bind))

        # add the missing part
        ret.extend(add_at_end)
        return ret

    def getDefaultValue(self, arg_name_to_bind=None):
        if self.hasDefault:
            return self.default

        minimum_size = self.getMinimumSize()
        if minimum_size is None:
            return []

        if self.checker.hasDefaultValue(arg_name_to_bind):
            return ([self.checker.getDefaultValue(arg_name_to_bind)] *
                    minimum_size)

        excmsg = "getDefaultValue, there is no default value"
        self._raiseArgException(excmsg, None, arg_name_to_bind)

    def hasDefaultValue(self, arg_name_to_bind=None):
        minimum_size = self.getMinimumSize()
        return (self.hasDefault or
                minimum_size is None or
                self.checker.hasDefaultValue(arg_name_to_bind))

    def getUsage(self):
        minimum_size = self.getMinimumSize()
        maximum_size = self.getMaximumSize()
        if minimum_size is None:
            if maximum_size is None:
                return ("("+self.checker.getUsage()+" ... " +
                        self.checker.getUsage()+")")
            elif maximum_size == 1:
                return "("+self.checker.getUsage()+")"
            elif maximum_size == 2:
                return ("("+self.checker.getUsage()+"0 " +
                        self.checker.getUsage()+"1)")

            return ("("+self.checker.getUsage()+"0 ... " +
                    self.checker.getUsage()+str(maximum_size-1)+")")
        else:
            if minimum_size == 0 and maximum_size == 1:
                return "("+self.checker.getUsage()+")"

            if minimum_size == 1:
                if maximum_size == 1:
                    return self.checker.getUsage()

                part1 = self.checker.getUsage()+"0"
            elif minimum_size == 2:
                part1 = (self.checker.getUsage()+"0 "+self.checker.getUsage() +
                         "1")
            else:
                part1 = (self.checker.getUsage()+"0 ... " +
                         self.checker.getUsage()+str(minimum_size-1))

            if maximum_size is None:
                return part1 + " (... "+self.checker.getUsage()+")"
            else:
                not_mandatory_space = maximum_size - minimum_size
                if not_mandatory_space == 0:
                    return part1
                if not_mandatory_space == 1:
                    return (part1 + " ("+self.checker.getUsage() +
                            str(maximum_size-1)+")")
                elif not_mandatory_space == 2:
                    return (part1 + " ("+self.checker.getUsage() +
                            str(maximum_size-2)+"" +
                            self.checker.getUsage() +
                            str(maximum_size-1)+")")
                else:
                    return (part1+" ("+self.checker.getUsage() +
                            str(minimum_size)+" ... " +
                            self.checker.getUsage() +
                            str(maximum_size-1)+")")

    def __str__(self):
        return "ListArgChecker : "+str(self.checker)

    def setEngine(self, engine):
        ArgChecker.setEngine(self, engine)
        self.checker.setEngine(engine)

    @classmethod
    def getTypeName(cls):
        return TYPENAME
