#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2012  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.command.exception import ExecutionException


def equalPath(path1, path2):
    same_length = True
    equals = True

    if len(path1) != len(path2):
        same_length = False
        equals = False

    equals_count = 0
    path1_is_higher = None
    for i in range(0, min(len(path1), len(path2))):
        if path1[i] != path2[i]:
            equals = False
            path1_is_higher = path1[i] > path2[i]
            break

        equals_count += 1

    return equals, same_length, equals_count, path1_is_higher


def isAValidIndex(li,
                  index,
                  cmd_name=None,
                  list_name=None,
                  context="engine",
                  ex=ExecutionException):
    try:
        li[index]
    except IndexError:
        if cmd_name is not None:
            cmd_name += ", "
        else:
            cmd_name = ""

        if list_name is not None:
            list_name = " on list '"+list_name+"'"
        else:
            list_name = ""

        raise ex("("+context+") "+cmd_name+"list index out of range"+list_name)


def equalMap(map1, map2):
    if map1 is None and map2 is None:
        return True

    if map1 is not None and map2 is not None:
        if len(map1) != len(map2):
            return False

        for i in range(0, len(map2)):
            if map1[i] != map2[i]:
                return False

        return True

    return False


def isValidMap(emap, expected_length):
    if emap is None:
        return True

    if not isinstance(emap, list):
        return False

    if len(emap) != expected_length:
        return False

    false_count = 0
    for b in emap:
        if type(b) != bool:
            return False

        if not b:
            false_count += 1

    if false_count == len(emap):
        return False

    return True


def raisIfInvalidMap(emap,
                     expected_length,
                     cmd_name=None,
                     context="engine",
                     ex=ExecutionException):
    if not isValidMap(emap, expected_length):
        if cmd_name is not None:
            cmd_name += ", "
        else:
            cmd_name = ""

        raise ex("("+context+") "+cmd_name+"list index out of range on "
                 "enabling map")


def raiseIfInvalidPath(cmd_path, cmd_list, meth_name):
    # check command path
    isAValidIndex(cmd_list, len(cmd_path)-1, meth_name, "command list")

    # check subindex
    for i in range(0, len(cmd_path)):
        isAValidIndex(cmd_list[i], cmd_path[i], meth_name, "sub command list")


def getFirstEnabledIndexInEnablingMap(enabling_map,
                                      cmd,
                                      starting=0,
                                      cmd_name=None,
                                      context="engine",
                                      ex=ExecutionException):
    i = 0
    if enabling_map is not None:
        # there is at least one True item in list, otherwise
        # raisIfInvalidMap had raise an exception
        for i in range(starting, len(enabling_map)):
            if enabling_map[i] and not cmd.isdisabledCmd(i):
                return i

        if cmd_name is not None:
            cmd_name += ", "
        else:
            cmd_name = ""

        raise ex("("+context+") "+cmd_name+" no enabled index on this enabling"
                 " map from "+str(starting)+" to the end")

    return i
