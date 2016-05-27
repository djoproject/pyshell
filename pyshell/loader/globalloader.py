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
from pyshell.loader.exception import RegisterException
from pyshell.utils.constants import DEFAULT_PROFILE_NAME
from pyshell.utils.constants import STATE_LOADED
from pyshell.utils.constants import STATE_LOADED_E
from pyshell.utils.constants import STATE_UNLOADED
from pyshell.utils.constants import STATE_UNLOADED_E
from pyshell.utils.exception import ListOfException

class GlobalLoader(AbstractLoader):
    def __init__(self):
        AbstractLoader.__init__(self)
        self.profile_list = {}
        self.last_updated_profile = None

    def getOrCreateLoader(self, loader_name, class_definition, profile=None):
        if profile is None:
            profile = DEFAULT_PROFILE_NAME

        if (profile in self.profile_list and
           loader_name in self.profile_list[profile]):
            return self.profile_list[profile][loader_name]

        # the loader does not exist, need to create it
        try:
            # need a child class of AbstractLoader
            if (not issubclass(class_definition, AbstractLoader) or
               class_definition.__name__ == "AbstractLoader"):
                excmsg = ("(GlobalLoader) getOrCreateLoader, try to create a "
                          "loader with an unallowed class '" +
                          str(class_definition)+"', must be a class definition"
                          " inheriting from AbstractLoader")
                raise RegisterException(excmsg)

        # raise by issubclass if one of the two argument
        # is not a class definition
        except TypeError:
            excmsg = ("(GlobalLoader) getOrCreateLoader, expected a class "
                      "definition, got '"+str(class_definition)+"', must be a"
                      " class definition inheriting from AbstractLoader")
            raise RegisterException(excmsg)

        if profile not in self.profile_list:
            self.profile_list[profile] = {}

        loader = class_definition()
        self.profile_list[profile][loader_name] = loader

        return loader

    def _innerLoad(self,
                   method_name,
                   parameter_manager,
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
            heapq.heappush(loaders_heap, (loader.getPriority(),
                                          insert_order,
                                          loader,))
            insert_order += 1

        while len(loaders_heap) > 0:
            priority, insert_order, loader = heapq.heappop(loaders_heap)
            # no need to test if attribute exist, it is supposed to call
            # load/unload or reload and loader is suppose to be an
            # AbstractLoader
            meth_to_call = getattr(loader, method_name)

            try:
                meth_to_call(parameter_manager, profile)
                loader.last_exception = None
            except Exception as ex:
                # TODO is it used somewhere ? will be overwrite on reload if
                # error on unload and on load
                loader.last_exception = ex
                exceptions.addException(ex)
                loader.last_exception.stackTrace = traceback.format_exc()

        if exceptions.isThrowable():
            self.last_updated_profile = (profile, next_state_if_error,)
            raise exceptions

        self.last_updated_profile = (profile, next_state,)

    _loadAllowedState = (STATE_UNLOADED, STATE_UNLOADED_E,)
    _unloadAllowedState = (STATE_LOADED, STATE_LOADED_E,)

    def load(self, parameter_manager, profile=None):
        if profile is None:
            profile = DEFAULT_PROFILE_NAME

        if (self.last_updated_profile is not None and
           self.last_updated_profile[1] not in GlobalLoader._loadAllowedState):
            if profile == self.last_updated_profile[0]:
                # TODO should we raise an exception if already loaded ?
                # excmsg = ("(GlobalLoader) 'load', profile '"+str(profile) +
                #           "' is already loaded")
                # raise LoadException(excmsg)
                return
            else:
                excmsg = ("(GlobalLoader) 'load', profile '"+str(profile)+"' "
                          "is not loaded but an other profile '" +
                          str(self.last_updated_profile[0])+"' is already "
                          "loaded")
                raise LoadException(excmsg)

        self._innerLoad("load",
                        parameter_manager=parameter_manager,
                        profile=profile,
                        next_state=STATE_LOADED,
                        next_state_if_error=STATE_LOADED_E)

    def unload(self, parameter_manager, profile=None):
        if profile is None:
            profile = DEFAULT_PROFILE_NAME

        allowed_state = GlobalLoader._unloadAllowedState
        if (self.last_updated_profile is None or
           self.last_updated_profile[0] != profile or
           self.last_updated_profile[1] not in allowed_state):
            excmsg = ("(GlobalLoader) 'unload', profile '"+str(profile)+"' is"
                      " not loaded")
            raise LoadException(excmsg)

        self._innerLoad("unload",
                        parameter_manager=parameter_manager,
                        profile=profile,
                        next_state=STATE_UNLOADED,
                        next_state_if_error=STATE_UNLOADED_E)

    def reload(self, parameter_manager, profile=None):
        if profile is None:
            profile = DEFAULT_PROFILE_NAME

        allowed_state = GlobalLoader._unloadAllowedState
        if (self.last_updated_profile is None or
           self.last_updated_profile[0] != profile or
           self.last_updated_profile[1] not in allowed_state):
            excmsg = ("(GlobalLoader) 'reload', profile '"+str(profile)+"' is"
                      " not loaded")
            raise LoadException(excmsg)

        self._innerLoad("reload",
                        parameter_manager=parameter_manager,
                        profile=profile,
                        next_state=STATE_LOADED,
                        next_state_if_error=STATE_LOADED_E)
