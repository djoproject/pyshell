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

from tries import tries
from tries.exception import ambiguousPathException
import sys,os
from math import log

try:
    pyrev = sys.version_info.major
except AttributeError:
    pyrev = sys.version_info[0]

if pyrev == 2:
    import ConfigParser 
else:
    import configparser as ConfigParser
    
KEYSTORE_SECTION_NAME = "keystore"
DEFAULT_KEYSTORE_FILE = os.path.join(os.path.expanduser("~"), ".pyshell_keystore")

class KeyStore(object):
    def __init__(self, filePath = None):
        self.filePath = filePath
        self.tries = tries()
        
    def load(self):
        #if no path, no load
        if filePath == None:
            return
        
        #if no file, no load
        if not os.path.exists(self.filePath):
            print("(KeyStore) load, file <"+str(self.filePath)+"> does not exist")
            return
        
        #try to load the keystore
        config = ConfigParser.RawConfigParser()
        try:
            config.read(self.filePath)
        except Exception as ex:
            print("(KeyStore) load, fail to read parameter file <"+str(self.filePath)+"> : "+str(ex))
            return
        
        #main section available ?
        if not config.has_section(KEYSTORE_SECTION_NAME):
            print("(KeyStore) load, config file <"+str(self.filePath)+"> is valid but does not hold keystore section")
            return
            
        for keyName in config.options(KEYSTORE_SECTION_NAME):
            try:
                self.tries.insert(keyName, Key(config.get(KEYSTORE_SECTION_NAME, keyName)))
            except Exception as ex:
                print("(KeyStore) load, fail to load key <"+str(keyName)+"> : "+str(ex))
        
    def save(self):
        if filePath is None:
            return
        
        config = ConfigParser.RawConfigParser()
        
        for k,v in self.tries.getKeyValue().items():
            config.set(KEYSTORE_SECTION_NAME, k, str(v))
            
        with open(self.filePath, 'wb') as configfile:
            config.write(configfile)
    
    def hasKey(self, keyNamePrefix):
        try:
            node = self.tries.search(keyNamePrefix)
            return node is not None
        except ambiguousPathException as ape:
            raise Exception("(KeyStore) hasKey, Ambiguous key name", ape)
        
    def setKey(self, keyname, keyString):
        self.setKeyInstance(keyname, Key(keyString))
    
    def setKeyInstance(self, keyname, instance):
        if not isinstance(instance, Key):
            raise Exception("(KeyStore) setKeyInstance, invalid key instance, expect Key instance, got <"+str(type(instance))+">")
    
        node = self.tries.search(keyname,True)
        if node is None:
            self.tries.insert(keyname, instance)
        else:
            self.tries.update(keyname, instance)
    
    def getKey(self, keyNamePrefix):
        try:
            node = self.tries.search(keyNamePrefix)
            
            if node is None:
                raise Exception("(KeyStore) getKey, unknown key name")
                
            return node.getValue()
            
        except ambiguousPathException:
            raise Exception("(KeyStore) getKey, Ambiguous key name", ape)
        
    def unsetKey(self, keyNamePrefix):
        try:
            node = self.tries.search(keyNamePrefix)
            if node is None:
                return
            
            self.tries.remove(node.getCompleteName())
                
        except ambiguousPathException as ape:
            raise Exception("(KeyStore) unsetKey, Ambiguous key name", ape)
        
    def getKeyList(self, prefix = ""):
        return self.tries.getKeyList(prefix)

    def removeAll(self):
        self.tries = tries()

class Key(object):
    KEYTYPE_HEXA  = 0
    KEYTYPE_BIT   = 1

    def __init__(self, keyString):
        #is it a string ?
        if type(keyString) != str and type(keyString) != unicode:
            raise Exception("(Key) __init__, invalid key string, expected a string, got <"+str(type(keyString))+">")
        
        keyString = keyString.lower()
    
        #find base
        if keyString.startswith("0x"):
            try:
                int(keyString, 16)
            except ValueError as ve:
                raise Exception("(Key) __init__, invalid hexa string, start with 0x but is not valid: "+str(ve))
        
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
                raise Exception("(Key) __init__, invalid binary string, start with 0b but is not valid: "+str(ve))
    
            self.keyType = Key.KEYTYPE_BIT
            self.key     = keyString[2:]
            self.keySize = len(self.key)
        else:
            raise Exception("(Key) __init__, invalid key string, must start with 0x or 0b, got <"+keyString+">")

    def __str__(self):
        if self.keyType == Key.KEYTYPE_HEXA:
            return "0x"+self.key
        else:
            return "0b"+self.key
        
    def __repr__(self):
        if self.keyType == Key.KEYTYPE_HEXA:
            return "0x"+self.key+" ( HexaKey, size="+str(self.keySize)+" byte(s) )"
        else:
            return "0b"+self.key+" ( BinaryKey, size="+str(self.keySize)+" bit(s) )"
    
    def getKey(self,start,end,paddingEnable=True):
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
                for b in self.key[start*2:limit*2]:
                    keyPart.append(int(b[start*2:start*2+2]))
            else:
                for b in self.key[start:limit]:
                    keyPart.append(int(b))

        #padding part
        if paddingEnable:
            paddingLength = (end - max(start,self.keySize) - 1)
            if paddingLength > 0:
                keyPart.extend([0] * paddingLength)
        
        return keyPart 
        
    def getKeyType():
        return self.keyType
        
    def getKeySize():
        return self.keySize      
    
    
    
