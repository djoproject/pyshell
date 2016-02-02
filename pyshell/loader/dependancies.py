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

from pyshell.loader.utils import getAndInitCallerModule, AbstractLoader
from pyshell.loader.exception import RegisterException, LoadException
from pyshell.utils.constants import ADDONLIST_KEY, DEFAULT_PROFILE_NAME, \
                                    STATE_LOADED, STATE_LOADED_E


def _local_getAndInitCallerModule(profile=None):
    return getAndInitCallerModule(DependanciesLoader.__module__+"." +
                                  DependanciesLoader.__name__,
                                  DependanciesLoader,
                                  profile)


def registerDependOnAddon(dependancyName,
                          dependancyProfile=None,
                          profile=None):
    if type(dependancyName) != str and type(dependancyName) != unicode:
        raise RegisterException("(Loader) registerDependOnAddon, only string "
                                "or unicode addon name are allowed, got '" +
                                str(type(dependancyName))+"'")

    if dependancyProfile is not None and (type(dependancyProfile) != str and
                                          type(dependancyProfile) != unicode):
        raise RegisterException("(Loader) registerDependOnAddon, only string "
                                "or unicode addon profile are allowed, got '" +
                                str(type(dependancyProfile))+"'")

    loader = _local_getAndInitCallerModule(profile)
    loader.dep.append((dependancyName, dependancyProfile,))


class DependanciesLoader(AbstractLoader):
    def __init__(self):
        AbstractLoader.__init__(self)
        self.dep = []

    def load(self, parameterManager, profile=None):
        AbstractLoader.load(self, parameterManager, profile)

        if len(self.dep) == 0:
            return

        param = parameterManager.environment.getParameter(ADDONLIST_KEY,
                                                          perfectMatch=True)
        if param is None:
            raise LoadException("(DependanciesLoader) load, no addon list "
                                "defined")

        addon_dico = param.getValue()

        for (dependancyName, dependancyProfile) in self.dep:
            if dependancyName not in addon_dico:
                raise LoadException("(DependanciesLoader) load, no addon '" +
                                    str(dependancyName)+"' loaded")

            loader = addon_dico[dependancyName]

            if dependancyProfile is None:
                dependancyProfile = DEFAULT_PROFILE_NAME

            if dependancyProfile not in loader.profileList:
                raise LoadException("(DependanciesLoader) load, addon '" +
                                    str(dependancyName)+"' has no profile '" +
                                    str(dependancyProfile)+"'")

            loaders, state = loader.profileList[dependancyProfile]

            if state not in (STATE_LOADED, STATE_LOADED_E,):
                raise LoadException("(DependanciesLoader) load, addon '" +
                                    str(dependancyName)+"', profile '" +
                                    str(dependancyProfile)+"' is not loaded")
