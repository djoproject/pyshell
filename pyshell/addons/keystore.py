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

from pyshell.arg.decorator             import shellMethod
from pyshell.arg.argchecker            import defaultInstanceArgChecker, parameterChecker, IntegerArgChecker
from pyshell.simpleProcess.postProcess import listFlatResultHandler, stringListResultHandler
from pyshell.loader.command            import registerSetGlobalPrefix, registerCommand, registerStopHelpTraversalAt
from pyshell.utils.keystore            import KEYSTORE_SECTION_NAME
from pyshell.loader.keystore           import registerKey

## DECLARATION PART ##

@shellMethod(keyName     = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             keyInstance = defaultInstanceArgChecker.getKeyChecker(),
             keyStore    = parameterChecker(KEYSTORE_SECTION_NAME))
def setKey(keyName, keyInstance, keyStore = None):
    keyStore.getValue().setKeyInstance(keyName, keyInstance)

@shellMethod(key      = defaultInstanceArgChecker.getKeyTranslatorChecker(),
             start    = IntegerArgChecker(),
             end      = IntegerArgChecker(),
             keyStore = parameterChecker(KEYSTORE_SECTION_NAME))
def getKey(key, start=0, end=None, keyStore=None):
    return key.getKey(start, end)

@shellMethod(keyStore = parameterChecker(KEYSTORE_SECTION_NAME))
def listKey(keyStore=None):
    toRet = []
    
    for k in keyStore.getValue().getKeyList():
        toRet.append(str(k)+": "+repr(keyStore.getValue().getKey(k)))
        
    return toRet

@shellMethod(keyName  = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             keyStore = parameterChecker(KEYSTORE_SECTION_NAME))
def unsetKey(keyName, keyStore=None):
    keyStore.getValue().unsetKey()
    
@shellMethod(keyStore = parameterChecker(KEYSTORE_SECTION_NAME))
def cleanKeyStore(keyStore=None):
    keyStore.getValue().removeAll()
    
@shellMethod(keyStore = parameterChecker(KEYSTORE_SECTION_NAME))
def saveKeyStore(keyStore=None):
    keyStore.getValue().save()

@shellMethod(keyStore = parameterChecker(KEYSTORE_SECTION_NAME))
def loadKeyStore(keyStore=None):
    keyStore.getValue().load()

## REGISTER PART ##

registerSetGlobalPrefix( ("key", ) )
registerCommand( ("set",) ,                    post=setKey)
registerCommand( ("get",) ,                    pre=getKey, pro=listFlatResultHandler)
registerCommand( ("unset",) ,                  pro=unsetKey)
registerCommand( ("list",) ,                   pre=listKey, pro=stringListResultHandler)
registerCommand( ("save",) ,                   pro=saveKeyStore)
registerCommand( ("load",) ,                   pro=loadKeyStore)
registerCommand( ("clean",) ,                  pro=cleanKeyStore)
registerStopHelpTraversalAt( () )
registerKey("test", "0x00112233445566778899aabbccddeeff")



