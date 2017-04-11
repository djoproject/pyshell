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

from abc import ABCMeta, abstractmethod

from pyshell.arg.exception import ArgException
from pyshell.arg.exception import ArgInitializationException

try:
    from collections import OrderedDict
except:
    from pyshell.utils.ordereddict import OrderedDict


# #############################################################################
# #### ArgsChecker ############################################################
# #############################################################################
class ArgsChecker():
    "abstract arg checker"
    __metaclass__ = ABCMeta

    #
    # @args_list, une liste de string
    # @return, un dico trie des arguments et de leur valeur : <name,value>
    #
    @abstractmethod
    def checkArgs(self, args_list, engine=None):
        pass

    @abstractmethod
    def usage(self):
        pass


class ArgFeeder(ArgsChecker):

    #
    # @param arg_type_list, une liste de tuple (Argname,ArgChecker)
    #
    def __init__(self, arg_type_list):
        # take an ordered dict as arg_type_list parameter
        if (not isinstance(arg_type_list, OrderedDict) and
           (not isinstance(arg_type_list, dict) or len(arg_type_list) != 0)):
            raise ArgInitializationException("(ArgFeeder) arg_type_list must "
                                             "be a valid instance of an "
                                             "ordered dictionnary")

        self.arg_type_list = arg_type_list

    def manageMappedArg(self, name, checker, args):
        if (checker.getMaximumSize() is not None and
           len(args) > checker.getMaximumSize()):
            args = args[:checker.getMaximumSize()]

        if (checker.getMinimumSize() is not None and
           len(args) < checker.getMinimumSize()):
            raise ArgException("(ArgFeeder) not enough data for the dash "
                               "mapped argument '"+name+"', expected at least"
                               " '"+str(checker.getMinimumSize())+"', got '" +
                               str(len(args))+"'")

        if checker.getMinimumSize() == checker.getMaximumSize() == 1:
            args = args[0]

        return checker.getValue(args, None, name)

    #
    # @args_list, une liste de n'importe quoi
    # @return, un dico trie des arguments et de leur valeur : <name,value>
    #
    def checkArgs(self, args_list, mapped_args={}, engine=None):
        if not hasattr(args_list, "__iter__"):
            # args_list must be a string
            # if type(args_list) != str and type(args_list) != unicode:
            #    raise ArgException("(ArgFeeder) string list was expected,
            #    got "+str(type(args_list)))

            # args_list = [args_list]
            args_list = (args_list,)
            # no need to check the other args, they will be checked into the
            # argcheckers

        ret = {}
        arg_checker_index = 0
        data_index = 0

        for (name, checker) in self.arg_type_list.items():
            # set the engine
            checker.setEngine(engine)

            # is it a mapped args ?
            if name in mapped_args:
                ret[name] = self.manageMappedArg(name,
                                                 checker,
                                                 mapped_args[name])
                arg_checker_index += 1
                continue

            # is there a minimum limit
            if checker.getMinimumSize() is not None:
                # is there at least getMinimumSize() item in the data stream?
                if len(args_list[data_index:]) < checker.getMinimumSize():
                    # no more string token, end of stream ?
                    if len(args_list[data_index:]) == 0:
                        # we will check if there is some default value
                        break
                    else:
                        # there are data but not enough
                        raise ArgException("(ArgFeeder) not enough data for "
                                           "the argument '"+name+"'")

            # is there a maximum limit?
            if checker.getMaximumSize() is None:
                # No max limit, it consumes all remaining data
                ret[name] = checker.getValue(args_list[data_index:],
                                             data_index,
                                             name)
                # will not stop the loop but will notify that every data has
                # been consumed
                data_index = len(args_list)
            else:
                # special case: checker only need one item? (most common case)
                if (checker.getMinimumSize() is not None and
                   checker.getMinimumSize() == checker.getMaximumSize() == 1):
                    max_index = data_index+checker.getMaximumSize()
                    value = args_list[data_index:max_index][0]
                else:
                    max_index = data_index+checker.getMaximumSize()
                    value = args_list[data_index:max_index]

                ret[name] = checker.getValue(value, data_index, name)
                data_index += checker.getMaximumSize()

            arg_checker_index += 1

        # MORE THAN THE LAST ARG CHECKER HAVEN'T BEEN CONSUMED YET
        items_list = list(self.arg_type_list.items())
        for i in range(arg_checker_index, len(self.arg_type_list)):
            (name, checker) = items_list[i]
            checker.setEngine(engine)

            # is it a mapped args ?
            if name in mapped_args:
                ret[name] = self.manageMappedArg(name,
                                                 checker,
                                                 mapped_args[name])
                continue

            # is there a default value ?
            if not checker.hasDefaultValue(name):
                raise ArgException("(ArgFeeder) some arguments aren't "
                                   "bounded, missing data : '"+name+"'")

            ret[name] = checker.getDefaultValue(name)

        # don't care about unused data in args_list, if every parameter are
        # binded, we are happy :)

        return ret

    def usage(self):
        if len(self.arg_type_list) == 0:
            return "no args needed"

        ret = ""
        first_mandatory = False
        for (name, checker) in self.arg_type_list.items():
            if not checker.isShowInUsage():
                continue

            if checker.hasDefaultValue(name) and not first_mandatory:
                ret += "["
                first_mandatory = True

            ret += name+":"+checker.getUsage()+" "

        ret = ret.strip()

        if first_mandatory:
            ret += "]"

        return ret
