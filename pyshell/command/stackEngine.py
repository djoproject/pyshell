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


class EngineStack(list):
    def push(self, data, cmd_path, instruction_type, cmd_map=None):
        self.append((data, cmd_path, instruction_type, cmd_map,))

    def raiseIfEmpty(self, meth_name=None):
        if len(self) == 0:
            if meth_name is None:
                raise ExecutionException("(engine) EngineStack, no item on "
                                         "the stack")
            else:
                raise ExecutionException("(engine) "+meth_name+", no item on "
                                         "the stack")

    # ## SIZE meth ## #
    def size(self):
        return len(self)

    def isEmpty(self):
        return len(self) == 0

    def isLastStackItem(self):
        return len(self) == 1

    # ##
    def data(self, index):
        return self[index][0]

    def path(self, index):
        return self[index][1]

    def type(self, index):
        return self[index][2]

    def enablingMap(self, index):
        return self[index][3]

    def cmdIndex(self, index):
        return len(self[index][1]) - 1

    def cmdLength(self, index):
        return len(self[index][1])

    def item(self, index):
        return self[index]

    def getCmd(self, index, cmd_list):
        return cmd_list[len(self[index][1])-1]

    def subCmdLength(self, index, cmd_list):
        return len(cmd_list[len(self[index][1])-1])

    def subCmdIndex(self, index):
        return self[index][1][-1]

    def setEnableMap(self, index, new_map):
        current = self[index]
        self[index] = (current[0], current[1], current[2], new_map,)

    def setPath(self, index, path):
        current = self[index]
        self[index] = (current[0], path, current[2], current[3],)

    def setType(self, index, new_type):
        current = self[index]
        self[index] = (current[0], current[1], new_type, current[3],)

    # ## MISC meth ## #

    def top(self):
        return self[-1]

    def getIndexBasedXRange(self):
        return xrange(0, len(self), 1)

    # #########
    def __getattr__(self, name):
        if name.endswith("OnTop"):
            index = -1
            sub = None
            name = name[:-5]
        elif name.endswith("OnIndex"):
            index = None
            sub = None
            name = name[:-7]
        elif name.endswith("OnDepth"):
            index = None
            sub = len(self)-1
            name = name[:-7]
        else:
            # return getattr(self,name)
            return object.__getattribute__(self, name)

        if name not in ["data", "path", "type", "enablingMap", "cmdIndex",
                        "cmdLength", "item", "getCmd", "subCmdLength",
                        "subCmdIndex", "setEnableMap", "setPath", "setType"]:
            raise ExecutionException("(EngineStack) __getattr__, try to get an"
                                     " unallowed or unexistant meth")

        meth_to_call = object.__getattribute__(self, name)

        def meth(*args):
            if index is None:
                if len(args) > 0:
                    lindex = int(args[0])
                    start_index = 1
                else:
                    # if index is not define, no need to do compute
                    # anything else
                    return meth_to_call(*args)
            else:
                start_index = 0
                lindex = index

            if sub is not None:
                lindex = sub - lindex

            nargs = [lindex]
            nargs.extend(args[start_index:])
            return meth_to_call(*nargs)

        return meth
