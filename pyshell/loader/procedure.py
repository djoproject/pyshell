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

from pyshell.loader.utils import getAndInitCallerModule, AbstractLoader

#TODO 
    #keep insertion order
    #forbid double insertion
        #just need a two level dict
                
    #error if override
    

def _local_getAndInitCallerModule(subLoaderName = None)
    return getAndInitCallerModule(ProcedureLoader.__module__+"."+ProcedureLoader.__name__,ProcedureLoader, 3, subLoaderName)

class ProcedureLoader(AbstractLoader):
    def __init__(self):
        #adding part
        self.listToLoad = []
        self.indexNotFree = {}
        
        #removing part
        self.procedureCreated = []
        self.indexAdded = []
        
    def load(self, parameterManager, subLoaderName = None):
        AbstractLoader.load(self, parameterManager, subLoaderName)
        
        for procedureName, procedureCommand, index in self.listToLoad:
            #TODO procedure exist ?
                #if not create it and register it as a new one
            
            if index is None:
                pass #TODO
            else:
                pass #TODO
                
            #TODO register the index to remove if it is an existing procedure
                #check in the procedureCreated list
            
            pass #TODO
        
    def unload(self, parameterManager, subLoaderName = None):
        AbstractLoader.unload(self, parameterManager, subLoaderName)
        
        for created in self.procedureCreated:
            pass #TODO remove or not ? if there is more cmd inside than at the insertion ?
        
        for index in self.indexAdded:
            pass #TODO remove or not ? how to know if it is still the same index ?
        
def registerAddProcedureCommand(procedureName, procedureCommand, subLoaderName = None):
    loader = _local_getAndInitCallerModule(subLoaderName)
    
    #TODO valid procedure name ?
    
    #TODO valid procedure command ?
        
    #add in list
    self.listToLoad.append( (procedureName, procedureCommand, None) )
    
def registerSetProcedureCommand(index, procedureName, procedureCommand, override = False, subLoaderName = None):
    loader = _local_getAndInitCallerModule(subLoaderName)
    
    #TODO valid index ?
    
    #TODO valid procedureName ?
    
    #TODO valid procedureCommand ?
    
    #TODO free index ?
    
    #add in list
    self.listToLoad.append( (procedureName, procedureCommand, index) )
