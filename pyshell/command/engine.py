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

#TODO
    #at this moment, multioutput is juste a list... 
    #the maximum execution counter has disappear.
        #add it into MultiCommand class
        #and manage it into the engine process
    #implement the special method, see TODO file (addcmd, addData, ...)

def executeMethod(cmd,subcmd, stackState):
    nextData = stackState[0][0]

    #TODO manage None args from command

    #prepare data
    if nextData != None:
        args = cmd.getArgs()[:]
        args.extend(nextData)
    else:
        args = cmd.getArgs()

    #execute checker
    if hasattr(cmd, "checker"):
        #TODO give the "env" and the "engine" from here to the checker
    
        data = cmd.checker.checkArgs(args) 
    else:
        data = {}

    #execute Xprocess
    r = subcmd(**data)
    
    #TODO r must be a multi output
    if not isinstance(r, ):#TODO
        pass #TODO convert r to multioutput

    return r

class engineV3(object):
    def __init__(self, cmdList, env=None):
        #cmd must be a not empty list
        if cmdList == None or not isinstance(cmdList, list) or len(cmdList) ==0:
            raise executionInitException("(engine) init, command list is not a valid list")

        #TODO reset the commands
            #and also check the type

        #TODO manage env
            #if env is none, create an empty dict
            #if not none, must be a dict
        self.env     = env
        
        self.stack   = []
        self.cmdList = cmdList #list of MultiCommand

        #init stack
        self.stack.append(  ([None], [0], 0,)  )
    
    def skipNextCommand(self, skipCount=1):
        pass #TODO skip the n following command on the current data
    
    def flushArgs(self):
        pass #TODO allow to remove the arg for the next command
    
    def flushData(self):
        pass #TODO remove every data from the current buffer
            #need an update of the engine code, to stop if there is no more data
            #even if every command has not been executed
    
    def addData(self, data, forAllCommand = True, offset=0):
        pass #TODO
    
    def setData(self, data, forAllCommand = True, offset=0):
        pass #TODO
    
    def getData(self, offset=0):
        pass #TODO
        
    def hasNextData(self):
        return self.getRemainingDataCount() > 0
        
    def getRemainingDataCount(self):
        if len(self.stack) == 0:
            return 0

        return len(self.stack[-1][0])
     
    def addCommand(self, cmd, onlyAddOnce = True):
        #TODO 
            #check the command
            #check stack and cmdList length
            #tag the command as dynamic
                #a solution is to keep the number of dynamic command added
                #and remove the X last command on the reset function
            #manage onlyAddOnce to protect the user of massive insertion of the same command
        
        self.cmdList[len(self.stack[-1][1]) -1].append(cmd)
        
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
                r = executeMethod(subcmd.preProcess, top)
                
                #manage result
                if len(top[1]) == len(self.cmdList): #no child, next step will be a process
                    to_stack = (r, top[1], 1, )
                else: #there are some child, next step will be another preprocess
                    new_path = top[1][:]
                    new_path.append(0)
                    to_stack = (r, new_path, 0, )
            
            ## PROCESS ##
            elif top[2] == 1: #pro
                r = executeMethod(subcmd.process, top)
                
                #manage result
                to_stack = (r, top[1], 2,)
            
            ## POST PROCESS ##
            elif top[2] == 0: #post
                r = executeMethod(subcmd.postProcess, top)
                
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
                if top[1][-1] < (len(cmd)-1): #still child to execute ?
                    top[1][-1] += 1 #select the nex child id
                    self.stack.append(  (top[0],top[1],top[2],)  ) #push on the stack again
                else: #every child has been executed with this data
                    if len(top[0]) > 1: #still data to execute ?
                        top[1][-1] = 0 #select the first child
                        self.stack.append(  (top[0][1:],top[1],top[2],)  ) #remove the last used data and push on the stack
            
            ### stack the result of the current process if needed ###
            if to_stack != None:
                self.stack.append(to_stack)
    
