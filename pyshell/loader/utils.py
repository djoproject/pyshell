#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import inspect,traceback
from pyshell.loader.exception import RegisterException,LoadException
from pyshell.utils.exception  import ListOfException
from pyshell.utils.constants  import DEFAULT_PROFILE_NAME, STATE_REGISTERED, STATE_LOADED, STATE_LOADED_E, STATE_UNLOADED, STATE_UNLOADED_E, STATE_RELOADED, STATE_RELOADED_E


def getAndInitCallerModule(callerLoaderKey, callerLoaderClassDefinition, profile = None, moduleLevel = 3):
    frm = inspect.stack()[moduleLevel]
    mod = inspect.getmodule(frm[0])

    if hasattr(mod,"_loaders"):        
        if not isinstance(mod._loaders,GlobalLoader): #must be an instance of GlobalLoader
            raise RegisterException("(loader) getAndInitCallerModule, the stored loader in the module '"+str(mod)+"' is not an instance of GlobalLoader, get '"+str(type(mod._loaders))+"'")
    else:
        setattr(mod, "_loaders", GlobalLoader()) #init loaders dictionnary
        
    return mod._loaders.getOrCreateLoader(callerLoaderKey, callerLoaderClassDefinition, profile)

class AbstractLoader(object):
    def __init__(self):
        self.lastException = None

    def load(self, parameterManager, profile = None):
        pass #TO OVERRIDE

    def unload(self, parameterManager, profile = None):
        pass #TO OVERRIDE
        
    def reload(self, parameterManager, profile = None):
        self.unload(parameterManager, profile)
        self.load(parameterManager, profile)
        #CAN BE OVERRIDEN TOO

class GlobalLoader(AbstractLoader):
    def __init__(self):
        AbstractLoader.__init__(self)
        self.profileList = {}

    def getOrCreateLoader(self, loaderName, classDefinition, profile = None): 
        if profile is None:
            profile = DEFAULT_PROFILE_NAME

        if profile in self.profileList and loaderName in self.profileList[profile][0]:
            return self.profileList[profile][0][loaderName]

        #the loader does not exist, need to create it
        try:
            if not issubclass(classDefinition, AbstractLoader) or classDefinition.__name__ == "AbstractLoader": #need a child class of AbstractLoader
                raise RegisterException("(GlobalLoader) getOrCreateLoader, try to create a loader with an unallowed class '"+str(classDefinition)+"', must be a class definition inheriting from AbstractLoader")
        except TypeError: #raise by issubclass if one of the two argument is not a class definition
            raise RegisterException("(GlobalLoader) getOrCreateLoader, expected a class definition, got '"+str(classDefinition)+"', must be a class definition inheriting from AbstractLoader")
        
        if profile not in self.profileList:
            self.profileList[profile] = ({},STATE_REGISTERED,)
            
        loader = classDefinition() 
        self.profileList[profile][0][loaderName] = loader

        return loader
            
    def _innerLoad(self,methodName, parameterManager, profile, allowedState, invalidStateMessage, nextState,nextStateIfError):
        exceptions = ListOfException()

        if profile is None:
            profile = DEFAULT_PROFILE_NAME

        #no loader available for this profile
        if profile not in self.profileList: 
            return

        loaders, state = self.profileList[profile]
        if state not in allowedState:
            raise LoadException("(GlobalLoader) '"+methodName+"', profile '"+str(profile)+"' "+invalidStateMessage) 

        for loaderName, loader in loaders.items():
            meth_toCall = getattr(loader, methodName) #no need to test if attribute exist, it is supposed to call load/unload or reload and loader is suppose to be an AbstractLoader

            try:
                meth_toCall(parameterManager,profile)
                loader.lastException = None
            except Exception as ex:
                loader.lastException = ex
                exceptions.addException(ex)
                loader.lastException.stackTrace = traceback.format_exc()
        
        if exceptions.isThrowable():
            self.profileList[profile] = (loaders, nextStateIfError, )
            raise exceptions
        
        self.profileList[profile] = (loaders, nextState, )

    _loadAllowedState   = (STATE_REGISTERED, STATE_UNLOADED, STATE_UNLOADED_E,)
    _unloadAllowedState = (STATE_LOADED, STATE_LOADED_E, STATE_RELOADED, STATE_RELOADED_E,)

    def load(self, parameterManager, profile=None):
        self._innerLoad("load",   parameterManager=parameterManager, profile=profile, allowedState=GlobalLoader._loadAllowedState,   invalidStateMessage="is already loaded",nextState=STATE_LOADED,  nextStateIfError=STATE_LOADED_E)

    def unload(self, parameterManager, profile=None):
        self._innerLoad("unload", parameterManager=parameterManager, profile=profile, allowedState=GlobalLoader._unloadAllowedState, invalidStateMessage="is not loaded",    nextState=STATE_UNLOADED,nextStateIfError=STATE_UNLOADED_E)

    def reload(self, parameterManager, profile=None):
        self._innerLoad("reload", parameterManager=parameterManager, profile=profile, allowedState=GlobalLoader._unloadAllowedState, invalidStateMessage="is not loaded",    nextState=STATE_RELOADED,nextStateIfError=STATE_RELOADED_E)
