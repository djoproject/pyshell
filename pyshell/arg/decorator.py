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

from pyshell.arg.argchecker import ArgChecker, defaultValueChecker, \
                                   defaultInstanceArgChecker
from pyshell.arg.argfeeder import ArgFeeder
from pyshell.arg.exception import decoratorException

import inspect
import types
import sys

if (sys.version_info[0] < 2 or
   (sys.version_info[0] < 3 and sys.version_info[0] < 7)):
    # TODO get from pipy, so the import path will change
    from pyshell.utils.ordereddict import OrderedDict
else:
    from collections import OrderedDict


class _C(object):

    @staticmethod
    def _m(self):
        pass

    staticMethType = type(_m)
staticMethType = _C.staticMethType

# #############################################################################
# #### UTIL FUNCTION ##########################################################
# #############################################################################


class funAnalyser(object):
    def __init__(self, fun):
        # is a function ?
        # TODO manage every function case ? difference between python2
        # and python3 ?
        if (not isinstance(fun, staticMethType) and
           not isinstance(fun, types.MethodType) and
           not isinstance(fun, types.InstanceType) and
           not isinstance(fun, types.ClassType) and
           not isinstance(fun, types.FunctionType)):
            raise decoratorException("(funAnalyser) init faile, need a "
                                     "function instance, got '" +
                                     str(type(fun))+"'")

        self.fun = fun
        self.inspect_result = inspect.getargspec(fun)

        # how much default value ?
        if self.inspect_result.defaults is None:
            self.lendefault = 0
        else:
            self.lendefault = len(self.inspect_result.defaults)

    def has_default(self, argname):
        # existing argument ?
        if argname not in self.inspect_result.args:
            raise decoratorException("(decorator) unknonw argument '" +
                                     str(argname)+"' at function '" +
                                     self.fun.__name__+"'")

        return not ((self.inspect_result.args.index(argname) <
                    (len(self.inspect_result.args) - self.lendefault)))

    def get_default(self, argname):
        # existing argument ?
        if argname not in self.inspect_result.args:
            raise decoratorException("(decorator) unknonw argument '" +
                                     str(argname)+"' at function '" +
                                     self.fun.__name__+"'")

        index = self.inspect_result.args.index(argname)
        if not (index < (len(self.inspect_result.args) - self.lendefault)):
            indexToReturn = (index -
                             len(self.inspect_result.args) -
                             len(self.inspect_result.defaults))
            return self.inspect_result.defaults[indexToReturn]

        raise decoratorException("(decorator) no default value to the "
                                 "argument '"+str(argname)+"' at function '" +
                                 self.fun.__name__+"'")

    def setCheckerDefault(self, argname, checker):
        if self.has_default(argname):
            checker.setDefaultValue(self.get_default(argname), argname)

        return checker


# #############################################################################
# #### DECORATOR ##############################################################
# #############################################################################

def defaultMethod(state=True):
    def decorator(fun):
        fun.isDefault = state
        return fun

    return decorator


def shellMethod(**argList):
    # no need to check collision key, it's a dictionary

    # check the checkers
    for key, checker in argList.iteritems():
        if not isinstance(checker, ArgChecker):
            raise decoratorException("(shellMethod decorator) the checker "
                                     "linked to the key '"+key+"' is not an "
                                     "instance of ArgChecker")

    # define decorator method
    def decorator(fun):
        # is there already a decorator ?
        if hasattr(fun, "checker"):
            raise decoratorException("(decorator) the function '" +
                                     fun.__name__+"' has already a "
                                     "shellMethod decorator")

        # inspect the function
        analyzed_fun = funAnalyser(fun)

        argCheckerList = OrderedDict()
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

            if argname in argList:  # check if the argname is in the argList
                checker = argList[argname]
                del argList[argname]
                argCheckerList[argname] = \
                    analyzed_fun.setCheckerDefault(argname, checker)

            # check if the arg has a DEFAULT value
            elif analyzed_fun.has_default(argname):
                argCheckerList[argname] = \
                    defaultValueChecker(analyzed_fun.get_default(argname))
            else:
                argCheckerList[argname] = \
                    defaultInstanceArgChecker.getArgCheckerInstance()

        # All the key are used in the function call?
        keys = argList.keys()
        if len(keys) > 0:
            string = ",".join(argList.keys())
            raise decoratorException("(shellMethod decorator) the following "
                                     "key(s) had no match in the function "
                                     "prototype : '"+string+"'")

        # set the checker on the function
        fun.checker = ArgFeeder(argCheckerList)
        return fun

    return decorator
