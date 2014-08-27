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

from pyshell.loader.utils     import getAndInitCallerModule, AbstractLoader
from pyshell.loader.exception import RegisterException, LoadException
from pyshell.utils.constants  import ENVIRONMENT_NAME, ADDONLIST_KEY, DEFAULT_SUBADDON_NAME

def _local_getAndInitCallerModule(subLoaderName = None):
    return getAndInitCallerModule(DependanciesLoader.__module__+"."+DependanciesLoader.__name__,DependanciesLoader, 3, subLoaderName)
    
def registerDependOnAddon(name, subName = None, subLoaderName = None):
    if type(name) != str and type(name) != unicode:
        raise RegisterException("(Loader) registerDependOnAddon, only string or unicode addon name are allowed")

    if subName != None and (type(subName) != str and type(subName) != unicode):
        raise RegisterException("(Loader) registerDependOnAddon, only string or unicode addon subName are allowed")

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.dep.append( (name,subName,) )
    
class DependanciesLoader(AbstractLoader):
    def __init__(self):
        AbstractLoader.__init__(self)
        self.dep = []
        
    def load(self, parameterManager, subLoaderName = None):
        AbstractLoader.load(self, parameterManager, subLoaderName)
        
        if len(self.dep) == 0:
            return
        
        if not parameterManager.hasParameter(ADDONLIST_KEY, ENVIRONMENT_NAME):
            raise LoadException("(DependanciesLoader) load, no addon list defined")
        
        addon_dico = parameterManager.getParameter(ADDONLIST_KEY, ENVIRONMENT_NAME).getValue()
        
        for (name, subname) in self.dep:
            if name not in addon_dico:
                raise LoadException("(DependanciesLoader) load, no addon '"+str(name)+"' loaded")
                
            loader = addon_dico[name]
            
            if subname is None:
                subname = DEFAULT_SUBADDON_NAME
            
            if subname not in loader.subAddons:
                raise LoadException("(DependanciesLoader) load, addon '"+str(name)+"', sub addon '"+str(subname)+"' is not loaded")
        
        
        
        
