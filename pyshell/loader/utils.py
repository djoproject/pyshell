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
#   prevoir un system simple pour permettre au loader d'indiquer si
#   des elements doivent etre sauver et un system pour les sauver

#   pour l'instant: procedure, environment, contexte, variable

#   each item can hold three hash:
#       hash_file: computed at file loading (set to None if item is
#                                            not updated)
#       hash_default (static): computed at registering, always the same from
#       an execution to another
#       current_hash: not computed but could be computed at any time

#   if hash_file is None and current_hash == hash_default => not a candidate to
#                                                            be saved
#   if hash_file is not None
#       if current_hash == hash_file => candidate to be save + does not
#                                       trigger file regeneration
#       if current_hash == hash_default => need to be remove of the file +
#                                          trigger file regeneration
#       else => need to be saved + trigger file regeneration

import inspect
import traceback
from pyshell.loader.exception import RegisterException, LoadException
from pyshell.utils.exception import ListOfException
from pyshell.utils.constants import DEFAULT_PROFILE_NAME, STATE_LOADED, \
                                    STATE_LOADED_E, STATE_UNLOADED, \
                                    STATE_UNLOADED_E


def getAndInitCallerModule(callerLoaderKey,
                           callerLoaderClassDefinition,
                           profile=None,
                           moduleLevel=3):
    frm = inspect.stack()[moduleLevel]
    mod = inspect.getmodule(frm[0])

    if hasattr(mod, "_loaders"):
        # must be an instance of GlobalLoader
        if not isinstance(mod._loaders, GlobalLoader):
            raise RegisterException("(loader) getAndInitCallerModule, the "
                                    "stored loader in the module '"+str(mod) +
                                    "' is not an instance of GlobalLoader, get"
                                    " '"+str(type(mod._loaders))+"'")
    else:
        setattr(mod, "_loaders", GlobalLoader())  # init loaders dictionnary

    return mod._loaders.getOrCreateLoader(callerLoaderKey,
                                          callerLoaderClassDefinition,
                                          profile)


class AbstractLoader(object):
    def __init__(self):
        self.lastException = None

    def load(self, parameterManager, profile=None):
        pass  # TO OVERRIDE

    def unload(self, parameterManager, profile=None):
        pass  # TO OVERRIDE

    def reload(self, parameterManager, profile=None):
        self.unload(parameterManager, profile)
        self.load(parameterManager, profile)
        # CAN BE OVERRIDEN TOO


class GlobalLoader(AbstractLoader):
    def __init__(self):
        AbstractLoader.__init__(self)
        self.profileList = {}
        self.lastUpdatedProfile = None

    def getOrCreateLoader(self, loaderName, classDefinition, profile=None):
        if profile is None:
            profile = DEFAULT_PROFILE_NAME

        if profile in self.profileList and \
           loaderName in self.profileList[profile]:
            return self.profileList[profile][loaderName]

        # the loader does not exist, need to create it
        try:
            # need a child class of AbstractLoader
            if not issubclass(classDefinition, AbstractLoader) or \
               classDefinition.__name__ == "AbstractLoader":
                raise RegisterException("(GlobalLoader) getOrCreateLoader, try"
                                        " to create a loader with an unallowed"
                                        " class '"+str(classDefinition) +
                                        "', must be a class definition "
                                        "inheriting from AbstractLoader")

        # raise by issubclass if one of the two argument
        # is not a class definition
        except TypeError:
            raise RegisterException("(GlobalLoader) getOrCreateLoader, "
                                    "expected a class definition, got '" +
                                    str(classDefinition)+"', must be a class "
                                    "definition inheriting from "
                                    "AbstractLoader")

        if profile not in self.profileList:
            self.profileList[profile] = {}

        loader = classDefinition()
        self.profileList[profile][loaderName] = loader

        return loader

    def _innerLoad(self,
                   methodName,
                   parameterManager,
                   profile,
                   nextState,
                   nextStateIfError):
        exceptions = ListOfException()

        # no loader available for this profile
        if profile not in self.profileList:
            return

        loaders = self.profileList[profile]

        for loaderName, loader in loaders.items():
            # no need to test if attribute exist, it is supposed to call
            # load/unload or reload and loader is suppose to be an
            # AbstractLoader
            meth_toCall = getattr(loader, methodName)

            try:
                meth_toCall(parameterManager, profile)
                loader.lastException = None
            except Exception as ex:
                # TODO is it used somewhere ? will be overwrite on reload if
                # error on unload and on load
                loader.lastException = ex
                exceptions.addException(ex)
                loader.lastException.stackTrace = traceback.format_exc()

        if exceptions.isThrowable():
            self.lastUpdatedProfile = (profile, nextStateIfError,)
            raise exceptions

        self.lastUpdatedProfile = (profile, nextState,)

    _loadAllowedState = (STATE_UNLOADED, STATE_UNLOADED_E,)
    _unloadAllowedState = (STATE_LOADED, STATE_LOADED_E,)

    def load(self, parameterManager, profile=None):
        if profile is None:
            profile = DEFAULT_PROFILE_NAME

        if self.lastUpdatedProfile is not None and \
           self.lastUpdatedProfile[1] not in GlobalLoader._loadAllowedState:
            if profile == self.lastUpdatedProfile[0]:
                raise LoadException("(GlobalLoader) 'load', profile '" +
                                    str(profile)+"' is already loaded")
            else:
                raise LoadException("(GlobalLoader) 'load', profile '" +
                                    str(profile)+"' is not loaded but an other"
                                    " profile '" +
                                    str(self.lastUpdatedProfile[0]) +
                                    "' is already loaded")

        self._innerLoad("load",
                        parameterManager=parameterManager,
                        profile=profile,
                        nextState=STATE_LOADED,
                        nextStateIfError=STATE_LOADED_E)

    def unload(self, parameterManager, profile=None):
        if profile is None:
            profile = DEFAULT_PROFILE_NAME

        if self.lastUpdatedProfile is None or \
           self.lastUpdatedProfile[0] != profile or \
           self.lastUpdatedProfile[1] not in GlobalLoader._unloadAllowedState:
            raise LoadException("(GlobalLoader) 'unload', profile '" +
                                str(profile)+"' is not loaded")

        self._innerLoad("unload",
                        parameterManager=parameterManager,
                        profile=profile,
                        nextState=STATE_UNLOADED,
                        nextStateIfError=STATE_UNLOADED_E)

    def reload(self, parameterManager, profile=None):
        if profile is None:
            profile = DEFAULT_PROFILE_NAME

        if self.lastUpdatedProfile is None or \
           self.lastUpdatedProfile[0] != profile or \
           self.lastUpdatedProfile[1] not in GlobalLoader._unloadAllowedState:
            raise LoadException("(GlobalLoader) 'reload', profile '" +
                                str(profile)+"' is not loaded")

        self._innerLoad("reload",
                        parameterManager=parameterManager,
                        profile=profile,
                        nextState=STATE_LOADED,
                        nextStateIfError=STATE_LOADED_E)

