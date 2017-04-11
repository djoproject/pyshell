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

from pyshell.register.loader.exception import LoadException
from pyshell.register.loader.exception import UnloadException
from pyshell.register.loader.internal import InternalLoader
from pyshell.register.profile.root import RootProfile
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_LOADED_E
from pyshell.utils.constants import STATE_LOADING
from pyshell.utils.constants import STATE_UNLOADED
from pyshell.utils.constants import STATE_UNLOADED_E
from pyshell.utils.constants import STATE_UNLOADING


class RootLoader(InternalLoader):
    @staticmethod
    def createProfileInstance(root_profile):
        return RootProfile()

    @classmethod
    def load(cls, profile_object, parameter_container):
        addon_informations = profile_object.getAddonInformations()
        last_profile_used = addon_informations.getLastProfileUsed()

        if (last_profile_used is not None and
           not last_profile_used.isUnloaded()):
            excmsg = ("(%s) 'load', the profile '%s' can not be loaded "
                      "because the profile '%s' is in the state '%s'")

            excmsg %= (cls.__name__,
                       profile_object.getName(),
                       last_profile_used.getName(),
                       last_profile_used.state)

            raise LoadException(excmsg)

        # remove results generated during the last unload
        profile_object.flush()

        addon_informations.setLastProfileUsed(profile_object)

        profile_object.setState(STATE_LOADING)
        try:
            InternalLoader.load(profile_object, parameter_container)
        except:
            profile_object.setState(STATE_LOADED_E)
            raise
        else:
            profile_object.setState(STATE_LOADED)

    @classmethod
    def unload(cls, profile_object, parameter_container):
        addon_informations = profile_object.getAddonInformations()
        last_profile_used = addon_informations.getLastProfileUsed()

        if (last_profile_used != profile_object or
           not profile_object.isLoaded()):
            excmsg = "(%s) 'unload', the profile '%s' is not loaded"
            excmsg %= (cls.__name__, profile_object.getName(),)
            raise UnloadException(excmsg)

        profile_object.setState(STATE_UNLOADING)
        try:
            InternalLoader.unload(profile_object, parameter_container)
        except:
            profile_object.setState(STATE_UNLOADED_E)
            raise
        else:
            profile_object.setState(STATE_UNLOADED)
