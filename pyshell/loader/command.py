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

from tries.exception import triesException

from pyshell.command.command import MultiCommand
from pyshell.command.command import UniCommand
from pyshell.loader.abstractloader import AbstractLoader
from pyshell.loader.exception import LoadException
from pyshell.loader.exception import RegisterException
from pyshell.loader.exception import UnloadException
from pyshell.loader.masterloader import MasterLoader
from pyshell.loader.utils import getRootLoader
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME
from pyshell.utils.constants import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.exception import ListOfException
from pyshell.utils.misc import raiseIfInvalidKeyList


def _localGetAndInitCallerModule(profile=None):
    master = getRootLoader(class_definition=MasterLoader)
    return master.getOrCreateLoader(CommandLoader, profile)


def setCommandLoadPriority(value, profile=None):
    try:
        priority = int(value)
    except ValueError:
        excmsg = ("(CommandRegister) setCommandLoadPriority an integer value"
                  " was expected for the argument value, got '" +
                  str(type(value))+"'")
        raise RegisterException(excmsg)

    loader = _localGetAndInitCallerModule(profile)
    loader.load_priority = priority


def setCommandUnloadPriority(value, profile=None):
    try:
        priority = int(value)
    except ValueError:
        excmsg = ("(CommandRegister) setCommandUnloadPriority an integer value"
                  " was expected for the argument value, got '" +
                  str(type(value))+"'")
        raise RegisterException(excmsg)

    loader = _localGetAndInitCallerModule(profile)
    loader.unload_priority = priority



def registerSetGlobalPrefix(key_list, profile=None):
    raiseIfInvalidKeyList(key_list,
                          RegisterException,
                          "CommandRegister",
                          "registerSetGlobalPrefix")
    loader = _localGetAndInitCallerModule(profile)
    loader.prefix = key_list


def registerSetTempPrefix(key_list, profile=None):
    raiseIfInvalidKeyList(key_list,
                          RegisterException,
                          "CommandRegister",
                          "registerSetTempPrefix")
    loader = _localGetAndInitCallerModule(profile)
    loader.TempPrefix = key_list


def registerResetTempPrefix(profile=None):
    loader = _localGetAndInitCallerModule(profile)
    loader.TempPrefix = None


def registerAnInstanciatedCommand(key_list, cmd, profile=None):
    # must be a multiCmd
    if not isinstance(cmd, MultiCommand):
        excmsg = ("(CommandRegister) addInstanciatedCommand, an instance of "
                  "MultiCommand was expected, got '"+str(type(cmd))+"'")
        raise RegisterException(excmsg)

    # check cmd and keylist
    raiseIfInvalidKeyList(key_list,
                          RegisterException,
                          "CommandRegister",
                          "registerAnInstanciatedCommand")

    loader = _localGetAndInitCallerModule(profile)
    loader.addCmd(key_list, cmd)
    return cmd


def registerCommand(key_list, pre=None, pro=None, post=None, profile=None):
    # check cmd and keylist
    raiseIfInvalidKeyList(key_list,
                          RegisterException,
                          "CommandRegister",
                          "registerCommand")

    loader = _localGetAndInitCallerModule(profile)
    cmd = UniCommand(pre, pro, post)
    loader.addCmd(key_list, cmd)
    return cmd


def registerAndCreateEmptyMultiCommand(key_list, profile=None):
    # check cmd and keylist
    raiseIfInvalidKeyList(key_list,
                          RegisterException,
                          "CommandRegister",
                          "registerCreateMultiCommand")

    loader = _localGetAndInitCallerModule(profile)
    cmd = MultiCommand()
    loader.addCmd(key_list, cmd)
    return cmd


def registerStopHelpTraversalAt(key_list=(), profile=None):
    # check cmd and keylist
    raiseIfInvalidKeyList(key_list,
                          RegisterException,
                          "CommandRegister",
                          "registerStopHelpTraversalAt")
    loader = _localGetAndInitCallerModule(profile)

    if loader.TempPrefix is not None:
        key_list_temp = list(loader.TempPrefix)
        key_list_temp.extend(key_list)
    else:
        key_list_temp = key_list

    loader.stoplist.add(tuple(key_list_temp))


class CommandLoader(AbstractLoader):
    def __init__(self, parent):
        AbstractLoader.__init__(self, parent)

        self.prefix = ()
        self.cmdDict = {}
        self.TempPrefix = None
        self.stoplist = set()

        self.loadedCommand = None
        self.loadedStopTraversal = None

    def load(self, parameter_container=None, profile=None):
        self.loadedCommand = []
        self.loadedStopTraversal = []

        AbstractLoader.load(self, parameter_container, profile)

        if not hasattr(parameter_container, ENVIRONMENT_ATTRIBUTE_NAME):
             excmsg = ("(CommandLoader) load, fail to load command because"
                       "container has not attribute '"+ 
                       ENVIRONMENT_ATTRIBUTE_NAME+"'")
             raise LoadException(excmsg)

        env_manager = getattr(parameter_container, ENVIRONMENT_ATTRIBUTE_NAME)
        param = env_manager.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY,
                                         perfect_match=True)

        if param is None:
            excmsg = ("(CommandLoader) load, fail to load command because "
                      "parameter has not a levelTries item")
            raise LoadException(excmsg)

        mltries = param.getValue()
        exceptions = ListOfException()

        # add command
        for key_list, cmd in self.cmdDict.items():
            key = list(self.prefix)
            key.extend(key_list)

            if len(cmd) == 0:
                excmsg = ("(CommandLoader) load, fail to insert key '" +
                          str(" ".join(key))+"' in multi tries: empty command")
                exceptions.addException(LoadException(excmsg))
                continue

            try:
                search_result = mltries.searchNode(key, True)

                if search_result is not None and search_result.isValueFound():
                    flat_key = str(" ".join(key))
                    excmsg = ("(CommandLoader) load, fail to insert key "
                              "'"+flat_key+"' in multi tries: path already"
                              " exists")
                    exceptions.addException(LoadException(excmsg))
                else:
                    mltries.insert(key, cmd)
                    self.loadedCommand.append(key)

            except triesException as te:
                excmsg = ("(CommandLoader) load, fail to insert key '" +
                          str(" ".join(key))+"' in multi tries: "+str(te))
                exceptions.addException(LoadException(excmsg))

        # stop traversal
        for stop in self.stoplist:
            key = list(self.prefix)
            key.extend(stop)

            try:
                if mltries.isStopTraversal(key):
                    continue

                mltries.setStopTraversal(key, True)
                self.loadedStopTraversal.append(key)
            except triesException as te:
                excmsg = ("(CommandLoader) load, fail to disable traversal for"
                          " key list '"+str(" ".join(stop))+"' in multi tries:"
                          " "+str(te))
                exceptions.addException(LoadException(excmsg))

        # raise error list
        if exceptions.isThrowable():
            raise exceptions

    def unload(self, parameter_container=None, profile=None):
        AbstractLoader.unload(self, parameter_container, profile)

        if not hasattr(parameter_container, ENVIRONMENT_ATTRIBUTE_NAME):
            excmsg = ("(CommandLoader) unload, fail to unload command because"
                      "container has not attribute '"+ 
                      ENVIRONMENT_ATTRIBUTE_NAME+"'")
            raise UnloadException(excmsg)

        env_manager = getattr(parameter_container, ENVIRONMENT_ATTRIBUTE_NAME)
        param = env_manager.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY,
                                         perfect_match=True)

        if param is None:
            excmsg = ("(CommandLoader) unload, fail to unload command because"
                      " parameter has not a levelTries item")
            raise UnloadException(excmsg)

        mltries = param.getValue()
        exceptions = ListOfException()

        # remove commands
        for key in self.loadedCommand:
            try:
                mltries.remove(key)
            except triesException as te:
                excmsg = ("(CommandLoader) unload, fail to remove key '" +
                          str(" ".join(key))+"' in multi tries: "+str(te))
                exceptions.addException(UnloadException(excmsg))

        # remove stop traversal
        for key in self.loadedStopTraversal:

            # if key does not exist, continue
            try:
                search_result = mltries.searchNode(key, True)

                if search_result is None or not search_result.isPathFound():
                    continue

            except triesException as te:
                excmsg = ("(CommandLoader) unload, fail to disable traversal "
                          "for key list '"+str(" ".join(key))+"' in multi "
                          "tries: "+str(te))
                exceptions.addException(UnloadException(excmsg))
                continue

            try:
                mltries.setStopTraversal(key, False)
            except triesException as te:
                excmsg = ("(CommandLoader) unload,fail to disable traversal "
                          "for key list '"+str(" ".join(key))+"' in multi "
                          "tries: "+str(te))
                exceptions.addException(UnloadException(excmsg))

        # raise error list
        if exceptions.isThrowable():
            raise exceptions

    def addCmd(self, key_list, cmd):
        if self.TempPrefix is not None:
            prefix = list(self.TempPrefix)
            prefix.extend(key_list)
        else:
            prefix = key_list
        
        final_cmd_key = tuple(prefix)
        
        if final_cmd_key in self.cmdDict:
            excmsg = ("(CommandLoader) addCmd, the following key already"
                      " exists: '"+str(" ".join(final_cmd_key)+"'"))
            raise RegisterException(excmsg)

        self.cmdDict[final_cmd_key] = cmd

        return cmd
