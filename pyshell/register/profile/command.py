#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2016  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.command.command import MultiCommand
from pyshell.register.profile.default import DefaultProfile
from pyshell.register.profile.exception import RegisterException
from pyshell.utils.raises import raiseIfInvalidKeyList
from pyshell.utils.raises import raiseIfNotInstance


class CommandLoaderProfile(DefaultProfile):

    def __init__(self):
        # TODO (issue #90) remove unload_priority/load_priority
        # Why load priority at 120.0 ?
        # because parameter priority is 100.0 and the mltries use by command
        # is created by parameter loader, if command loader is executed
        # before the parameter loader, an error will occur.
        # It will be fixed as soon as the command will have their own
        # manager.
        # Why unload priority at 80.0 ?
        # commands need to be unload before the destruction of the mltries
        # in the environment loader.
        DefaultProfile.__init__(self,
                                unload_priority=80.0,
                                load_priority=120.0)

        self.prefix = ()
        self.cmdDict = {}
        self.tempPrefix = None
        self.stopList = set()

        self.loadedCommand = None
        self.loadedStopTraversal = None

    def setTempPrefix(self, key_list):
        raiseIfInvalidKeyList(key_list,
                              RegisterException,
                              self.__class__.__name__,
                              "setTempPrefix")
        self.tempPrefix = key_list

    def unsetTempPrefix(self):
        self.tempPrefix = None

    def getTempPrefix(self):
        return self.tempPrefix

    def setPrefix(self, key_list):
        raiseIfInvalidKeyList(key_list,
                              RegisterException,
                              self.__class__.__name__,
                              "setPrefix")
        self.prefix = key_list

    def getPrefix(self):
        return self.prefix

    def addStopTraversal(self, key_list):
        raiseIfInvalidKeyList(key_list,
                              RegisterException,
                              self.__class__.__name__,
                              "addStopTraversal")

        if self.tempPrefix is not None:
            stop = list(self.tempPrefix)
            stop.extend(key_list)
        else:
            stop = key_list

        self.stopList.add(tuple(stop))

    def hasStopTraversal(self, key_list):
        raiseIfInvalidKeyList(key_list,
                              RegisterException,
                              self.__class__.__name__,
                              "hasStopTraversal")
        return tuple(key_list) in self.stopList

    def addCmd(self, key_list, cmd):
        raiseIfInvalidKeyList(key_list,
                              RegisterException,
                              self.__class__.__name__,
                              "addCmd")

        raiseIfNotInstance(cmd,
                           "cmd",
                           MultiCommand,
                           RegisterException,
                           "addCmd",
                           self.__class__.__name__)

        if self.tempPrefix is not None:
            prefix = list(self.tempPrefix)
            prefix.extend(key_list)
        else:
            prefix = key_list

        final_cmd_key = tuple(prefix)

        if final_cmd_key in self.cmdDict:
            excmsg = ("(CommandLoader) addCmd, the following key already"
                      " exists: '" + str(" ".join(final_cmd_key) + "'"))
            raise RegisterException(excmsg)

        self.cmdDict[final_cmd_key] = cmd

        return cmd

    def hasCmd(self, key_list):
        raiseIfInvalidKeyList(key_list,
                              RegisterException,
                              self.__class__.__name__,
                              "hasCmd")
        return tuple(key_list) in self.cmdDict
