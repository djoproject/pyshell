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

from pyshell.loader.abstractloader import AbstractLoader
from pyshell.loader.exception import LoadException
from pyshell.loader.exception import RegisterException
from pyshell.loader.masterloader import MasterLoader
from pyshell.loader.utils import getRootLoader
from pyshell.utils.constants import ADDONLIST_KEY
from pyshell.utils.constants import DEFAULT_PROFILE_NAME
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_LOADED_E
from pyshell.utils.exception import ListOfException
from pyshell.utils.string import isString


def _localGetAndInitCallerModule(profile=None):
    master = getRootLoader(class_definition=MasterLoader)
    return master.getOrCreateLoader(DependanciesLoader, profile)


def setDependanciesLoadPriority(value, profile=None):
    try:
        priority = int(value)
    except ValueError:
        excmsg = ("(Loader) setDependanciesLoadPriority an integer value"
                  " was expected for the argument value, got '" +
                  str(type(value))+"'")
        raise RegisterException(excmsg)

    loader = _localGetAndInitCallerModule(profile)
    loader.load_priority = priority


def setDependanciesUnloadPriority(value, profile=None):
    try:
        priority = int(value)
    except ValueError:
        excmsg = ("(Loader) setDependanciesUnloadPriority an integer value"
                  " was expected for the argument value, got '" +
                  str(type(value))+"'")
        raise RegisterException(excmsg)

    loader = _localGetAndInitCallerModule(profile)
    loader.unload_priority = priority



def registerDependOnAddon(dependancy_name,
                          dependancy_profile=None,
                          profile=None):
    if not isString(dependancy_name):
        raise RegisterException("(Loader) registerDependOnAddon, only string "
                                "or unicode addon name are allowed, got '" +
                                str(type(dependancy_name))+"'")

    if dependancy_profile is not None and not isString(dependancy_profile):
        raise RegisterException("(Loader) registerDependOnAddon, only string "
                                "or unicode addon profile are allowed, got '" +
                                str(type(dependancy_profile))+"'")

    loader = _localGetAndInitCallerModule(profile)
    loader.dep.append((dependancy_name, dependancy_profile,))


def _isAddonLoaded(addon_dico, addon_name, addon_profile):
    if addon_name not in addon_dico:
        return False

    loader = addon_dico[addon_name]

    if addon_profile is None:
        addon_profile = DEFAULT_PROFILE_NAME

    if addon_profile not in loader.profile_list:
        return False

    loaders, state = loader.profile_list[addon_profile]
    return state in (STATE_LOADED, STATE_LOADED_E,)

class DependanciesLoader(AbstractLoader):
    def __init__(self, parent):
        AbstractLoader.__init__(self, 
                                parent,
                                load_priority=0.0,
                                unload_priority=0.0)
        self.dep = []

    def load(self, parameter_container=None, profile=None):
        AbstractLoader.load(self, parameter_container, profile)

        if len(self.dep) == 0:
            return

        param = parameter_container.environment.getParameter(
            ADDONLIST_KEY,
            perfect_match=True)
        if param is None:
            raise LoadException("(DependanciesLoader) load, no addon list "
                                "defined")

        addon_dico = param.getValue()

        for (dep_name, dep_profile) in self.dep:
            exceptions = ListOfException()
            if not _isAddonLoaded(addon_dico, dep_name, dep_profile):
                ex = LoadException("(DependanciesLoader) load, addon '" +
                                   str(dep_name)+"', profile '" +
                                   str(dep_profile)+"' is not loaded")
                exceptions.addException(ex)

            if exceptions.isThrowable():
                raise exceptions

    def unload(self, parameter_manager=None, profile=None):
        pass
