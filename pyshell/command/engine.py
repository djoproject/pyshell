#!/usr/bin/python

from buffer import InputManager
from heapq import *
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
    
    
def buildTree(commandList):
    #each time a command as several sub command, split the tree and copy the sub tree on the several node
        #take care about the id node
    pass #TODO
    
def executeTree(tree):
    #TODO faire deux queues
        #une pour le pre
        #une pour les posts
        #et toujours executer les posts avant les pre
    
    pqueue = []
    #while breakpoint queue is not empty, do
    while len(pqueue) > 0:
        #TODO manage multioutput on post 
    
        #take the first breakpoint in the Queue
        level, currentNode = heappop(pqueue)
        
        #execute remaining preprocess if needed
        while currentNode != None:
            currentNode.executePreprocess(pqueue)
            
            if len(currentNode) > 0: #has a next child ?
                currentNode = currentNode.childs[0]
            
                for i in range(1,len(currentNode.childs)):
                    heappush(pqueue, (currentNode.id, currentNode.childs[i])) #TODO pas convaincu pas les ID
            else:
                break
        
        #execute process if needed
        currentNode.executeProcess(pqueue)
            
        #execute remaining postprocess if needed
        while currentNode != None:
            currentNode.executePostprocess(pqueue)
            currentNode = currentNode.parent

    
