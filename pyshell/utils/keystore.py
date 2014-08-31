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

from tries                   import tries
from tries.exception         import ambiguousPathException
import sys,os
from math                    import log
from pyshell.utils.valuable  import Valuable
from pyshell.utils.constants import KEYSTORE_SECTION_NAME
from pyshell.utils.exception import KeyStoreLoadingException, KeyStoreException, ListOfException

try:
    pyrev = sys.version_info.major
except AttributeError:
    pyrev = sys.version_info[0]

if pyrev == 2:
    import ConfigParser 
else:
    import configparser as ConfigParser

class KeyStore(object):
    def __init__(self,filePath = None):
        if filePath != None and not isinstance(filePath,Valuable):
            raise KeyStoreException("(KeyStore) __init__, filePath must be a Valuable object")
    
        self.filePath = filePath
        self.tries = tries()
        
    def load(self):
        #if no path, no load
        if self.filePath == None:
            return
        
        #if no file, no load, no keystore file, loading not possible but no error
        if not os.path.exists(self.filePath.getValue()):
            return
        
        #try to load the keystore
        config = ConfigParser.RawConfigParser()
        try:
            config.read(self.filePath.getValue())
        except Exception as ex:
            raise KeyStoreLoadingException("(KeyStore) load, fail to read parameter file '"+str(self.filePath.getValue())+"' : "+str(ex))
        
        #main section available ?
        if not config.has_section(KEYSTORE_SECTION_NAME):
            raise KeyStoreLoadingException("(KeyStore) load, config file '"+str(self.filePath.getValue())+"' is valid but does not hold keystore section")
        
        exceptions = ListOfException()
        for keyName in config.options(KEYSTORE_SECTION_NAME):
            try:
                self.tries.insert(keyName, Key(config.get(KEYSTORE_SECTION_NAME, keyName), transient=False))
            except Exception as ex:
                exceptions.append( KeyStoreLoadingException("(KeyStore) load, fail to load key '"+str(keyName)+"' : "+str(ex)))

        if exceptions.isThrowable():
            raise exceptions
        
    def save(self):
        if self.filePath is None:
            return
        
        config = ConfigParser.RawConfigParser()
        config.add_section(KEYSTORE_SECTION_NAME)
        
        keyCount = 0
        for k,v in self.tries.getKeyValue().items():
            if v.transient:
                continue
        
            config.set(KEYSTORE_SECTION_NAME, k, str(v))
            keyCount+= 1
        
        if keyCount == 0 and not os.path.exists(self.filePath.getValue()):
            return
            
        with open(self.filePath.getValue(), 'wb') as configfile:
            config.write(configfile)
    
    def hasKey(self, keyNamePrefix):
        try:
            node = self.tries.search(keyNamePrefix)
            return node is not None
        except ambiguousPathException as ape:
            raise KeyStoreException("(KeyStore) hasKey, Ambiguous key name", ape)
        
    def setKey(self, keyname, keyString):
        self.setKeyInstance(keyname, Key(keyString))
    
    def setKeyInstance(self, keyname, instance):
        if not isinstance(instance, Key):
            raise KeyStoreException("(KeyStore) setKeyInstance, invalid key instance, expect Key instance, got '"+str(type(instance))+"'")
    
        node = self.tries.search(keyname,True)
        if node is None:
            self.tries.insert(keyname, instance)
        else:
            self.tries.update(keyname, instance)
    
    def getKey(self, keyNamePrefix):
        try:
            node = self.tries.search(keyNamePrefix)
            
            if node is None:
                raise KeyStoreException("(KeyStore) getKey, unknown key name")
                
            return node.getValue()
            
        except ambiguousPathException:
            raise KeyStoreException("(KeyStore) getKey, Ambiguous key name", ape)
        
    def unsetKey(self, keyNamePrefix):
        try:
            node = self.tries.search(keyNamePrefix)
            if node is None:
                return
            
            self.tries.remove(node.getCompleteName())
                
        except ambiguousPathException as ape:
            raise KeyStoreException("(KeyStore) unsetKey, Ambiguous key name", ape)
        
    def getKeyList(self, prefix = ""):
        return self.tries.getKeyList(prefix)

    def removeAll(self):
        self.tries = tries()

class Key(object):
    KEYTYPE_HEXA  = 0
    KEYTYPE_BIT   = 1

    def __init__(self, keyString, transient=True):
        #is it a string ?
        if type(keyString) != str and type(keyString) != unicode:
            raise KeyStoreException("(Key) __init__, invalid key string, expected a string, got '"+str(type(keyString))+"'")
        
        keyString = keyString.lower()
    
        #find base
        if keyString.startswith("0x"):
            try:
                int(keyString, 16)
            except ValueError as ve:
                raise KeyStoreException("(Key) __init__, invalid hexa string, start with 0x but is not valid: "+str(ve))
        
            self.keyType = Key.KEYTYPE_HEXA
            self.key     = keyString[2:]
            
            tempKeySize = float(len(keyString) - 2)
            tempKeySize /= 2
            self.keySize = int(tempKeySize)
            
            if tempKeySize > int(tempKeySize):
                self.keySize += 1
                self.key = "0"+self.key            
        
        elif keyString.startswith("0b"):
            try:
                int(keyString, 2)
            except ValueError as ve:
                raise KeyStoreException("(Key) __init__, invalid binary string, start with 0b but is not valid: "+str(ve))
    
            self.keyType = Key.KEYTYPE_BIT
            self.key     = keyString[2:]
            self.keySize = len(self.key)
        else:
            raise KeyStoreException("(Key) __init__, invalid key string, must start with 0x or 0b, got '"+keyString+"'")

        self.setTransient(transient)
    
    def setTransient(self, state):
        if type(state) != bool:
            raise KeyStoreException("(Key) setTransient, expected a bool type as state, got '"+str(type(state))+"'")
    
        self.transient = state
    
    def __str__(self):
        if self.keyType == Key.KEYTYPE_HEXA:
            return "0x"+self.key
        else:
            return "0b"+self.key
        
    def __repr__(self):
        if self.keyType == Key.KEYTYPE_HEXA:
            return "0x"+self.key+" ( HexaKey, size="+str(self.keySize)+" byte(s), transient="+str(self.transient)+" )"
        else:
            return "0b"+self.key+" ( BinaryKey, size="+str(self.keySize)+" bit(s), transient="+str(self.transient)+" )"
    
    def getKey(self,start,end=None,paddingEnable=True):
        if end != None and end < start:
            return ()
        
        #part to extract from key
        if start >= self.keySize:
            if end is None or not paddingEnable:
                return ()
            
            keyPart = []
        else:
            limit = self.keySize
            if end != None:
                if end <= self.keySize:
                    limit = end
            else:
                end = self.keySize

            keyPart = []
            if self.keyType == Key.KEYTYPE_HEXA:
                #for b in self.key[start*2:limit*2]:
                for index in range(start*2, limit*2, 2):
                    keyPart.append(int(self.key[index:index+2], 16))
            else:
                for b in self.key[start:limit]:
                    keyPart.append(int(b, 2))
        #padding part
        if paddingEnable:
            paddingLength = (end - max(start,self.keySize) - 1)
            if paddingLength > 0:
                keyPart.extend([0] * paddingLength)
        
        return keyPart 
        
    def getKeyType(self):
        return self.keyType
        
    def getKeySize(self):
        return self.keySize      
    
    
    
