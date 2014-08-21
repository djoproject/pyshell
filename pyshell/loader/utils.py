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
from pyshell.loader.exception import RegisterException
from pyshell.utils.exception  import ListOfException, AbstractListableException

#TODO catch and manage ListOfLoadException somewhere
    #in executer
    #in addon addon
    #... (don't think there is other place)

def getAndInitCallerModule(callerLoaderKey, callerLoaderClassDefinition, moduleLevel = 2, subLoaderName = None):
    frm = inspect.stack()[3]
    mod = inspect.getmodule(frm[0])

    #print inspect.stack()[3]

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
    STATE_NONE     = "NOT LOADED" 
    STATE_LOADED   = "LOADED"
    STATE_UNLOADED = "UNLOADED"
    STATE_RELOADED = "RELOADED"    

    def __init__(self):
        self.isLoaded    = None #TODO boolean is not enought, because 4 state (no state, loaded, unloaded, reloaded)
        self.noticeList  = []
        self.warningList = []
        self.errorList   = []

    def isLoaded(self):
        return self.isLoaded is not None and self.isLoaded
        
    def isUnloaded(self):
        return self.isLoaded is not None and not self.isLoaded
        
    def setLoaded(self,state):
        self.isLoaded = state

    def load(self, parameterManager, subLoaderName = None):
        pass #TO OVERRIDE

    def unload(self, parameterManager, subLoaderName = None):
        pass #TO OVERRIDE
        
    def reload(self, parameterManager, subLoaderName = None):
        self.unload(parameterManager, subLoaderName)
        self.load(parameterManager, subLoaderName)
        
        #could overrided

#brainstorming
    #what
        #we need to know which module.submodule has been loaded or not
        #a place to store the erreur/warning/notice/... generated during the module load/unloading process

    #fact
        #a module only know the name of submodule to load
        #a module does not know its own name
        #an error/exception can occur during loading process
    
    #prblm
        #where to store the information "module.submodule loaded or not" ?
        #where to store erreur/warning/notice information ?
            #in parent module
                #prblm
                    #not the best place to store these information
                    #information must be linked to module loader, not parent
                    #imply to update current structure
                
                #good point
                    #catch easyli state and information
                    #no need of update from user in source code
                                
            #in module
                #prblm
                    #need to call parent unload/load method when it is overriden
                    #need to store itself the erreur/warning/notice information in structure
                    #an unexpected error can occur in loading process and prevent the registration of any information
                    #some user could create loader and forget to register information
                    #imply to update current structure
                
                #good point
                    #it is the most logical point where to store these informations
                
            #outside
                #prblm
                    #a structure already exist where we can store the information, it is ridiculous to build a equivalent structure just near the existing one
            
            #BEST SOLUTION
                #grab the information in parent module
                #but store the informations in module
            
        #when to considere a module is loaded ?
            #once the method is called
                #best solution because even if there is some error, we can't block the unload
                #if some elements had been loaded
                #BEST SOLUTION
            
            #once the method is called and there is no error
                #prblm
                    #some elements had maybe been loaded
            
            #...
            
class GlobalLoader(AbstractLoader):
    def __init__(self):
        AbstractLoader.__init__(self)
        self.subloader = {}
        
    def getLoaderNameList(self):
        return self.subloader.keys()

    def getSubLoaderDictionnary(self, loaderName):
        if loaderName not in self.subloader:
            raise Exception("(GlobalLoader) getSubLoaderDictionnary, unknown loader name '"+str(loaderName)+"'")
            
        return self.subloader[loaderName]
        
    def getLoader(self, loaderName, classDefinition, subLoaderName = None):
        if loaderName not in self.subloader:
            self.subloader[loaderName] = {}
            
        if subLoaderName not in self.subloader[loaderName]:
            self.subloader[loaderName][subLoaderName] = classDefinition()
            
        return self.subloader[loaderName][subLoaderName]
        
    def load(self, parameterManager, subLoaderName = None):
        exception = ListOfException()
    
        for loaderName, subLoaderDic in self.subloader.items():
            if subLoaderName in subLoaderDic:
                #TODO manage load state
            
                try:
                    subLoaderDic[subLoaderName].load(parameterManager)
                except AbstractListableException as ale:
                    exception.addException(ale)
                    
                #TODO register informations
                    
        if exception.isThrowable():
            raise exception

    def unload(self, parameterManager, subLoaderName = None):
        exception = ListOfException()
    
        for loaderName, subLoaderDic in self.subloader.items():
            if subLoaderName in subLoaderDic:
                #TODO manage load state
            
                try:
                    subLoaderDic[subLoaderName].unload(parameterManager)
                except AbstractListableException as ale:
                    exception.addException(ale)
        
                #TODO register informations
        
        if exception.isThrowable():
            raise exception
        
    def reload(self, parameterManager, subLoaderName = None):
        exception = ListOfException()
    
        for loaderName, subLoaderDic in self.subloader.items():
            if subLoaderName in subLoaderDic:
                #TODO manage load state
            
                try:
                    subLoaderDic[subLoaderName].reload(parameterManager)
                except AbstractListableException as ale:
                    exception.addException(ale)
                    
                #TODO register informations

        if exception.isThrowable():
            raise exception

    
        
