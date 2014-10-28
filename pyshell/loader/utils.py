#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject,net>

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
from pyshell.utils.constants  import DEFAULT_SUBADDON_NAME


def getAndInitCallerModule(callerLoaderKey, callerLoaderClassDefinition, moduleLevel = 2, subAddonName = None):
    frm = inspect.stack()[3]
    mod = inspect.getmodule(frm[0])

    #init loaders dictionnary
    loadersDict = None
    if hasattr(mod,"_loaders"):
        loadersDict = mod._loaders
        
        #must be an instance of GlobalLoader
        if not isinstance(loadersDict,GlobalLoader):
            raise RegisterException("(loader) getAndInitCallerModule, the stored loader in the module '"+str(mod)+"' is not an instance of GlobalLoader, get '"+str(type(loadersDict))+"'")
        
    else:
        loadersDict = GlobalLoader()
        mod._loaders = loadersDict
        
    return mod._loaders.getLoader(callerLoaderKey, callerLoaderClassDefinition, subAddonName)

class AbstractLoader(object):
    def __init__(self):
        self.lastException = None

    def load(self, parameterManager, subAddonName = None):
        pass #TO OVERRIDE

    def unload(self, parameterManager, subAddonName = None):
        pass #TO OVERRIDE
        
    def reload(self, parameterManager, subAddonName = None):
        self.unload(parameterManager, subAddonName)
        self.load(parameterManager, subAddonName)
        
        #can be overrided too

class GlobalLoaderLoadingState(object):
    STATE_REGISTERED = "REGISTERED BUT NOT LOADED" 
    STATE_LOADED     = "LOADED"
    STATE_LOADED_E   = "LOADED WITH ERROR"
    STATE_UNLOADED   = "UNLOADED"
    STATE_UNLOADED_E = "UNLOADED WITH ERROR"
    STATE_RELOADED   = "RELOADED" 
    STATE_RELOADED_E = "RELOADED WITH ERROR" 

    def __init__(self):
        self.state = GlobalLoaderLoadingState.STATE_REGISTERED

class GlobalLoader(AbstractLoader):
    def __init__(self):
        AbstractLoader.__init__(self)
        self.subAddons = {}
        
    def getSubAddonsAvailable(self):
        return self.subAddons.keys()

    def getLoaderDictionary(self, subAddonName = None):
        if subAddonName is None:
            subAddonName = DEFAULT_SUBADDON_NAME
    
        if subAddonName not in self.subAddons:
            raise Exception("(GlobalLoader) getLoaderDictionary, sub addon '"+str(subAddonName)+"' does not exist")

        return self.subAddons[subAddonName]

    def getLoader(self, loaderName, classDefinition, subAddonName = None):        
        try:
            if not issubclass(classDefinition, AbstractLoader):
                raise RegisterException("(GlobalLoader) getLoader, try to create a loader with an unallowed class loader definition, must be a class definition inheriting from AbstractLoader")
        
        except TypeError:
                raise RegisterException("(GlobalLoader) getLoader, try to create a loader with an invalid class definition, must be a class definition inheriting from AbstractLoader")
        
        if subAddonName is None:
            subAddonName = DEFAULT_SUBADDON_NAME
        
        if subAddonName not in self.subAddons:
            self.subAddons[subAddonName] = ({},GlobalLoaderLoadingState(),) 
            
        if loaderName not in self.subAddons[subAddonName][0]:
            self.subAddons[subAddonName][0][loaderName] = classDefinition() 
            
        return self.subAddons[subAddonName][0][loaderName]
    

    def _innerLoad(self,methodName, parameterManager, subAddonName, allowedState, invalidStateMessage, nextState,nextStateIfError):
        exceptions = ListOfException()

        if subAddonName is None:
            subAddonName = DEFAULT_SUBADDON_NAME

        #nothing to do for this subAddons
        if subAddonName not in self.subAddons: 
            return

        currentState = self.subAddons[subAddonName][1]
        if currentState.state not in allowedState:
            raise LoadException("(GlobalLoader) '"+methodName+"', sub loader '"+str(subAddonName)+"' "+invalidStateMessage)

        for loaderName, loader in self.subAddons[subAddonName][0].items():
            meth_toCall = getattr(loader, methodName)

            try:
                meth_toCall(parameterManager,subAddonName)
                loader.lastException = None
            except Exception as ex:
                loader.lastException = ex
                exceptions.addException(ex)
                loader.lastException.stackTrace = traceback.format_exc()
    
        if exceptions.isThrowable():
            currentState.state = nextStateIfError
            raise exceptions
        else:
            currentState.state = nextState

    def load(self, parameterManager, subAddonName = None):
        allowedState = [GlobalLoaderLoadingState.STATE_REGISTERED, 
                        GlobalLoaderLoadingState.STATE_UNLOADED, 
                        GlobalLoaderLoadingState.STATE_UNLOADED_E]

        self._innerLoad("load", parameterManager, subAddonName, allowedState, "is already loaded",GlobalLoaderLoadingState.STATE_LOADED,GlobalLoaderLoadingState.STATE_LOADED_E)

    def unload(self, parameterManager, subAddonName = None):
        allowedState = [GlobalLoaderLoadingState.STATE_LOADED, 
                        GlobalLoaderLoadingState.STATE_LOADED_E, 
                        GlobalLoaderLoadingState.STATE_RELOADED, 
                        GlobalLoaderLoadingState.STATE_RELOADED_E]

        self._innerLoad("unload", parameterManager, subAddonName, allowedState, "is not loaded",GlobalLoaderLoadingState.STATE_UNLOADED,GlobalLoaderLoadingState.STATE_UNLOADED_E)

    def reload(self, parameterManager, subAddonName = None):
        allowedState = [GlobalLoaderLoadingState.STATE_LOADED, 
                        GlobalLoaderLoadingState.STATE_LOADED_E, 
                        GlobalLoaderLoadingState.STATE_RELOADED, 
                        GlobalLoaderLoadingState.STATE_RELOADED_E]
                        
        self._innerLoad("reload", parameterManager, subAddonName, allowedState, "is not loaded",GlobalLoaderLoadingState.STATE_RELOADED,GlobalLoaderLoadingState.STATE_RELOADED_E)


    
        
