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

from utils                   import getAndInitCallerModule, AbstractLoader
from exceptions              import LoadException
from pyshell.utils.keystore  import Key, KeyStore
from pyshell.utils.parameter import EnvironmentParameter
from pyshell.utils.constants import KEYSTORE_SECTION_NAME, ENVIRONMENT_NAME

LOADING_METHOD_NAME    = "load"
UNLOADING_METHOD_NAME  = "unload"

def _local_getAndInitCallerModule(subLoaderName = None):
    return getAndInitCallerModule(KeyStoreLoader.__module__+"."+KeyStoreLoader.__name__,KeyStoreLoader, 3, subLoaderName)

def _initAndGetKeyStore(parameterManager, methName):
    if not parameterManager.hasParameter(KEYSTORE_SECTION_NAME, ENVIRONMENT_NAME):
        raise LoadException("(KeyStoreLoader) "+str(methName)+", fail to load keys because parameter has not a keyStore item") 
            
    keyStore = parameterManager.getParameter(KEYSTORE_SECTION_NAME, ENVIRONMENT_NAME).getValue()
    
    if not isinstance(keyStore, KeyStore):
        raise LoadException("(KeyStoreLoader) "+str(methName)+", the keyStore item retrieved from parameters is not a valid instance of KeyStore, got <"+str(type(keyStore))+">")
        
    return keyStore

class KeyStoreLoader(AbstractLoader):
    def __init__(self):
        self.keys = {}

    def load(self, parameterManager):
        keyStore = _initAndGetKeyStore(parameterManager, LOADING_METHOD_NAME)
        
        for keyName, value in self.keys.items():
            keyInstance, override = value
            
            if keyStore.hasKey(keyName) and not override:
                continue
                
            keyStore.setKeyInstance(keyName, keyInstance)
            

    def unload(self, parameterManager):
        keyStore = _initAndGetKeyStore(parameterManager, UNLOADING_METHOD_NAME)
    
        for keyName, value in self.keys.items():
            keyStore.unsetKey(keyName)
        
def registerKey(keyName, keyString, override = True, transient=True, subLoaderName = None):
    keyInstance          = Key(keyString, transient)
    loader               = _local_getAndInitCallerModule(subLoaderName)
    loader.keys[keyName] = (keyInstance, override,)
    
    
    
