#!/usr/bin/python
# -*- coding: utf-8 -*-

from command import MultiCommand
from exception import LoadException

#XXX BRAINSTORMING XXX
    #must be able to load, unload, reload
    #could be single or several loader in the same package
    #must be used as simple as possible
        #if its possible to avoid a class creation/extension
    
#XXX SOLUTION XXX
    #1) just a method call, a kind of register
        #how differanciate a package from another ?
        #need to have a global list, in the addons.__init__ ?
            #what about multiple addons directory ?
                #WRONG WAY, need a generic solution
        
        #could register create a new variable in the module ?
            #need to access to the caller module, it could be possible
            #http://stackoverflow.com/questions/1095543/get-name-of-calling-functions-module-in-python

_raiseIfInvalidKeyList(keyList, methName):
    if not hasattr(keyList,"__iter__"):
        raise LoadException("(Loader) "+methName+", keyList is not iterable")

    for key in keyList:
        if type(key) != str and type(key) != unicode:
            raise LoadException("(Loader) "+methName+", only string or unicode key are allowed")

        if len(key) == 0:
            raise LoadException("(Loader) "+methName+", empty key is not allowed")

class Loader(object):
    def __init__(self, prefix=()):
        self.prefix  = prefix
        self.cmdDict = {}

    def addInstanciatedCommand(self, keyList, cmd):
        #must be a multiCmd
        if not isinstance(cmd, MultiCommand):
            raise LoadException("(Loader) addInstanciatedCommand, cmd must be an instance of MultiCommand")

        #check cmd and keylist
        _raiseIfInvalidKeyList(keyList, "addInstanciatedCommand")
    
        self.cmdDict[" ".join(keyList)] = (keyList, cmd,)
    
    def addCommand(self, keyList, pre=None,pro=None,post=None, showInHelp=True):
        #check cmd and keylist
        _raiseIfInvalidKeyList(keyList, "addCommand")

        name = " ".join(keyList)
        self.cmdDict[name] = (keyList,UniCommand(name, pre,pro,post, showInHelp),)
        
    def createMultiCommand(self, keyList, showInHelp=True):
        #check cmd and keylist
        _raiseIfInvalidKeyList(keyList, "createMultiCommand")

        name = " ".join(keyList)
        cmd = MultiCommand(name, showInHelp)
        self.cmdDict[name] = (keyList, cmd,)

        return cmd
    
    def _load(self, mltries):
        for k,v in self.cmdDict:
            keyList, cmd = v
            key = list(self.prefix)
            key.extend(keyList)
            mltries.insert(key, cmd)
        
    def _unload(self, mltries):
        for k,v in self.cmdDict:
            keyList, cmd = v
            key = list(self.prefix)
            key.extend(keyList)
            mltries.remove(key)
        
    def _reload(self, mltries):
        self.unload(mltries)
        self.load(mltries)
