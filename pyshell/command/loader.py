#!/usr/bin/python
# -*- coding: utf-8 -*-

class loader(object):
    def __init__(self, prefix=()):
        self.prefix  = prefix
        self.cmdDict = {}

    def addCommand(self, keyList, cmd):
        #TODO check cmd and keylist
    
        self.cmdDict[" ".join(keyList)] = (keyList, cmd,)
    
    def addCommand(self, keyList, pre=None,pro=None,post=None):
        pass #TODO create and add a singlecommand
        
    def createMultiCommand(self, keyList):
        pass #TODO return an empty multicommand

    #TODO create more command adder
    
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
