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
from pyshell.loader.exception import LoadException
from pyshell.loader.exception import RegisterException
from pyshell.loader.utils import AbstractLoader
from pyshell.loader.utils import getAndInitCallerModule
from pyshell.utils.constants import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.exception import ListOfException
from pyshell.utils.misc import raiseIfInvalidKeyList


def _localGetAndInitCallerModule(profile=None):
    return getAndInitCallerModule(CommandLoader.__module__+"." +
                                  CommandLoader.__name__,
                                  CommandLoader,
                                  profile)


def _checkBoolean(boolean, boolean_name, meth):
    if type(boolean) != bool:
        excmsg = ("(CommandRegister) "+meth+" a boolean value was expected for"
                  " the argument "+boolean_name+", got '"+str(type(boolean)) +
                  "'")
        raise RegisterException(excmsg)


def setCommandLoaderPriority(value, profile=None):
    try:
        priority = int(value)
    except ValueError:
        excmsg = ("(CommandRegister) setCommandLoaderPriority an integer value"
                  " was expected for the argument value, got '" +
                  str(type(value))+"'")
        raise RegisterException(excmsg)

    loader = _localGetAndInitCallerModule(profile)
    loader.priority = priority


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


def registerAnInstanciatedCommand(key_list,
                                  cmd,
                                  raise_if_exist=True,
                                  override=False,
                                  profile=None):
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
    _checkBoolean(raise_if_exist,
                  "raise_if_exist",
                  "registerAnInstanciatedCommand")
    _checkBoolean(override, "override", "registerAnInstanciatedCommand")

    loader = _localGetAndInitCallerModule(profile)
    loader.addCmd(key_list, cmd, raise_if_exist, override)
    return cmd


def registerCommand(key_list,
                    pre=None,
                    pro=None,
                    post=None,
                    raise_if_exist=True,
                    override=False,
                    profile=None):
    # check cmd and keylist
    raiseIfInvalidKeyList(key_list,
                          RegisterException,
                          "CommandRegister",
                          "registerCommand")
    _checkBoolean(raise_if_exist, "raise_if_exist", "registerCommand")
    _checkBoolean(override, "override", "registerCommand")

    loader = _localGetAndInitCallerModule(profile)
    cmd = UniCommand(pre, pro, post)
    loader.addCmd(key_list, cmd, raise_if_exist, override)
    return cmd


def registerAndCreateEmptyMultiCommand(key_list,
                                       raise_if_exist=True,
                                       override=False,
                                       profile=None):
    # check cmd and keylist
    raiseIfInvalidKeyList(key_list,
                          RegisterException,
                          "CommandRegister",
                          "registerCreateMultiCommand")
    _checkBoolean(raise_if_exist,
                  "raise_if_exist",
                  "registerAndCreateEmptyMultiCommand")
    _checkBoolean(override, "override", "registerAndCreateEmptyMultiCommand")

    loader = _localGetAndInitCallerModule(profile)
    cmd = MultiCommand()
    loader.addCmd(key_list, cmd, raise_if_exist, override)
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
    def __init__(self):
        AbstractLoader.__init__(self)

        self.prefix = ()
        self.cmdDict = {}
        self.TempPrefix = None
        self.stoplist = set()

        self.loadedCommand = None
        self.loadedStopTraversal = None

    def load(self, parameter_manager, profile=None):
        self.loadedCommand = []
        self.loadedStopTraversal = []

        AbstractLoader.load(self, parameter_manager, profile)
        env = parameter_manager.environment
        param = env.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY,
                                 perfect_match=True)

        if param is None:
            excmsg = ("(CommandLoader) load, fail to load command because "
                      "parameter has not a levelTries item")
            raise LoadException(excmsg)

        mltries = param.getValue()
        exceptions = ListOfException()

        # add command
        for key_list, cmdInfo in self.cmdDict.items():
            cmd, raise_if_exist, override = cmdInfo
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
                    if raise_if_exist:
                        flat_key = str(" ".join(key))
                        excmsg = ("(CommandLoader) load, fail to insert key "
                                  "'"+flat_key+"' in multi tries: path already"
                                  " exists")
                        exceptions.addException(LoadException(excmsg))
                        continue

                    if not override:
                        continue

                    mltries.update(key, cmd)
                    self.loadedCommand.append(key)

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

    def unload(self, parameter_manager, profile=None):
        AbstractLoader.unload(self, parameter_manager, profile)
        env = parameter_manager.environment
        param = env.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY,
                                 perfect_match=True)

        if param is None:
            excmsg = ("(CommandLoader) unload, fail to load command because "
                      "parameter has not a levelTries item")
            raise LoadException(excmsg)

        mltries = param.getValue()
        exceptions = ListOfException()

        # remove commands
        for key in self.loadedCommand:
            try:
                mltries.remove(key)
            except triesException as te:
                excmsg = ("(CommandLoader) unload, fail to remove key '" +
                          str(" ".join(key))+"' in multi tries: "+str(te))
                exceptions.addException(LoadException(excmsg))

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
                exceptions.addException(LoadException(excmsg))
                continue

            try:
                mltries.setStopTraversal(key, False)
            except triesException as te:
                excmsg = ("(CommandLoader) unload,fail to disable traversal "
                          "for key list '"+str(" ".join(key))+"' in multi "
                          "tries: "+str(te))
                exceptions.addException(LoadException(excmsg))

        # raise error list
        if exceptions.isThrowable():
            raise exceptions

    def addCmd(self, key_list, cmd, raise_if_exist=True, override=False):
        if self.TempPrefix is not None:
            prefix = list(self.TempPrefix)
            prefix.extend(key_list)
        else:
            prefix = key_list

        self.cmdDict[tuple(prefix)] = (cmd, raise_if_exist, override,)

        return cmd
