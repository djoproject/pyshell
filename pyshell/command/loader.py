#!/usr/bin/python
# -*- coding: utf-8 -*-

from command import MultiCommand
from exception import LoadException

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
