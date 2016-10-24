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

from pyshell.loader.abstractloader import AbstractLoader
from pyshell.loader.exception import LoadException
from pyshell.loader.exception import LoaderException
from pyshell.loader.exception import RegisterException
from pyshell.loader.exception import UnloadException
from pyshell.loader.file import FileLoader
from pyshell.loader.utils import getLoaderSignature
from pyshell.loader.utils import getNearestModule
from pyshell.utils.constants import DEFAULT_PROFILE_NAME
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_LOADED_E
from pyshell.utils.constants import STATE_UNLOADED
from pyshell.utils.constants import STATE_UNLOADED_E
from pyshell.utils.exception import ListOfException
from pyshell.utils.exception import SYSTEM_NOTICE

try:
    from collections import OrderedDict
except:
    from pyshell.utils.ordereddict import OrderedDict


class MasterLoader(AbstractLoader):
    def __init__(self, addon_name):
        AbstractLoader.__init__(self)
        self.addon_name = addon_name
        self.profile_list = {}
        self.last_updated_profile = None

    def getOrCreateLoader(self, class_definition, profile=None, create=True):
        if profile is None:
            profile = DEFAULT_PROFILE_NAME

        # the loader does not exist, need to create it
        try:
            # need a child class of AbstractLoader
            if (not issubclass(class_definition, AbstractLoader) or
               class_definition.__name__ == "AbstractLoader"):
                excmsg = ("(MasterLoader) getOrCreateLoader, try to create a "
                          "loader with an unallowed class '" +
                          str(class_definition)+"', must be a class definition"
                          " inheriting from AbstractLoader")
                raise RegisterException(excmsg)

        # raise by issubclass if one of the two argument
        # is not a class definition
        except TypeError:
            excmsg = ("(MasterLoader) getOrCreateLoader, expected a class "
                      "definition, got '"+str(class_definition)+"', must be a"
                      " class definition inheriting from AbstractLoader")
            raise RegisterException(excmsg)

        loader_name = getLoaderSignature(class_definition)

        if (profile in self.profile_list and
           loader_name in self.profile_list[profile]):
            return self.profile_list[profile][loader_name]

        if not create:
            return None

        if profile not in self.profile_list:
            self.profile_list[profile] = OrderedDict()

        loader = class_definition(self)
        self.profile_list[profile][loader_name] = loader

        return loader

    def _innerLoad(self,
                   method_name,
                   priority_method_name,
                   parameter_container,
                   profile,
                   next_state,
                   next_state_if_error):
        exceptions = ListOfException()

        # no loader available for this profile
        if profile not in self.profile_list:
            return

        loaders = self.profile_list[profile]

        loaders_heap = []

        insert_order = 0
        for loader in loaders.values():
            get_priority_meth = getattr(loader, priority_method_name)
            heapq.heappush(loaders_heap, (get_priority_meth(),
                                          insert_order,
                                          loader,))
            insert_order += 1

        while len(loaders_heap) > 0:
            priority, insert_order, loader = heapq.heappop(loaders_heap)
            # no need to test if attribute exist, it is supposed to call
            # load/unload and loader is suppose to be an
            # AbstractLoader
            meth_to_call = getattr(loader, method_name)

            try:
                meth_to_call(parameter_container, profile)
                loader.last_exception = None
            except Exception as ex:
                # assign the exception to the loader where it comes from
                # it will allow to retrieve the exception later
                loader.last_exception = ex
                loader.last_exception.stackTrace = traceback.format_exc()

                exceptions.addException(ex)

        if exceptions.isThrowable():
            self.last_updated_profile = (profile, next_state_if_error,)
            raise exceptions

        self.last_updated_profile = (profile, next_state,)

    _loadAllowedState = (STATE_UNLOADED, STATE_UNLOADED_E,)
    _unloadAllowedState = (STATE_LOADED, STATE_LOADED_E,)

    def load(self, parameter_container=None, profile=None):
        if profile is None:
            profile = DEFAULT_PROFILE_NAME

        if (self.last_updated_profile is not None and
           self.last_updated_profile[1] not in MasterLoader._loadAllowedState):
            if profile == self.last_updated_profile[0]:
                excmsg = ("(MasterLoader) 'load', profile '"+str(profile) +
                          "' is already loaded")
                exc = LoadException(excmsg)
                exc.severity = SYSTEM_NOTICE
                raise exc
            else:
                excmsg = ("(MasterLoader) 'load', profile '"+str(profile)+"' "
                          "is not loaded but an other profile '" +
                          str(self.last_updated_profile[0])+"' is already "
                          "loaded")
                raise LoadException(excmsg)

        self._innerLoad("load",
                        "getLoadPriority",
                        parameter_container=parameter_container,
                        profile=profile,
                        next_state=STATE_LOADED,
                        next_state_if_error=STATE_LOADED_E)

    def unload(self, parameter_container=None, profile=None):
        if profile is None:
            profile = DEFAULT_PROFILE_NAME

        allowed_state = MasterLoader._unloadAllowedState
        if (self.last_updated_profile is None or
           self.last_updated_profile[0] != profile or
           self.last_updated_profile[1] not in allowed_state):
            excmsg = ("(MasterLoader) 'unload', profile '"+str(profile)+"' is"
                      " not loaded")
            raise UnloadException(excmsg)

        self._innerLoad("unload",
                        "getUnloadPriority",
                        parameter_container=parameter_container,
                        profile=profile,
                        next_state=STATE_UNLOADED,
                        next_state_if_error=STATE_UNLOADED_E)

    def saveCommands(self, section_name, command_list, addons_set=None):
        if (self.last_updated_profile is None or
           self.last_updated_profile[1] not in MasterLoader._loadAllowedState):
            excmsg = ("(MasterLoader) saveCommands, can not add commands to"
                      "save, no profile loaded")
            raise LoaderException(excmsg)

        profile = self.last_updated_profile[0]
        if profile not in self.profile_list:
            excmsg = ("(MasterLoader) saveCommands, the profile found is not"
                      " loaded.")
            raise LoaderException(excmsg)

        loaders = self.profile_list[profile]
        loader_name = getLoaderSignature(FileLoader)

        if loader_name not in loaders:
            file_loader = FileLoader(self)
            loaders[loader_name] = file_loader
        else:
            file_loader = loaders[loader_name]

        file_loader.saveCommands(section_name, command_list, addons_set)
