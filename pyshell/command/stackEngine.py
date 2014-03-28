#!/usr/bin/python
# -*- coding: utf-8 -*-

#TODO
	#need to create stack iterator/generator/... ?

from exception import *

class engineStack(list):
    def push(self, data, cmdPath, instructionType, cmdMap = None):
        self.append([(data, cmdPath, instructionType,cmdMap) ])
        
    def raiseIfEmpty(self, methName = None):
        if len(self) == 0:
            if methName == None:
                raise executionException("(engine) engineStack, no item on the stack")
            else:
                raise executionException("(engine) "+cmdName+", no item on the stack")
    
    ### SIZE meth ###
    def size(self):
        return len(self)

    def isEmpty(self):
        return len(self) == 0

    def isLastStackItem(self):
        return len(self.stack) == 1

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
        #else: #TODO cause recurisvity...
        #    return self.name

        if name not in ["data", "path", "type", "enablingMap", "cmdIndex", "cmdLength", "item", "getCmd", "subCmdLength", "subCmdIndex"]:
            pass #TODO raise

        methToCall  = getattr(self,name)

        def meth(*args):
            if index == None:
                if len(args) == 0:
                    pass #TODO raise

                lindex = int(args[0])
            else:
                lindex = index

            if sub != None:
                lindex = sub - lindex
            
            args.insert(0,lindex)
            methToCall(*args)

        return meth


