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
#   only one profile by addon can be load, adapt printing if needed
#   on list print, don't print any profile name if unloaded
#   profile is not saved with addon to load list, find a way to store it

import os
import traceback

from pyshell.arg.argchecker import CompleteEnvironmentChecker
from pyshell.arg.argchecker import DefaultInstanceArgChecker
from pyshell.arg.argchecker import EnvironmentParameterChecker
from pyshell.arg.argchecker import StringArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.loader.command import registerCommand
from pyshell.loader.command import registerSetGlobalPrefix
from pyshell.loader.command import registerSetTempPrefix
from pyshell.loader.command import registerStopHelpTraversalAt
from pyshell.utils.constants import ADDONLIST_KEY
from pyshell.utils.constants import DEFAULT_PROFILE_NAME
from pyshell.utils.constants import ENVIRONMENT_ADDON_TO_LOAD_KEY
from pyshell.utils.constants import ENVIRONMENT_TAB_SIZE_KEY
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_UNLOADED
from pyshell.utils.exception import ListOfException
from pyshell.utils.postprocess import listResultHandler
from pyshell.utils.postprocess import printColumn
from pyshell.utils.printing import formatBolt
from pyshell.utils.printing import formatException
from pyshell.utils.printing import formatGreen
from pyshell.utils.printing import formatOrange
from pyshell.utils.printing import formatRed
from pyshell.utils.printing import notice

ADDON_PREFIX = "pyshell.addons."

# # FUNCTION SECTION # #


def _tryToGetDicoFromParameters(parameters):
    param = parameters.environment.getParameter(ADDONLIST_KEY,
                                                perfect_match=True)
    if param is None:
        raise Exception("no addon list defined")

    return param.getValue()


def _tryToGetAddonFromDico(addon_dico, name):
    if name not in addon_dico:
        raise Exception("unknown addon '"+str(name)+"'")

    return addon_dico[name]


def _tryToGetAddonFromParameters(parameters, name):
    return _tryToGetAddonFromDico(_tryToGetDicoFromParameters(parameters),
                                  name)


def _tryToImportLoaderFromFile(name):
    try:
        mod = __import__(name, fromlist=["_loaders"])
    except ImportError as ie:
        raise Exception(
            "fail to load addon '" +
            str(name) +
            "', reason: " +
            str(ie))

    if not hasattr(mod, "_loaders"):
        raise Exception("invalid addon '"+str(name)+"', no loader found. "
                        "don't forget to register something in the addon")

    return mod._loaders


def _formatState(state, printok, printwarning, printerror):
    if state == STATE_LOADED:
        return printok(state)
    elif state == STATE_UNLOADED:
        return printwarning(state)
    else:
        return printerror(state)


@shellMethod(addon_dico=EnvironmentParameterChecker(ADDONLIST_KEY))
def listAddonFun(addon_dico):
    "list the available addons"

    # get dico of loaded addon
    addon_dico = addon_dico.getValue()

    # create addon list from default addon directory (that does not include
    # addon loaded from outside)
    local_addon = []
    if os.path.exists("./pyshell/addons/"):
        for dirname, dirnames, filenames in os.walk('./pyshell/addons/'):
            for name in filenames:
                if name.endswith(".py") and name != "__init__.py":
                    local_addon.append(ADDON_PREFIX + name[0:-3])

    l = []
    for name, loader in addon_dico.items():
        if name in local_addon:
            local_addon.remove(name)

        # TODO could be None if not loader, manage it
        profileName, profileState = loader.last_updated_profile
        l.append((name,
                  profileName,
                  _formatState(profileState,
                               formatGreen,
                               formatOrange,
                               formatRed),))

    # print not loaded local addon
    for name in local_addon:
        l.append((name, "", formatOrange(STATE_UNLOADED), ))

    l.sort()

    if len(l) == 0:
        return [("No addon available",)]

    l.insert(0,
             (formatBolt("Addon name"),
              formatBolt("Profile"),
              formatBolt("State"),))
    return l


@shellMethod(name=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
             sub_addon=StringArgChecker(),
             parameters=CompleteEnvironmentChecker())
def unloadAddon(name, parameters, sub_addon=None):
    "unload an addon"

    addon = _tryToGetAddonFromParameters(parameters, name)
    addon.unload(parameters, sub_addon)
    notice(str(name) + " unloaded !")


@shellMethod(name=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
             sub_addon=StringArgChecker(),
             parameters=CompleteEnvironmentChecker())
def reloadAddon(name, parameters, sub_addon=None):
    "reload an addon from memory"

    addon = _tryToGetAddonFromParameters(parameters, name)
    addon.reload(parameters, sub_addon)
    notice(str(name) + " reloaded !")


@shellMethod(name=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
             sub_addon=StringArgChecker(),
             parameters=CompleteEnvironmentChecker())
def hardReload(name, parameters, sub_addon=None):
    "reload an addon from file"

    # get addon list and addon
    addon_dico = _tryToGetDicoFromParameters(parameters)
    addon = _tryToGetAddonFromDico(addon_dico, name)

    # unload addon
    addon.unload(parameters, sub_addon)

    # load addon from file
    loader = _tryToImportLoaderFromFile(name)

    # load and register
    addon_dico[name] = loader
    loader.load(parameters, sub_addon)

    notice(name + " hard reloaded !")


@shellMethod(name=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
             addon_dico=EnvironmentParameterChecker(ADDONLIST_KEY),
             tabsize=EnvironmentParameterChecker(ENVIRONMENT_TAB_SIZE_KEY))
def getAddonInformation(name, addon_dico, tabsize, ):
    "print all available information about an addon"

    tab = " " * tabsize.getValue()

    # if not in the list, try to load it
    addon_dico = addon_dico.getValue()
    if name not in addon_dico:
        addon = _tryToImportLoaderFromFile(name)
    else:
        addon = addon_dico[name]

    lines = []
    # extract information from _loaders
    # current name
    lines.append(formatBolt("Addon") + " '" + str(name) + "'")

    # each sub addon
    for sub_addon_name, (subloaders, status, ) in addon.profile_list.items():
        # current status
        lines.append(tab+formatBolt("Sub addon")+" '"+str(sub_addon_name) +
                     "': "+_formatState(status,
                                        formatGreen,
                                        formatOrange,
                                        formatRed))

        # loader in each subbadon
        for name, loader in subloaders.items():
            # print information error for each loader
            if loader.last_exception is not None:
                if isinstance(loader.last_exception, ListOfException):
                    formatedcount = formatRed(
                        str(len(loader.last_exception.exceptions)))
                    lines.append(tab*2+formatBolt("Loader")+" '"+str(name) +
                                 "' (error count = "+formatedcount+")")

                    for exc in loader.last_exception.exceptions:
                        lines.append(tab * 5 + "*" + formatException(exc))

                else:
                    lines.append(
                        tab *
                        2 +
                        formatBolt("Loader") +
                        " '" +
                        str(name) +
                        "' (error count = " +
                        formatRed("1") +
                        ")")
                    lines.append(
                        tab * 3 + formatRed(str(loader.last_exception)))

                    if (hasattr(loader.last_exception, "stackTrace") and
                       loader.last_exception is not None):
                        last_exception_splitted = \
                            loader.last_exception.split("\n")
                        for string in last_exception_splitted:
                            lines.append(tab * 3 + string)
            else:
                lines.append(tab*2+formatBolt("Loader")+" '"+str(name) +
                             "' (error count = 0)")

    return lines


@shellMethod(
    name=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
    sub_loader_name=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
    sub_addon=StringArgChecker(),
    parameters=CompleteEnvironmentChecker())
def subLoaderReload(name, sub_loader_name, parameters, sub_addon=None):
    "reload a profile of an addon from memory"

    # addon name exist ?
    addon = _tryToGetAddonFromParameters(parameters, name)

    if sub_addon is None:
        sub_addon = DEFAULT_PROFILE_NAME

    # sub_addon exist ?
    if sub_addon not in addon.profile_list:
        raise Exception("Unknown sub addon '" + str(sub_addon) + "'")

    loaderDictionnary, status = addon.profile_list[sub_addon]

    # subloader exist ?
    if sub_loader_name not in loaderDictionnary:
        raise Exception("Unknown sub loader '" + str(sub_loader_name) + "'")

    loader = loaderDictionnary[sub_loader_name]

    # reload subloader
    try:
        loader.reload(parameters, sub_addon)
    except Exception as ex:
        loader.last_exception = ex
        loader.last_exception.stackTrace = traceback.format_exc()
        raise ex

    notice("sub loader '" + str(sub_loader_name) + "' reloaded !")


@shellMethod(
    addon_name=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
    addon_list_on_start_up=EnvironmentParameterChecker(
        ENVIRONMENT_ADDON_TO_LOAD_KEY))
def addOnStartUp(addon_name, addon_list_on_start_up):
    "add an addon loading on startup"

    # package exist ?
    _tryToImportLoaderFromFile(addon_name)

    addon_list = addon_list_on_start_up.getValue()

    if addon_name not in addon_list:
        addon_list.append(addon_name)
        addon_list_on_start_up.setValue(addon_list)


@shellMethod(
    addon_name=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
    addon_list_on_start_up=EnvironmentParameterChecker(
        ENVIRONMENT_ADDON_TO_LOAD_KEY))
def removeOnStartUp(addon_name, addon_list_on_start_up):
    "remove an addon loading from startup"

    addon_list = addon_list_on_start_up.getValue()

    if addon_name in addon_list:
        addon_list.remove(addon_name)
        addon_list_on_start_up.setValue(addon_list)


@shellMethod(addon_list_on_start_up=EnvironmentParameterChecker(
    ENVIRONMENT_ADDON_TO_LOAD_KEY))
def listOnStartUp(addon_list_on_start_up):
    "list addon enabled on startup"

    addons = addon_list_on_start_up.getValue()

    if len(addons) == 0:
        return ()

    r = []
    r.append((formatBolt("Order"), formatBolt("Addon name"),))
    for i in range(0, len(addons)):
        r.append((str(i), str(addons[i]), ))

    return r


@shellMethod(
    addon_name=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
    addon_list_on_start_up=EnvironmentParameterChecker(
        ENVIRONMENT_ADDON_TO_LOAD_KEY))
def downAddonInList(addon_name, addon_list_on_start_up):
    "reduce the loading priority at startup for an addon"

    addon_list = addon_list_on_start_up.getValue()

    if addon_name not in addon_list:
        raise Exception("unknown addon name '" + str(addon_name) + "'")

    position = addon_list.index(addon_name)
    addon_list.remove(addon_name)
    addon_list.insert(position + 1, addon_name)


@shellMethod(
    addon_name=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
    addon_list_on_start_up=EnvironmentParameterChecker(
        ENVIRONMENT_ADDON_TO_LOAD_KEY))
def upAddonInList(addon_name, addon_list_on_start_up):
    "increase the loading priority at startup for an addon"

    addon_list = addon_list_on_start_up.getValue()

    if addon_name not in addon_list:
        raise Exception("unknown addon name '" + str(addon_name) + "'")

    position = addon_list.index(addon_name)
    addon_list.remove(addon_name)
    addon_list.insert(max(position - 1, 0), addon_name)


@shellMethod(
    addon_name=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
    position=DefaultInstanceArgChecker.getIntegerArgCheckerInstance(),
    addon_list_on_start_up=EnvironmentParameterChecker(
        ENVIRONMENT_ADDON_TO_LOAD_KEY))
def setAddonPositionInList(addon_name, position, addon_list_on_start_up):
    "set the loading position at startup for an addon"

    addon_list = addon_list_on_start_up.getValue()

    if addon_name not in addon_list:
        raise Exception("unknown addon name '" + str(addon_name) + "'")

    addon_list.remove(addon_name)
    addon_list.insert(max(position, 0), addon_name)


# TODO load all

# ## REGISTER SECTION ## #

registerSetGlobalPrefix(("addon", ))
registerStopHelpTraversalAt()
registerCommand(("list",), pro=listAddonFun, post=printColumn)
registerCommand(("unload",), pro=unloadAddon)
registerSetTempPrefix(("reload",))
registerCommand(("addon",), pro=reloadAddon)
registerCommand(("hard",), pro=hardReload)
registerCommand(("subloader",), pro=subLoaderReload)
registerStopHelpTraversalAt()
registerSetTempPrefix(())
registerCommand(("info",), pro=getAddonInformation, post=listResultHandler)
registerSetTempPrefix(("onstartup",))
registerCommand(("add",), pro=addOnStartUp)
registerCommand(("remove",), pro=removeOnStartUp)
registerCommand(("list",), pro=listOnStartUp, post=printColumn)
registerCommand(("up",), pro=upAddonInList)
registerCommand(("down",), pro=downAddonInList)
registerCommand(("index",), pro=setAddonPositionInList)
registerStopHelpTraversalAt()
