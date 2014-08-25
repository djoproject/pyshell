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
        self.state         = GlobalLoaderLoadingState.STATE_REGISTERED

class GlobalLoader(AbstractLoader):
    def __init__(self):
        AbstractLoader.__init__(self)
        self.subAddons = {}
        
    def getSubLoaderAvailable(self): #TODO change name
        return self.subAddons.keys()

    def getLoaderDictionary(self, subAddonName = None):
        if subAddonName not in self.subAddons:
            raise Exception("(GlobalLoader) getLoaderDictionary, sub addon '"+str(subAddonName)+"' does not exist")

        return self.subAddons[subAddonName]

    def getLoader(self, loaderName, classDefinition, subAddonName = None):
        #TODO classDefinition had to be a definition of AbstractLoader
            #equal does not work, and is not an instance, so instanceof will not work too...

        #if classDefinition != AbstractLoader:
        #    raise RegisterException("(GlobalLoader) getLoader, class definition provided is not a valid definition of AbstractLoader, got '"+str(classDefinition)+"'")

        if subAddonName not in self.subAddons:
            self.subAddons[subAddonName] = ({},GlobalLoaderLoadingState(),) 
            
        if loaderName not in self.subAddons[subAddonName][0]:
            self.subAddons[subAddonName][0][loaderName] = classDefinition() 
            
        return self.subAddons[subAddonName][0][loaderName]
    

    def _innerLoad(self,methodName, parameterManager, subAddonName, allowedState, invalidStateMessage, nextState,nextStateIfError):
        exception = ListOfException()

        #nothing to do for this subAddons
        if subAddonName not in self.subAddons: 
            return

        currentState = self.subAddons[subAddonName][1]
        if currentState.state not in allowedState:
            raise LoadException("(GlobalLoader) methodName, sub loader '"+str(subAddonName)+"' "+invalidStateMessage)

        for loaderName, loader in self.subAddons[subAddonName][0].items():
            meth_toCall = getattr(loader, methodName)

            try:
                meth_toCall(parameterManager,subAddonName)
                loader.lastException = None
            except AbstractListableException as ale:
                exception.addException(ale)
                loader.lastException = ale
            except Exception as ex:
                exception = ex
                loader.lastException = ex

        #TODO prblm
            #Exception as ex must raise immediately
            #but loop over each addon before to raise
            #so other Exception can occur and overwrite the last one

            #solution:
                #raise immediately and stop loading of the others addons
                #add the exception in the list of exception

            #but have to raise something at the end of loading
                #because serious error occured, so we can't show "xxx loaed !!!"
    
        if not isinstance(exception,AbstractListableException) or exception.isThrowable():
            currentState.state = nextStateIfError
            raise exception
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


    
        
