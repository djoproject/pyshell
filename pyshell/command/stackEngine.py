#!/usr/bin/python
# -*- coding: utf-8 -*-

#TODO
	#need to create stack iterator/generator/... ?

from exception import *

class engineStack(list):
    def push(self, data, cmdPath, instructionType, cmdMap = None):
        self.append((data, cmdPath, instructionType,cmdMap,))
        
    def raiseIfEmpty(self, methName = None):
        if len(self) == 0:
            if methName == None:
                raise executionException("(engine) engineStack, no item on the stack")
            else:
                raise executionException("(engine) "+methName+", no item on the stack")
    
    ### SIZE meth ###
    def size(self):
        return len(self)

    def isEmpty(self):
        return len(self) == 0

    def isLastStackItem(self):
        return len(self) == 1

    ### 
    def data(self, index):
        return self[index][0]

    def path(self, index):
        return self[index][1]

    def type(self, index):
        return self[index][2]

    def enablingMap(self, index):
        return self[index][3]

    def cmdIndex(self, index):
        return len(self[index][1]) - 1

    def cmdLength(self, index):
        return len(self[index][1])

    def item(self, index):
        return self[index]

    def getCmd(self, index, cmdList):
        return cmdList[len(self[index][1])-1]

    def subCmdLength(self, index, cmdList):
        return len(cmdList[len(self[index][1])-1])

    def subCmdIndex(self, index):
        return self[index][1][-1]

    def setEnableMap(self,index,newMap):
        current = self[index]
        self[index] = (current[0], current[1], current[2], newMap, )

	def setPath(self, index, path):
		self[index] = (current[0], path, current[2], current[3], )

	def setType(self, index, newType):
		self[index] = (current[0], current[1], newType, current[3], )

    ### MISC meth ###

    def top(self):
        return self[-1]

    def getIndexBasedXRange(self):
        return xrange(0,len(self),1)

    ##########
    def __getattr__(self, name):
        if name.endswith("OnTop"):
            index = -1
            sub   = None
            name = name[:-5]
        elif name.endswith("OnIndex"):
            index = None
            sub   = None
            name = name[:-7]
        elif name.endswith("OnDepth"):
            index = None
            sub = len(self)-1
            name = name[:-7]
        else:
            #return getattr(self,name)
            return object.__getattribute__(self, name)

        if name not in ["data", "path", "type", "enablingMap", "cmdIndex", "cmdLength", "item", "getCmd", "subCmdLength", "subCmdIndex", "setEnableMap", "setPath", "setType"]:
            raise executionException("(engineStack) __getattr__, try to get an unallowed meth")

        methToCall  = getattr(self,name)

        def meth(*args):
            if index == None:
                if len(args) > 0:
                    lindex = int(args[0])
                    startIndex = 1
                else:
                    #if index is not define, no need to do compute anything else
                    return methToCall(*args)
            else:
                startIndex = 0
                lindex = index

            if sub != None:
                lindex = sub - lindex

            nargs = [lindex]
            nargs.extend(args[startIndex:])
            return methToCall(*nargs)

        return meth


