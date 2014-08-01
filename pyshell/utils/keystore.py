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
import sys

try:
    pyrev = sys.version_info.major
except AttributeError:
    pyrev = sys.version_info[0]

if pyrev == 2:
    import ConfigParser 
else:
    import configparser as ConfigParser
    

KEYTYPE_HEXA = 0
KEYTYPE_BIT  = 1
KEYSTORE_SECTION_NAME = "keystore"

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
                self.tries.insert(keyName, Key.parseAndCreateInstance(config.get(KEYSTORE_SECTION_NAME, keyName)))
            except Exception as ex:
                print("(KeyStore) load, fail to load key <"+str(keyName)+"> : "+str(ex))
        
    def save(self):
        if filePath == None:
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
        self.setKeyInstance(keyname, Key.parseAndCreateInstance(keyString))
    
    def setKeyInstance(self, keyname, instance):
        #TODO instance must be a key instance
    
        node = self.tries.search(keyname,True)
        if node is none:
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
        
class Key(object):
    def __init__(self, key, keyType = KEYTYPE_HEXA):
        #must be a string or a unicode
        
        #must start with 0x or 0b
        
        #must be one big token or hexa byte token or bit token
    
        pass #TODO
        
    def __str__(self):
        pass #TODO
        
    def getType():
        return self.type
    
    @staticmethod
    def parseAndCreateInstance(keyString):
        pass #TODO
        
    #TODO faire des méthodes pour 
        #récupérer la taille
        #une partie de la clé, avec ou sans padding
        #...
    
    
