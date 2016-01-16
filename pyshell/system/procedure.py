#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

#Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#TODO
    #once procedureInQueue will be finished and in use, merge Procedure and procedureInQueue

from pyshell.utils.exception    import DefaultPyshellException, PyshellException, ERROR, USER_ERROR, ListOfException, ParameterException, ParameterLoadingException, ProcedureStackableException
from pyshell.utils.executing    import execute
from pyshell.command.command    import UniCommand, MultiCommand
from pyshell.command.exception  import engineInterruptionException
from pyshell.arg.decorator      import shellMethod
from pyshell.arg.argchecker     import ArgChecker,listArgChecker, defaultInstanceArgChecker
from pyshell.utils.parsing      import Parser
from pyshell.system.variable    import VarParameter
from pyshell.system.settings    import GlobalSettings
from pyshell.utils.printing     import warning,getPrinterFromExceptionSeverity,printShell
from pyshell.utils.constants    import SYSTEM_VIRTUAL_LOADER
from pyshell.utils.synchronized import synchronous, FAKELOCK

import thread, threading, sys

if sys.version_info[0] < 2 or (sys.version_info[0] < 3 and sys.version_info[0] < 7):
    from pyshell.utils.ordereddict import OrderedDict #TODO get from pipy, so the path will change
else:
    from collections import OrderedDict 
                
### UTILS COMMAND ###
    
def getAbsoluteIndex(index, listSize): #TODO will be deleted with procedureInList class
    "convert any positive or negative index into an absolute positive one"

    if index >= 0:
        return index
    
    index = listSize + index
    
    #because python list.insert works like that, a value can be inserted with a negativ value out of boud
    #but some other function like update does not manage negativ out of bound value, and that's why it is set to 0
    if index < 0:
        return 0
    
    return index

class Procedure(UniCommand):
    def __init__(self, name, settings = None):
        UniCommand.__init__(self, self._internalProcess, None, None) #by default, enable on pre process #TODO this information should be stored
        
        self.name = name
        self.setStopProcedureOnFirstError() #default error policy  #TODO should be in settings
                
        if settings is not None:
            if not isinstance(settings, GlobalSettings):
                raise ParameterException("(EnvironmentParameter) __init__, a LocalSettings was expected for settings, got '"+str(type(settings))+"'")

            self.settings = settings
        else:
            self.settings = GlobalSettings()
            
        #transient var
        self.interrupt        = False
        self.interruptReason  = None
        
    ### PRE/POST process ###
    
    def _setArgs(self,parameters, args):
        parameters.variable.setParameter("*", VarParameter(' '.join(str(x) for x in args)), localParam = True)    #all in one string
        parameters.variable.setParameter("#", VarParameter(len(args)), localParam = True)                         #arg count
        parameters.variable.setParameter("@", VarParameter(args), localParam = True)                              #all args
        parameters.variable.setParameter("?", VarParameter( ()), localParam = True)                               #value from last command
        parameters.variable.setParameter("!", VarParameter( ()), localParam = True)                               #last pid started in background        
        parameters.variable.setParameter("$", VarParameter(parameters.getCurrentId()), localParam = True) #current process id 

    def enableOnPreProcess(self):
        del self[:]
        MultiCommand.addProcess(self,self._internalProcess,None,None)
        
    def enableOnProcess(self):
        del self[:]
        MultiCommand.addProcess(self,None,self._internalProcess,None)
        
    def enableOnPostProcess(self):
        del self[:]
        MultiCommand.addProcess(self,None,None,self._internalProcess)

    @shellMethod(args       = listArgChecker(ArgChecker()),
                 parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())            
    def _internalProcess(self, args, parameters):
        parameters.pushVariableLevelForThisThread(self)
        
        threadID, level = parameters.getCurrentId()
        
        if level == 0 and self.errorGranularity is not None:
            warning("WARN: execution of the procedure "+str(self.name)+" at level 0 with an error granularity equal to '"+str(self.errorGranularity)+"'.  Any error with a granularity equal or lower will interrupt the application.")
        
        self._setArgs(parameters, args)
        try:
            return self.execute(parameters)
        finally:
            parameters.popVariableLevelForThisThread()
    
    def interrupt(self, reason=None):
        self.interruptReason = reason
        self.interrupt       = True #ALWAYS keep interrupt at last, because it will interrupt another thread, and the other thread could be interrupt before the end of this method if interrupt is not set at the end

    def execute(self, parameters):
        pass #XXX TO OVERRIDE AND USE _innerExecute
        
    def _innerExecute(self, cmd, name, parameters):
        if self.interrupt:
            if self.interruptReason is None:
                raise engineInterruptionException("this process has been interrupted", abnormal=True)
            else:
                raise engineInterruptionException("this process has been interrupted, reason: '"+str(self.interruptReason)+"'", abnormal=True)

        lastException, engine = execute(cmd, parameters, name)  
        param = parameters.variable.getParameter("?",perfectMatch = True, localParam = True, exploreOtherLevel=False)

        if lastException is not None: 
            #set empty the variable "?"
            param.setValue( () )
            
            #manage exception
            if isinstance(lastException, PyshellException):
                severity = lastException.severity
            else:
                severity = ERROR
            
            if self.errorGranularity is not None and severity <= self.errorGranularity:
                if isinstance(lastException, ProcedureStackableException):
                    lastException.append( (cmd, name,) )
                    raise lastException
                
                exception = ProcedureStackableException(severity, lastException)
                exception.procedureStack.append( (cmd, name,) )
                
                threadID, level = param.getCurrentId()
                if level == 0:
                    self._printProcedureStack(exception, threadID, 0)
                
                raise exception
            
            if isinstance(lastException, ProcedureStackableException):
                threadID, level = param.getCurrentId()
                lastException.procedureStack.append( (cmd, name,) )
                self._printProcedureStack(lastException, threadID, level)
            
        else:
            if engine is not None and engine.getLastResult() is not None and len(engine.getLastResult()) > 0:
                param.setValue( engine.getLastResult() )
            else:
                param.setValue( () )

        return lastException, engine
    
    def _printProcedureStack(self, stackException, threadID, currentLevel):
        if len(stackException.procedureStack) == 0:
            return
    
        toPrint = ""
        for i in range(0,len(stackException.procedureStack)):
            cmd, name = stackException.procedureStack[ len(stackException.procedureStack) - i - 1 ]
            toPrint += (i * " ") + str(name) + " : " + str(cmd) + "(level="+str(currentLevel+i)+")\n"
        
        toPrint = toPrint[:-1]
        colorFun = getPrinterFromExceptionSeverity(stackException.severity)
        printShell(colorFun(toPrint))
    
    ###### get/set method
    
    def setNextCommandIndex(self, index): #TODO remove me 
        raise DefaultPyshellException("(Procedure) setNextCommandIndex, not possible to set next command index on this king of procedure")
                    
    def setStopProcedureOnFirstError(self):
        self.setStopProcedureIfAnErrorOccuredWithAGranularityLowerOrEqualTo(sys.maxint)
        
    def setNeverStopProcedureIfErrorOccured(self):
        self.setStopProcedureIfAnErrorOccuredWithAGranularityLowerOrEqualTo(None)
            
    def setStopProcedureIfAnErrorOccuredWithAGranularityLowerOrEqualTo(self, value): 
        """
        Every error granularity bellow this limit will stop the execution of the current procedure.  A None value is equal to no limit.  
        """
        
        if value is not None and (type(value) != int or value < 0):
            raise ParameterException("(Procedure) setStopProcedureIfAnErrorOccuredWithAGranularityLowerOrEqualTo, expected a integer value bigger than 0, got '"+str(type(value))+"'")

        self.errorGranularity = value
    
    def getErrorGranularity(self):
        return self.errorGranularity
                
    def clone(self, From=None):
        if From is None:
            From = Procedure(self.name, settings = self.settings.clone())
        
        From.errorGranularity = self.errorGranularity
        return UniCommand.clone(self,From)
        
    def __hash__(self):
        return hash(self.settings)
            
class ProcedureFromList(Procedure): #TODO obsolete, will be replaced by ProcedureInQueue, don't care about TODO in this class
    def __init__(self, name, settings = None):
        Procedure.__init__(self, name, settings)
        
        #specific command system
        self.stringCmdList    = [] 
        self.lockedTo         = -1 #TODO should be a properties of settings
        self.nextCommandIndex = None
    
    def setLockedTo(self, value):
        try:
            value = int(value)
        except ValueError as va:
            raise ParameterException("(Procedure) setLockedTo, expected an integer value as parameter: "+str(va))
    
        if value < -1 or value >= len(self.stringCmdList):
            if len(self.stringCmdList) == 0:
                raise ParameterException("(Procedure) setLockedTo, only -1 is allowed because procedure list is empty, got '"+str(value)+"'")
            else:
                raise ParameterException("(Procedure) setLockedTo, only a value from -1 to '"+str(len(self.stringCmdList) - 1)+"' is allowed, got '"+str(value)+"'")
            
        self.lockedTo = value
        
    def getLockedTo(self):
        return self.lockedTo
        
    def getStringCmdList(self):
        return self.stringCmdList
                
    def execute(self, parameters):
        #e = self.clone() #make a copy of the current procedure   
        engine = None
        
        #for cmd in self.stringCmdList:
        i = 0
        while i < len(self.stringCmdList):
            lastException, engine = self._innerExecute(self.stringCmdList[i], self.name + " (index: "+str(i)+")", parameters)

            if self.nextCommandIndex is not None:
                i = self.nextCommandIndex
                self.nextCommandIndex = None
            else:
                i += 1

        #return the result of last command in the procedure
        if engine is None:
            return ()
            
        return engine.getLastResult()
                
    #### business method

    def setNextCommandIndex(self, index):
        try:
            value = int(index)
        except ValueError as va:
            raise ParameterException("(Procedure) setNextCommandIndex, expected an integer index as parameter, got '"+str(type(va))+"'")
    
        if value < 0:
            raise ParameterException("(Procedure) setNextCommandIndex, negativ value not allowed, got '"+str(value)+"'")
            
        self.nextCommandIndex = value
    
    def setCommand(self, index, commandStringList):
        self._checkAccess("setCommand", (index,), False)

        parser = Parser(commandString)
        parser.parse()

        if len(parser) == 0:
            raise ParameterException("(Procedure) addCommand, try to add a command string that does not hold any command")

        index = getAbsoluteIndex(index, len(self.stringCmdList))
        
        if index >= len(self.stringCmdList):
            self.stringCmdList.append( [commandStringList] )
            return len(self.stringCmdList) - 1
        else:
            self.stringCmdList[index] = [commandStringList] 
        
        return index

    def addCommand(self, commandString):
        self._checkAccess("addCommand")
        parser = Parser(commandString)
        parser.parse()

        if len(parser) == 0:
            raise ParameterException("(Procedure) addCommand, try to add a command string that does not hold any command")

        #TODO mark the command if loader, origin information should be available through settings

        self.stringCmdList.append( parser )
        return len(self.stringCmdList) - 1
            
    def removeCommand(self, index):
        self._checkAccess("removeCommand", (index,))
    
        try:
            del self.stringCmdList[index]
        except IndexError:
            pass #do nothing
        
    def moveCommand(self,fromIndex, toIndex):
        self._checkAccess("moveCommand", (fromIndex,toIndex,))
        fromIndex = getAbsoluteIndex(fromIndex, len(self.stringCmdList))
        toIndex = getAbsoluteIndex(toIndex, len(self.stringCmdList))
            
        if fromIndex == toIndex:
            return
        
        #manage the case when we try to insert after the existing index
        if fromIndex < toIndex:
            toIndex -= 1
            
        self.stringCmdList.insert(toIndex, self.stringCmdList.pop(fromIndex))
    
    def _checkAccess(self,methName, indexToCheck = (), raiseIfOutOfBound = True):
        if self.settings.isReadOnly():
            raise ParameterException("(Procedure) "+methName+", this procedure is readonly, can not do any update on its content")
            
        for index in indexToCheck:
            #check validity
            try:
                self.stringCmdList[index]
            except IndexError:
                if raiseIfOutOfBound:
                    if len(self.stringCmdList) == 0:
                        message = "Command list is empty"
                    elif len(self.stringCmdList) == 1:
                        message = "Only index 0 is available"
                    else:
                        message = "A value between 0 and "+str(len(self.stringCmdList)-1) + " was expected"
                
                    raise ParameterException("(Procedure) "+methName+", index out of bound. "+message+", got '"+str(index)+"'")
            except TypeError as te:
                raise ParameterException("(Procedure) "+methName+", invalid index: "+str(te))
        
            #make absolute index
            index = getAbsoluteIndex(index, len(self.stringCmdList))
        
            #check access
            if index <= self.lockedTo:                
                if len(self.stringCmdList) == 0:
                    message = "Command list is empty"
                elif len(self.stringCmdList) == 1:
                    message = "Only index 0 is available"
                else:
                    message = "A value between 0 and "+str(len(self.stringCmdList)-1) + " was expected"
            
                raise ParameterException("(Procedure) "+methName+", invalid index. "+message+", got '"+str(index)+"'")
        
    def upCommand(self,index):
        self.moveCommand(index,index-1)
        
    def downCommand(self,index):
        self.moveCommand(index,index+1)
    
    def clone(self, From=None):
        if From is None:
            From = ProcedureFromList(self.name)
        
        From.stringCmdList = self.stringCmdList[:]
        From.lockedTo      = self.lockedTo
        
        return Procedure.clone(self,From)
        
    def __hash__(self):
        pass #TODO
        
    def getListOfCommandsToSave(self):
        pass #TODO       
        
class ProcedureFromFile(Procedure): #TODO probably remove this class, and replace by a method to load a file into a ProcedureInQueue, don't care about TODO in this class
    def __init__(self, filePath, settings = None):
        Procedure.__init__(self, "execute "+str(filePath), settings)
        self.setFilePath(filePath)
    
    def getFilePath(self):
        return self.filePath
        
    def setFilePath(self, filePath):
        #TODO readOnly, path validity, ...
        self.filePath = filePath
    
    def execute(self, parameters):
        #make a copy of the current procedure
        engine = None
        
        #for cmd in self.stringCmdList:
        index = 1
        with open(self.filePath) as f:
            for line in f:
                lastException, engine = self._innerExecute(line, self.name + " (line: "+str(index)+")", parameters) 
                index += 1

        #return the result of last command in the procedure
        if engine is None:
            return ()
            
        return engine.getLastResult()
    
    def clone(self, From=None):
        if From is None:
            From = ProcedureFile(self.filePath)
            
        return Procedure.clone(self,From)
        
    def __hash__(self):
        return hash(str(hash(Procedure.__hash__(self))) + str(hash(self.filePath)))

######################################################################################################################################################

#concept
    #executer queue can change (add/remove/move/swap/...)
    #in loader queue, no swapping/move
        #registered command will never move or be removed
        #extra command are always added at the end and can be added or removed
    
    #key are never swapped, if two node are exchanged, the key stay attached to the node, not to the position in the queue
    
    #don't allow command merging from different loader 
        #it won't be saved, so why allow to merge command from different loader at running time ? just considere a loader group like a individual statement
        #but allow to order the loaders

#TODO implementation
    #TODO need a granularity in the loader execution and between the loader execution
        #the inner granularity will stop the loader execution
            #store it in loader state
            #has to be used in hashing and to be saved if needed
        
        #the outer granularity will stop the whole execution
            #should be stored in setting
            #and be saved if updated
        
    #TODO false branching

#TODO BRAINSTORMING TODO
    
    #PRBLM 1: how to save loader order ? SOLVED
        #prblm, loader are not always loaded in the same order
        #in system, like fantom settings ?
            #uuuh, how to store that ? 
                #always before/after other loader ?
                #at least position x ?
                #store full loader list ?
                #...
        #no order, executed in front of loading order ? easiest one
            #loaders are independant and execution order shouldn't have any impact on them
            #if a loader need to be executed after another one, just add a dependancy in the loader to require the other loader to be loaded before XXX
    
    #PRBLM 2a: what about loader isolation ? if a loader loops forever? TODO (? do we really need to manage that ?)
        #if a loader loop forever, hard to execute the next loader statement
        #a procedure is mono threading, no easy way to solve that
        
        #SOLUTION 1: execute each sub loader in its own thread
            #could be a boolean option to enable mono/multi threading in process execution
        
        #SOLUTION 2: implement a forever loop detection (uhuh, easy one)
            #forget this solution
            
        #SOLUTION 3: 
        
    #PRBLM 2b: what about loader isolation ? if a loader crashes ? SOLVED
        #about crashed? add a settings or an error isolation level (so each loader statement has its error level + one isolation level for the whole procedure)
        #store the information in the loader config.profile file
    
    #PRBLM 3: how to store command in memory for each loader? SOLVED
        #GOAL: insert/remove in o(1) and unload in o(n) with n the amount of command into a loader queue
        
        #still used the double linked queue with dict, but for each loader
        #each command are tagged as registered/extra, count the amount of registered command
        #key generation is isolated in each loader, so two command in two different loader can have the same key
        #can also disable command
        #only extra command are removable, registered command are not removable, only disabling
        #registered command hold the x first key, no more, no less, the x is a constant
        #each key up to the x first is an extra key, no more need of boolean to identify extra command
        
        #on unload, iterate from the first command in list
            #if register at the correct place (compare key and position), do nothing
            #if register at the wrong place, add moveCommand
            #if extra before the last registered, addCommand + moveCommand
                #move what ? extra or registered ? extra.
                    #registered will always be added before extra, and a move occur in front of existing thing, so move extra
            #if extra after last registed, just addCommand
            
        #PRBLM 3.1: define move
            #relative move ? absolute move ? in front of key ? in front of zero ?
            #key can move
            
            #ONLY SOLUTION for this structure:
                #can only move in front of an existing key (after/before)
                #can move before first, after last
                
                #in loading, always move in front of the nearest registered key
                #or if there is no registering key, in front of the first command in list
            
    #PRBLM 4: what about goto/false jump with this structure ? (see brainstorming above) SOLVED
        #goto can only work FROM and TO instruction of the same loader
        #what about command move ?
        
        #SOLUTION 1: goto hold the string key (into the command call)
            #--- if the target node is removed, the key is useless
        
        #SOLUTION 2: goto hold reference node (into an interpreted argument of the command call)
            #--- if the target node is removed, hold a reference to an unexistant node
        
        #SOLUTION 3: goto is stored into node, use special node for goto instruction
        
        
        #SOLUTION 4: each node is a binary crossroad and can go to a "true" or a "false" direction XXX
            #create a field falseNext in node
            #create a method to set next node (not bases on the key like now)
                #a method like "use falseNext if difined" (?) or raise ?
            #create a method to change the branching and call this method in the addon method directly
            
            #PRBLM 1: a node can ben targetted by more than one other node SOLVED
                #it breaks the paradigms of double linked list
                
                #SOLUTION 1: do not hold falsePrev
                
                #SOLUTION 2: hoold a falsePrev list
                    #could create a real mess
                    #no easy way to manage removable
                
                #SOLUTION 3a: a node can only hold a single falsePrev
                    #so if a node already hold a falsePrev, add a dummy node (without command) before the targetted node
                    #this node is not removable
                    #this node will be automaticaly removed if its source node is removed
                    
                #SOLUTION 3b: same as 3a but only dumb node can hold falsePrev XXX
                    #could be better to forbide a legit node to be targetted as falseNext
                    #so if a legit node is removed, and it possess a false link, remove the dumb node at the opposite side of the link
                    
                    #a dumb node does not really need to hold a falsePrev reference to its legit node
                        #this information will never be used during operation
                        #it is only usefull during printing
                        #to conclude, keep it :)
                        
                    #a dumb node does not hold a key, it is not possible to access to it, and so, not possible to remove it
                    
                    #if an insertion of a legit node occurs BEFORE a legit node, AND the node already existing before this legit node is a dumb node
                        #insert the new legit node before every existing dumb node that exist before the targetted legit node
                        
                    #PRBLM 1: if a legit node is removed, it won't be possible to restore the previous situation with a simple add
                        #because it is forbid to insert legit node after a dumb node
                        
                        #SOLUTION: give a key to the dumb node, and allow to insert after/before them
                            #in this case of a such insertion, it is not a problem to have dumb node before
                            
                            #BUT if we insert before a legit node, it is still forbidden to have dumb node before !
            
            #PRBLM 2: what if the target node is removed ? SOLVED
                #SOLUTION 1: keep a list of source node in the target one
                    #then what ? 
                        #remove source node ?
                            #will probably change procedure behaviour
                        #move the goto to the next node ?
                            #risk to create forever loop in procedure
                            
                #SOLUTION 2: keep a source counter
                    #if try to remove the node and the counter is bigger than 0, raise
                    #event "force" argument won't be able to remove the node
                    
                #SOLUTION 3: gave the choice to the user
                    #remove on cascade
                    #jump to next 
                    #raise if the node is targetted (default behavior)
                    #other ?
                    
                #SOLUTION 4: keep a list of parentNextFalse
                    #if a node is removed, removed its reference from any other node prevFalse
                    #and in the procedure showing, print a red reference next the GOTO without falseNext
                    
                #SOLUTION 5: dumb node system, see problem 1 XXX
                
    #PRBLM 5: we will have a language of procedure definition AND a language of procedure execution. TODO
        #and the procedure definition language can be used in procedure execution
        #so a procedure could itself update its code
            #NOT POSSIBLE, a procedure execution is a clone of the updatable procedure, an update won't have any impact on the current execution
            #only runtime commands have an impact on the current execution
            
        #ideally should be reduced to a single execution language, even if some method allow
        #it is better to see a procedure in script file like it will execute, not like it will be build...
            
        #a command like 'goto' could exist but its target will be interpreted at running time, not at definition
            #and so could be a mistake seed...
        
        #SOLUTION 1: add a syntax element 'target' than will be interpreted on syntax parsing
            #ex: 'target:', '[target]', ...

            #TODO create a new kind of node, target node (think about it)
            
        #SOLUTION 2: stay like that
        
        #SOLUTION 3:

## CONST DECLARATION ##

DEFAULT_KEY_NAME     = "key"
FIRST_KEY_NAME       = "first key"
SECOND_KEY_NAME      = "second key"
DESTINATION_KEY_NAME = "destination key"

## NODE DECLARATION ##

class AbstractCommandNode(object):
    def __init__(self, key):
        self.key        = key
        self.parser     = None
        self.enabled    = True

    def isEnabled(self):
        return self.enabled

    def isCommandNode(self):
        return self.parser is not None

    def isDumbNode(self):
        return self.parser is None

class CommandNode(AbstractCommandNode):
    def __init__(self, key, parser):
        AbstractCommandNode.__init__(self, key)
        self.parser = parser

        #list of execution
        self.prev      = None
        self.next      = None
        self.nextFalse = None
                
    def __hash__(self):
        return hash(str(self.key)+str(self.enabled)+str(hash(self.parser))) 

class DumbCommandNode(AbstractCommandNode):
    def __init__(self, key, originNode):
        AbstractCommandNode.__init__(self,key)
        self.falsePrev = originNode

    def __hash__(self):
        return hash(str(self.key)+str(self.enabled)+str(hash(self.falsePrev.parser))) 

## QUEUE DECLARATION ##

class CommandQueue(object):
    def __init__(self, queueGranularity=None):
        self.commandMap       = {}
        self.firstCommand     = None
        self.lastCommand      = None
        self.nextAvailableKey = 0
        self.registeredCount  = 0

    def extractCommandFromQueue(self, cmd):
        if cmd.prev is not None:
            cmd.prev.next = cmd.next

        if cmd.next is not None:
            cmd.next.prev = cmd.prev
            
        if cmd is self.firstCommand:
            self.firstCommand = cmd.next
            
        if cmd is self.lastCommand:
            self.lastCommand = cmd.prev

        cmd.prev = cmd.next = None

        return cmd
        
    def addAfter(self, nodeToInsert, targetNode):
        if nodeToInsert is targetNode:
            return nodeToInsert
            
        if targetNode is None:
            self.firstCommand = self.lastCommand = nodeToInsert
            return nodeToInsert
            
        nodeToInsert.next = targetNode.next
        nodeToInsert.prev = targetNode
        
        if targetNode is self.firstCommand:
            self.firstCommand = nodeToInsert
        else:
            nodeToInsert.next.prev = nodeToInsert
        
        targetNode.next = nodeToInsert
        
        return nodeToInsert
        
    def addBefore(self, nodeToInsert, targetNode):
        if nodeToInsert is targetNode:
            return nodeToInsert
            
        if targetNode is None:
            self.firstCommand = self.lastCommand = nodeToInsert
            return nodeToInsert
            
        nodeToInsert.next = targetNode
        nodeToInsert.prev = targetNode.prev
        
        if targetNode is self.firstCommand:
            self.firstCommand = nodeToInsert
        else:
            nodeToInsert.prev.next = nodeToInsert
        
        targetNode.prev = nodeToInsert
        
        return nodeToInsert
            
    def exchangeCommand(self, firstCommand, secondCommand):
        firstNext = firstCommand.next
        firstPrev = firstCommand.prev
        
        firstCommand.next = secondCommand.next
        firstCommand.prev = secondCommand.prev
        
        if secondCommand is self.firstCommand:
            self.firstCommand = firstCommand
            
        if secondCommand is self.lastCommand:
            self.lastCommand = firstCommand
            
        secondCommand.next = firstNext
        secondCommand.prev = firstPrev
        
        if firstCommand is self.firstCommand:
            self.firstCommand = secondCommand
            
        if firstCommand is self.lastCommand:
            self.lastCommand = secondCommand
            
    def createNewNode(self,parser):
        newNode = CommandNode(self.nextAvailableKey,parser)
        self.nextAvailableKey += 1
        self.size += 1
        return newNode

    #TODO create false node (really needed ? is it not possible to do it in setNextFalse ?)
        
    def getNode(self, key, origin, methName, keyName = DEFAULT_KEY_NAME): #TODO add a parameter forUpdate
        #TODO if for update and is a dumb, raise

        if key not in self.commandMap:
            raise ParameterException("(ProcedureInQueue) "+str(methName)+", not existant "+str(keyName)+" '"+str(key)+"' for loader '"+str(origin)+"'")
            
        return self.commandMap[key]

    def setNextFalse(self, command, nextFalseCommand): #TODO some update to do in front of dumb node system
        if command.nextFalse is not None:
            #TODO find first real node then compare
            #if command.nextFalse is nextFalseCommand:
            #    return

            self.extractCommandFromQueue(command.nextFalse)

        command.nextFalse = nextFalseCommand

        if nextFalseCommand is not None:
            if nextFalseCommand.falsePrev is None:
                nextFalseCommand.falsePrev = set()

            nextFalseCommand.falsePrev.add(command)
        
    def __hash__(self):
        hashString = ""
        currentNode = self.firstCommand
        
        while currentNode is not None:
            hashString += str(hash(currentNode))
            currentNode = currentNode.next
        
        return hash(hashString)
        
    def clone(self): #TODO manage new dumb node system
        cloned = CommandQueue()
        cloned.nextAvailableKey = self.nextAvailableKey
        cloned.registeredCount = self.registeredCount
        
        if self.firstCommand is not None:
            currentNode         = self.firstCommand
            
            currentClonedNode   = CommandNode(self.firstCommand.key, self.firstCommand.parser)
            cloned.firstCommand = currentClonedNode
            clones.commandMap[currentClonedNode.key] = currentClonedNode
            
            while currentNode.next is not None:
                newClonedNode = CommandNode(currentNode.next.key, currentNode.next.parser)
                clones.commandMap[newClonedNode.key] = newClonedNode
                currentClonedNode.next = newClonedNode
                newClonedNode.prev     = currentClonedNode
                
                currentNode = currentNode.next
                currentClonedNode = newClonedNode
                
            cloned.lastCommand = currentClonedNode

        return cloned   

## PROCEDURE DECLARATION ##

class ProcedureInQueue(UniCommand):
    def __init__(self, name, settings = None, cloned=False):
        UniCommand.__init__(self, self._internalProcess, None, None) #by default, enable on pre process #TODO this information should be stored

        self.setStopProcedureOnFirstError() #default error policy  #TODO should be in settings
                
        if settings is not None:
            if not isinstance(settings, GlobalSettings):
                raise ParameterException("(EnvironmentParameter) __init__, a LocalSettings was expected for settings, got '"+str(type(settings))+"'")

            self.settings = settings
        else:
            self.settings = GlobalSettings()
            
        #persistent fields
        self.name        = name
        self.loopEnabled = False #TODO should be in settings
            
        #working fields
        self.interrupt          = False
        self.interruptReason    = None
        self.nextCommand        = None
        self.currentLoader      = None
        self.currentLoaderState = None
        self.useFalseBranch     = False
        
        #transient fields
        self.size = 0

        #cloned procedure does not need to be protected, will never be used in several thread
        if cloned: 
            self._internalLock = FAKELOCK
        else:
            self._internalLock = threading.Lock()
        
    ### PRE/POST process ###
    
    def _setArgs(self,parameters, args):
        parameters.variable.setParameter("*", VarParameter(' '.join(str(x) for x in args)), localParam = True)    #all in one string
        parameters.variable.setParameter("#", VarParameter(len(args)), localParam = True)                         #arg count
        parameters.variable.setParameter("@", VarParameter(args), localParam = True)                              #all args
        parameters.variable.setParameter("?", VarParameter( ()), localParam = True)                               #value from last command
        parameters.variable.setParameter("!", VarParameter( ()), localParam = True)                               #last pid started in background        
        parameters.variable.setParameter("$", VarParameter(parameters.getCurrentId()), localParam = True) #current process id 

    def enableOnPreProcess(self):
        del self[:]
        MultiCommand.addProcess(self,self._internalProcess,None,None)
        
    def enableOnProcess(self):
        del self[:]
        MultiCommand.addProcess(self,None,self._internalProcess,None)
        
    def enableOnPostProcess(self):
        del self[:]
        MultiCommand.addProcess(self,None,None,self._internalProcess)

    @shellMethod(args       = listArgChecker(ArgChecker()),
                 parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())            
    def _internalProcess(self, args, parameters):
        parameters.pushVariableLevelForThisThread(self)
        
        threadID, level = parameters.getCurrentId()
        
        if level == 0 and self.errorGranularity is not None:
            warning("execution of the procedure "+str(self.name)+" at level 0 with an error granularity equal to '"+str(self.errorGranularity)+"'.  Any error with a granularity equal or lower will stop the application.")
        
        self._setArgs(parameters, args)
        try:
            return self.execute(parameters)
        finally:
            parameters.popVariableLevelForThisThread()
    
    def interrupt(self, reason=None):
        self.interruptReason = reason
        self.interrupt       = True #ALWAYS keep interrupt at last, because it will interrupt another thread, and the other thread could be interrupt before the end of this method if interrupt is not set at the end
        
    def _innerExecute(self, cmd, name, parameters):
        if self.interrupt:
            if self.interruptReason is None:
                raise engineInterruptionException("this process has been interrupted", abnormal=True)
            else:
                raise engineInterruptionException("this process has been interrupted, reason: '"+str(self.interruptReason)+"'", abnormal=True)

        lastException, engine = execute(cmd, parameters, name)  
        param = parameters.variable.getParameter("?",perfectMatch = True, localParam = True, exploreOtherLevel=False)

        if lastException is not None: 
            #set empty the variable "?"
            param.setValue( () )
            
            #manage exception
            if isinstance(lastException, PyshellException):
                severity = lastException.severity
            else:
                severity = ERROR
            
            if self.errorGranularity is not None and severity <= self.errorGranularity:
                if isinstance(lastException, ProcedureStackableException):
                    lastException.append( (cmd, name,) )
                    raise lastException
                
                exception = ProcedureStackableException(severity, lastException)
                exception.procedureStack.append( (cmd, name,) )
                
                threadID, level = param.getCurrentId()
                if level == 0:
                    self._printProcedureStack(exception, threadID, 0)
                
                raise exception
            
            if isinstance(lastException, ProcedureStackableException):
                threadID, level = param.getCurrentId()
                lastException.procedureStack.append( (cmd, name,) )
                self._printProcedureStack(lastException, threadID, level)
            
        else:
            if engine is not None and engine.getLastResult() is not None and len(engine.getLastResult()) > 0:
                param.setValue( engine.getLastResult() )
            else:
                param.setValue( () )

        return lastException, engine
    
    def _printProcedureStack(self, stackException, threadID, currentLevel):
        if len(stackException.procedureStack) == 0:
            return
    
        toPrint = ""
        for i in range(0,len(stackException.procedureStack)):
            cmd, name = stackException.procedureStack[ len(stackException.procedureStack) - i - 1 ]
            toPrint += (i * " ") + str(name) + " : " + str(cmd) + "(level="+str(currentLevel+i)+")\n"
        
        toPrint = toPrint[:-1]
        colorFun = getPrinterFromExceptionSeverity(stackException.severity)
        printShell(colorFun(toPrint))
    
    ###### get/set method
                    
    def setStopProcedureOnFirstError(self):
        self.setStopProcedureIfAnErrorOccuredWithAGranularityLowerOrEqualTo(sys.maxint)
        
    def setNeverStopProcedureIfErrorOccured(self):
        self.setStopProcedureIfAnErrorOccuredWithAGranularityLowerOrEqualTo(None)
            
    def setStopProcedureIfAnErrorOccuredWithAGranularityLowerOrEqualTo(self, value): 
        """
        Every error granularity bellow this limit will stop the execution of the current procedure.  A None value is equal to no limit.  
        """
        
        if value is not None and (type(value) != int or value < 0):
            raise ParameterException("(Procedure) setStopProcedureIfAnErrorOccuredWithAGranularityLowerOrEqualTo, expected a integer value bigger than 0, got '"+str(type(value))+"'")

        self.errorGranularity = value
    
    def getErrorGranularity(self):
        return self.errorGranularity
                
    ## overrided methods ##
    
    def execute(self, parameters):
        engine = None

        #TODO manage inner granularity

        while True:
            for self.currentLoader, self.currentLoaderState in self.settings.getLoaders().items():
                currentCommand = self.currentLoaderState.firstCommand
                while currentCommand is not None:
                
                    #TODO if currentCommand is dumb, jump to next
                
                    if currentCommand.isEnabled():
                        lastException, engine = self._innerExecute(currentCommand.parser, self.name + " (key: "+str(currentCommand.key)+", loader: '"+str(self.currentLoader)+"')", parameters)

                    if self.nextCommand is not None:
                        currentCommand = self.nextCommand
                        self.nextCommand = None
                    else:
                        currentCommand = currentCommand.next

            if not self.loopEnabled:
                break

        self.currentLoader      = None
        self.currentLoaderState = None

        #return the result of last command in the procedure
        if engine is None:
            return ()
            
        return engine.getLastResult()
        
    ## runtime method ##
    
    def setNextCommandToExecute(self, key):
        if self.currentLoaderState is None or self.currentLoader is None:
            raise ParameterException("(ProcedureInQueue) setNextCommandToExecute, not possible to set next command to execute, the procedure is not running")

        self.nextCommand = self.currentLoaderState.getNode(key, self.currentLoader, "setNextCommandToExecute")
        
    def tryToUseFalseBranching(self): #TODO should check if running mode 
        self.useFalseBranch = True
                        
    ## check methods ##
    
    def _checkOrigin(self, origin, methName, createIfDoesNotExist=False):
        if origin is None:
            origin = SYSTEM_VIRTUAL_LOADER

        if not self.settings.hasLoaderState(origin):
            if not createIfDoesNotExist:
                raise ParameterException("(ProcedureInQueue) "+str(methName)+", the loader '"+str(origin)+"' does not exist in this procedure")

            loaderInfo = self.settings.setLoaderState(origin,CommandQueue())
        else:
            loaderInfo = self.settings.getLoaderState(origin)

        return origin, loaderInfo

    def _checkCommandString(self, commandStringList, methName):
        if not isinstance(commandStringList, Parser):
            parser = commandStringList
        else:
            parser = Parser(commandString)

        if not parser.isParsed():
            parser.parse()

        if len(parser) == 0:
            raise ParameterException("(Procedure) '"+str(methName)+"', try to add a command string that does not hold any command")

        return parser
            
    ## add method ##
    
    @synchronous()
    def removeCommand(self, key, origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "removeCommand", createIfDoesNotExist=False)
        target = loaderInfo.getNode(key, origin, "removeCommand")
        
        #TODO if target is a dumbNode, raise
        
        #is a command registered ? call disabling then return.  removing not allowed
        if target.key < loaderInfo.registeredCount:
            target.enabled = False
            return
        
        #remove from executing queue
        loaderInfo.extractCommandFromQueue(target)      
        self.size -= 1

        #TODO if a fals branching exist, remove it

    @synchronous()
    def addCommandBefore(self, key, commandStringList, origin=None):
        parser             = self._checkCommandString(commandStringList, "addCommandBefore")
        origin, loaderInfo = self._checkOrigin(origin, "addCommandBefore", createIfDoesNotExist=False)
        target             = loaderInfo.getNode(key, origin, "addCommandBefore")
        newNode            = loaderInfo.createNewNode(parser)
        
        #TODO if target.prev is a dumb node, need to retrieve the first node to the bigging with a prev == None or equal to a legit node
        
        return loaderInfo.addBefore(self, newNode, target)
    
    @synchronous()
    def addCommandAfter(self, key, commandStringList, origin=None):
        parser             = self._checkCommandString(commandStringList, "addCommandAfter")
        origin, loaderInfo = self._checkOrigin(origin, "addCommandAfter", createIfDoesNotExist=False)
        target             = loaderInfo.getNode(key, origin, "addCommandAfter")
        newNode            = loaderInfo.createNewNode(parser)
        
        return loaderInfo.addAfter(self, newNode, target)
    
    @synchronous()
    def addCommandFirst(self, commandString, origin=None):
        parser             = self._checkCommandString(commandStringList, "addCommandFirst")
        origin, loaderInfo = self._checkOrigin(origin, "addCommandFirst", createIfDoesNotExist=True)
        newNode            = loaderInfo.createNewNode(parser)
        
        return loaderInfo.addBefore(self, newNode, loaderInfo.firstCommand)
    
    @synchronous()
    def addCommandLast(self, commandString, origin=None):
        parser             = self._checkCommandString(commandStringList, "addCommandLast")
        origin, loaderInfo = self._checkOrigin(origin, "addCommandLast", createIfDoesNotExist=True)
        newNode            = loaderInfo.createNewNode(parser)
        
        return loaderInfo.addAfter(self, newNode, loaderInfo.lastCommand)
    
    ## exchange method ##
    
    @synchronous()
    def exchangeCommand(self,firstKey, secondKey, origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "exchangeCommand", createIfDoesNotExist=False)
        firstNode          = loaderInfo.getNode(firstKey, origin, "exchangeCommand",FIRST_KEY_NAME)
        secondNode         = loaderInfo.getNode(secondKey, origin, "exchangeCommand",SECOND_KEY_NAME)
        
        loaderInfo.exchangeCommand(firstNode, secondNode)
    
    @synchronous()
    def upCommand(self,key, origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "upCommand", createIfDoesNotExist=False)
        node               = loaderInfo.getNode(firstKey, origin, "upCommand")
        
        if node.prev is None:
            return
            
        loaderInfo.exchangeCommand(node.prev, node)
    
    @synchronous()
    def downCommand(self,key, origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "downCommand", createIfDoesNotExist=False)
        node               = loaderInfo.getNode(firstKey, origin, "downCommand")
        
        if node.next is None:
            return
            
        loaderInfo.exchangeCommand(node.next, node)
    
    ## move method ##
    
    @synchronous()
    def moveCommandAfter(self, key, destinationKey, origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "moveCommandBefore", createIfDoesNotExist=False)
        nodeToMove         = loaderInfo.getNode(key, origin, "moveCommandAfter")
        nodeDestination    = loaderInfo.getNode(destinationKey, origin, "moveCommandAfter",DESTINATION_KEY_NAME)
                
        if nodeToMove is nodeDestination or nodeDestination.next is nodeToMove: #position is already ok
            return
            
        loaderInfo.extractCommandFromQueue(nodeToMove)
        loaderInfo.addAfter(nodeToMove, nodeDestination)
    
    @synchronous()
    def moveCommandBefore(self, key, destinationKey, origin=None): 
        origin, loaderInfo = self._checkOrigin(origin, "moveCommandBefore", createIfDoesNotExist=False)
        nodeToMove         = loaderInfo.getNode(key, origin, "moveCommandBefore")
        nodeDestination    = loaderInfo.getNode(destinationKey, origin, "moveCommandBefore",DESTINATION_KEY_NAME)
                
        if nodeToMove is nodeDestination or nodeDestination.prev is nodeToMove: #position is already ok
            return
        
        #TODO if nodeDestination.prev is a dumb node, need to retrieve the first node to the bigging with a prev == None or equal to a legit node
        
        loaderInfo.extractCommandFromQueue(nodeToMove)
        loaderInfo.addBefore(nodeToMove, nodeDestination)
    
    @synchronous()
    def moveCommandFirst(self, key, origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "moveCommandBefore", createIfDoesNotExist=False)
        nodeToMove         = loaderInfo.getNode(key, origin, "moveCommandBefore")
                
        if nodeToMove is loaderInfo.firstCommand: #position is already ok
            return
            
        loaderInfo.extractCommandFromQueue(nodeToMove)
        loaderInfo.addBefore(nodeToMove, loaderInfo.firstCommand)
    
    @synchronous()
    def moveCommandLast(self, key, origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "moveCommandBefore", createIfDoesNotExist=False)
        nodeToMove         = loaderInfo.getNode(key, origin, "moveCommandAfter")
                
        if nodeToMove is loaderInfo.lastCommand: #position is already ok
            return
            
        loaderInfo.extractCommandFromQueue(nodeToMove)
        loaderInfo.addAfter(nodeToMove, loaderInfo.lastCommand)

    ## false next method ##

    def setFalseBranching(self, key, targetKey, origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "setFalseBranching", createIfDoesNotExist=False)
        nodeToSet          = loaderInfo.getNode(key, origin, "setFalseBranching")
        nodeDestination    = loaderInfo.getNode(targetKey, origin, "setFalseBranching",DESTINATION_KEY_NAME)
        
        #TODO nodeToSet can not be a dumb node
        
        #TODO nodeDestination can not be a sumb node
        
        #TODO if a falseBranching exist on nodeToSet, remove it
        
        #TODO create and insert new false branching
    
    ## loop method ##
    
    def enableLoop(self):
        self.loopEnabled = True
        
    def disableLoop(self):
        self.loopEnabled = False
        
    def isLoop(self):
        return self.loopEnabled
        
    ## enabling method ##
        
    @synchronous()
    def enableCommand(self, key,origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "enableCommand")
        node               = loaderInfo.getNode(key, origin, "enableCommand")
        node.enabled = True
        
    @synchronous()
    def disableCommand(self, key,origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "disableCommand")
        node               = loaderInfo.getNode(key, origin, "disableCommand")
        node.enabled = False
    
    @synchronous()
    def isCommandDisabled(self, key,origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "isCommandDisabled")
        node               = loaderInfo.getNode(key, origin, "isCommandDisabled")
        return node.isEnabled()
    
    ## misc method ##
            
    def __hash__(self):
        return hash(self.settings)
    
    def getSize(self):
        return self.size
            
    @synchronous()
    def clone(self, From=None):
        if From is None:
            From = ProcedureInQueue(name=self.name, settings = self.settings.clone(), cloned=True)
        
        From.errorGranularity = self.errorGranularity
        From.size             = self.size
        From.loopEnabled      = self.loopEnabled
                            
        return Procedure.clone(From)
                
