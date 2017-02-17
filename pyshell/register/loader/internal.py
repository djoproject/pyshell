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

import heapq
import traceback

from pyshell.register.loader.abstractloader import AbstractLoader
from pyshell.register.loader.exception import LoadException
from pyshell.register.loader.exception import UnloadException
from pyshell.register.profile.internal import InternalLoaderProfile
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_LOADED_E
from pyshell.utils.constants import STATE_UNLOADED
from pyshell.utils.constants import STATE_UNLOADED_E
from pyshell.utils.exception import ListOfException


class InternalLoader(AbstractLoader):

    @staticmethod
    def createProfileInstance():
        return InternalLoaderProfile()

    @staticmethod
    def _innerLoad(method_name,
                   priority_method_name,
                   parameter_container,
                   profile_object,
                   next_state,
                   next_state_if_error):
        exceptions = ListOfException()
        loaders_heap = []
        insert_order = 0

        for loader_class, loader_profile in profile_object.children.items():
            heap_priority = getattr(loader_profile, priority_method_name)()
            heapq.heappush(loaders_heap, (heap_priority,
                                          insert_order,
                                          loader_class,
                                          loader_profile,))
            insert_order += 1

        while len(loaders_heap) > 0:
            priority, insert_order, loader, loader_profile = \
                heapq.heappop(loaders_heap)
            # no need to test if attribute exist, it is supposed to call
            # load/unload and loader is suppose to be an
            # AbstractLoader
            meth_to_call = getattr(loader, method_name)

            try:
                meth_to_call(loader_profile, parameter_container)
                loader_profile.setLastException(None, None)
            except Exception as ex:
                # assign the exception to the loader where it comes from
                # it will allow to retrieve the exception later
                loader_profile.setLastException(ex, traceback.format_exc())
                exceptions.addException(ex)

        if exceptions.isThrowable():
            profile_object.setState(next_state_if_error)
            raise exceptions

        profile_object.setState(next_state)

    @classmethod
    def load(cls, profile_object, parameter_container):
        global_profile = profile_object.getGlobalProfile()
        addon_informations = global_profile.getAddonInformations()
        current_profile_name = global_profile.getName()
        loaded_profile_name = addon_informations.getLoadedProfileName()

        if profile_object.isRoot():
            if loaded_profile_name is not None:
                if loaded_profile_name != current_profile_name:
                    excmsg = ("(MasterLoader) 'load', the profile '%s' "
                              "can not be loaded because the profile '%s' "
                              "is already loaded")
                    excmsg %= (current_profile_name, loaded_profile_name,)
                else:
                    excmsg = ("(MasterLoader) 'load', the profile '%s' is "
                              "already loaded")
                    excmsg %= current_profile_name

                raise LoadException(excmsg)

            addon_informations.setLoadedProfileName(current_profile_name)

        cls._innerLoad("load",
                       "getLoadPriority",
                       parameter_container=parameter_container,
                       profile_object=profile_object,
                       next_state=STATE_LOADED,
                       next_state_if_error=STATE_LOADED_E)

    @classmethod
    def unload(cls, profile_object, parameter_container):
        global_profile = profile_object.getGlobalProfile()
        addon_informations = global_profile.getAddonInformations()
        current_profile_name = global_profile.getName()
        loaded_profile_name = addon_informations.getLoadedProfileName()

        if profile_object.isRoot():
            if loaded_profile_name != current_profile_name:
                excmsg = ("(MasterLoader) 'unload', the profile '%s' is not "
                          "loaded")
                raise UnloadException(excmsg % current_profile_name)

            addon_informations.unsetLoadedProfileName()

        cls._innerLoad("unload",
                       "getUnloadPriority",
                       parameter_container=parameter_container,
                       profile_object=profile_object,
                       next_state=STATE_UNLOADED,
                       next_state_if_error=STATE_UNLOADED_E)
