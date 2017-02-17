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

from pyshell.addons.utils.addon import formatState
from pyshell.addons.utils.addon import tryToGetAddonFromDico
from pyshell.addons.utils.addon import tryToGetAddonFromParameters
from pyshell.addons.utils.addon import tryToGetDicoFromParameters
from pyshell.addons.utils.addon import tryToImportLoaderFromFile
from pyshell.arg.argchecker import CompleteEnvironmentChecker
from pyshell.arg.argchecker import DefaultInstanceArgChecker
from pyshell.arg.argchecker import EnvironmentParameterChecker
from pyshell.arg.argchecker import StringArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.register.command import registerCommand
from pyshell.register.command import registerSetGlobalPrefix
from pyshell.register.command import registerSetTempPrefix
from pyshell.register.command import registerStopHelpTraversalAt
from pyshell.utils.constants import ADDONLIST_KEY
from pyshell.utils.constants import ENVIRONMENT_ADDON_TO_LOAD_KEY
from pyshell.utils.constants import ENVIRONMENT_TAB_SIZE_KEY
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
                  formatState(profileState,
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

    addon = tryToGetAddonFromParameters(parameters, name)
    addon.unload(container=parameters, profile_name=sub_addon)
    notice(str(name) + " unloaded !")


@shellMethod(name=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
             sub_addon=StringArgChecker(),
             parameters=CompleteEnvironmentChecker())
def hardReload(name, parameters, sub_addon=None):
    "reload an addon from file"

    # get addon list and addon
    addon_dico = tryToGetDicoFromParameters(parameters)
    addon = tryToGetAddonFromDico(addon_dico, name)

    # unload addon
    addon.unload(container=parameters, profile_name=sub_addon)

    # load addon from file
    loader = tryToImportLoaderFromFile(name)

    # load and register
    addon_dico[name] = loader
    loader.load(container=parameters, profile_name=sub_addon)

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
        addon = tryToImportLoaderFromFile(name)
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
                     "': "+formatState(status,
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
    addon_name=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
    addon_list_on_start_up=EnvironmentParameterChecker(
        ENVIRONMENT_ADDON_TO_LOAD_KEY))
def addOnStartUp(addon_name, addon_list_on_start_up):
    "add an addon loading on startup"

    # package exist ?
    tryToImportLoaderFromFile(addon_name)

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
registerCommand(("hard",), pro=hardReload)
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
