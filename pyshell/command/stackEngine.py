#!/usr/bin/python
# -*- coding: utf-8 -*-

#TODO
	#need to create stack iterator/generator/... ?

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

    ### TOP meth ###
    def top(self):
        return self[-1]
    
    def dataOnTop(self):
        return self[-1][0]
        
    def pathOnTop(self):
        return self[-1][1]
        
    def typeOnTop(self):
        return self[-1][2]
        
    def enablingMapOnTop(self):
        return self[-1][3]
        
    def cmdIndexOnTop(self):
        return len(self[-1][1]) - 1
        
    def cmdLengthOnTop(self):
        return len(self[-1][1])
        
    def getCmdOnTop(self, cmdList):
        return self.engine.cmdList[len(self[-1][1])-1]
    
    def subCmdLengthOnTop(self, cmdList):
        return len(self.engine.cmdList[len(self[-1][1])-1])
        
    def subCmdIndexOnTop(self):
        return self[-1][1][-1]
    
    ### INDEX meth ###
    def dataOnIndex(self, index):
        return self[index][0]
        
    def pathOnIndex(self, index):
        return self[index][1]
        
    def typeOnIndex(self, index):
        return self[index][2]
        
    def enablingMapOnIndex(self, index):
        return self[index][3]
        
    def cmdIndexOnIndex(self, index):
        return len(self[index][1]) - 1
        
    def getCmdOnIndex(self, index, cmdList):
        return self.engine.cmdList[len(self[index][1])-1]
    
    def getIndexBasedXRange(self):
        return xrange(0,len(self),1)

    def subCmdLengthOnIndex(self, index, cmdList):
        return len(self.engine.cmdList[len(self[index][1])-1])
    
    ### DEPTh meth ###
    def itemOnDepth(self, depth):
        return self[len(self)-1-depth]
    
    def dataOnDepth(self, depth):
        return self[len(self)-1-depth][0]
        
    def pathOnDepth(self, depth):
        return self[len(self)-1-depth][1]
        
    def typeOnDepth(self, depth):
        return self[len(self)-1-depth][2]
        
    def enablingMapOnDepth(self, depth):
        return self[len(self)-1-depth][3]
        
    def cmdIndexOnDepth(self, depth):
        return len(self[len(self)-1-depth][1]) - 1
        
    def getCmdOnDepth(self, depth, cmdList):
        return self.engine.cmdList[len(self[len(self)-1-depth][1])-1]
    
    ### MISC meth ###
    def getCmdLength(indexOnStack, cmdList):
        return len(cmdList[len(self[indexOnStack][1])-1])
