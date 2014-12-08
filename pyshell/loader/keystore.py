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
from pyshell.loader.exception import LoadException
from pyshell.utils.keystore   import Key, KeyStore
from pyshell.utils.parameter  import EnvironmentParameter
from pyshell.utils.constants  import KEYSTORE_SECTION_NAME
from pyshell.utils.exception  import ListOfException

LOADING_METHOD_NAME    = "load"
UNLOADING_METHOD_NAME  = "unload"

def _local_getAndInitCallerModule(subLoaderName = None):
    return getAndInitCallerModule(KeyStoreLoader.__module__+"."+KeyStoreLoader.__name__,KeyStoreLoader, 3, subLoaderName)

def _initAndGetKeyStore(parameterManager, methName):
    if not parameterManager.environment.hasParameter(KEYSTORE_SECTION_NAME):
        raise LoadException("(KeyStoreLoader) "+str(methName)+", fail to load keys because parameter has not a keyStore item") 
            
    keyStore = parameterManager.environment.getParameter(KEYSTORE_SECTION_NAME).getValue()
    
    if not isinstance(keyStore, KeyStore):
        raise LoadException("(KeyStoreLoader) "+str(methName)+", the keyStore item retrieved from parameters is not a valid instance of KeyStore, got '"+str(type(keyStore))+"'")
        
    return keyStore

class KeyStoreLoader(AbstractLoader):
    def __init__(self):
        AbstractLoader.__init__(self)
        self.keys = {}
        self.loadedKeys = None

    def load(self, parameterManager, subLoaderName = None):
        self.loadedKeys = []
        AbstractLoader.load(self, parameterManager, subLoaderName)

        keyStore = _initAndGetKeyStore(parameterManager, LOADING_METHOD_NAME)
        exceptions = ListOfException()
        
        for keyName, value in self.keys.items():
            keyInstance, override = value
            
            if keyStore.hasKey(keyName) and not override:
                exceptions.addException( LoadException("fail to register key '"+str(keyName)+"', key alreay exists") )
                continue
                
            keyStore.setKeyInstance(keyName, keyInstance)
            self.loadedKeys.append(keyName)
            
        #raise error list
        if exceptions.isThrowable():
            raise exceptions 

    def unload(self, parameterManager, subLoaderName = None):
        AbstractLoader.unload(self, parameterManager, subLoaderName)
        
        keyStore = _initAndGetKeyStore(parameterManager, UNLOADING_METHOD_NAME)
    
        for keyName in self.loadedKeys:
            if keyStore.hasKey(keyName):
                keyStore.unsetKey(keyName)
        
def registerKey(keyName, keyString, override = True, transient=True, subLoaderName = None):
    keyInstance          = Key(keyString, transient)
    loader               = _local_getAndInitCallerModule(subLoaderName)
    loader.keys[keyName] = (keyInstance, override,)
    
    
    
