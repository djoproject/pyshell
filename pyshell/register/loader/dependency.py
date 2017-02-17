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

from pyshell.register.loader.abstractloader import AbstractLoader
from pyshell.register.loader.exception import LoadException
from pyshell.register.profile.dependency import DependencyLoaderProfile
from pyshell.utils.constants import ADDONLIST_KEY
from pyshell.utils.constants import DEFAULT_PROFILE_NAME
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_LOADED_E
from pyshell.utils.exception import ListOfException


def _isAddonLoaded(addon_dico, addon_name, addon_profile):
    if addon_name not in addon_dico:
        return False

    loader = addon_dico[addon_name]

    if addon_profile is None:
        addon_profile = DEFAULT_PROFILE_NAME

    if not loader.hasProfile(addon_profile):
        return False

    root_profile = loader.getRootLoaderProfile(addon_profile)
    return root_profile.getState() in (STATE_LOADED, STATE_LOADED_E,)


class DependencyLoader(AbstractLoader):

    @staticmethod
    def createProfileInstance():
        return DependencyLoaderProfile()

    @classmethod
    def load(cls, profile_object, parameter_container):
        if len(profile_object.dep) == 0:
            return

        if parameter_container is None:
            excmsg = ("(" + cls.__name__ + ") unload, parameter "
                      "container is not defined.  It is needed to unload the "
                      "parameters")
            raise LoadException(excmsg)

        if not hasattr(parameter_container, ENVIRONMENT_ATTRIBUTE_NAME):
            excmsg = ("(" + cls.__name__ + ") unload, parameter "
                      "container does not have the attribute '" +
                      str(ENVIRONMENT_ATTRIBUTE_NAME) + "'")
            raise LoadException(excmsg)

        parameter_manager = getattr(parameter_container,
                                    ENVIRONMENT_ATTRIBUTE_NAME)

        param = parameter_manager.getParameter(ADDONLIST_KEY,
                                               perfect_match=True)
        if param is None:
            raise LoadException("(DependanciesLoader) load, no addon list "
                                "defined")

        addon_dico = param.getValue()

        for dep_name, dep_profile in profile_object.dep.items():
            exceptions = ListOfException()
            if not _isAddonLoaded(addon_dico, dep_name, dep_profile):
                ex = LoadException("(DependanciesLoader) load, addon '" +
                                   str(dep_name) + "', profile '" +
                                   str(dep_profile) + "' is not loaded")
                exceptions.addException(ex)

            if exceptions.isThrowable():
                raise exceptions
