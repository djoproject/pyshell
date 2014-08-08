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

from utils import getAndInitCallerModule, AbstractLoader
from pyshell.command.command import MultiCommand, UniCommand
from exceptions import RegisterException
from tries.exception import triesException

def _local_getAndInitCallerModule(subLoaderName = None):
    return getAndInitCallerModule(CommandLoader.__module__+"."+CommandLoader.__name__,CommandLoader, 3, subLoaderName)

def _raiseIfInvalidKeyList(keyList, methName):
    if not hasattr(keyList,"__iter__"):
        raise RegisterException("(Loader) "+methName+", keyList is not iterable")

    for key in keyList:
        if type(key) != str and type(key) != unicode:
            raise RegisterException("(Loader) "+methName+", only string or unicode key are allowed")

        if len(key) == 0:
            raise RegisterException("(Loader) "+methName+", empty key is not allowed")

def registerSetGlobalPrefix(keyList, subLoaderName = None):
    _raiseIfInvalidKeyList(keyList, "registerSetGlobalPrefix")
    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.prefix = keyList

def registerSetTempPrefix(keyList, subLoaderName = None):
    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "registerSetTempPrefix")

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.TempPrefix = keyList
    
def registerResetTempPrefix(subLoaderName = None):
    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.TempPrefix = None

def registerAnInstanciatedCommand(keyList, cmd, subLoaderName = None):
    #must be a multiCmd
    if not isinstance(cmd, MultiCommand):
        raise RegisterException("(Loader) addInstanciatedCommand, cmd must be an instance of MultiCommand")

    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "registerAnInstanciatedCommand")

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.addCmd(" ".join(keyList), keyList, cmd)
    return cmd

def registerCommand(keyList, pre=None,pro=None,post=None, showInHelp=True, subLoaderName = None):
    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "registerCommand")
    loader = _local_getAndInitCallerModule(subLoaderName)
    
    if loader.TempPrefix != None:
        name = " ".join(loader.TempPrefix) + " " + " ".join(keyList)
    else:
        name = " ".join(keyList)
        
    cmd = UniCommand(name, pre,pro,post, showInHelp)
    
    loader.addCmd(name, keyList, cmd)
    return cmd

def registerCreateMultiCommand(keyList, showInHelp=True, subLoaderName = None):
    loader = _local_getAndInitCallerModule(subLoaderName)

    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "registerCreateMultiCommand")
    
    if loader.TempPrefix != None:
        name = " ".join(loader.TempPrefix) + " " + " ".join(keyList)
    else:
        name = " ".join(keyList)
    
    cmd = MultiCommand(name, showInHelp)
    loader.addCmd(name, keyList, cmd)

    return cmd

def registerStopHelpTraversalAt(keyList,subLoaderName = None):
    loader = _local_getAndInitCallerModule(subLoaderName)

    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "registerCreateMultiCommand")
    loader.stoplist.append(keyList)
    
class CommandLoader(AbstractLoader):
    def __init__(self, prefix=()):
        AbstractLoader.__init__(self)
    
        self.prefix     = prefix
        self.cmdDict    = {}
        self.TempPrefix = None
        self.stoplist   = []
    
    def load(self, parameterManager):
    
        if not parameterManager.hasParameter("levelTries"):
            print("(CommandLoader) load, fail to load command because parameter has not a levelTries item")
            return    
            
        mltries = parameterManager.getParameter("levelTries").getValue()
    
        #TODO don't print error message here, group the error in a listException
    
        #add command
        for k,v in self.cmdDict.iteritems():
            keyList, cmd = v
            key = list(self.prefix)
            key.extend(keyList)
            try:
                mltries.insert(key, cmd)
            except triesException as te:
                print "fail to insert key <"+str(" ".join(key))+"> in multi tries: "+str(te)

        #stop traversal
        for stop in self.stoplist:
            key = list(self.prefix)
            key.extend(stop)
        
            try:
                mltries.setStopTraversal(key, True)
            except triesException as te:
                print "fail to disable traversal for key list <"+str(" ".join(stop))+"> in multi tries: "+str(te)

    def unload(self, parameterManager):
        if not parameterManager.hasParameter("levelTries"):
            print("(CommandLoader) load, fail to load command because parameter has not a levelTries item")
            return
            
        mltries = parameterManager.getParameter("levelTries").getValue()
    
        #TODO don't print error message here, group the error in a listException
    
        for k,v in self.cmdDict.iteritems():
            keyList, cmd = v
            key = list(self.prefix)
            key.extend(keyList)
            
            try:
                mltries.remove(key)
            except triesException as te:
                print("fail to remove key <"+str(" ".join(key))+"> in multi tries: "+str(te))
        
    def addCmd(self, name, keyList, cmd):
        if self.TempPrefix != None:
            prefix = list(self.TempPrefix)
            prefix.extend(keyList)
        else:
            prefix = keyList
    
        self.cmdDict[name] = (prefix, cmd,)