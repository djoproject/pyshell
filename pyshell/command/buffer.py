#!/usr/bin/python

class InputManager(object):
    def __init__(self,processCount = 1):
        self.inputList = []
        self.processCount = processCount
        self.work = 0
        for i in range(0,(processCount*2)+1):
            self.inputList.append([])
    
    def hasStillWorkToDo(self):
        return self.work != 0
    
    ### GENERIC ###
    def hasInput(self,indice):
        return len(self.inputList[indice]) > 0
        
    def getNextInput(self,indice):
        self.work -=1
        ret = self.inputList[indice][0]
        self.inputList[indice] = self.inputList[indice][1:]
        return ret
    
    def addOutput(self,indice,output):
        #manage multioutput
        if isinstance(output,MultiOutput):
            for o in output:
                self.inputList[indice].append(o)
                self.work +=1
        else:
            self.inputList[indice].append(output)
            self.work +=1
    
    ### PRE ###
    def getNextPreProcess(self):
        for i in range(0,self.processCount):
            if len(self.inputList[i]) != 0:
                return i

        return -1
        
    def hasPreProcessInput(self,indice):
        return self.hasInput(indice)
    
    def getNextPreProcessInput(self,indice):
        return self.getNextInput(indice)
        
    def addOutputToNextPreProcess(self,indice,output):
        self.addOutput(indice+1,output)
        
    def getPreProcessInputBuffer(self,indice):
        return self.inputList[indice]
    
    ### PROCESS ###
    def hasProcessInput(self):
        return self.hasInput(self.processCount)
    
    def getNextProcessInput(self):
        return self.getNextInput(self.processCount)
        
    def addProcessOutput(self,output):
        self.addOutput(self.processCount+1,output)
    
    def getProcessInputBuffer(self):
        return self.inputList[self.processCount+1]
    
    ### POST ###
    def getNextPostProcess(self):
        for i in range(0,self.processCount):
            if len(self.inputList[i + self.processCount + 1]) != 0:
                return i

        return -1

    def hasPostProcessInput(self,indice):
        return self.hasInput(self.processCount+1+indice)
        
    def getNextPostProcessInput(self,indice):
        return self.getNextInput(self.processCount+1+indice)
        
    def addOutputToNextPostProcess(self,indice,output):
        if (self.processCount+1+indice+1) < len(self.inputList):
            self.addOutput(self.processCount+1+indice+1,output)
    
    def getPostProcessInputBuffer(self,indice):
        return self.inputList[self.processCount+1+indice]
    
    def __str__(self):
        return str(self.inputList)
