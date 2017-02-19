#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

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

import threading

from pyshell.command.procedure import AbstractLevelHandler
from pyshell.register.utils.misc import getLoaderClass
from pyshell.register.utils.parent import ParentAddon
from pyshell.system.manager.parent import ParentManager
from pyshell.utils.exception import DefaultPyshellException


MAIN_LEVEL = "main"
PROCEDURE_LEVEL = "procedure"


class ControlCenter(ParentAddon, ParentManager, AbstractLevelHandler):
    def __init__(self):
        ParentAddon.__init__(self)
        ParentManager.__init__(self)
        AbstractLevelHandler.__init__(self)
        # small explanation about levels: A thread can access to two
        # different level, the main one and the procedure one.  The
        # goal is to force developper to create python procedure
        # in place of shell procedure.
        #
        # In the main thread, the main level is occupied by the shell
        # or by a main script (init script or daemon script), it is
        # possible to run a sub script that will be in the procedure
        # level.  A command in the procedure level won't be allowed
        # to create another procedure level.
        #
        # In any secondary thread, the main level will be occupied
        # by a command started from another thread.  It is not
        # possible to have a procedure in the main level because
        # it needs to be started by a command.  The command in
        # the main level can execute a procedure in the procedure
        # level.  And as for the main thread, the procedure
        # won't be allowed to create another procedure level.
        self.thread_in_procedure = set()

    def isMainThread(self):
        return isinstance(threading.current_thread(), threading._MainThread)

# ## Level part ## #

    def decrementLevel(self):
        tid = threading.current_thread().ident

        if tid in self.thread_in_procedure:
            self.thread_in_procedure.remove(tid)

    def incrementLevel(self):
        tid = threading.current_thread().ident

        if tid in self.thread_in_procedure:
            excmsg = ("(ParameterContainer) incrementLevel, this thread"
                      " already executes a procedure, only one level of "
                      "procedure is allowed.  If your design requires"
                      "embedded procedure, this is a mistake.  Write them"
                      "in python language instead.")
            raise DefaultPyshellException(excmsg)

        self.thread_in_procedure.add(tid)

    def getCurrentLevel(self):
        tid = threading.current_thread().ident

        if tid in self.thread_in_procedure:
            return tid, PROCEDURE_LEVEL

        return tid, MAIN_LEVEL

# ## ParentManager part ## #

    def getCurrentId(self):
        return self.getCurrentLevel()

    # TODO (issue #83) it will only be allowed to set/unset at LOADED state
    #   Loading/unloading will become osbolete, remove them.

    def checkForSetGlobalParameter(self, group_name, loader_name):
        addons = self.getAddonManager()
        if group_name not in addons:
            excmsg = ("(%s) checkForSetGlobalParameter, the addon '%s' does"
                      " not exist.")
            excmsg %= (self.__class__.__name__, str(group_name),)
            raise DefaultPyshellException(excmsg)

        loader_class = getLoaderClass(loader_name)

        if loader_class is None:
            excmsg = ("(%s) checkForSetGlobalParameter, unknown loader class"
                      " '%s'.")
            excmsg %= (self.__class__.__name__, str(loader_name),)
            raise DefaultPyshellException(excmsg)

        addon_loader = addons[group_name]
        loaded_profile = addon_loader.getInformations().getLoadedProfileName()

        if loaded_profile is None:
            excmsg = ("(%s) checkForSetGlobalParameter, addon '%s' is not "
                      "loaded.")
            excmsg %= (self.__class__.__name__, str(group_name),)
            raise DefaultPyshellException(excmsg)

        root_profile = addon_loader.getRootLoaderProfile(loaded_profile)

        if not root_profile.isLoading() and not root_profile.isLoaded():
            excmsg = ("(%s) checkForSetGlobalParameter, addon '%s' is not "
                      "loaded or loading.")
            excmsg %= (self.__class__.__name__, str(group_name),)
            raise DefaultPyshellException(excmsg)

        # loader is already binded
        if addon_loader.isLoaderBindedToProfile(loader_class, loaded_profile):
            return

        addon_loader.bindLoaderToProfile(loader_class, loaded_profile)

    def checkForUnsetGlobalParameter(self, group_name, loader_name):
        addons = self.getAddonManager()
        if group_name not in addons:
            excmsg = ("(%s) checkForUnsetGlobalParameter, the addon '%s' does"
                      " not exist.")
            excmsg %= (self.__class__.__name__, str(group_name),)
            raise DefaultPyshellException(excmsg)

        addon_loader = addons[group_name]
        loaded_profile = addon_loader.getInformations().getLoadedProfileName()

        if loaded_profile is None:
            excmsg = ("(%s) checkForUnsetGlobalParameter, addon '%s' is not "
                      "loaded.")
            excmsg %= (self.__class__.__name__, str(group_name),)
            raise DefaultPyshellException(excmsg)

        root_profile = addon_loader.getRootLoaderProfile(loaded_profile)

        if not root_profile.isUnloading() and not root_profile.isLoaded():
            excmsg = ("(%s) checkForUnsetGlobalParameter, addon '%s' is not "
                      "loaded or unloading.")
            excmsg %= (self.__class__.__name__, str(group_name),)
            raise DefaultPyshellException(excmsg)
