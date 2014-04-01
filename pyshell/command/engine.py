#!/usr/bin/python
# -*- coding: utf-8 -*-

### STACK PROPERTIES ###
    #TODO

from command import MultiOutput, MultiCommand
from exception import *
from stackEngine import engineStack
from utils import *

#TODO
    #voir les notes dans le fichier TODO
    #be able to split/merge anywhere on the stack, not only on the top
    #eviter de redefinir directement des items sur la stack ou dans les command
        #la structure pourrait encore changer, et il faudrait rechanger l'ensemble des lignes de code...
        #exemple, faire un setMap pour la stack, un setSubCmdState pour les commands, ...
    #check map and path arguments if not done
        #build a method to check path
    #be carefull for an insertion on the stack(with engine for example) after an inject
        #if some data are insert later than the next item to stack in the engine
    #update the index in disable method for every needed item on the stack
    #compute the first index in the inject method, if a map is given
        #same for split/merge

DEFAULT_EXECUTION_LIMIT = 255
PREPROCESS_INSTRUCTION  = 0
PROCESS_INSTRUCTION     = 1
POSTPROCESS_INSTRUCTION = 2

class engineV3(object):
    ### INIT ###
    def __init__(self, cmdList, env=None):#, cmdControlMapping=True):
        #cmd must be a not empty list
        if cmdList == None or not isinstance(cmdList, list) or len(cmdList) == 0:
            raise executionInitException("(engine) init, command list is not a valid populated list")

        #reset every commands
        for c in cmdList:
            if not isinstance(c, MultiCommand):#only the MultiCommand are allowed in the list
                raise executionInitException("(engine) init, a object in the command list is not a MultiCommand instance, got <"+str(type(c))+">")
            
            if len(c) == 0: #empty multi command are not allowed
                raise executionInitException("(engine) init, a command is empty")
            
            #reset the information stored in the command from a previous execution
            c.reset()
        
        self.cmdList = cmdList #list of MultiCommand
        
        #check env variable
        if env == None:
            self.env = {}
        elif isinstance(env, dict):
            self.env  = env
        else:
            raise executionInitException("(engine) init, env must be a dictionnary or None, got <"+str(type(env))+">")

        self.stack          = engineStack()
        self._isInProcess   = False
        self.selfkillreason = None 

        #init stack with a None data, on the subcmd 0 of the command 0, with a preprocess action
        self.stack.push([None], [0], PREPROCESS_INSTRUCTION) #init data to start the engine

    def _getTheIndexWhereToStartTheSearch(self,processType):
        #check processType, must be pre/pro/post
        if processType != PREPROCESS_INSTRUCTION and processType != PROCESS_INSTRUCTION and processType != POSTPROCESS_INSTRUCTION:
            raise executionException("(engine) _getTheIndexWhereToStartTheSearch, unknown process type : "+str(processType)) 
                    
        #check stack size
        stackLength = self.stack.size()

        #if stack is empty, the new data can be directly inserted
        if stackLength == 0:
            return 0
        
        #index will store the higher element of asked type, or the last of one of the previous type
        index = stackLength - 1
        
        #find the place to start the lookup
        if processType != POSTPROCESS_INSTRUCTION:
            for i in range(0, stackLength):
                index = stackLength - i - 1
            
                if self.stack[index][2] == POSTPROCESS_INSTRUCTION or (self.stack[index][2] == PROCESS_INSTRUCTION and processType == PREPROCESS_INSTRUCTION):
                    continue
                    
                break
                
        else: #POSTPROCESS_INSTRUCTION
            if self.stack[-1][2] != POSTPROCESS_INSTRUCTION:
                return stackLength

    def _findIndexToInjectPre(self, cmdPath):
        #check command path
        isAValidIndex(self.cmdList, len(cmdPath)-1,"findIndexToInject", "command list")
        
        for i in range(0,len(cmdPath)):
            isAValidIndex(self.cmdList[i], cmdPath[i],"findIndexToInject", "sub command list")

        index = self._getTheIndexWhereToStartTheSearch(PREPROCESS_INSTRUCTION)
        
        #lookup
        to_ret = None
        while index >= 0:
            equals, sameLength, equalsCount, path1IsHigher = equalPath(self.stack[index][1], cmdPath)
            if equals or (sameLength and equalsCount == len(cmdPath)-1):
                if to_ret == None:
                    to_ret = []

                to_ret.append( (self.stack[index], index,))
            
            if to_ret != None:
                return to_ret

            if path1IsHigher:
                return ( (None, index+1,),)
            
            index -= 1 
            
        return ( (None, index+1,),)

    def _findIndexToInjectProOrPost(self, cmdPath, processType):
        if processType == PREPROCESS_INSTRUCTION:
            raise executionException("(engine) _findIndexToInjectProOrPost, can't use preprocess with this function, use _findIndexToInjectPre instead")

        #if PROCESS_INSTRUCTION, only root path are allowed
        if processType == PROCESS_INSTRUCTION and len(cmdPath) != len(self.cmdList):
            raise executionException("(engine) _findIndexToInjectProOrPost, can only insert data to the process of the last command") 

        #check command path
        isAValidIndex(self.cmdList, len(cmdPath)-1,"findIndexToInject", "command list")
        
        for i in range(0,len(cmdPath)):
            isAValidIndex(self.cmdList[i], cmdPath[i],"findIndexToInject", "sub command list")

        index = self._getTheIndexWhereToStartTheSearch(processType)
       
        #lookup
        while index >= 0 and self.stack[index][2] == processType:
            equals, sameLength, equalsCount, path1IsHigher = equalPath(self.stack[index][1], cmdPath)

            if equals:
                return self.stack[index], index
            
            if path1IsHigher:
                return None, index+1
            
            index -= 1 
            
        return None, index+1
    
    def injectDataProOrPos(self, data, cmdPath, processType, onlyAppend = False):
        obj, index = self._findIndexToInjectProOrPost(cmdPath, processType)
        
        if obj == None:
            #can only append ?
            if onlyAppend:
                raise executionException("(engine) injectDataProOrPos, there is no similar item on the stack and the system can only append, not create") 
            
            #insert a new object
            self.stack.insert(index, ([data], cmdPath[:], processType, None, ))
        
        else:
            obj[0].append(data)        
    
    def _injectDataPreToExecute(self, data, cmdPath, index, enablingMap = None, onlyAppend = False):
        itemCandidateList = self._findIndexToInjectPre(cmdPath, PREPROCESS_INSTRUCTION)

        #check map (is a list, valid length, only boolean value)
        if not isValidMap(enablingMap, len(self.cmdList[len(cmdPath)-1])):
            raise executionException("(engine) _injectDataPreToExecute, invalid map")

        if len(itemCandidateList) == 1 and itemCandidateList[0][0] == None:
            if onlyAppend:
                raise executionException("(engine) _injectDataPreToExecute, no corresponding item on the stack")
                
            #insert at index
            self.stack.insert(itemCandidateList[0][1], ([data], cmdPath[:], PREPROCESS_INSTRUCTION, enablingMap, ))

        else: #there ara already data with the same path
            #compare the map of the element at the top and the current map
                
            if equalMap(itemCandidateList[index][0][3], enablingMap):
                itemCandidateList[index][0][1].append(data)
            else:
                if onlyAppend:
                    raise executionException("(engine) _injectDataPreToExecute, no corresponding item found on the stack")
                
                #insert at index + 1
                self.stack.insert(itemCandidateList[index][1] + 1 + index, ([data], cmdPath[:], processType, enablingMap, ))
    
    def injectDataPreToExecuteAsSoonAsPossible(self, data, cmdPath, enablingMap = None, onlyAppend = False):
        self._injectDataPreToExecute(data, cmdPath, 0, enablingMap, onlyAppend)
        
    def injectDataPreToExecuteAsLateAsPossible(self, data, cmdPath, enablingMap = None, onlyAppend = False):
        self._injectDataPreToExecute(data, cmdPath, -1, enablingMap, onlyAppend)
        
    def injectDataPre(self, data, cmdPath, enablingMap = None): 
        #only append on perfect match(path, type, map)
        #or insert on empty stack match
        #otherwise raise

        itemCandidateList = self._findIndexToInjectPre(cmdPath, PREPROCESS_INSTRUCTION)
        if len(itemCandidateList) == 1 and itemCandidateList[0][0] == None:
            #insert at index
            self.stack.insert(itemCandidateList[0][1], ([data], cmdPath[:], PREPROCESS_INSTRUCTION, enablingMap, ))
        else:
            for item, index in itemCandidateList:
                if not equalMap(enablingMap, item[3]):
                    continue

                #append
                item[0].append(data)
                return

            #not found
            raise executionException("(engine) injectDataPre, no match foundwhere insert")
    
    def insertDataToPreProcess(self, data, onlyForTheLinkedSubCmd = True):
        self.stack.raiseIfEmpty("insertDataToPreProcess")
        
        #the current process must be pro or pos
        if self.stack.typeOnTop() == PREPROCESS_INSTRUCTION:
            self.appendData(data)
            return
            
        #computer map
        enablingMap = None
        if onlyForTheLinkedSubCmd:
            enablingMap = [False] * self.stack.cmdLengthOnTop()
            enablingMap[self.subCmdIndexOnTop()] = True
        
        #inject data
        self.injectDataPreToExecuteAsSoonAsPossible(data,self.stack.pathOnTop(),enablingMap,False)

    def insertDataToProcess(self, data):
        self.stack.raiseIfEmpty("insertDataToProcess")
        
        #the current process must be pos
        if self.stack.typeOnTop() != POSTPROCESS_INSTRUCTION:
            raise executionException("(engine) insertDataToProcess, only a process in postprocess state can execute this function")
            
        #the current process must be on a root path
        if not self.isCurrentRootCommand():
            raise executionException("(engine) insertDataToProcess, only the root command can insert data to the process")

        #inject data
        self.injectData(data, self.stack.pathOnTop(),PROCESS_INSTRUCTION)

    def insertDataToNextSubCommandPreProcess(self,data):
        self.stack.raiseIfEmpty("insertDataToNextSubCommandPreProcess")
                
        #is there a next pre process sub command ?
        if self.stack.subCmdIndexOnTop() == self.stack.subCmdLengthOnTop(self.cmdList)-1:
            raise executionException("(engine) insertDataToNextSubCommandPreProcess, there is no next pre process available to insert new data")
        
        cmdPath = self.stack.pathOnTop()[:]
        cmdPath[-1] += 1
        
        #create enabling map 
        enablingMap = [False] * self.stack.subCmdLengthOnTop(self.cmdList)
        enablingMap[cmdPath[-1]] = True
        
        #inject in asLateAsPossible
        self.injectDataPreToExecuteAsLateAsPossible(data, cmdPath, enablingMap,False)
            
### COMMAND meth ###

    def skipNextSubCommandOnTheCurrentData(self, skipCount=1):
        self.stack.raiseIfEmpty("skipNextSubCommandOnTheCurrentData")
        # can only skip the next command if the state is pre_process
        if self.stack.typeOnTop() != PREPROCESS_INSTRUCTION:
            raise executionException("(engine) skipNextCommandOnTheCurrentData, can only skip method on PREPROCESS item")
        
        self.stack[-1][1][-1] += skipCount

    def skipNextSubCommandForTheEntireDataBunch(self, skipCount=1):
        self.stack.raiseIfEmpty("skipNextSubCommandForTheEntireExecution")
        currentCmdID = self.stack.pathOnTop()[-1]
    
        enablingMap = self.stack.enablingMapOnTop()

        if enablingMap == None:
            enablingMap = [True] * self.stack.subCmdLengthOnTop(self.cmdList)

        for i in xrange(currentCmdID+1, min(currentCmdID+1+skipCount, len(enablingMap))):
            if not enablingMap[i]:
                continue

            enablingMap[i] = False

        item = self.stack[-1]
        self.stack[-1] = (item[0], item[1], item[2], enablingMap,)
        
    def skipNextSubCommandForTheEntireExecution(self, skipCount=1):
        self.stack.raiseIfEmpty("skipNextSubCommandForTheEntireExecution")
        cmdID        = self.stack.cmdIndexOnTop()
        isAValidIndex(self.cmdList, cmdID,"skipNextSubCommandForTheEntireExecution", "command list")
        currentCmdID = self.stack.pathOnTop()[-1]

        for i in xrange(currentCmdID+1, min(len(self.cmdList[cmdID]),  currentCmdID+1+skipCount)):
            c,u,e = self.cmdList[cmdID][i]

            #already disabled ?
            if not e:
                continue

            self.cmdList[cmdID][i] = (c,u,False,)
    
    def disableEnablingMapOnDataBunch(self,dept=0):
        index = self.stack.size() - 1 - dept
        isAValidIndex(self.stack, index,"disableEnablingMapOnDataBunch", "stack")
        mapping = self.stack.enablingMapOnDepth(dept)

        if mapping != None:
            self.stack[index] = (self.stack[index][0],self.stack[index][1],self.stack[index][2],None,)

    def enableSubCommandInCurrentDataBunchMap(self, indexSubCmd):
        self.stack.raiseIfEmpty("enableSubCommandInCurrentDataBunchMap")
        self._setStateSubCmdInDataBunch(-1,indexSubCmd, True)
    
    def enableSubCommandInCommandMap(self, indexCmd, indexSubCmd):
        self._setStateSubCmdInCmd(indexCmd, indexSubCmd, True)
        
    def disableSubCommandInCurrentDataBunchMap(self, indexSubCmd):
        self.stack.raiseIfEmpty("enableSubCommandInCurrentDataBunchMap")
        self._setStateSubCmdInDataBunch(-1,indexSubCmd, False)
    
    def disableSubCommandInCommandMap(self, indexCmd, indexSubCmd):
        self._setStateSubCmdInCmd(indexCmd, indexSubCmd, False)
        
    def _setStateSubCmdInCmd(self,cmdIndex, subCmdIndex, value):
        isAValidIndex(self.cmdList, cmdIndex,"_setStateSubCmdInCmd", "command list")
        isAValidIndex(self.cmdList[cmdIndex], subCmdIndex,"_setStateSubCmdInCmd", "sub command list")
        current = self.cmdList[cmdIndex]
        self.cmdList[cmdIndex] = (current[0], current[1], value)
        
    def _setStateSubCmdInDataBunch(self, dataBunchIndex, subCmdIndex, value):
        isAValidIndex(self.stack, dataBunchIndex,"_setStateSubCmdInDataBunch", "stack")
        enablingMap = self.stack.enablingMapOnIndex(dataBunchIndex)

        if enablingMap == None:
            enablingMap = [True] * self.stack.subCmdLengthOnIndex(dataBunchIndex, self.cmdList)
            self.stack[dataBunchIndex] = (self.stack[dataBunchIndex][0], self.stack[dataBunchIndex][1],self.stack[dataBunchIndex][2],enablingMap,)

        isAValidIndex(enablingMap, subCmdIndex,"_setStateSubCmdInDataBunch", "enabling mapping on data bunch")
        enablingMap[subCmdIndex] = value
    
    def flushArgs(self, index=None): #None index means current command
        if index == None:
            self.stack.raiseIfEmpty("flushArgs")
            cmdID = self.stack.cmdIndexOnTop()
        else:
            cmdID = index
        
        isAValidIndex(self.cmdList, cmdID,"flushArgs", "command list")
        self.cmdList[cmdID].flushArgs()
    
    def addSubCommand(self, cmdID = None, onlyAddOnce = True, useArgs = True):
        #compute the current command index where the sub command will be insert, check the cmd path on the stack
        if cmdID == None:
            self.stack.raiseIfEmpty("addSubCommand")
            cmdID = self.stack.cmdIndexOnTop()
        
        if cmdID > 0 or cmdID >= len(self.cmdList):
            raise executionException("(engine) addSubCommand, invalid command index")
        
        #add the sub command
        self.cmdList[cmdID].addDynamicCommand(cmd, onlyAddOnce, useArgs)
        
        #extend the enablingMapping existed on the stack
        for i in range(0, self.stack.size()):
            currentStackItem = self.stack[i]
            if currentStackItem[2] != PREPROCESS_INSTRUCTION:
                break
            
            #is it a wrong path ?
            if len(currentStackItem[1]) != cmdID+1:
                continue
            
            #is there an enabled mapping ?
            if currentStackItem[3] == None:
                continue
            
            currentStackItem[3].extend(True)
            self.stack[i] = (currentStackItem[0],currentStackItem[1],currentStackItem[2],currentStackItem[3],)     
    
    def addCommand(self, cmd, convertProcessToPreProcess = False):
        if not isinstance(cmd, MultiCommand):#only the MultiCommand are allowed in the list
            raise executionInitException("(engine) addCommand, cmd is not a MultiCommand instance, got <"+str(type(cmd))+">")
        
        #The process (!= pre and != post), must always be the process of the last command in the list
        #if we add a new command, the existing process on the stack became invalid

        #if there are not top item with process type
        if convertProcessToPreProcess:
            #convert the existing process on the stack into preprocess of the new command
            for i in range(1,count):
                currentStackItem = self.stack[self.stack.size() - 1 - i]
                
                if currentStackItem[2] == PREPROCESS_INSTRUCTION:
                    break
                    
                if currentStackItem[2] == POSTPROCESS_INSTRUCTION:
                    continue
                
                new_path = currentStackItem[1][:]
                new_path.append(0)
                self.stack[len(self.stack) - 1 - i] = (currentStackItem[0], new_path, PREPROCESS_INSTRUCTION, currentStackItem[3])
        else:
            #if the top item is a process type with more than one data
            if self.stack.typeOnTop() == PROCESS_INSTRUCTION and len(self.stack.dataOnTop()) > 1:
                raise executionInitException("(engine) addCommand, the current process type is pro and has at least 1 execution remaining, can not add a new command")
            
            for i in range(1,count):
                currentStackItem = self.stack[len(self.stack) - 1 - i]
                
                #if we reach a preprocess, we never reach again a process
                if currentStackItem[2] == PREPROCESS_INSTRUCTION:
                    break
                
                if currentStackItem[2] == POSTPROCESS_INSTRUCTION:
                    continue
                    
                raise executionInitException("(engine) addCommand, some process are waiting on the stack, can not add a command")
            
        
        cmd.reset()
        self.cmdList.append(cmd)
        
    def isCurrentRootCommand(self):
        self.stack.raiseIfEmpty("isCurrentRootCommand")
        return self.stack.cmdIndexOnTop() == 0
    
### SPLIT/MERGE meth ###
    
    def mergeDataAndSetEnablingMap(self, newMap = None, count = 2):
        self.stack.raiseIfEmpty("mergeDataAndSetEnablingMap")
        
        #check new map
        if newMap != None and len(newMap) != self.stack.subCmdLengthOnTop(self.cmdList):
            raise executionException("(engine) mergeDataAndSetEnablingMap, invalid map size, must be equal to the sub command list size")
        
        self.mergeData(count, None)
        top = self.stack.pop()
        self.stack.push(top[0], top[1], top[2], newMap)

    def mergeData(self, count = 2, depthOfTheMapToKeep = None):
        #need at least two item to merge
        if count < 1:
            return False#no need to merge
        
        #the stack need to hold at least count
        if self.stack.size() < count:
            raise executionException("(engine) mergeDataOnStack, no enough of data on stack to merge")

        #extract information from first item
        pathOnTop = self.stack.pathOnTop()
        actionToExecute = self.stack.typeOnTop()
        
        #can only merge on PREPROCESS
        if actionToExecute != PREPROCESS_INSTRUCTION:
            raise executionException("(engine) mergeDataOnStack, try to merge a not preprocess action")
        
        #check dept and get map
        if depthOfTheMapToKeep != None:
            if depthOfTheMapToKeep < 0 or depthOfTheMapToKeep > count-1:
                raise executionException("(engine) mergeDataOnStack, the selected map to apply is not one the map of the selected items")
            
            #set the valid map
            enablingMap = self.stack.enablingMapOnDepth(depthOfTheMapToKeep)
        else:
            enablingMap = None

        for depth in range(1,count):
            currentStackItem = self.stack.itemOnDepth(i)

            #the path must be the same for each item to merge
                #execpt for the last command, the items not at the top of the stack must have 0 or the cmdStartLimit
            if len(currentStackItem[1]) != len(pathOnTop):
                raise executionException("(engine) mergeDataOnStack, the command path is different for the item at depth <"+str(depth)+">")
            
            for j in range(0,len(pathOnTop)-1):
                if currentStackItem[1][j] != pathOnTop[j]:
                    raise executionException("(engine) mergeDataOnStack, a subcommand index is different for the item at index <"+str(j)+">")
            
            #the action must be the same type
            if currentStackItem[2] != actionToExecute:
                raise executionException("(engine) mergeDataOnStack, the action of the item at depth <"+str(depth)+"> is different of the action ot the top item 0")

        #merge data and keep start/end command
        dataBunch = []
        for i in range(0,count):
            data = self.stack.pop()
            dataBunch.extend(data)
        
        self.stack.push(dataBunch, pathOnTop, actionToExecute, enablingMap)
        return True
        
    def splitDataAndSetEnablingMap(self, splitAtDataIndex=0, map1 = None, map2=None):
        self.stack.raiseIfEmpty("splitDataAndSetEnablingMap")
        
        if map1 != None and len(map1) != self.stack.subCmdLengthOnTop(self.cmdList):
            raise executionException("(engine) mergeDataAndSetEnablingMap, invalid map1 size, must be equal to the sub command list size")
            
        if map2 != None and len(map2) != self.stack.subCmdLengthOnTop(self.cmdList):
            raise executionException("(engine) mergeDataAndSetEnablingMap, invalid map2 size, must be equal to the sub command list size")
        
        state = self.splitData(splitAtDataIndex, True)
        self.stack[-1] = (self.stack[-1][0],self.stack[-1][1],self.stack[-1][2],map1)
        
        if state: #if state is false, no split has occurred, so no need to set the second map
            self.stack[-2] = (self.stack[-2][0],self.stack[-2][1],self.stack[-2][2],map1)

        return state
    
    def splitData(self,splitAtDataIndex=0, resetEnablingMap = False): #split the data into two separate stack item at the index, but will not change anything in the process order
        #is empty stack ?
        self.stack.raiseIfEmpty("splitData")
        
        #is it a pre ? (?)
        if self.stack.typeOnTop() != PREPROCESS_INSTRUCTION:
            raise executionException("(engine) splitData, can't split the data of a PRO/POST process because it will not change anything on the execution")
        
        topdata = self.stack.dataOnTop()
        #split point exist ?
        if splitAtDataIndex < 0 or splitAtDataIndex > (len(topdata)-1):
            raise executionException("(engine) splitData, split index out of bound")
        
        #has enought data to split ?
        if len(topdata) < 2 or splitAtDataIndex == 0:
            return False
        
        #split, pop, then push the two new items
        top = self.stack.pop()
        path = top[1][:]
        path[-1] = 0 
        
        if resetEnablingMap:
            enableMap = None
        else:
            enableMap = top[3]
        
        self.stack.append( (top[0][splitAtDataIndex:], path, top[2], enableMap) )
        self.stack.append( (top[0][0:splitAtDataIndex], top[1], top[2], enableMap) )
        
        return True

### DATA meth (data of the top item on the stack) ###
    
    def flushData(self):
        self.stack.raiseIfEmpty("flushData")
        del self.stack.dataOnTop()[:] #remove everything, the engine is able to manage an empty data bunch
    
    def appendData(self, newdata):
        self.stack.raiseIfEmpty("addData")
        self.stack.dataOnTop().append(newdata)
    
    def addData(self, newdata, offset=1, forbideInsertionAtZero = True):    
        self.stack.raiseIfEmpty("addData")
        if forbideInsertionAtZero and offset == 0:
            raise executionException("(engine) addData, can't insert a data at offset 0, it could create infinite loop. it is possible to override this check with the boolean forbideInsertionAtZero, set it to False")
    
        self.stack.dataOnTop().insert(offset,newdata)
            
    def removeData(self, offset=0, resetSubCmdIndexIfOffsetZero=True):
        self.stack.raiseIfEmpty("removeData")
        data = self.stack.dataOnTop()
        
        #valid offset ?
        if offset >= len(data) or offset < (-1)*len(data): #allow offset with minus
            raise executionException("(engine) removeData, offset out of bound, the offset <"+str(offset)+"> can be reach because the data length is <"+str(len(data))+">")
        
        #remove the data
        del data[offset]
        
        #set the current cmd index to startIndex -1 (the minus 1 is because the engine will make a plus 1 to execute the next command)
        if resetSubCmdIndexIfOffsetZero and (offset == 0 or len(data) == 0): #len(data) == 0 is to manage the removal of the last item with -1 index on a data bunch of size 1
            #the engine will compute the first enabled cmd, if there is no more data, let the engine compute the cmd index too
            self.stack[-1][1][-1] = -1
            
    def setData(self, newdata, offset=0):
        self.stack.raiseIfEmpty("setData")
        data = self.stack.dataOnTop()
        
        if offset >= len(data):
            raise executionException("(engine) setData, offset out of bound, the offset <"+str(offset)+"> can be reach because the data length is <"+str(len(data))+">")
        
        data[offset] = newdata

    def getData(self, offset=0):
        self.stack.raiseIfEmpty("getData")
        data = self.stack.dataOnTop()
        
        if offset >= len(data):
            raise executionException("(engine) getData, offset out of bound, the offset <"+str(offset)+"> can be reach because the data length is <"+str(len(data))+">")
        
        return data[offset]
        
    def hasNextData(self):
        self.stack.raiseIfEmpty("hasNextData")
        return len(self.stack.dataOnTop()) > 1 #1 and not zero, because there are the current data and the next one
        
    def getRemainingDataCount(self):
        self.stack.raiseIfEmpty("getRemainingDataCount")
        return len(self.stack.dataOnTop())-1 # -1 because we don't care about the current data
        
    def getDataCount(self):
        self.stack.raiseIfEmpty("getDataCount")
        return len(self.stack.dataOnTop())

### VARIOUS meth ###
    
    def getEnv(self):
        return self.env
    
### ENGINE meth ###

    def execute(self):
        #compute the first index to execute on the first cmd to execute (this index will be executed immediately)
        if self.stack.size() != 0: 
            cmd = self.stack.getCmdOnTop(self.cmdList)
            nextData, newIndex = self._computeTheNextChildToExecute(cmd, len(cmd)-1, self.stack.enablingMapOnTop())

            #the first cmd has no subcmd enabled, impossible to start the engine
            if newIndex == -1:
                raise executionException("(engine) execute, no enabled subcmd on first execution")

            #set newIndex
            path = self.stack.pathOnTop()
            path[-1] = newIndex
            

        #consume stack
        while self.stack.size() != 0: #while there is some item into the stack
            ### EXTRACT DATA FROM STACK ###
            top                      = self.stack.top()
            cmd                      = self.stack.getCmdOnTop(self.cmdList)
            subcmd, useArgs, enabled = cmd[top[1][-1]]
            insType = self.stack.typeOnTop()
            
            ### EXECUTE command ###
            to_stack = None #prepare the var to push on the stack, if the var keep the none value, nothing will be stacked

            ## PRE PROCESS
            if insType == PREPROCESS_INSTRUCTION: #pre           
                r = self._executeMethod(cmd, subcmd.preProcess, top, useArgs)
                subcmd.preCount += 1
                
                #manage result
                if len(top[1]) == len(self.cmdList): #no child, next step will be a process
                    to_stack = (r, top[1][:], PROCESS_INSTRUCTION, )
                else: #there are some child, next step will be another preprocess
                    #build first index to execute, it's not always 0
                    new_cmd = self.cmdList[len(top[1])] #the -1 is not missing, we want the next cmd, not the current
                    nextData, newIndex = self._computeTheNextChildToExecute(new_cmd, len(new_cmd)-1, None)

                    #the first cmd has no subcmd enabled, impossible to start the engine
                    if newIndex == -1:
                        raise executionException("(engine) execute, no enabled subcmd on the cmd "+str(len(top[1])))
                
                    new_path = top[1][:] #copy the path
                    new_path.append(newIndex) #then add the first index of the next command
                    to_stack = (r, new_path, PREPROCESS_INSTRUCTION, )
            
            ## PROCESS ##
            elif insType == PROCESS_INSTRUCTION: #pro
                r = self._executeMethod(cmd, subcmd.process, top, useArgs)
                subcmd.proCount += 1
                
                #manage result
                to_stack = (r, top[1], POSTPROCESS_INSTRUCTION,)
            
            ## POST PROCESS ##
            elif insType == POSTPROCESS_INSTRUCTION: #post
                r = self._executeMethod(cmd, subcmd.postProcess, top, useArgs)
                subcmd.postCount += 1
                
                #manage result
                if len(top[1]) > 1: #not on the root node
                     to_stack = (r, top[1][:-1], POSTPROCESS_INSTRUCTION,) #just remove one item in the path to get the next postprocess to execute
            else:
                raise executionException("(engine) execute, unknwon process command <"+str(insType)+">")
        
            if self.selfkillreason != None:
                reason,abnormal = self.selfkillreason
                raise engineInterruptionException("(engine) stopExecution, execution stop, reason: "+reason, abnormal)

            if subcmd.preCount > DEFAULT_EXECUTION_LIMIT or subcmd.proCount > DEFAULT_EXECUTION_LIMIT or subcmd.postCount > DEFAULT_EXECUTION_LIMIT :
                raise executionException("(engine) execute, this subcommand reach the execution limit count")
            
            ### MANAGE STACK, need to repush the current item ? ###
            self.stack.pop()
            if insType == PROCESS_INSTRUCTION or insType == POSTPROCESS_INSTRUCTION: #process or postprocess ?
                if len(top[0]) > 1: #still data to execute ?
                    self.stack.push( top[0][1:],top[1],top[2]) #remove the last used data and push on the stack
            else:# insType == 0 #preprocess, can't be anything else, a test has already occured sooner in the engine function
                nextData, newIndex = self._computeTheNextChildToExecute(cmd,top[1][-1], top[3])
                #something to do ? (if newIndex == -1, there is no more enabled cmd for this data bunch)                
                if ((not nextData and len(top[0]) > 0) or len(top[0]) > 1) and newIndex >= 0:
                    #if we need to use the next data, we need to remove the old one
                    if nextData:
                        del top[0][0] #remove the used data

                    top[1][-1] = newIndex #select the next child id
                    self.stack.push(top[0],top[1],top[2],top[3]) #push on the stack again

            ### STACK THE RESULT of the current process if needed ###
            if to_stack != None:
                self.stack.push(*to_stack)
    
    def _computeTheNextChildToExecute(self,cmd, currentSubCmdIndex, enablingMap):
        startingIndex = currentSubCmdIndex
        executeOnNextData = False
        while True:
            #increment
            startingIndex = (startingIndex+1) % len(cmd)
            
            #did it reach the next data ?
            if startingIndex == 0:
                executeOnNextData = True
            
            #is it a valid command to execute ?
            if cmd[startingIndex][2] and (enablingMap == None or enablingMap[startingIndex]):
                return executeOnNextData,startingIndex
            
            #stop condition
            if startingIndex == currentSubCmdIndex:
                return executeOnNextData, -1
            
    
    def _executeMethod(self, cmd,subcmd, stackState, useArgs):
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
        if hasattr(subcmd, "checker"):         
            data = subcmd.checker.checkArgs(args, self)
        else:
            data = {}

        #execute Xprocess
        self._isInProcess = True
        try:
            r = subcmd(**data)
        finally:
            self._isInProcess = False
        
        #r must be a multi output
        if not isinstance(r, MultiOutput):
            return [r]

        return r
    
    def stopExecution(self, reason = None,afterThisProcess = True, abnormal = False):
        if not self._isInProcess:
            raise executionException("(engine) stopExecution, can not execute this method outside of a process")

        if reason == None:
            reason = "unknown"

        if not afterThisProcess:
            raise engineInterruptionException("(engine) stopExecution, execution stop, reason: "+reason, abnormal)
        else:
            self.selfkillreason = (reason,abnormal,)
        
### DEBUG meth ###
    
    def getExecutionSnapshot(self):
        info = {}

        if self.stack.isEmpty(): 
            info["cmdIndex"]    = -1
            info["cmd"]         = None
            info["subCmdIndex"] = -1
            info["subCmd"]      = None
            info["data"]        = None
            info["processType"] = -1
        else:
            top = self.stack.top()

            info["cmdIndex"]    = self.stack.cmdIndexOnTop()               #the index of the current command in execution
            info["cmd"]         = self.stack.getCmdOnTop(self.cmdList)                 #the object instance of the current command in execution
            info["subCmdIndex"] = top[1][-1]                               #the index of the current sub command in execution
            info["subCmd"]      = self.cmdList[len(top[1]) -1][top[1][-1]] #the object instance of the current sub command in execution
            info["data"]        = top[0][0]                                #the data of the current execution
            info["processType"] = self.stack.typeOnTop()                   #the process type of the current execution
    
        return info

    def printStack(self):
        for i in range(self.stack.size()-1, -1, -1):
            cmdEnabled = self.stack[i][3]
            if cmdEnabled == None:
                cmdEnabled = "(disabled)"
            
            print "#["+str(i)+"] data=", self.stack[i][0], ", path=", self.stack[i][1], ", action=",self.stack[i][2], ", cmd enabled=",cmdEnabled
    
    def printCmdList(self):
        if len(self.cmdList) == 0:
            print "no command in the engine"
            return
        
        for i in range(0, len(self.cmdList)):
            print "Command <"+str(i)+"> "+self.cmdList[i].name
            for j in range(0, len(self.cmdList[i])):
                c,a,e = self.cmdList[i][j]
                print "    SubCommand <"+str(j)+"> (useArgs="+str(a)+", enabled="+str(e)+")"
    
    def printCmdPath(self, path = None):
        if len(self.cmdList) == 0:
            print "no command in the engine"
            return

        if path == None:
            if self.stack.isEmpty():
                print "no item on the stack, and so no path available"

            path = self.stack.pathOnTop()

        for i in range(0, len(topPath)):
            if i >= len(self.cmdList):
                print "#["+str(i)+"] out of bound index"
                continue

            if topPath[i] < 0 or topPath[i] >= len(self.cmdList[i]):
                print "#["+str(i)+"] out of bound index in the command"
                continue

            if len(self.cmdList[i]) == 1:
                print "#["+str(i)+"]"+self.cmdList[i].name
                continue

            print "#["+str(i)+"]"+self.cmdList[i].name+" (sub="+str(topPath[i])+")"

