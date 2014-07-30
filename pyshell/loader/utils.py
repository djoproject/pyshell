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

def getAndInitCallerModule(callerLoaderKey, callerLoaderClassDefinition, moduleLevel = 2, subLoaderName = None):
    frm = inspect.stack()[moduleLevel]
    mod = inspect.getmodule(frm[0])

    #init loaders dictionnary
    loadersDict = None
    if hasattr(mod,"_loaders"):
        loadersDict = mod._loaders
    else:
        loadersDict = {}
        mod._loaders = loadersDict
    
    #the current loader already exists ?
    if callerLoaderKey not in loadersDict:
        loadersDict[callerLoaderKey] = {}

    #subloader already exist ?
    if subLoaderName in loadersDict[callerLoaderKey]:
        return loadersDict[callerLoaderKey][subLoaderName]

    loader = callerLoaderClassDefinition()
    loadersDict[callerLoaderKey][subLoaderName] = loader
    return loader

def _local_getAndInitCallerModule(subLoaderName = None)
    return getAndInitCallerModule(DefaultLoader.__module__+"."+DefaultLoader.__name__,DefaultLoader, 3, subLoaderName)

def registerDependOnAddon(name, subLoaderName = None):
    if type(name) != str and type(name) != unicode:
        raise LoadException("(Loader) registerDependOnAddon, only string or unicode addon name are allowed")

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.dep.append(name)

class AbstractLoader(object):
    def load(self, parameterManager):
        pass #TO OVERRIDE

    def unload(self, parameterManager):
        pass #TO OVERRIDE
        
    def reload(self, parameterManager):
        pass #TO OVERRIDE

class DefaultLoader(AbstractLoader):
    def __init__(self):
        AbstractLoader.__init__(self)
        self.dep = []
        
    def load(self, parameterManager):
        pass #TODO raise if a dependancies is not satisfied
    
        
