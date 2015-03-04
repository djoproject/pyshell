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

#TODO BRAINSTORMING
    #is it still usefull to keep a keystore like this ?
        #for the moment keystore is an EnvironmentParameter, each key should be a single parameter
    
        #could be stored in environment container as list EnvironmentParameter
            #with a keyArgChecker
            
        #+++
            #become an homogene part of the current system
            #generic way to save and load
        
        #---
            #keystore will be in the same file as every parameters
            #if we want to cipher key, it becomes more complicated
            
        #PRBLM
            #1 storing the key should be a string BUT retrieving the key in a command should be a list of int
                #SOLUTION 1
                    #create a serializable method in parameter
                        #for key, it will return a different value as the getValue
                        #but for the others parameter the behaviour will be the same as 
                    
                    #create a method to get serialized type
                        #because a string is not a list    
                #SOLUTION 2 XXX prefere this one
                    #the opposite of solution 1, a key is always a string and so an environmentParameter that is not a list
                    #but key method are still available (getSize, getItem, getType, ...)
                
            #2 how to know if it is a binary of a byte key
                #create a new object that inherit from EnvironmentParameter and add a field bynaryOrNot
            #2b yeah, then how to kwon in shell if it is binnary or not?
                #don't think it is possible to know it with the current system, so not really a prblm
                #so if we retrieve key object in a command, a key method will be available to know this information
            #3 how to list them
                #create a whole new container just to them

            #XXX MAIN SOLUTION XXX
                #keep Key object
                #remove KeyStore object
                #Parameter Container for key (as new keystore object)
                    #set should allow string and key object
                #EnvironmentParameter with keyArgChecker
                    #just override constructor
                #adapt keyStoreTranslatorArgChecker, KeyArgChecker
                #adapt addon/keystore

            
from tries                   import tries
from tries.exception         import ambiguousPathException
from pyshell.utils.exception import KeyStoreException

class KeyStore(object):
    def __init__(self):
        self.tries = tries()
    
    def __str__(self):
        return repr(self)
        
    def __repr__(self):
        return str(self.tries.countValue())+" key(s) stored"
        
    def hasKey(self, keyNamePrefix):
        try:
            node = self.tries.search(keyNamePrefix)
            return node is not None
        except ambiguousPathException as ape:
            raise KeyStoreException("(KeyStore) hasKey, Ambiguous key name", ape)
        
    def setKey(self, keyname, keyString, transient=True):
        self.setKeyInstance(keyname, Key(keyString, transient))
    
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
        if end is not None and end < start:
            return ()
        
        #part to extract from key
        if start >= self.keySize:
            if end is None or not paddingEnable:
                return ()
            
            keyPart = []
        else:
            limit = self.keySize
            if end is not None:
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
        
    def getTypeString(self):
        if self.keyType == Key.KEYTYPE_HEXA:
            return "byte"
        else:
            return "bit"
    
    
