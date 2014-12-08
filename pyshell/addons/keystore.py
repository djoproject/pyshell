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
from pyshell.arg.argchecker    import defaultInstanceArgChecker, environmentParameterChecker, IntegerArgChecker, booleanValueArgChecker, contextParameterChecker
from pyshell.loader.command    import registerSetGlobalPrefix, registerCommand, registerStopHelpTraversalAt
from pyshell.loader.keystore   import registerKey
from pyshell.utils.constants   import KEYSTORE_SECTION_NAME, ENVIRONMENT_KEY_STORE_FILE_KEY, ENVIRONMENT_SAVE_KEYS_KEY
from pyshell.utils.printing    import formatGreen, formatBolt
from pyshell.utils.postProcess import listFlatResultHandler, printColumn
from pyshell.utils.exception   import KeyStoreLoadingException, ListOfException

import sys, os
try:
    pyrev = sys.version_info.major
except AttributeError:
    pyrev = sys.version_info[0]

if pyrev == 2:
    import ConfigParser 
else:
    import configparser as ConfigParser

## DECLARATION PART ##

@shellMethod(keyName     = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             keyInstance = defaultInstanceArgChecker.getKeyChecker(),
             keyStore    = environmentParameterChecker(KEYSTORE_SECTION_NAME),
             transient   = booleanValueArgChecker())
def setKey(keyName, keyInstance, keyStore = None, transient=False):
    "set a key"
    keyInstance.setTransient(transient)
    keyStore.getValue().setKeyInstance(keyName, keyInstance)

@shellMethod(key      = defaultInstanceArgChecker.getKeyTranslatorChecker(),
             start    = IntegerArgChecker(),
             end      = IntegerArgChecker(),
             keyStore = environmentParameterChecker(KEYSTORE_SECTION_NAME))
def getKey(key, start=0, end=None, keyStore=None):
    "get a key"
    return key.getKey(start, end)

@shellMethod(keyStore = environmentParameterChecker(KEYSTORE_SECTION_NAME))
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
             keyStore = environmentParameterChecker(KEYSTORE_SECTION_NAME))
def unsetKey(keyName, keyStore=None):
    "remove a key from the keystore"
    keyStore.getValue().unsetKey(keyName)
    
@shellMethod(keyStore = environmentParameterChecker(KEYSTORE_SECTION_NAME))
def cleanKeyStore(keyStore=None):
    "remove every keys from the keystore"
    keyStore.getValue().removeAll()
    
@shellMethod(filePath    = environmentParameterChecker(ENVIRONMENT_KEY_STORE_FILE_KEY),
             useKeyStore = environmentParameterChecker(ENVIRONMENT_SAVE_KEYS_KEY),
             keyStore    = environmentParameterChecker(KEYSTORE_SECTION_NAME))
def saveKeyStore(filePath, useKeyStore, keyStore=None):
    "save keystore from file"

    if not useKeyStore.getValue():
        return

    filePath = filePath.getValue()
    keyStore = keyStore.getValue()
    
    config = ConfigParser.RawConfigParser()
    config.add_section(KEYSTORE_SECTION_NAME)
    
    keyCount = 0
    for k,v in keyStore.tries.getKeyValue().items():
        if v.transient:
            continue
    
        config.set(KEYSTORE_SECTION_NAME, k, str(v))
        keyCount+= 1
    
    if keyCount == 0 and not os.path.exists(filePath):
        return
        
    #create config directory
    if not os.path.exists(os.path.dirname(filePath)):
        os.makedirs(os.path.dirname(filePath))

    #save key store
    with open(filePath, 'wb') as configfile:
        config.write(configfile)

@shellMethod(filePath = environmentParameterChecker(ENVIRONMENT_KEY_STORE_FILE_KEY),
             useKeyStore = environmentParameterChecker(ENVIRONMENT_SAVE_KEYS_KEY),
             keyStore = environmentParameterChecker(KEYSTORE_SECTION_NAME))
def loadKeyStore(filePath, useKeyStore, keyStore=None):
    "load keystore from file"

    if not useKeyStore.getValue():
        return

    filePath = filePath.getValue()
    keyStore = keyStore.getValue()
    
    #if no file, no load, no keystore file, loading not possible but no error
    if not os.path.exists(filePath):
        return
    
    #try to load the keystore
    config = ConfigParser.RawConfigParser()
    try:
        config.read(filePath)
    except Exception as ex:
        raise KeyStoreLoadingException("(KeyStore) load, fail to read parameter file '"+str(filePath)+"' : "+str(ex))
    
    #main section available ?
    if not config.has_section(KEYSTORE_SECTION_NAME):
        raise KeyStoreLoadingException("(KeyStore) load, config file '"+str(filePath)+"' is valid but does not hold keystore section")
    
    exceptions = ListOfException()
    for keyName in config.options(KEYSTORE_SECTION_NAME):
        try:
            keyStore.setKey(keyName,config.get(KEYSTORE_SECTION_NAME, keyName), False)
        except Exception as ex:
            exceptions.append( KeyStoreLoadingException("(KeyStore) load, fail to load key '"+str(keyName)+"' : "+str(ex)))

    if exceptions.isThrowable():
        raise exceptions


@shellMethod(key   = defaultInstanceArgChecker.getKeyTranslatorChecker(),
             state = booleanValueArgChecker())
def setTransient(key, state):
    key.setTransient(state)

## REGISTER PART ##

#TODO where do come from all the keystore variable, need to load them ?

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



