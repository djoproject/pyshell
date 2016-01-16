#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

#Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.utils.exception import KeyStoreException

class CryptographicKey(object):
    KEYTYPE_HEXA  = 0
    KEYTYPE_BIT   = 1

    def __init__(self, keyString):
        #is it a string ?
        if type(keyString) != str and type(keyString) != unicode:
            raise KeyStoreException("("+self.__class__.__name__+") __init__, invalid key string, expected a string, got '"+str(type(keyString))+"'")
        
        keyString = keyString.lower()
    
        #find base
        if keyString.startswith("0x"):
            try:
                int(keyString, 16)
            except ValueError as ve:
                raise KeyStoreException("("+self.__class__.__name__+") __init__, invalid hexa string, start with 0x but is not valid: "+str(ve))
        
            self.keyType = CryptographicKey.KEYTYPE_HEXA
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
                raise KeyStoreException("("+self.__class__.__name__+") __init__, invalid binary string, start with 0b but is not valid: "+str(ve))
    
            self.keyType = CryptographicKey.KEYTYPE_BIT
            self.key     = keyString[2:]
            self.keySize = len(self.key)
        else:
            raise KeyStoreException("("+self.__class__.__name__+") __init__, invalid key string, must start with 0x or 0b, got '"+keyString+"'")
    
    def __str__(self):
        if self.keyType == CryptographicKey.KEYTYPE_HEXA:
            return "0x"+self.key
        else:
            return "0b"+self.key
        
    def __repr__(self):
        if self.keyType == CryptographicKey.KEYTYPE_HEXA:
            return "0x"+self.key+" ( HexaKey, size="+str(self.keySize)+" byte(s))"
        else:
            return "0b"+self.key+" ( BinaryKey, size="+str(self.keySize)+" bit(s))"
    
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
            if end is not None and end <= self.keySize:
                    limit = end

            keyPart = []
            if self.keyType == CryptographicKey.KEYTYPE_HEXA:
                #for b in self.key[start*2:limit*2]:
                for index in range(start*2, limit*2, 2):
                    keyPart.append(int(self.key[index:index+2], 16))
            else:
                for b in self.key[start:limit]:
                    keyPart.append(int(b, 2))
        #padding part
        if paddingEnable and end is not None and end > self.keySize:
            paddingLength = end - self.keySize
            if paddingLength > 0:
                keyPart.extend([0] * paddingLength)
        
        return keyPart 
        
    def getKeyType(self):
        return self.keyType
        
    def getKeySize(self):
        return self.keySize   
        
    def getTypeString(self):
        if self.keyType == CryptographicKey.KEYTYPE_HEXA:
            return "byte"
        else:
            return "bit"
