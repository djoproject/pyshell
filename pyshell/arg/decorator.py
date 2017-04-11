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
#   use wraps https://docs.python.org/2/library/functools.html#functools.wraps

import inspect
import sys
import types

from pyshell.arg.abstract import AbstractArg
from pyshell.arg.argfeeder import ArgFeeder
from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.defaultvalue import DefaultValueChecker
from pyshell.arg.exception import DecoratorException

try:
    from collections import OrderedDict
except:
    from pyshell.utils.ordereddict import OrderedDict


class _Class(object):

    @staticmethod
    def _method(self):
        pass

    staticMethType = type(_method)
staticMethType = _Class.staticMethType

PY3 = sys.version_info[0] == 3

# #############################################################################
# #### UTIL FUNCTION ##########################################################
# #############################################################################


class FunAnalyser(object):
    def __init__(self, fun):
        # is a function ?

        # TODO manage every function case ? difference between python2
        # and python3 ?
        allowed_type = [staticMethType, types.MethodType, types.FunctionType]

        if not PY3:
            allowed_type.append(types.InstanceType)
            allowed_type.append(types.ClassType)

        for clazz in allowed_type:
            if isinstance(fun, clazz):
                break
        else:
            excmsg = "(%s) init faile, need a function instance, got '%s'"
            excmsg %= (self.__class__.__name__, type(fun),)
            raise DecoratorException(excmsg)

        self.fun = fun
        self.inspect_result = inspect.getargspec(fun)

        # how much default value ?
        if self.inspect_result.defaults is None:
            self.lendefault = 0
        else:
            self.lendefault = len(self.inspect_result.defaults)

    def hasDefault(self, argname):
        # existing argument ?
        if argname not in self.inspect_result.args:
            excmsg = "(%s) unknonw argument '%s' at function '%s'"
            excmsg %= (self.__class__.__name__, argname, self.fun.__name__,)
            raise DecoratorException(excmsg)

        return not ((self.inspect_result.args.index(argname) <
                    (len(self.inspect_result.args) - self.lendefault)))

    def getDefault(self, argname):
        # existing argument ?
        if argname not in self.inspect_result.args:
            excmsg = "(%s) unknonw argument '%s' at function '%s'"
            excmsg %= (self.__class__.__name__, argname, self.fun.__name__,)
            raise DecoratorException(excmsg)

        index = self.inspect_result.args.index(argname)
        if not (index < (len(self.inspect_result.args) - self.lendefault)):
            index_to_return = (index -
                               (len(self.inspect_result.args) -
                                len(self.inspect_result.defaults)))
            return self.inspect_result.defaults[index_to_return]

        excmsg = "(%s) no default value to the argument '%s' at function '%s'"
        excmsg %= (self.__class__.__name__, argname, self.fun.__name__,)
        raise DecoratorException(excmsg)

    def setCheckerDefault(self, argname, checker):
        if self.hasDefault(argname):
            # TODO (issue #41) setDefaultValue could raise, add the fun name
            #   in the exc message
            checker.setDefaultValue(self.getDefault(argname), argname)

        return checker


# #############################################################################
# #### DECORATOR ##############################################################
# #############################################################################

def defaultMethod(state=True):
    def decorator(fun):
        fun.isDefault = state
        return fun

    return decorator


def shellMethod(**arg_list):
    # no need to check collision key, it's a dictionary

    # check the checkers
    for key, checker in arg_list.items():
        if not isinstance(checker, AbstractArg):
            raise DecoratorException("(shellMethod) the checker "
                                     "linked to the key '"+key+"' is not an "
                                     "instance of AbstractArg")

    # define decorator method
    def decorator(fun):
        # inspect the function AND insure fun hold a function
        analyzed_fun = FunAnalyser(fun)

        # is there already a decorator ?
        if hasattr(fun, "checker"):
            excmsg = ("(shellMethod) the function '%s' has already a "
                      "shellMethod decorator")
            excmsg %= fun.__name__
            raise DecoratorException(excmsg)

        arg_checker_list = OrderedDict()
        for i in range(0, len(analyzed_fun.inspect_result.args)):
            # for argname in analyzed_fun.inspect_result.args:
            argname = analyzed_fun.inspect_result.args[i]

            # don't care about the self arg, the python framework will
            # manage it
            if i == 0 and argname == "self" and type(fun) != staticMethType:
                # http://stackoverflow.com/questions/8793233/
                frames = inspect.stack()
                if (len(frames) > 2 and
                   frames[2][4][0].strip().startswith('class ')):
                    continue

            if argname in arg_list:  # check if the argname is in the arg_list
                checker = arg_list[argname]
                del arg_list[argname]
                checker = analyzed_fun.setCheckerDefault(argname, checker)
                arg_checker_list[argname] = checker

            # check if the arg has a DEFAULT value
            elif analyzed_fun.hasDefault(argname):
                checker = DefaultValueChecker(analyzed_fun.getDefault(argname))
                arg_checker_list[argname] = checker
            else:
                arg_checker_list[argname] = DefaultChecker.getArg()

        # All the key are used in the function call?
        keys = arg_list.keys()
        if len(keys) > 0:
            string = ",".join(arg_list.keys())
            excmsg = ("(shellMethod) the following key(s) have no match in the"
                      " '%s' function prototype : '%s'")
            excmsg %= (fun.__name__, string,)
            raise DecoratorException(excmsg)

        # set the checker on the function
        fun.checker = ArgFeeder(arg_checker_list)
        return fun

    return decorator
