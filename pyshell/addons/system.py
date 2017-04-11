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

import os

from tries import multiLevelTries

import pyshell.addons
from pyshell.arg.accessor.default import DefaultAccessor
from pyshell.arg.accessor.environment import EnvironmentAccessor
from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.file import FilePathArgChecker
from pyshell.arg.checker.integer import IntegerArgChecker
from pyshell.arg.checker.string43 import StringArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.register.command import registerCommand
from pyshell.register.context import registerContextInteger
from pyshell.register.context import registerContextString
from pyshell.register.environment import registerEnvironment
from pyshell.register.environment import registerEnvironmentAny
from pyshell.register.environment import registerEnvironmentBoolean
from pyshell.register.environment import registerEnvironmentListString
from pyshell.register.environment import registerEnvironmentString
from pyshell.register.file import enableConfigSaving
from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.system.setting.environment import EnvironmentGlobalSettings
from pyshell.utils.constants import ADDON_PREFIX
from pyshell.utils.constants import CONTEXT_COLORATION_DARK
from pyshell.utils.constants import CONTEXT_COLORATION_KEY
from pyshell.utils.constants import CONTEXT_COLORATION_LIGHT
from pyshell.utils.constants import CONTEXT_COLORATION_NONE
from pyshell.utils.constants import CONTEXT_EXECUTION_DAEMON
from pyshell.utils.constants import CONTEXT_EXECUTION_KEY
from pyshell.utils.constants import CONTEXT_EXECUTION_SHELL
from pyshell.utils.constants import DEBUG_ENVIRONMENT_NAME
from pyshell.utils.constants import DEFAULT_CONFIG_DIRECTORY
from pyshell.utils.constants import ENVIRONMENT_ADDON_TO_LOAD_DEFAULT
from pyshell.utils.constants import ENVIRONMENT_ADDON_TO_LOAD_KEY
from pyshell.utils.constants import ENVIRONMENT_CONFIG_DIRECTORY_KEY
from pyshell.utils.constants import ENVIRONMENT_HISTORY_FILE_NAME_KEY
from pyshell.utils.constants import ENVIRONMENT_HISTORY_FILE_NAME_VALUE
from pyshell.utils.constants import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.constants import ENVIRONMENT_PROMPT_DEFAULT
from pyshell.utils.constants import ENVIRONMENT_PROMPT_KEY
from pyshell.utils.constants import ENVIRONMENT_SAVE_KEYS_DEFAULT
from pyshell.utils.constants import ENVIRONMENT_SAVE_KEYS_KEY
from pyshell.utils.constants import ENVIRONMENT_TAB_SIZE_KEY
from pyshell.utils.constants import ENVIRONMENT_USE_HISTORY_KEY
from pyshell.utils.constants import ENVIRONMENT_USE_HISTORY_VALUE
from pyshell.utils.constants import TAB_SIZE
from pyshell.utils.exception import ListOfException
from pyshell.utils.exception import PyshellException
from pyshell.utils.printing import error
from pyshell.utils.printing import notice
from pyshell.utils.printing import warning


# # ENVIRONMENT_CONFIG_DIRECTORY_KEY

checker = FilePathArgChecker(exist=None,
                             readable=True,
                             writtable=None,
                             is_file=False)

settings = EnvironmentGlobalSettings(transient=True,
                                     read_only=False,
                                     removable=False,
                                     checker=checker)

param = EnvironmentParameter(value=DEFAULT_CONFIG_DIRECTORY, settings=settings)
registerEnvironment(ENVIRONMENT_CONFIG_DIRECTORY_KEY, param)

# # ENVIRONMENT_PROMPT_KEY

param = registerEnvironmentString(ENVIRONMENT_PROMPT_KEY,
                                  ENVIRONMENT_PROMPT_DEFAULT)
param.settings.setRemovable(False)

# # ENVIRONMENT_TAB_SIZE_KEY

settings = EnvironmentGlobalSettings(transient=False,
                                     read_only=False,
                                     removable=False,
                                     checker=IntegerArgChecker(0))

param = EnvironmentParameter(value=TAB_SIZE, settings=settings)
registerEnvironment(ENVIRONMENT_TAB_SIZE_KEY, param)

# # ENVIRONMENT_LEVEL_TRIES_KEY

param = registerEnvironmentAny(ENVIRONMENT_LEVEL_TRIES_KEY, multiLevelTries())
param.settings.setRemovable(False)
param.settings.setTransient(True)
param.settings.setReadOnly(True)

# # ENVIRONMENT_SAVE_KEYS_KEY

param = registerEnvironmentBoolean(ENVIRONMENT_SAVE_KEYS_KEY,
                                   ENVIRONMENT_SAVE_KEYS_DEFAULT)
param.settings.setRemovable(False)

# # ENVIRONMENT_HISTORY_FILE_NAME_KEY

checker = FilePathArgChecker(exist=None,
                             readable=True,
                             writtable=None,
                             is_file=True)

settings = EnvironmentGlobalSettings(transient=False,
                                     read_only=False,
                                     removable=False,
                                     checker=checker)

param = EnvironmentParameter(value=ENVIRONMENT_HISTORY_FILE_NAME_VALUE,
                             settings=settings)

registerEnvironment(ENVIRONMENT_HISTORY_FILE_NAME_KEY, param)

# # ENVIRONMENT_USE_HISTORY_KEY

param = registerEnvironmentBoolean(ENVIRONMENT_USE_HISTORY_KEY,
                                   ENVIRONMENT_USE_HISTORY_VALUE)
param.settings.setRemovable(False)

# # ENVIRONMENT_ADDON_TO_LOAD_KEY


param = registerEnvironmentListString(ENVIRONMENT_ADDON_TO_LOAD_KEY,
                                      ENVIRONMENT_ADDON_TO_LOAD_DEFAULT)
param.settings.setRemovable(False)

# # DEBUG_ENVIRONMENT_NAME

param = registerContextInteger(DEBUG_ENVIRONMENT_NAME, tuple(range(0, 5)))
param.settings.setIndex(1)
param.settings.setRemovable(False)
param.settings.setReadOnly(True)

# # CONTEXT_EXECUTION_KEY

values = (CONTEXT_EXECUTION_SHELL, CONTEXT_EXECUTION_DAEMON,)
param = registerContextString(CONTEXT_EXECUTION_KEY, values)
param.settings.setRemovable(False)
param.settings.setTransient(True)
param.settings.setReadOnly(True)

# # CONTEXT_COLORATION_KEY

values = (CONTEXT_COLORATION_LIGHT,
          CONTEXT_COLORATION_DARK,
          CONTEXT_COLORATION_NONE,)
param = registerContextString(CONTEXT_COLORATION_KEY, values)
param.settings.setRemovable(False)
param.settings.setReadOnly(True)

##


@shellMethod(name=DefaultChecker.getString(),
             parameters=DefaultAccessor.getContainer(),
             profile_name=StringArgChecker())
def loadAddonFun(name, parameters, profile_name=None):
    "load an addon"

    addon_dico = parameters.getAddonManager()

    # is it already loaded ?
    if name in addon_dico:
        loader = addon_dico[name]
    else:
        # load and register
        try:
            mod = __import__(name, fromlist=["_loaders"], level=0)
        except ImportError as ie:
            excmsg = "addon '%s', fail to load.  Reason: %s"
            excmsg %= (str(name), str(ie),)
            error(excmsg)
            return

        if not hasattr(mod, "_loaders"):
            excmsg = ("addon '%s' is not valid, no loader found. don't forget"
                      " to register something in the addon")
            excmsg %= str(name)
            error(excmsg)
            return

        loader = mod._loaders
        addon_dico[name] = loader

    if not loader.hasProfile(profile_name):
        error("addon '%s' has no profile named '%s'" % (name, profile_name))
        return

    profile_to_load = loader.getRootLoaderProfile(profile_name)

    if profile_to_load.isLoaded():
        msg = "addon '%s', profile '%s', is already loaded !"
        msg %= (name, profile_to_load.getName(),)
        warning(msg)
        return

    if profile_to_load.isLoading():
        msg = "addon '%s', profile '%s', is loading !"
        msg %= (name, profile_to_load.getName(),)
        warning(msg)
        return

    loaded_profile = loader.getInformations().getLastProfileUsed()

    # is another profile loaded/loading ?
    if loaded_profile is not None and not loaded_profile.isUnloaded():
        msg = ("failed to load addon '%s' with profile '%s', profile '%s' is "
               "not unloaded")
        msg %= (name, profile_to_load.getName(), loaded_profile.getName(),)
        error(msg)
        return

    profile_name = profile_to_load.getName()
    try:
        loader.load(container=parameters, profile_name=profile_name)
    except PyshellException:
        warning("addon '%s', profile '%s', problems encountered during "
                "loading" % (name, profile_to_load.getName(),))
        raise
    else:
        notice(name + " loaded !")


def _isLoaded(addon_manager, addon_name):
    if addon_name not in addon_manager:
        return False

    addon_loader = addon_manager[addon_name]
    profile_object = addon_loader.getInformations().getLastProfileUsed()

    if profile_object is None:
        return False

    return profile_object.isLoaded()


@shellMethod(
    params=DefaultAccessor.getContainer(),
    addon_list_on_start_up=EnvironmentAccessor(ENVIRONMENT_ADDON_TO_LOAD_KEY),
    profile_name=StringArgChecker())
def loadAddonOnStartUp(params, addon_list_on_start_up, profile_name=None):
    "load every addon registered to be load at statup"

    if addon_list_on_start_up is None:
        return

    addon_list = addon_list_on_start_up.getValue()

    error_list = ListOfException()
    addon_manager = params.getAddonManager()
    for addon_name in addon_list:
        if _isLoaded(addon_manager, addon_name):
            continue

        try:
            loadAddonFun(addon_name, params, profile_name)
        except Exception as ex:
            error_list.addException(ex)

    if error_list.isThrowable():
        raise error_list


@shellMethod(
    params=DefaultAccessor.getContainer(),
    addon_list_on_start_up=EnvironmentAccessor(ENVIRONMENT_ADDON_TO_LOAD_KEY),
    profile_name=StringArgChecker())
def loadAll(params, addon_list_on_start_up, profile_name=None):

    addon_set = set()
    addon_directory = os.path.abspath(pyshell.addons.__file__)
    addon_directory = os.path.dirname(addon_directory)
    if os.path.exists(addon_directory):
        for entry in os.listdir(addon_directory):
            if not os.path.isfile(os.path.join(addon_directory, entry)):
                continue

            if not entry.endswith(".py") or entry == "__init__.py":
                continue

            addon_set.add(ADDON_PREFIX + entry[0:-3])

    if addon_list_on_start_up is not None:
        for addon_name in addon_list_on_start_up.getValue():
            addon_set.add(addon_name)

    error_list = ListOfException()
    addon_manager = params.getAddonManager()
    for addon_name in addon_set:
        if _isLoaded(addon_manager, addon_name):
            continue

        try:
            loadAddonFun(addon_name, params, profile_name)
        except Exception as ex:
            error_list.addException(ex)

    if error_list.isThrowable():
        raise error_list


registerCommand(("addon", "load",), pro=loadAddonFun)
registerCommand(("addon", "load", "all",), pro=loadAll)
registerCommand(("addon", "onstartup", "load",), pro=loadAddonOnStartUp)
enableConfigSaving()
