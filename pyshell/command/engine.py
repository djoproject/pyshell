#!/usr/bin/python
# -*- coding: utf-8 -*-

from command import MultiOutput

#TODO
    #voir les notes dans le fichier TODO

    #at this moment, multioutput is juste a list... 
        #must stay a list
        #TODO check if the multioutput is not converted into a simple list in the process
            #because there is a risk to lose the cmd limit
            

DEFAULT_EXECUTION_LIMIT = 255
    
class engineV3(object):
### INIT ###
    def __init__(self, cmdList, env=None):
        #cmd must be a not empty list
        if cmdList == None or not isinstance(cmdList, list) or len(cmdList) ==0:
            raise executionInitException("(engine) init, command list is not a valid list")

        #reset the commands
        for c in cmdList:
            if not isinstance(c, MultiCommand):
                raise executionInitException("(engine) init, a object in the command list is not a MultiCommand instance, got <"+str(type(c))+">")
                
            c.reset()
        
        self.cmdList = cmdList #list of MultiCommand
        
        #check env variable
        if env == None:
            self.env = {}
        elif isinstance(env, dict):
            self.env  =env
        else:
            raise executionInitException("(engine) init, env must be a dictionnary or None, got <"+str(type(env))+">")

        #init stack
        self.stack = [([None], [0], 0,) ]
    
### COMMAND special meth ###
    
    def skipNextCommand(self, skipCount=1):
        if len(self.stack) == 0: 
            raise executionException("(engine) flushArgs, no item on the stack")
            
        self.stack[-1][1][-1] += skipCount
    
    def flushArgs(self):
        if len(self.stack) == 0: 
            raise executionException("(engine) flushArgs, no item on the stack")
    
        cmdID = len(self.stack[-1][1]) -1
        
        if cmdID >= len(self.cmdList):
            raise executionException("(engine) flushArgs, invalid command index")
            
        self.cmdList[cmdID].flushArgs()
    
    def addCommand(self, cmd, onlyAddOnce = True, useArgs = True):    
        #is there still some items on the stack ?
        if len(self.stack) == 0: 
            raise executionException("(engine) addCommand, no item on the stack")
    
        #compute command index
        cmdID = len(self.stack[-1][1]) -1
        
        if cmdID >= len(self.cmdList):
            raise executionException("(engine) addCommand, invalid command index")
        
        #check if there is not a command limit on these data bunch
        topData = self.stack[-1][0]
        
        currentStartCmdIndex = 0
        if hasattr(topData,"cmdStartIndex"): #is there already a cmd start index ?
            currentStartCmdIndex = topData.cmdStartIndex
        
        currentStopCmdIndex = None
        if hasattr(topData,"cmdStopIndex"): #is there already a cmd stop index ?
            currentStopDataIndex = topData.cmdStopIndex
        
        newCmdIndex = len(self.cmdList[cmdID])
        
        if newCmdIndex < currentStartCmdIndex or (currentStopCmdIndex != None and currentStopCmdIndex < newCmdIndex):
            raise executionException("(engine) addCommand, the command bounds on this data do not enclose the new command") 
        
        
        #add the sub command
        self.cmdList[cmdID].addDynamicCommand(cmd, onlyAddOnce, useArgs)
    
### DATA special meth ###
    
    def flushData(self):
        if len(self.stack) == 0: 
            raise executionException("(engine) flushData, no item on the stack")
    
        data = self.stack[-1][0]
        del data[:]
    
    def addData(self, newdata, offset=0):    
        if len(self.stack) == 0: 
            raise executionException("(engine) addData, no item on the stack")
    
        data = self.stack[-1][0]
        data.insert(offset,newdata)
    
    def setData(self, newdata, offset=0):
        if len(self.stack) == 0: 
            raise executionException("(engine) setData, no item on the stack")
    
        data = self.stack[-1][0]
        
        if offset >= len(data):
            raise executionException("(engine) setData, offset out of bound, the offset <"+str(offset)+"> can be reach because the data length is <"+str(len(data))+">")
        
        data[offset] = newdata
    
    def mergeDataOnStack(count = 2, firstCmd = 0, cmdLength = None):
        pass #TODO
            #the path must be the same for each item on stack
            #what about the starting data index ?
                #don't care ? or set the current. of the top? what about the current of the second top ?
                    #so the current must be in the bounds
    
    def setDataCmdRange(self, startData = 0, dataLength=None, firstCmd = 0, cmdLength = None):
        if len(self.stack) == 0: 
            raise executionException("(engine) setDataCmdRange, no item on the stack")
    
        #get the data list at the top of the stack
        topData = self.stack[-1][0]
        
        ## is data index valid? ##
        if startData > (len(topData)-1): #start index must be in the current data range
            raise executionException("(engine) setDataCmdRange, startData index is not in the data bounds")
            
        if dataLength != None and dataLength < 1: #data range must be None or bigger than zero
            return
        
        ## is cmd index valid ? ##
        currentCmdLength = len(self.cmdList[self.stack[-1][1]])
    
        #the new index must be in the cmd range
        if firstCmd >= currentCmdLength:
            raise executionException("(engine) setDataCmdRange, firstCmd index is not in the command bound") 
        
        newStopIndex = None
        if cmdLength != None:
            if (firstCmd+cmdLength) > currentCmdLength:
                raise executionException("(engine) setDataCmdRange, cmdLength is bigger than the command list size")
                    #we can not set cmdLength to None because if the user set a limit then add new command
                    #is different of set a None limit then add command
            
            newStopIndex = firstCmd+cmdLength-1
        
        #the current data index must be in the cmd range
        currentCmdIndex = top[-1][1][-1]
        if currentCmdIndex < firstCmd or (cmdLength != None and (firstCmd+cmdLength-1) < currentCmdIndex):
            raise executionException("(engine) setDataCmdRange, the bounds must enclose the current cmd index") 
        
        ## get current limit ##
        currentStartCmdIndex = 0
        if hasattr(topData,"cmdStartIndex"): #is there already a cmd start index ?
            currentStartCmdIndex = topData.cmdStartIndex
        
        currentStopCmdIndex = None
        if hasattr(topData,"cmdStopIndex"): #is there already a cmd stop index ?
            currentStopDataIndex = topData.cmdStopIndex
        
        if currentStartCmdIndex == firstCmd and currentStopCmdIndex == newStopIndex:
            return #nothing to do, the limit are already set
        
        #the whole data is used? no need to split ?
        top = self.stack.pop()
        
        #TODO compressible dans un truc comme ça
            #TODO doivent etre empile dans l'autre sens...
        """#0 to startData-1 (set parent cmd limit), last inserted on stack
        dataBunch = MultiOutput(top[0][0:startData])
        if len(dataBunch) > 0:
            dataBunch.cmdStartIndex = currentStartCmdIndex
            dataBunch.cmdStopIndex  = currentStopDataIndex
            self.stack.append( (dataBunch, top[1], top[2], ) )
        
        #startData to startData+dataLength-1 (+ set cmd limit), second inserted on stack
        if dataLength != None:
            dataBunch = MultiOutput(top[0][startData:(startData+dataLength)])
        else:
            dataBunch = MultiOutput(top[0][startData:])
        dataBunch.cmdStartIndex = firstCmd
        dataBunch.cmdStopIndex  = newStopIndex
        self.stack.append( (dataBunch, top[1], top[2], ) )
        
        if dataLength != None:
            #startData+dataLength to None (set parent cmd limit), first inserted on stack
            dataBunch = MultiOutput(top[0][(startData+dataLength):])
            dataBunch.cmdStartIndex = currentStartCmdIndex
            dataBunch.cmdStopIndex  = currentStopDataIndex
            self.stack.append( (dataBunch, top[1], top[2], ) )"""
        
        if startData == 0:
            if (dataLength == None or dataLength >= len(topData)): #no data limite
                #0 to None (+ set cmd limit), update on stack
                dataBunch = MultiOutput(top[0])
                dataBunch.cmdStartIndex = firstCmd
                dataBunch.cmdStopIndex  = newStopIndex
                self.stack.append( (dataBunch, top[1], top[2], ) )
            else:
                #0 to startData+dataLength-1 (+ set cmd limit), last inserted on stack
                dataBunch = MultiOutput(top[0][0:(startData+dataLength)])
                dataBunch.cmdStartIndex = firstCmd
                dataBunch.cmdStopIndex  = newStopIndex
                self.stack.append( (dataBunch, top[1], top[2], ) )
                
                #startData+dataLength to None (set parent cmd limit), first inserted on stack
                dataBunch = MultiOutput(top[(startData+dataLength):])
                dataBunch.cmdStartIndex = currentStartCmdIndex
                dataBunch.cmdStopIndex  = currentStopDataIndex
                self.stack.append( (dataBunch, top[1], top[2], ) )
        else:
            if (dataLength == None or dataLength >= len(topData)):
                #0 to startData-1 (set parent cmd limit), last inserted on stack
                dataBunch = MultiOutput(top[0][0:startData])
                dataBunch.cmdStartIndex = currentStartCmdIndex
                dataBunch.cmdStopIndex  = currentStopDataIndex
                self.stack.append( (dataBunch, top[1], top[2], ) )
                
                #startData to None (+ set cmd limit), first inserted on stack
                dataBunch = MultiOutput(top[0][startData:])
                dataBunch.cmdStartIndex = firstCmd
                dataBunch.cmdStopIndex  = newStopIndex
                self.stack.append( (dataBunch, top[1], top[2], ) )
            else:
                #0 to startData-1 (set parent cmd limit), last inserted on stack
                dataBunch = MultiOutput(top[0][0:startData])
                dataBunch.cmdStartIndex = currentStartCmdIndex
                dataBunch.cmdStopIndex  = currentStopDataIndex
                self.stack.append( (dataBunch, top[1], top[2], ) )
                
                #startData to startData+dataLength-1 (+ set cmd limit), second inserted on stack
                dataBunch = MultiOutput(top[0][startData:(startData+dataLength)])
                dataBunch.cmdStartIndex = firstCmd
                dataBunch.cmdStopIndex  = newStopIndex
                self.stack.append( (dataBunch, top[1], top[2], ) )
                
                #startData+dataLength to None (set parent cmd limit), first inserted on stack
                dataBunch = MultiOutput(top[0][(startData+dataLength):])
                dataBunch.cmdStartIndex = currentStartCmdIndex
                dataBunch.cmdStopIndex  = currentStopDataIndex
                self.stack.append( (dataBunch, top[1], top[2], ) )
    
    def getData(self, offset=0):
        if len(self.stack) == 0: 
            raise executionException("(engine) getData, no item on the stack")
            
        data = self.stack[-1][0]
        
        if offset >= len(data):
            raise executionException("(engine) getData, offset out of bound, the offset <"+str(offset)+"> can be reach because the data length is <"+str(len(data))+">")
        
        return data[offset]
        
    def hasNextData(self):
        return self.getRemainingDataCount() > 0
        
    def getRemainingDataCount(self):
        if len(self.stack) == 0:
            return 0

        return len(self.stack[-1][0])

### VARIOUS meth ###

    def getEnv(self):
        return self.env
    
### ENGINE meth ###
    
    def execute(self):
        #consume stack
        while len(self.stack) != 0: #while there is some item into the stack
            
            ### EXTRACT DATA FROM STACK ###
            top     = self.stack[-1]#.pop()
            #top[0] contain the current data of this item
            #top[1] contain the command path
            #top[2] contain the process type to execute
            
            cmd             = self.cmdList[len(top[1]) -1]
            subcmd, useArgs = cmd[top[1][-1]]
            
            ### EXECUTE command ###
            to_stack = None #prepare the var to push on the stack, if the var keep the none value, nothing will be stacked
            try:
                ## PRE PROCESS
                if top[2] == 0: #pre
                    r = self.executeMethod(subcmd.preProcess, top, useArgs)
                    subcmd.preCount += 1
                    
                    #manage result
                    if len(top[1]) == len(self.cmdList): #no child, next step will be a process
                        to_stack = (r, top[1], 1, )
                    else: #there are some child, next step will be another preprocess
                        new_path = top[1][:]
                        new_path.append(0)
                        to_stack = (r, new_path, 0, )
                
                ## PROCESS ##
                elif top[2] == 1: #pro
                    r = self.executeMethod(subcmd.process, top, useArgs)
                    subcmd.proCount += 1
                    
                    #manage result
                    to_stack = (r, top[1], 2,)
                
                ## POST PROCESS ##
                elif top[2] == 0: #post
                    r = self.executeMethod(subcmd.postProcess, top, useArgs)
                    subcmd.postCount += 1
                    
                    #manage result
                    if len(top[1]) > 1: #not on the root node
                         to_stack = (r, top[1][:-1], 2,)
                    
                else:
                    raise executionException("(engine) execute, unknwon process command <"+str(top[2])+">")
            
                if subcmd.preCount > DEFAULT_EXECUTION_LIMIT or subcmd.proCount > DEFAULT_EXECUTION_LIMIT or subcmd.postCount > DEFAULT_EXECUTION_LIMIT :
                    raise executionException("(engine) execute, this subcommand reach the execution limit count")
            
            except BaseException as e: #catch any execution exception, add more information then raise again
                e.cmd         = cmd
                e.subCmdIndex = top[1][-1]
                e.data        = self.stack[-1][0][0]
                
                raise e
            
            ### MANAGE STACK, need to repush the current item ? ###
            self.stack.pop()
            if top[2] == 1 or top[2] == 2: #process or postprocess ?
                if len(top[0]) > 1: #still data to execute ?
                    self.stack.append(  (top[0][1:],top[1],top[2],)  ) #remove the last used data and push on the stack
            else:# top[2] == 0 #preprocess
                
                #compute the limit of command to execute
                if hasattr(top[0],"cmdStopIndex") and top[0].cmdStopIndex != None:
                    limit = top[0].cmdStopIndex
                else:
                    limit = len(cmd)-1
            
                if top[1][-1] < limit: #still child to execute ?
                    if len(top[0]) > 0: #still data to execute ?
                        top[1][-1] += 1 #select the nex child id
                        self.stack.append(  (top[0],top[1],top[2],)  ) #push on the stack again
                else: #every child has been executed with this data, the current is the last one
                    if len(top[0]) > 1: #still data to execute ?
                    
                        #compute the first command to execute
                        if hasattr(top[0],"cmdStartIndex") and top[0].cmdStartIndex != None:
                            starting = top[0].cmdStartIndex
                        else:
                            starting = 0
                    
                        top[1][-1] = starting #select the first child
                        self.stack.append(  (top[0][1:],top[1],top[2],)  ) #remove the last used data and push on the stack
            
            ### STACK THE RESULT of the current process if needed ###
            if to_stack != None:
                self.stack.append(to_stack)
                
    def executeMethod(self, cmd,subcmd, stackState, useArgs):
        nextData = stackState[0][0]

        #prepare data
        args = cmd.getArgs()
        if args != None and useArgs:
            if nextData != None:
                args = args[:]
                args.extend(nextData)
        elif nextData != None:
            args = nextData
        else:
            args = []

        #execute checker
        if hasattr(cmd, "checker"):         
            data = cmd.checker.checkArgs(args, self)
        else:
            data = {}

        #execute Xprocess
        r = subcmd(**data)
        
        #r must be a multi output
        if not isinstance(r, MultiOutput):
            return [r]

        return r


