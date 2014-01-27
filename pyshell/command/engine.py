#!/usr/bin/python



#TODO
    #voir les notes dans le fichier TODO
    #resoudre la gestion des exceptions qui doivent remonter dans le shell et aussi l'affichage sur le shell
        #les self.printOnShell doivent disparaitre
        #solution, ne pas gérer les exceptions ici mais dans le shell
            #catch everything, add the command at the origin of the problem, then raise again the catched exception

    #XXX prevoir des methodes non divisible ?
        #interet?
        #lance une exception si tentative de division ?

def commandEngine(rawCommandList):
    ### STEP 3: manage and prepare the multicommand (flatenning) ###
        #example rawCommandList = [c1, c2(c2_1, c2_2), c3]
        #MultiCommandList will contains [[c1, c2_1, c3], [c1, c2_2, c3]]
    
    commandList = []
    MultiCommandList = [commandList]
    for rawCommand,args in rawCommandList:
        if isinstance(rawCommand,MultiCommand): #every command must 
            newMultiCommandList = []
            for commandList in MultiCommandList:
                for c in rawCommand:
                    tmp = list(commandList)
                    tmp.append((c,args))
                    newMultiCommandList.append(tmp)
            MultiCommandList = newMultiCommandList
        elif isinstance(rawCommand,Command):    #custom command
            pass #TODO just append in each list
        else:
            #TODO raise
        
            self.printOnShell("ERROR : a non command is into the tries : "+str(type(rawCommand)))
            return False 
    
    ### STEP 4: EXECUTION ###
    for commandList in MultiCommandList: #Multicommand
        inputManager = InputManager(len(commandList)) #the buffer is independant for each flattened command list
        
        #set the buffer to the command
        for i in range(0,len(commandList)-1):
            c,a = commandList[i]
            c.setBuffer(inputManager.getPreProcessInputBuffer(i),None,inputManager.getPostProcessInputBuffer(i))
        
        c,a = commandList[-1]
        c.setBuffer(inputManager.getPreProcessInputBuffer(len(commandList)-1),inputManager.getProcessInputBuffer(),inputManager.getPostProcessInputBuffer(len(commandList)-1))
        
        #set the starting point
        inputManager.addOutput(0,None) #TODO not better to add an empty list ? not sure because the None is not added
            #TODO pourquoi ne pas directement mettre les args de la premiere commande ?
        
        #print "init : "+str(inputManager)
        
        indice = 0
        while inputManager.hasStillWorkToDo(): #the buffer are not empty
            try: #critical section
                ### PREPROCESS ###
                for indice in range(inputManager.getNextPreProcess(),len(commandList)):
                    if inputManager.hasPreProcessInput(indice):
                        commandToExecute,args = commandList[indice]
                    
                        args_tmp = list(args)
                        #append the previous value to the args
                        commandInput = inputManager.getNextPreProcessInput(indice)
                        if commandInput != None: #TODO pourquoi None est-il refusé ? ça doit toujours etre une liste ?
                            if isinstance(commandInput,list):
                                #TODO why not an extend ???
                                for item in commandInput:
                                    args_tmp.append(item)
                            else:
                                args_tmp.append(commandInput)

                        inputManager.addOutputToNextPreProcess(indice,commandToExecute.preProcessExecution(args_tmp) )
                        #print "pre "+str(indice)+" : "+str(inputManager)

                ### PROCESS ###
                indice = len(commandList)-1 #TODO not used, then reassigned...
                if inputManager.hasProcessInput():
                    command,args = commandList[len(commandList)-1]
                    inputManager.addProcessOutput(command.ProcessExecution(inputManager.getNextProcessInput()))
                    #print "pro : "+str(inputManager)

                ### POSTPROCESS ###
                for indice in range(inputManager.getNextPostProcess(),len(commandList)):
                    if inputManager.hasPostProcessInput(indice):
                        command,args = commandList[len(commandList)-1-indice]
                        inputManager.addOutputToNextPostProcess(indice,command.postProcessExecution(inputManager.getNextPostProcessInput(indice)))

                        #print "post "+str(indice)+" : "+str(inputManager)
            except Exception as ex:
                c,a = commandList[indice]
                ex.command = c
                raise ex
            
            """except argExecutionException as aee:
                c,a = commandList[indice]
                
                self.printOnShell(""+str(aee)+" at "+c.parentContainer.name)
                return True
            except argException as aee:
                c,a = commandList[indice]
                #TODO to fix
                    #fix what ?
                self.printOnShell(str(aee)+" at "+c.parentContainer.name)
                self.printOnShell("USAGE : "+c.parentContainer.usage())
                
                return True
            except argPostExecutionException as aee:
                c,a = commandList[indice]
                self.printOnShell(""+str(aee)+" at "+c.parentContainer.name)
                return True
            except Exception as ex:
                c,a = commandList[indice]
                self.printOnShell("SEVERE : "+str(ex)+" at "+c.parentContainer.name)
                if self.environment["debug"]:
                    traceback.print_exc()
                return False"""
            
    return True

EXECUTION_LIMIT = 255

class executionEngine(object): #TODO not sure a class is needed
    def __init__(self, commandList):
        self.commandList = commandList
        self.startingItems = []
        self.parseArgAndReset()
        self.buildTree()

    def parseArgAndReset(self):
        for c,arg in self.commandList:
            #reset the command state
            c.reset()
            
            #
            
        
        #TODO parse arg
            #before to execute anything, every command args in the list will be parsed
            #we don't want an interrumption in the middle of the process because some arg are invalid
            #on ne veut pas avoir d'argException lancée depuis le executeTree
            
            #prblm
                #sometimes, the args are not checked by the preProcess, or even the process
                    #identify which checker to call

        #TODO reset every command, if theyr stored some content from a previous execution

        #TODO le truc chiant c'est que la methode genericProcess va interpreter a nouveau les args
            #le meme travail est fait 2 fois...
            #solution:
                #soit le taggé comme déja traité
                #soit le faire passer par un autre circuit qui evite genericProcess

    def buildTree(self):
        #TODO ça eclate qd meme pas mal la memoire tout ça :/
            #solution 1: mettre le buffer PRE des childs dans le parent, comme ça on evite de le dupliquer
                #foire car on ne sais plus quand on doit supprimer la ressource du buffer
                    #et si on repasse plusieurs fois sur le même child, il y aura tjs la même valeur
                    #dans le buffer tant que tous les autres childs ne l'auront pas consommé
            
            #solution 2: mettre le parent ou la valeur d'execution sur la stack
                #on ne peut pas mettre le parent, on alors il faudrait mettre toute la liste des parents
                #mettre la valeur a executé revient à occuper le même espace que si chaque child avait
                #son propre buffer, donc foireux...
                
            #comment sauvegarder les path sans eclater la mémoire ? ...
                #dans tous les cas, il faut connaitre le path
    
        currentLevel = None
        self.startingItems = []
        starting = True
        for c,arg in self.commandList:
            if not isinstance(c, MultiCommand):
                c = [c]
            
            #manage root level
            if starting:
                for subc in c:
                    self.startingItems.append(executionNode(subc, arg))
                
                currentLevel = self.startingItems
                starting = False
                continue
            
            #manage normal level
            newLevel = []
            for subc in c:
                for parentc in currentLevel:
                    enode = executionNode(subc, arg, parentc)
                    parentc.childs.append(enode)
                    newLevel.append(enode)
                    
            currentLevel = newLevel
        
    def executeTree(self):
        #STACK axioms
            #the element at the top of the stack is always the lowest item on the tree
                #not really true, the next elements in the stack could be at the same level as the item at the top of the stack
                #but no element in the stack can be at a lower level than the item at the top of the stack
            #only the childs of the current node can be insert on the stack
                #(current node = the item at the top of the stack)
                #and the child of a node are always at a more bottom level
    
        stack = []#the stack of breakpoint
        
        #init the stack
        for i in range(0, len(self.startingItems)):
            stack.append( (0,self.startingItems[len(self.startingItems) - i - 1],) )
    
        #consume the stack
        while len(stack) > 0:
            #take the first breakpoint in the pre Queue
            state, currentNode = stack.pop()
            
            if state == 0:
                currentNode.executePreprocess(stack)
            elif state == 1:
                currentNode.executeProcess(stack)
            elif state == 2:
                currentNode.executePostprocess(stack)
            else:
                pass #TODO raise
    
            #check execution count
            if currentNode.executionCount[0] > EXECUTION_LIMIT:
                pass #TODO raise
            elif currentNode.executionCount[1] > EXECUTION_LIMIT:
                pass #TODO raise
            elif currentNode.executionCount[2] > EXECUTION_LIMIT:
                pass #TODO raise

##############################################################################################################################

class MultiOutput(list):
    pass

#TODO
    #at this moment, multioutput is juste a list... 
        #must stay a list
        #TODO check if the multioutput is not converted into a simple list in the process
            #because there is a risk to lose the cmd limit
    #the maximum execution counter has disappear.
        #add it into MultiCommand class
        #and manage it into the engine process

#XXX
    #prblm, manage forAllCommand
        #solution 1: in MultiOutput
            #direct and powerfull control on the data
            #loss the principle of tag
            #need to create a new method and indicate for which method the data are needed
                #lost the power of the list
        
        #solution 2: special process state (execute_once, execute_all_except, ...)
            #need more data stored in each stack item

        #solution 3: use the other method to escape the data
            #with skipMethod and addData
                #it is possible but more complicated

        #solution 4: each data list are associated to firstCmdIndex and lastCmdIndex
            #like the solution 2, add some data on the stack
            #but more powerfull
            #and easy to manage
            #no need to update the MultiOutput tag
            
class engineV3(object):
    def __init__(self, cmdList, env=None):
        #cmd must be a not empty list
        if cmdList == None or not isinstance(cmdList, list) or len(cmdList) ==0:
            raise executionInitException("(engine) init, command list is not a valid list")

        #reset and check the command
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
    
    ## command special meth ##
    
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
    
    def addCommand(self, cmd, onlyAddOnce = True):    
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
        self.cmdList[cmdID].addDynamicCommand(cmd, onlyAddOnce)
    
    ## data special meth ##
    
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
        if cmdLength != None
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

    ## various meth ##

    def getEnv(self):
        return self.env
    
    ## engine meth ##
    
    def execute(self):
        #consume stack
        while len(self.stack) != 0: #while there is some item into the stack
            
            ### EXTRACT DATA FROM STACK ###
            top     = self.stack[-1]#.pop()
            #top[0] contain the current data of this item
            #top[1] contain the command path
            #top[2] contain the process type to execute
            
            cmd     = self.cmdList[len(top[1]) -1]
            subcmd  = cmd[top[1][-1]]
            
            ### execute command ###
            to_stack = None #prepare the var to push on the stack, if the var keep the none value, nothing will be stacked
            
            ## PRE PROCESS
            if top[2] == 0: #pre
                r = self.executeMethod(subcmd.preProcess, top)
                
                #manage result
                if len(top[1]) == len(self.cmdList): #no child, next step will be a process
                    to_stack = (r, top[1], 1, )
                else: #there are some child, next step will be another preprocess
                    new_path = top[1][:]
                    new_path.append(0)
                    to_stack = (r, new_path, 0, )
            
            ## PROCESS ##
            elif top[2] == 1: #pro
                r = self.executeMethod(subcmd.process, top)
                
                #manage result
                to_stack = (r, top[1], 2,)
            
            ## POST PROCESS ##
            elif top[2] == 0: #post
                r = self.executeMethod(subcmd.postProcess, top)
                
                #manage result
                if len(top[1]) > 1: #not on the root node
                     to_stack = (r, top[1][:-1], 2,)
                
            else:
                raise executionException("(engine) execute, unknwon process command <"+str(top[2])+">")
            
            ### manage stack, need to repush the current item ? ###
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
            
            ### stack the result of the current process if needed ###
            if to_stack != None:
                self.stack.append(to_stack)
                
    def executeMethod(self, cmd,subcmd, stackState):
        nextData = stackState[0][0]

        #prepare data
        args = cmd.getArgs()
        if args != None:
            if nextData != None:
                args = args[:]
                args.extend(nextData)
        elif nextData != None:
            args = nextData
        else:
            args = []

        #execute checker
        if hasattr(cmd, "checker"):         
            data = cmd.checker.checkArgs(args, self) #TODO update checker method to take care about "self" that is the engine
        else:
            data = {}

        #execute Xprocess
        r = subcmd(**data)
        
        #r must be a multi output
        if not isinstance(r, MultiOutput):
            return [r]

        return r


