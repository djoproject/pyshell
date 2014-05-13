#!/usr/bin/python
# -*- coding: utf-8 -*-

from command import MultiCommand, UniCommand
from exception import LoadException
import inspect

#TODO
    #be able to load a module
    #be able to load subpart of a module
    #be able to set temporary prefix

def _raiseIfInvalidKeyList(keyList, methName):
    if not hasattr(keyList,"__iter__"):
        raise LoadException("(Loader) "+methName+", keyList is not iterable")

    for key in keyList:
        if type(key) != str and type(key) != unicode:
            raise LoadException("(Loader) "+methName+", only string or unicode key are allowed")

        if len(key) == 0:
            raise LoadException("(Loader) "+methName+", empty key is not allowed")

def _getAndInitCallerModule():
    frm = inspect.stack()[2]
    mod = inspect.getmodule(frm[0])

    if hasattr(mod,"_loader"):
        return mod._loader
    else:
        loader = Loader()
        mod._loader = loader
        return loader

def registerSetGlobalPrefix(keyList):
    loader = _getAndInitCallerModule()
    _raiseIfInvalidKeyList(keyList, "registerSetGlobalPrefix")
    loader.prefix = keyList

def registerAnInstanciatedCommand(keyList, cmd):
    loader = _getAndInitCallerModule()

    #must be a multiCmd
    if not isinstance(cmd, MultiCommand):
        raise LoadException("(Loader) addInstanciatedCommand, cmd must be an instance of MultiCommand")

    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "addInstanciatedCommand")

    loader.cmdDict[" ".join(keyList)] = (keyList, cmd,)

    return cmd

def registerCommand(keyList, pre=None,pro=None,post=None, showInHelp=True):
    loader = _getAndInitCallerModule()

    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "addCommand")

    name = " ".join(keyList)
    cmd = UniCommand(name, pre,pro,post, showInHelp)
    loader.cmdDict[name] = (keyList,cmd,)
    return cmd

def registerCreateMultiCommand(keyList, showInHelp=True):
    loader = _getAndInitCallerModule()

    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "createMultiCommand")

    name = " ".join(keyList)
    cmd = MultiCommand(name, showInHelp)
    loader.cmdDict[name] = (keyList, cmd,)

    return cmd

class Loader(object):
    def __init__(self, prefix=()):
        self.prefix  = prefix
        self.cmdDict = {}        
    
    def _load(self, mltries):
        for k,v in self.cmdDict.iteritems():
            keyList, cmd = v
            key = list(self.prefix)
            key.extend(keyList)
            mltries.insert(key, cmd)
        
    def _unload(self, mltries):
        for k,v in self.cmdDict.iteritems():
            keyList, cmd = v
            key = list(self.prefix)
            key.extend(keyList)
            mltries.remove(key)
        
    def _reload(self, mltries):
        self.unload(mltries)
        self.load(mltries)
