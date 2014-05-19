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

from pyshell.command.command import MultiCommand, UniCommand
from exception import LoadException
from tries.exception import triesException
import inspect

def _raiseIfInvalidKeyList(keyList, methName):
    if not hasattr(keyList,"__iter__"):
        raise LoadException("(Loader) "+methName+", keyList is not iterable")

    for key in keyList:
        if type(key) != str and type(key) != unicode:
            raise LoadException("(Loader) "+methName+", only string or unicode key are allowed")

        if len(key) == 0:
            raise LoadException("(Loader) "+methName+", empty key is not allowed")

def _getAndInitCallerModule(loaderName = None):
    frm = inspect.stack()[2]
    mod = inspect.getmodule(frm[0])

    loaderDict = None
    if hasattr(mod,"_loader"):
        loaderDict = mod._loader
    else:
        loaderDict = {}
        mod._loader = loaderDict
        
    if loaderName == "":
        loaderName = None
    
    if loaderName in loaderDict:
        return loaderDict[loaderName]

    loader = Loader()
    loaderDict[loaderName] = loader
    return loader

def registerSetGlobalPrefix(keyList, subLoaderName = None):
    _raiseIfInvalidKeyList(keyList, "registerSetGlobalPrefix")
    loader = _getAndInitCallerModule(subLoaderName)
    loader.prefix = keyList

def registerSetTempPrefix(keyList, subLoaderName = None):
    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "registerSetTempPrefix")

    loader = _getAndInitCallerModule(subLoaderName)
    loader.TempPrefix = keyList
    
def registerResetTempPrefix(subLoaderName = None):
    loader = _getAndInitCallerModule(subLoaderName)
    loader.TempPrefix = None

def registerAnInstanciatedCommand(keyList, cmd, subLoaderName = None):
    #must be a multiCmd
    if not isinstance(cmd, MultiCommand):
        raise LoadException("(Loader) addInstanciatedCommand, cmd must be an instance of MultiCommand")

    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "registerAnInstanciatedCommand")

    loader = _getAndInitCallerModule(subLoaderName)
    loader._addCmd(" ".join(keyList), keyList, cmd)
    return cmd

def registerCommand(keyList, pre=None,pro=None,post=None, showInHelp=True, subLoaderName = None):
    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "registerCommand")

    name = " ".join(keyList)
    cmd = UniCommand(name, pre,pro,post, showInHelp)
    loader = _getAndInitCallerModule(subLoaderName)
    loader._addCmd(name, keyList, cmd)
    return cmd

def registerCreateMultiCommand(keyList, showInHelp=True, subLoaderName = None):
    loader = _getAndInitCallerModule(subLoaderName)

    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "registerCreateMultiCommand")

    name = " ".join(keyList)
    cmd = MultiCommand(name, showInHelp)
    loader._addCmd(name, keyList, cmd)

    return cmd

def registerAddActionOnEvent(eventType, action):
    pass #TODO
    
def registerAddValueToContext(contextKey, value):
    pass #TODO
    
def registerAddValueListToContext(contextKey, value):
    pass #TODO
    
def registerAddParameter(ParameterParentName, key, value, overrideIfExist = False):
    pass #TODO

class Loader(object):
    def __init__(self, prefix=()):
        self.prefix  = prefix
        self.cmdDict = {}
        self.TempPrefix = None    
    
    def _load(self, mltries):
        for k,v in self.cmdDict.iteritems():
            keyList, cmd = v
            key = list(self.prefix)
            key.extend(keyList)
            try:
                mltries.insert(key, cmd)
            except triesException as te:
                print "fail to insert key <"+str(" ".join(key))+"> in multi tries: "+str(te)
            
    def _unload(self, mltries):
        for k,v in self.cmdDict.iteritems():
            keyList, cmd = v
            key = list(self.prefix)
            key.extend(keyList)
            
            try:
                mltries.remove(key)
            except triesException as te:
                print "fail to remove key <"+str(" ".join(key))+"> in multi tries: "+str(te)
            
    def _reload(self, mltries):
        self.unload(mltries)
        self.load(mltries)
        
    def _addCmd(self, name, keyList, cmd):
        if self.TempPrefix != None:
            prefix = list(self.TempPrefix)
            prefix.append(keyList)
        else:
            prefix = keyList
    
        self.cmdDict[name] = (prefix, cmd,)
        
        
        
        
