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

import inspect
from pyshell.loader.exception import RegisterException,LoadException
from pyshell.utils.exception  import ListOfException, AbstractListableException

#TODO replace None by Default in the exception message for default sub addon

def getAndInitCallerModule(callerLoaderKey, callerLoaderClassDefinition, moduleLevel = 2, subLoaderName = None):
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
        
    return mod._loaders.getLoader(callerLoaderKey, callerLoaderClassDefinition, subLoaderName)

class AbstractLoader(object):
    def __init__(self):
        pass

    def load(self, parameterManager, subLoaderName = None):
        pass #TO OVERRIDE

    def unload(self, parameterManager, subLoaderName = None):
        pass #TO OVERRIDE
        
    def reload(self, parameterManager, subLoaderName = None):
        self.unload(parameterManager, subLoaderName)
        self.load(parameterManager, subLoaderName)
        
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
        self.state         = GlobalLoaderLoadingState.STATE_REGISTERED
        self.lastException = None

class GlobalLoader(AbstractLoader):
    def __init__(self):
        AbstractLoader.__init__(self)
        self.subloader = {}
        
    def getSubLoaderAvailable(self):
        return self.subloader.keys()

    def getLoaderDictionary(self, subLoaderName = None):
        if subLoaderName not in self.subloader:
            raise Exception("(GlobalLoader) getLoaderDictionary, sub loader '"+str(subLoaderName)+"' does not exist")

        return self.subloader[subLoaderName]

    def getLoader(self, loaderName, classDefinition, subLoaderName = None):
        if subLoaderName not in self.subloader:
            self.subloader[subLoaderName] = ({},GlobalLoaderLoadingState(),) 
            
        if loaderName not in self.subloader[subLoaderName][0]:
            self.subloader[subLoaderName][0][loaderName] = classDefinition() 
            
        return self.subloader[subLoaderName][0][loaderName]
    

    def _innerLoad(self,methodName, parameterManager, subLoaderName, allowedState, invalidStateMessage, nextState,nextStateIfError):
        exception = ListOfException()

        #nothing to do for this subloader
        if subLoaderName not in self.subloader: 
            return

        currentState = self.subloader[subLoaderName][1]
        if currentState.state not in allowedState:
            raise LoadException("(GlobalLoader) methodName, sub loader '"+str(subLoaderName)+"' "+invalidStateMessage)

        for loaderName, loader in self.subloader[subLoaderName][0].items():
            meth_toCall = getattr(loader, methodName)

            try:
                meth_toCall(parameterManager,subLoaderName)
            except AbstractListableException as ale:
                exception.addException(ale)
            except Exception as ex:
                exception = ex
    
        if not isinstance(exception,AbstractListableException) or exception.isThrowable():
            currentState.state = nextStateIfError
            currentState.lastException = exception
            raise exception
        else:
            currentState.state = nextState
            currentState.lastException = None

    def load(self, parameterManager, subLoaderName = None):
        allowedState = [GlobalLoaderLoadingState.STATE_REGISTERED, 
                        GlobalLoaderLoadingState.STATE_UNLOADED, 
                        GlobalLoaderLoadingState.STATE_UNLOADED_E]

        self._innerLoad("load", parameterManager, subLoaderName, allowedState, "is already loaded",GlobalLoaderLoadingState.STATE_LOADED,GlobalLoaderLoadingState.STATE_LOADED_E)

    def unload(self, parameterManager, subLoaderName = None):
        allowedState = [GlobalLoaderLoadingState.STATE_LOADED, 
                        GlobalLoaderLoadingState.STATE_LOADED_E, 
                        GlobalLoaderLoadingState.STATE_RELOADED, 
                        GlobalLoaderLoadingState.STATE_RELOADED_E]

        self._innerLoad("unload", parameterManager, subLoaderName, allowedState, "is not loaded",GlobalLoaderLoadingState.STATE_UNLOADED,GlobalLoaderLoadingState.STATE_UNLOADED_E)

    def reload(self, parameterManager, subLoaderName = None):
        allowedState = [GlobalLoaderLoadingState.STATE_LOADED, 
                        GlobalLoaderLoadingState.STATE_LOADED_E, 
                        GlobalLoaderLoadingState.STATE_RELOADED, 
                        GlobalLoaderLoadingState.STATE_RELOADED_E]
                        
        self._innerLoad("reload", parameterManager, subLoaderName, allowedState, "is not loaded",GlobalLoaderLoadingState.STATE_RELOADED,GlobalLoaderLoadingState.STATE_RELOADED_E)


    
        
