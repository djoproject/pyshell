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
#   add a check on the targeted addon, to block at unload if a dependancy exist
#   remove the check to the dependancy if the dependant addon is removed

from pyshell.loader.abstractloader import AbstractLoader
from pyshell.loader.exception import LoadException
from pyshell.loader.exception import RegisterException
from pyshell.loader.utils import getAndInitCallerModule
from pyshell.utils.constants import ADDONLIST_KEY
from pyshell.utils.constants import DEFAULT_PROFILE_NAME
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_LOADED_E


def _localGetAndInitCallerModule(profile=None):
    return getAndInitCallerModule(DependanciesLoader.__module__+"." +
                                  DependanciesLoader.__name__,
                                  DependanciesLoader,
                                  profile)


def setDependanciesLoaderPriority(value, profile=None):
    try:
        priority = int(value)
    except ValueError:
        excmsg = ("(Loader) setDependanciesLoaderPriority an integer value"
                  " was expected for the argument value, got '" +
                  str(type(value))+"'")
        raise RegisterException(excmsg)

    loader = _localGetAndInitCallerModule(profile)
    loader.priority = priority


def registerDependOnAddon(dependancy_name,
                          dependancy_profile=None,
                          profile=None):
    if type(dependancy_name) != str and type(dependancy_name) != unicode:
        raise RegisterException("(Loader) registerDependOnAddon, only string "
                                "or unicode addon name are allowed, got '" +
                                str(type(dependancy_name))+"'")

    if (dependancy_profile is not None and
       (type(dependancy_profile) != str and
            type(dependancy_profile) != unicode)):
        raise RegisterException("(Loader) registerDependOnAddon, only string "
                                "or unicode addon profile are allowed, got '" +
                                str(type(dependancy_profile))+"'")

    loader = _localGetAndInitCallerModule(profile)
    loader.dep.append((dependancy_name, dependancy_profile,))


class DependanciesLoader(AbstractLoader):
    def __init__(self):
        AbstractLoader.__init__(self)
        self.dep = []

    def load(self, parameter_manager, profile=None):
        AbstractLoader.load(self, parameter_manager, profile)

        if len(self.dep) == 0:
            return

        param = parameter_manager.environment.getParameter(ADDONLIST_KEY,
                                                           perfect_match=True)
        if param is None:
            raise LoadException("(DependanciesLoader) load, no addon list "
                                "defined")

        addon_dico = param.getValue()

        for (dependancy_name, dependancy_profile) in self.dep:
            if dependancy_name not in addon_dico:
                raise LoadException("(DependanciesLoader) load, no addon '" +
                                    str(dependancy_name)+"' loaded")

            loader = addon_dico[dependancy_name]

            if dependancy_profile is None:
                dependancy_profile = DEFAULT_PROFILE_NAME

            if dependancy_profile not in loader.profile_list:
                raise LoadException("(DependanciesLoader) load, addon '" +
                                    str(dependancy_name)+"' has no profile '" +
                                    str(dependancy_profile)+"'")

            loaders, state = loader.profile_list[dependancy_profile]

            if state not in (STATE_LOADED, STATE_LOADED_E,):
                raise LoadException("(DependanciesLoader) load, addon '" +
                                    str(dependancy_name)+"', profile '" +
                                    str(dependancy_profile)+"' is not loaded")
