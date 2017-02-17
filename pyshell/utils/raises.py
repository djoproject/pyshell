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

# TODO use these methods everywhere in the code

from inspect import isclass

from pyshell.utils.string import isString

STRING_INSTANCE1 = ("the element, used to check if the variable '%s' is an "
                    "instance, is not a valid class definition.  it "
                    "contains '%s'")
STRING_INSTANCE2 = ("the variable '%s' does not contain an instance of the "
                    "class '%s'")

STRING_MSG = ("only string or unicode addon name are allowed for variable '%s'"
              ", got '%s'")

SUBCLASS_MSG1 = ("the variable '%s' does not contain a class defintion but "
                 "contains a '%s'")
SUBCLASS_MSG2 = ("the element, used to check if the variable '%s' is a sub "
                 "class, is not a valid class definition.  it "
                 "contains '%s'")
SUBCLASS_MSG3 = ("the class definition stored in variable '%s' is not a "
                 "subclass of the class '%s'")


def _buildMessage(message, method=None, context=None):
    if method is None:
        if context is None:
            return message
        else:
            return "(%s) %s" % (context, message)
    else:
        if context is None:
            return "%s, %s" % (context, message)
        else:
            return "(%s) %s, %s" % (context, method, message)


def raiseIfInvalidKeyList(key_list, exception_class, package_name, meth_name):
    # TODO test if a simple string could be a valid key_list,
    # it shouldn't be the case

    if not hasattr(key_list, "__iter__") or isString(key_list):
        raise exception_class("("+package_name+") "+meth_name+", list of "
                              "string is not iterable")

    for key in key_list:
        if not isString(key):
            raise exception_class("("+package_name+") "+meth_name+", only "
                                  "string or unicode key are allowed")

        # trim key
        key = key.strip()

        if len(key) == 0:
            raise exception_class("("+package_name+") "+meth_name+", empty "
                                  "key is not allowed")

    return key_list


def raiseIfNotInstance(obj,
                       obj_name,
                       classdef,
                       exc,
                       method=None,
                       context=None):
    if not isclass(classdef):
        type_got = str(type(classdef))
        msg = _buildMessage(STRING_INSTANCE1 % (obj_name, type_got),
                            method,
                            context)
        raise exc(msg)

    if isinstance(obj, classdef):
        return

    type_got = str(type(obj))
    msg = _buildMessage(STRING_INSTANCE2 % (obj_name, type_got),
                        method,
                        context)
    raise exc(msg)


def raiseIfNotString(obj, obj_name, exc, method=None, context=None):
    if isString(obj):
        return

    type_got = str(type(obj))
    msg = _buildMessage(STRING_MSG % (obj_name, type_got), method, context)
    raise exc(msg)


def raiseIfNotSubclass(classdef,
                       obj_name,
                       parent,
                       exc,
                       method=None,
                       context=None):
    if not isclass(classdef):
        type_got = str(type(classdef))
        msg = _buildMessage(SUBCLASS_MSG1 % (obj_name, type_got),
                            method,
                            context)
        raise exc(msg)

    if not isclass(parent):
        type_got = str(type(parent))
        msg = _buildMessage(SUBCLASS_MSG2 % (obj_name, type_got),
                            method,
                            context)
        raise exc(msg)

    # reason of the second part of this condition:
    #   issubclass(A,A) return True...
    if issubclass(classdef, parent) and classdef is not parent:
        return

    pname = parent.__name__
    msg = _buildMessage(SUBCLASS_MSG3 % (obj_name, pname), method, context)
    raise exc(msg)
