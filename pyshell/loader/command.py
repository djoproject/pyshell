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

from tries.exception          import triesException
from pyshell.loader.utils     import getAndInitCallerModule, AbstractLoader
from pyshell.command.command  import MultiCommand, UniCommand
from pyshell.loader.exception import LoadException, RegisterException
from pyshell.utils.constants  import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.exception  import ListOfException
from pyshell.utils.misc       import raiseIfInvalidKeyList

def _local_getAndInitCallerModule(profile = None):
    return getAndInitCallerModule(CommandLoader.__module__+"."+CommandLoader.__name__,CommandLoader, profile)

def registerSetGlobalPrefix(keyList, profile = None):
    raiseIfInvalidKeyList(keyList, RegisterException,"Loader", "registerSetGlobalPrefix")
    loader = _local_getAndInitCallerModule(profile)
    loader.prefix = keyList

def registerSetTempPrefix(keyList, profile = None):
    raiseIfInvalidKeyList(keyList, RegisterException,"Loader", "registerSetTempPrefix")
    loader = _local_getAndInitCallerModule(profile)
    loader.TempPrefix = keyList
    
def registerResetTempPrefix(profile = None):
    loader = _local_getAndInitCallerModule(profile)
    loader.TempPrefix = None

def registerAnInstanciatedCommand(keyList, cmd, profile = None):
    #must be a multiCmd
    if not isinstance(cmd, MultiCommand):
        raise RegisterException("(Loader) addInstanciatedCommand, cmd must be an instance of MultiCommand") #TODO improve error message, expect and get

    #check cmd and keylist
    raiseIfInvalidKeyList(keyList, RegisterException,"Loader", "registerAnInstanciatedCommand")
    loader = _local_getAndInitCallerModule(profile)
    loader.addCmd(keyList, cmd)
    return cmd

def registerCommand(keyList, pre=None,pro=None,post=None, showInHelp=True, profile = None):
    #check cmd and keylist
    raiseIfInvalidKeyList(keyList, RegisterException,"Loader", "registerCommand")
    loader = _local_getAndInitCallerModule(profile)
    
    if loader.TempPrefix is not None:
        name = " ".join(loader.TempPrefix) + " " + " ".join(keyList)
    else:
        name = " ".join(keyList)
        
    cmd = UniCommand(name, pre,pro,post, showInHelp)
    
    loader.addCmd(keyList, cmd)
    return cmd

def registerAndCreateEmptyMultiCommand(keyList, showInHelp=True, profile = None):
    #check cmd and keylist
    raiseIfInvalidKeyList(keyList, RegisterException,"Loader", "registerCreateMultiCommand")
    loader = _local_getAndInitCallerModule(profile)
    
    if loader.TempPrefix is not None:
        name = " ".join(loader.TempPrefix) + " " + " ".join(keyList)
    else:
        name = " ".join(keyList)
    
    cmd = MultiCommand(name, showInHelp)
    loader.addCmd(keyList, cmd)

    return cmd

def registerStopHelpTraversalAt(keyList=(),profile = None):
    #check cmd and keylist
    raiseIfInvalidKeyList(keyList, RegisterException,"Loader", "registerCreateMultiCommand")
    loader = _local_getAndInitCallerModule(profile)
    
    if loader.TempPrefix is not None:
        keyListTemp = list(loader.TempPrefix)
        keyListTemp.extend(keyList)
    else:
        keyListTemp = keyList
    
    loader.stoplist.append(keyListTemp)
    
class CommandLoader(AbstractLoader):
    def __init__(self, prefix=()):
        AbstractLoader.__init__(self)
    
        self.prefix     = prefix
        self.cmdDict    = {}
        self.TempPrefix = None
        self.stoplist   = []
        
        self.loadedCommand       = None
        self.loadedStopTraversal = None
        
    def load(self, parameterManager, profile = None):
        self.loadedCommand       = []
        self.loadedStopTraversal = []
        
        AbstractLoader.load(self, parameterManager, profile)
        param = parameterManager.environment.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY, perfectMatch = True)
        
        if param is None:
            raise LoadException("(CommandLoader) load, fail to load command because parameter has not a levelTries item")
            
        mltries = param.getValue()
        exceptions = ListOfException()
    
        #add command
        for keyList, cmd in self.cmdDict.iteritems():
            key = list(self.prefix)
            key.extend(keyList)
            try:
                mltries.insert(key, cmd)
                self.loadedCommand.append(key)
            except triesException as te:
                exceptions.addException( LoadException("fail to insert key '"+str(" ".join(key))+"' in multi tries: "+str(te)))

        #stop traversal
        for stop in self.stoplist:
            key = list(self.prefix)
            key.extend(stop)
        
            try:
                if mltries.isStopTraversal(key):
                    continue
            
                mltries.setStopTraversal(key, True)
                self.loadedStopTraversal.append(key)
            except triesException as te:
                exceptions.addException( LoadException("fail to disable traversal for key list '"+str(" ".join(stop))+"' in multi tries: "+str(te)))
                
        #raise error list
        if exceptions.isThrowable():
            raise exceptions

    def unload(self, parameterManager, profile = None):
        AbstractLoader.unload(self, parameterManager, profile)
        param = parameterManager.environment.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY, perfectMatch = True)
        
        if param is None:
            raise LoadException("(CommandLoader) load, fail to load command because parameter has not a levelTries item")
            
        mltries = param.getValue()
        exceptions = ListOfException()
    
        for key in self.loadedCommand:           
            try:
                mltries.remove(key)
            except triesException as te:
                exceptions.addException( LoadException( "fail to remove key '"+str(" ".join(key))+"' in multi tries: "+str(te)))
        
        #remove stop traversal
        for key in self.loadedStopTraversal:
            
            #if key does not exist, continue
            try:
                searchResult = mltries.searchNode(key, True)
                
                if searchResult is None or not searchResult.isPathFound():
                    continue
                
            except triesException as te:
                exceptions.addException( LoadException("fail to disable traversal for key list '"+str(" ".join(key))+"' in multi tries: "+str(te)))
                continue
        
            try:
                mltries.setStopTraversal(key, False)
            except triesException as te:
                exceptions.addException( LoadException("fail to disable traversal for key list '"+str(" ".join(key))+"' in multi tries: "+str(te)))
        
        #raise error list
        if exceptions.isThrowable():
            raise exceptions 
        
    def addCmd(self, keyList, cmd):
        if self.TempPrefix is not None:
            prefix = list(self.TempPrefix)
            prefix.extend(keyList)
        else:
            prefix = keyList
    
        self.cmdDict[tuple(prefix)] = cmd 
