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

from pyshell.arg.decorator  import shellMethod
from pyshell.arg.argchecker import defaultInstanceArgChecker, parameterChecker
from pyshell.simpleProcess.postProcess import listFlatResultHandler, stringListResultHandler
from pyshell.loader.command import registerSetGlobalPrefix, registerCommand, registerStopHelpTraversalAt

## DECLARATION PART ##

@shellMethod(keyName   = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             keyInstance = defaultInstanceArgChecker.getKeyChecker(),
             keyStore  = parameterChecker("keyStore"))
def setKey(keyName, keyInstance, keyStore = None):
    keyStore.getValue().setKeyInstance(keyName, keyInstance)

@shellMethod(keyName  = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             start    = defaultInstanceArgChecker.getIntegerArgCheckerInstance(),
             end      = defaultInstanceArgChecker.getIntegerArgCheckerInstance(),
             keyStore = parameterChecker("keyStore"))
def getKey(keyName, start=0, end=None, keyStore=None):
    if not keyStore.getValue().hasKey(keyName):
        raise Exception("unknow key name: <"+str(keyName)+">")
        
    return keyStore.getValue().getKey(keyName).getKey(start, end)

@shellMethod(keyStore = parameterChecker("keyStore"))
def listKey(keyStore=None):
    toRet = []
    
    for k in keyStore.getValue().getKeyList():
        toRet.append(str(k)+": "+repr(keyStore.getValue().getKey(k)))
        
    return toRet

@shellMethod(keyName  = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             keyStore = parameterChecker("keyStore"))
def unsetKey(keyName, keyStore=None):
    keyStore.getValue().unsetKey()
    
@shellMethod(keyStore = parameterChecker("keyStore"))
def cleanKeyStore(keyStore=None):
    keyStore.getValue().removeAll()
    
@shellMethod(keyStore = parameterChecker("keyStore"))
def saveKeyStore(keyStore=None):
    keyStore.getValue().save()

@shellMethod(keyStore = parameterChecker("keyStore"))
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



