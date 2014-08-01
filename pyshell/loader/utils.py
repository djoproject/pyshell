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
from exceptions import RegisterException, ListOfLoadException

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
            raise RegisterException("(loader) getAndInitCallerModule, the stored loader in the module <"+str(mod)+"> is not an instance of GlobalLoader, get <"+str(type(loadersDict))+">")
        
    else:
        loadersDict = GlobalLoader()
        mod._loaders = loadersDict
        
    return mod._loaders.getLoader(callerLoaderKey, callerLoaderClassDefinition, subLoaderName)

class AbstractLoader(object):
    def load(self, parameterManager, subLoaderName = None):
        pass #TO OVERRIDE

    def unload(self, parameterManager, subLoaderName = None):
        pass #TO OVERRIDE
        
    def reload(self, parameterManager, subLoaderName = None):
        self.unload(parameterManager, subLoaderName)
        self.load(parameterManager, subLoaderName)

class GlobalLoader(AbstractLoader):
    def __init__(self):
        AbstractLoader.__init__(self)
        self.subloader = {}
        
    def getLoader(self, loaderName, classDefinition, subLoaderName = None):
        if loaderName not in self.subloader:
            self.subloader[loaderName] = {}
            
        if subLoaderName not in self.subloader[loaderName]:
            self.subloader[loaderName][subLoaderName] = classDefinition()
            
        return self.subloader[loaderName][subLoaderName]
        
    def load(self, parameterManager, subLoaderName = None):
        exception = ListOfLoadException()
    
        for loaderName, subLoaderDic in self.subloader.items():
            if subLoaderName in subLoaderDic:
                try:
                    subLoaderDic[subLoaderName].load(parameterManager)
                except LoadException as le:
                    exception.addException(le)
                except ListOfLoadException as lle:
                    exception.addException(lle)
                    
        if exception.isThrowable():
            raise exception

    def unload(self, parameterManager, subLoaderName = None):
        exception = ListOfLoadException()
    
        for loaderName, subLoaderDic in self.subloader.items():
            if subLoaderName in subLoaderDic:
                try:
                    subLoaderDic[subLoaderName].unload(parameterManager)
                except LoadException as le:
                    exception.addException(le)
                except ListOfLoadException as lle:
                    exception.addException(lle)
        
        if exception.isThrowable():
            raise exception
        
    def reload(self, parameterManager, subLoaderName = None):
        exception = ListOfLoadException()
    
        for loaderName, subLoaderDic in self.subloader.items():
            if subLoaderName in subLoaderDic:
                try:
                    subLoaderDic[subLoaderName].reload(parameterManager)
                except LoadException as le:
                    exception.addException(le)
                except ListOfLoadException as lle:
                    exception.addException(lle)

        if exception.isThrowable():
            raise exception

    
        
