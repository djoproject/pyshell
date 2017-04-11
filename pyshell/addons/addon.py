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

import os

import pyshell.addons
from pyshell.arg.accessor.default import DefaultAccessor
from pyshell.arg.accessor.environment import EnvironmentAccessor
from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.string43 import StringArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.register.command import registerCommand
from pyshell.register.command import registerSetGlobalPrefix
from pyshell.register.command import registerSetTempPrefix
from pyshell.register.command import registerStopHelpTraversalAt
from pyshell.utils.constants import ADDON_PREFIX
from pyshell.utils.constants import ENVIRONMENT_ADDON_TO_LOAD_KEY
from pyshell.utils.constants import ENVIRONMENT_TAB_SIZE_KEY
from pyshell.utils.exception import ListOfException
from pyshell.utils.exception import PyshellException
from pyshell.utils.postprocess import listResultHandler
from pyshell.utils.postprocess import printColumn
from pyshell.utils.printing import error
from pyshell.utils.printing import formatBolt
from pyshell.utils.printing import formatException
from pyshell.utils.printing import formatGreen
from pyshell.utils.printing import formatOrange
from pyshell.utils.printing import formatRed
from pyshell.utils.printing import notice
from pyshell.utils.printing import warning

# python3 reload
try:
    from importlib import reload
except ImportError:
    pass


def formatState(profile_object):
    if profile_object.hasError():
        if profile_object.isLoaded():
            return formatRed("loaded with error")
        elif profile_object.isUnloaded():
            return formatRed("unloaded with error")

    if profile_object.isLoading():
        return formatOrange("loading")
    elif profile_object.isLoaded():
        return formatGreen("loaded")
    elif profile_object.isUnloading():
        return formatOrange("unloading")
    elif profile_object.isUnloaded():
        return formatGreen("unloaded")

    return formatOrange("unknown state")


# # FUNCTION SECTION # #

@shellMethod(addon_dico=DefaultAccessor.getAddon())
def listAddonFun(addon_dico):
    "list the available addons"

    # create addon list from default addon directory (that does not include
    # addon loaded from outside)
    local_addon = []
    addon_directory = os.path.abspath(pyshell.addons.__file__)
    addon_directory = os.path.dirname(addon_directory)
    if os.path.exists(addon_directory):
        for entry in os.listdir(addon_directory):
            if not os.path.isfile(os.path.join(addon_directory, entry)):
                continue

            if not entry.endswith(".py") or entry == "__init__.py":
                continue

            local_addon.append(ADDON_PREFIX + entry[0:-3])

    l = []
    for name, loader in addon_dico.items():
        if name in local_addon:
            local_addon.remove(name)

        addon_information = loader.getInformations()
        last_used_profile = addon_information.getLastProfileUsed()

        if last_used_profile is None:
            state = formatOrange("-")
            profile_name = formatOrange("none")
        else:
            state = formatState(last_used_profile)
            profile_name = formatGreen(last_used_profile.getName())

        l.append((name, profile_name, state))

    # print not loaded local addon
    for name in local_addon:
        l.append((name, formatOrange("none"), formatOrange("-"), ))

    if len(l) == 0:
        return [("No addon available",)]

    l.sort()
    title = (formatBolt("Addon name"),
             formatBolt("Last profile used"),
             formatBolt("State"),)
    l.insert(0, title)
    return l


@shellMethod(name=DefaultChecker.getString(),
             addon_dico=DefaultAccessor.getAddon(),
             parameters=DefaultAccessor.getContainer(),
             profile_name=StringArgChecker())
def unloadAddon(name, addon_dico, parameters, profile_name=None):
    "unload an addon"

    if name not in addon_dico:
        error("unknown addon '%s'" % name)
        return

    addon = addon_dico[name]
    addon.unload(container=parameters, profile_name=profile_name)
    notice(str(name) + " unloaded !")


@shellMethod(name=DefaultChecker.getString(),
             addon_dico=DefaultAccessor.getAddon(),
             parameters=DefaultAccessor.getContainer())
def hardReload(name, addon_dico, parameters):
    "reload an addon from file"

    loaded = False
    if name in addon_dico:
        addon = addon_dico[name]
        addon_name = addon.getInformations().getName()
        last_loaded_profile = addon.getInformations().getLastProfileUsed()
        loaded = (last_loaded_profile is not None and
                  last_loaded_profile.isLoaded())
        if loaded:
            try:
                addon.unload(container=parameters,
                             profile_name=last_loaded_profile.getName())
            except PyshellException as pe:
                exc_msg = "error on addon '%s' unloading: %s"
                exc_msg %= (addon_name, formatException(pe),)
                error(exc_msg)
    else:
        addon_name = name

    try:
        mod = __import__(addon_name, fromlist=["_loaders"], level=0)
    except ImportError as ie:
        excmsg = "fail to retrieve addon module '%s', reason: %s"
        excmsg %= (addon_name, ie,)
        error(excmsg)
        return

    if hasattr(mod, "_loaders"):
        delattr(mod, "_loaders")

    mod = reload(mod)

    if not hasattr(mod, "_loaders"):
        excmsg = ("addon '%s' is not valid, no loader found even after the "
                  "reload. don't forget to register something in the addon")
        excmsg %= str(name)
        error(excmsg)
        return

    addon = mod._loaders

    # load and register
    addon_dico[name] = addon

    if loaded:
        try:
            addon.load(container=parameters,
                       profile_name=last_loaded_profile.getName())
        except PyshellException:
            warning("addon '%s', profile '%s', problems encountered during"
                    " loading" % (name, last_loaded_profile.getName(),))
            raise

    notice(name + " hard reloaded !")


@shellMethod(name=DefaultChecker.getString(),
             addon_dico=DefaultAccessor.getAddon(),
             tabsize=EnvironmentAccessor(ENVIRONMENT_TAB_SIZE_KEY))
def getAddonInformation(name, addon_dico, tabsize):
    "print all available information about an addon"
    tab = " " * tabsize.getValue()

    # if not in the list, try to load it
    if name not in addon_dico:
        try:
            mod = __import__(name, fromlist=["_loaders"], level=0)
        except ImportError as ie:
            excmsg = "fail to import addon '%s', reason: %s"
            excmsg %= (str(name), str(ie),)
            error(excmsg)
            return

        if not hasattr(mod, "_loaders"):
            excmsg = ("invalid addon '%s', no loader found. don't forget to "
                      "register something in the addon")
            excmsg %= str(name)
            error(excmsg)
            return

        addon = mod._loaders
        addon_dico[name] = addon
    else:
        addon = addon_dico[name]

    lines = []

    name = addon.getInformations().getName()
    line = "%s '%s'" % (formatBolt("Addon"), name,)
    lines.append(line)

    # each sub addon
    for profile_name in addon.getProfileNameList():
        root_profile = addon.getRootLoaderProfile(profile_name)
        status = formatState(root_profile)
        title = formatBolt("Profile")
        line = "%s%s '%s': %s" % (tab, title, profile_name, status,)

        # current status
        lines.append(line)

        # print information error for each loader
        keys = sorted(root_profile.getChildKeys(), key=lambda c: c.__name__)
        for loader_class in keys:
            loader_profile = addon.getLoaderProfile(loader_class, profile_name)
            last_exception = loader_profile.getLastException()

            if last_exception is None:
                exceptions = ()
            elif isinstance(last_exception, ListOfException):
                exceptions = last_exception.exceptions
            else:
                exceptions = (last_exception,)

            if len(exceptions) > 0:
                ecount = formatRed("error")
            else:
                ecount = formatGreen("ok")

            line = "%s%s '%s' (status=%s)"
            lname = loader_class.__name__
            line %= (tab*2, formatBolt("Loader"), lname, ecount,)
            lines.append(line)

            if len(exceptions) > 0:
                line = "%s%s count=<%s>:"
                lname = loader_class.__name__
                line %= (tab*3, formatBolt("Error(s)"), len(exceptions),)
                lines.append(line)

                for exc in exceptions:
                    line = "%s* %s" % (tab*4, formatException(exc),)
                    lines.append(line)

                if (not isinstance(last_exception, ListOfException) and
                   hasattr(last_exception, "stacktrace") and
                   last_exception.stacktrace is not None):
                    lines.append("")
                    trace = last_exception.stacktrace
                    splitted_trace = trace.split("\n")
                    for string in splitted_trace:
                        line = "%s%s" % (tab*4, string,)
                        lines.append(line)

            content = loader_profile.getContentList()
            if len(content) > 0:
                line = "%s%s count=<%s>:"
                lname = loader_class.__name__
                line %= (tab*3, formatBolt("Content"), len(content),)
                lines.append(line)

                for obj in content:
                    line = "%s%s" % (tab*4, obj,)
                    lines.append(line)
            lines.append("")

    return lines


@shellMethod(
    addon_name=DefaultChecker.getString(),
    addon_list_on_start_up=EnvironmentAccessor(ENVIRONMENT_ADDON_TO_LOAD_KEY))
def addOnStartUp(addon_name, addon_list_on_start_up):
    "add an addon loading on startup"

    try:
        mod = __import__(addon_name, fromlist=["_loaders"], level=0)
    except ImportError as ie:
        excmsg = "fail to import addon '%s', reason: %s"
        excmsg %= (addon_name, str(ie),)
        error(excmsg)
        return

    if not hasattr(mod, "_loaders"):
        excmsg = ("invalid addon '%s', no loader found. don't forget to "
                  "register something in the addon")
        excmsg %= addon_name
        error(excmsg)
        return

    addon_list = addon_list_on_start_up.getValue()

    if addon_name not in addon_list:
        addon_list.append(addon_name)
        addon_list_on_start_up.setValue(addon_list)


@shellMethod(addon_name=DefaultChecker.getString(),
             addon_list_on_start_up=EnvironmentAccessor(
                 ENVIRONMENT_ADDON_TO_LOAD_KEY))
def removeOnStartUp(addon_name, addon_list_on_start_up):
    "remove an addon loading from startup"

    addon_list = addon_list_on_start_up.getValue()

    if addon_name in addon_list:
        addon_list.remove(addon_name)
        addon_list_on_start_up.setValue(addon_list)


@shellMethod(
    addon_list_on_start_up=EnvironmentAccessor(ENVIRONMENT_ADDON_TO_LOAD_KEY))
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
    addon_name=DefaultChecker.getString(),
    addon_list_on_start_up=EnvironmentAccessor(ENVIRONMENT_ADDON_TO_LOAD_KEY))
def downAddonInList(addon_name, addon_list_on_start_up):
    "reduce the loading priority at startup for an addon"

    addon_list = addon_list_on_start_up.getValue()

    if addon_name not in addon_list:
        raise Exception("unknown addon name '" + str(addon_name) + "'")

    position = addon_list.index(addon_name)
    addon_list.remove(addon_name)
    addon_list.insert(position + 1, addon_name)


@shellMethod(
    addon_name=DefaultChecker.getString(),
    addon_list_on_start_up=EnvironmentAccessor(ENVIRONMENT_ADDON_TO_LOAD_KEY))
def upAddonInList(addon_name, addon_list_on_start_up):
    "increase the loading priority at startup for an addon"

    addon_list = addon_list_on_start_up.getValue()

    if addon_name not in addon_list:
        raise Exception("unknown addon name '" + str(addon_name) + "'")

    position = addon_list.index(addon_name)
    addon_list.remove(addon_name)
    addon_list.insert(max(position - 1, 0), addon_name)


@shellMethod(
    addon_name=DefaultChecker.getString(),
    position=DefaultChecker.getInteger(),
    addon_list_on_start_up=EnvironmentAccessor(ENVIRONMENT_ADDON_TO_LOAD_KEY))
def setAddonPositionInList(addon_name, position, addon_list_on_start_up):
    "set the loading position at startup for an addon"

    addon_list = addon_list_on_start_up.getValue()

    if addon_name not in addon_list:
        raise Exception("unknown addon name '" + str(addon_name) + "'")

    addon_list.remove(addon_name)
    addon_list.insert(max(position, 0), addon_name)

# ## REGISTER SECTION ## #

registerSetGlobalPrefix(("addon", ))
registerStopHelpTraversalAt()
registerCommand(("list",), pro=listAddonFun, post=printColumn)
registerCommand(("unload",), pro=unloadAddon)
registerCommand(("reload",), pro=hardReload)
registerCommand(("info",), pro=getAddonInformation, post=listResultHandler)
registerSetTempPrefix(("onstartup",))
registerCommand(("add",), pro=addOnStartUp)
registerCommand(("remove",), pro=removeOnStartUp)
registerCommand(("list",), pro=listOnStartUp, post=printColumn)
registerCommand(("up",), pro=upAddonInList)
registerCommand(("down",), pro=downAddonInList)
registerCommand(("index",), pro=setAddonPositionInList)
registerStopHelpTraversalAt()
