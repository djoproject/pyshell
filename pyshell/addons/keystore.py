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

from pyshell.arg.decorator     import shellMethod
from pyshell.arg.argchecker    import defaultInstanceArgChecker, parameterChecker, IntegerArgChecker, booleanValueArgChecker, contextParameterChecker
from pyshell.loader.command    import registerSetGlobalPrefix, registerCommand, registerStopHelpTraversalAt
from pyshell.loader.keystore   import registerKey
from pyshell.utils.constants   import KEYSTORE_SECTION_NAME, ENVIRONMENT_NAME
from pyshell.utils.printing    import formatGreen, formatBolt
from pyshell.utils.postProcess import listFlatResultHandler, printColumn

## DECLARATION PART ##

@shellMethod(keyName     = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             keyInstance = defaultInstanceArgChecker.getKeyChecker(),
             keyStore    = parameterChecker(KEYSTORE_SECTION_NAME, ENVIRONMENT_NAME),
             transient   = booleanValueArgChecker())
def setKey(keyName, keyInstance, keyStore = None, transient=False):
    "set a key"
    keyInstance.setTransient(transient)
    keyStore.getValue().setKeyInstance(keyName, keyInstance)

@shellMethod(key      = defaultInstanceArgChecker.getKeyTranslatorChecker(),
             start    = IntegerArgChecker(),
             end      = IntegerArgChecker(),
             keyStore = parameterChecker(KEYSTORE_SECTION_NAME, ENVIRONMENT_NAME))
def getKey(key, start=0, end=None, keyStore=None):
    "get a key"
    return key.getKey(start, end)

@shellMethod(keyStore = parameterChecker(KEYSTORE_SECTION_NAME, ENVIRONMENT_NAME))
def listKey(keyStore):
    "list available key in the keystore"
    
    keyStore = keyStore.getValue()    
    toRet = []
    
    for k in keyStore.getKeyList():
        key = keyStore.getKey(k)
        toRet.append( (k,key.getTypeString(),str(key.getKeySize()),formatGreen(str(key)), ) )
    
    if len(toRet) == 0:
        return [("No key available",)]
    
    toRet.insert(0, (formatBolt("Key name"),formatBolt("Type"),formatBolt("Size"), formatBolt("Value"), ) )
    return toRet

@shellMethod(keyName  = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             keyStore = parameterChecker(KEYSTORE_SECTION_NAME, ENVIRONMENT_NAME))
def unsetKey(keyName, keyStore=None):
    "remove a key from the keystore"
    keyStore.getValue().unsetKey(keyName)
    
@shellMethod(keyStore = parameterChecker(KEYSTORE_SECTION_NAME, ENVIRONMENT_NAME))
def cleanKeyStore(keyStore=None):
    "remove every keys from the keystore"
    keyStore.getValue().removeAll()
    
@shellMethod(keyStore = parameterChecker(KEYSTORE_SECTION_NAME, ENVIRONMENT_NAME))
def saveKeyStore(keyStore=None):
    "save keystore from file"
    keyStore.getValue().save()

@shellMethod(keyStore = parameterChecker(KEYSTORE_SECTION_NAME, ENVIRONMENT_NAME))
def loadKeyStore(keyStore=None):
    "load keystore from file"
    keyStore.getValue().load()

@shellMethod(key   = defaultInstanceArgChecker.getKeyTranslatorChecker(),
             state = booleanValueArgChecker())
def setTransient(key, state):
    key.setTransient(state)

## REGISTER PART ##

registerSetGlobalPrefix( ("key", ) )
registerCommand( ("set",) ,                    post=setKey)
registerCommand( ("get",) ,                    pre=getKey, pro=listFlatResultHandler)
registerCommand( ("unset",) ,                  pro=unsetKey)
registerCommand( ("list",) ,                   pre=listKey, pro=printColumn)
registerCommand( ("save",) ,                   pro=saveKeyStore)
registerCommand( ("load",) ,                   pro=loadKeyStore)
registerCommand( ("clean",) ,                  pro=cleanKeyStore)
registerCommand( ("transient",) ,              pro=setTransient)
registerStopHelpTraversalAt( () )
registerKey("test", "0x00112233445566778899aabbccddeeff")



