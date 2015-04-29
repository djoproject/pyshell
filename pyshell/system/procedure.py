#!/usr/bin/python
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

#TODO brainstorming about origin usage, see TODO file

from pyshell.utils.exception   import DefaultPyshellException, PyshellException, ERROR, USER_ERROR, ListOfException, ParameterException, ParameterLoadingException, ProcedureStackableException
from pyshell.utils.executing   import execute
from pyshell.command.command   import UniCommand, MultiCommand
from pyshell.command.exception import engineInterruptionException
from pyshell.arg.decorator     import shellMethod
from pyshell.arg.argchecker    import ArgChecker,listArgChecker, defaultInstanceArgChecker
from pyshell.utils.parsing     import Parser
from pyshell.system.variable   import VarParameter
from pyshell.system.settings   import GlobalSettings
from pyshell.utils.printing    import warning,getPrinterFromExceptionSeverity,printShell
from pyshell.utils.constants   import SYSTEM_VIRTUAL_LOADER
import thread, threading, sys
                
### UTILS COMMAND ###
    
def getAbsoluteIndex(index, listSize):
    "convert any positive or negative index into an absolute positive one"

    if index >= 0:
        return index
    
    index = listSize + index
    
    #because python list.insert works like that, a value can be inserted with a negativ value out of boud
    #but some other function like update does not manage negativ out of bound value, and that's why it is set to 0
    if index < 0:
        return 0
    
    return index

class Procedure(UniCommand):#TODO should implement hash system, like parameter
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
    
    def setNextCommandIndex(self, index):
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
            From = Procedure(self.name)
        
        From.errorGranularity = self.errorGranularity
        #TODO does not clone settings ?
        return UniCommand.clone(self,From)
        
    def __hash__(self):
        return hash(self.settings)
            
class ProcedureFromList(Procedure): #TODO obsolete, will be replaced by ProcedureInQueue
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
        
class ProcedureFromFile(Procedure): #TODO probably remove this class, and replace by a method to load a file into a ProcedureInQueue
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

#concept
    #executer queue can change (add/remove/move/swap/...)
    #in loader queue, no swapping/move
        #registered command will never move or be removed
        #extra command are always added at the end and can be added or removed
    #key are never swapped

#TODO        
    #need way to protect command on update
        #because an execution could occur during an update and there is protection
        #during a cloning, a procedure shouldn't be updated
        #but a cloned one will never be cloned again, so no need to have lock in cloned

#TODO BRAINSTORMING about false branching
    #goto can only work FROM and TO instruction of the same loader
    
    #SOLUTION 1: goto hold the string key
    
    #SOLUTION 2: goto hold reference node
    
    #SOLUTION 3: goto is stored into node
    
    #SOLUTION 4: 
    

#TODO PRBLM 1: need to differenciate a registered command from an extra one 
    #why ? because a registered command can not be deleted
    #why ? because it will be pretty impossible to reverse the remove from a user instruction
    
    #could be interresting to find a solution without new variable
        #it should be possible to do that :/
    
    #SOLUTION 1: a boolean to indicate registering from extra XXX (for the moment)
        #easy to access, but need one more var
    
    #SOLUTION 2: keep the key value of the last registered, every bigger key are extra command
        #need a link to the loader information, so one more var too
        
    #SOLUTION 3: 

#TODO PRBLM 2: 
    #need to find an easy way to identify move between command of the same loader on the loader unload
    #need to have a tools that identify if a command is before or after another one in o(1)
        #no necessary needed to compute exact index, just have a tools "<"
    
    #SOLUTION 1: recompute index for the whole queue from the insertion point
        #--- insertion will become o(n)
        #no need to update other meth like remove
        #switch need to exchange key
    
    #SOLUTION 2: each CommandInQueue has a number, bigger than its previous but lower than its followers
        #yeah, then how to generate this number ?
        #and be carefull with float python precision
        
        #ALGO 1: sum of the two key then divide by two.
            #LIMITATION: after 40 insertion between two node, reach the python float limit...
            
        #ALGO 2: key concat (string)
            #e.g: previous has key "0", next has key "1", if we want to insert betweem these two key, the in-between key will be "0-1"
            # 0 < 1, 0< 0-1, 0-1 < 1
            #if we insert between 0-1 and 1, in-between key will be 0-1-1
            
            #--- string comparison
            #--- memory increase
            #--- comparison time increase in case of multiple insertion
            
        #ALGO 3: key concat (number)
            #same as algo 2 but use list of integer
            #take the key of the previous and the next and put them into a list
            #no size limit, integer comparison
            
            #--- memory increase
            #--- comparison time increase in case of multiple insertion
            
        #ALGO 4: TODO ???
            #need a key comparison in constant time
            #need a constant key size
            #no insertion limitation by key accuracy loss
    
    #SOLUTION 3: 
        #concept: each node hold: command, next in the same cat, prev in the same loader
                 #a method exist to find the next command in another loader 
                 
        #ALGO 1:  
        
    #SOLUTION 4: don't allow command merging from different loader XXX
        #it won't be saved, so why allow to merge command from different loader at running time ? just considere a loader group like a individual statement
        #but allow to order the loaders
        
        #PRBLM 1: how to save loader order ? TODO
            #in system, like fantom settings ?
                #uuuh, how to store that ? 
            #no order, executed in front of loading order ?
        
        #PRBLM 2: what about loader isolation ? if a loader loop forever or crashed ?
            #if a loader loop forever, hard to execute the next loader statement
            #about crashed? add a settings or an error isolation level (so each loader statement has its error level + one isolation level for the whole procedure)
            #where to store this information? phantom settings in system
        
        #PRBLM 3: how to store command in memory for each loader?
            #insert/remove in o(1) and unload in o(n) with n the amount of command into a loader queue
            
            #still used the double linked queue with dict, but for each loader
            #each command are tagged as registered/extra, count the amount of registered command
            #key generation is isolated in each loader, so two command in two different loader can have the same key
            #can also disable command
            #registered command hold the x first key, no more, no less
            #each key up to the x first is an extra key
            
            #on unload, iterate from the first command in list
                #if register at the correct order, do nothing
                #if register at the wrong place, add moveCommand
                #if extra before the last registered, addCommand + moveCommand
                #if extra after last registed, just addCommand
            
        

DEFAULT_KEY_NAME     = "key"
FIRST_KEY_NAME       = "first key"
SECOND_KEY_NAME      = "second key"
DESTINATION_KEY_NAME = "destination key"

class _CommandInQueue(object):
    def __init__(self, key, parser):
        self.key    = key
        self.parser = parser
        
        #list of execution (order can change)
        self.prev = None
        self.next = None
        
        #list of insertion (order never change)
        self.loaderPrev = None
        self.loaderNext = None
        
        self.enabled    = True
        self.registered = False #TODO set it to True in loader
        
    def isEnabled():
        return self.enabled
        
    def isAregisteredCommand():
        return self.registered
        
class ProcedureInQueue(Procedure):
    def __init__(self, name, settings = None):
        Procedure.__init__(self, name, settings)
        self.nextAvailableKey = 0
        self.size             = 0
        self.firstCommand     = None
        self.lastCommand      = None
        self.commandMap       = {}
        self.nextCommand      = None
        
    def execute(self, parameters):
        engine = None
        
        #for cmd in self.stringCmdList:
        i = 0
        currentCommand = self.firstCommand
        while currentCommand is not None:
            if currentCommand.isEnabled():
                lastException, engine = self._innerExecute(currentCommand.parser, self.name + " (key: "+str(currentCommand.key)+")", parameters)

            if self.nextCommand is not None:
                currentCommand = self.nextCommand
                self.nextCommand = None
            else:
                currentCommand = currentCommand.nextTrue

        #return the result of last command in the procedure
        if engine is None:
            return ()
            
        return engine.getLastResult()
                
    #### business method
    
    def getSize(self):
        return self.size
    
    def _raiseIfInvalidKey(self, key, methName, keyName = DEFAULT_KEY_NAME):
        if key not in self.commandMap:
            raise ParameterException("(ProcedureInQueue) "+str(methName)+", not existant "+str(keyName)+": "+str(key))
            
        return self.commandMap[key]

    def setNextCommandToExecute(self, key):
        self.nextCommand = self._raiseIfInvalidKey(key, "setNextCommandToExecute")
    
    def _extractCommandFromQueue(self, cmd):
        if cmd.prev is not None:
            cmd.prev.next = next
            
        if cmd.next is not None:
            cmd.next.prev = cmd.prev
            
        if cmd is self.firstCommand:
            self.firstCommand = cmd.next
            
        if cmd is self.lastCommand:
            self.lastCommand = cmd.prev
    
    def _addCommandBefore(self, commandNode, commandStringList, origin=None):
        parser = Parser(commandString)
        parser.parse()

        if len(parser) == 0:
            raise ParameterException("(Procedure) _addCommandBefore, try to add a command string that does not hold any command")
        
        #None origin is system
        if origin is None:
            origin = SYSTEM_VIRTUAL_LOADER
        
        newNode = CommandInQueue(self.nextAvailableKey,parser)
        self.nextAvailableKey += 1
        
        #first insertion
        if commandNode is None: 
            self.firstCommand = self.lastCommand = newNode
            self.settings.setLoaderState(origin, newNode)
            return

        if commandNode.prev is not None:
            newNode.prev = commandNode.prev
            newNode.prev.next = newNode
            
        commandNode.prev = newNode
        newNode.next = commandNode
        
        if commandNode is self.firstCommand:
            self.firstCommand = newNode
        
        if not self.settings.hasLoaderState(origin):
            self.settings.setLoaderState(origin, newNode)
            return
            
        previousState = self.settings.getLoaderState()
        previousState.loaderNext = newNode
        newNode.loaderPrev = previousState
        self.settings.setLoaderState(origin, newNode)
        
        self.size += 1
        
        return newNode
        
    def _addCommandAfter(self, commandNode, commandStringList, origin=None):
        parser = Parser(commandString)
        parser.parse()

        if len(parser) == 0:
            raise ParameterException("(Procedure) _addCommandAfter, try to add a command string that does not hold any command")
        
        #None origin is system
        if origin is None:
            origin = SYSTEM_VIRTUAL_LOADER
        
        newNode = CommandInQueue(self.nextAvailableKey,parser)
        self.nextAvailableKey += 1
        
        #first insertion
        if commandNode is None: 
            self.firstCommand = self.lastCommand = newNode
            self.settings.setLoaderState(origin, newNode)
            return

        if commandNode.next is not None:
            newNode.next = commandNode.next
            newNode.next.prev = newNode
            
        commandNode.next = newNode
        newNode.prev = commandNode
        
        if commandNode is self.lastCommand:
            self.lastCommand = newNode
        
        if not self.settings.hasLoaderState(origin):
            self.settings.setLoaderState(origin, newNode)
            return
            
        previousState = self.settings.getLoaderState()
        previousState.loaderNext = newNode
        newNode.loaderPrev = previousState
        self.settings.setLoaderState(origin, newNode)
        
        self.size += 1
        
        return newNode
        
    def removeCommand(self, key):
        ciq = self._raiseIfInvalidKey(key, "removeCommand")
        
        #is a command registered ? call disabling then return.  removing not allowed
        if ciq.isAregisteredCommand():
            ciq.enabled = False
            return
        
        #remove from executing queue
        self._extractCommandFromQueue(ciq)
        
        #remove from loader queue
        if ciq.loaderPrev is not None:
            ciq.loaderPrev.loaderNext = ciq.loaderNext
        
        if ciq.loaderNext is not None:
            ciq.loaderNext.loaderPrev = ciq.loaderPrev
            
        self.size -= 1
        
    def addCommandBefore(self, key, commandStringList, origin=None):
        return self._addCommandBefore(self, self._raiseIfInvalidKey(key, "addCommandBefore"), commandStringList, origin)
        
    def addCommandAfter(self, key, commandStringList, origin=None):
        return self._addCommandAfter(self, self._raiseIfInvalidKey(key, "addCommandAfter"), commandStringList, origin)
        
    def addCommandFirst(self, commandString, origin=None):
        return self._addCommandBefore(self, self.firstCommand, commandStringList, origin)
        
    def addCommandLast(self, commandString, origin=None):
        return self._addCommandAfter(self, self.lastCommand, commandStringList, origin)
            
    def _exchangeCommand(self, firstCommand, secondCommand):
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
                
    def exchangeCommand(self,firstKey, secondKey):
        self._exchangeCommand(self._raiseIfInvalidKey(firstKey, "exchangeCommand",FIRST_KEY_NAME), self._raiseIfInvalidKey(secondKey, "exchangeCommand", SECOND_KEY_NAME))
            
    def upCommand(self,key):
        ciq = self._raiseIfInvalidKey(key, "upCommand")
        
        if ciq.prev is None:
            return
            
        self._exchangeCommand(ciq.prev, ciq)
        
    def downCommand(self,key):
        ciq = self._raiseIfInvalidKey(key, "downCommand")
        
        if ciq.next is None:
            return
            
        self._exchangeCommand(ciq.next, ciq)
                
    def moveCommandAfter(self, key, destinationKey): #TODO could be possible to create a common code with addAfter
        if key == destinationKey: #can not move a command on itself
            return
    
        ciq_toMove = self._raiseIfInvalidKey(key, "moveCommandAfter")
        ciq_destination = self._raiseIfInvalidKey(destinationKey, "moveCommandAfter",DESTINATION_KEY_NAME)
                
        if ciq_destination.next is ciq_toMove: #position is already ok
            return
            
        #remove command from its place
        self._extractCommandFromQueue(ciq_toMove)
        
        #put the command at its new place
        ciq_toMove.prev = ciq_destination
        ciq_toMove.next = ciq_destination.next
        ciq_destination.next = ciq_toMove
        
        if ciq_toMove.next is not None:
            ciq_toMove.next.prev = ciq_toMove
            
        if ciq_destination is self.lastCommand:
            self.lastCommand = ciq_toMove
        
    def moveCommandBefore(self, key, destinationKey): #TODO could be possible to create a common code with addBefore
        if key == destinationKey: #can not move a command on itself
            return
    
        ciq_toMove = self._raiseIfInvalidKey(key, "moveCommandBefore")
        ciq_destination = self._raiseIfInvalidKey(destinationKey, "moveCommandBefore",DESTINATION_KEY_NAME)
                
        if ciq_destination.prev is ciq_toMove: #position is already ok
            return
            
        #remove command from its place
        self._extractCommandFromQueue(ciq_toMove)
        
        #put the command at its new place
        ciq_toMove.next = ciq_destination
        ciq_toMove.prev = ciq_destination.prev
        ciq_destination.prev = ciq_toMove
        
        if ciq_toMove.prev is not None:
            ciq_toMove.prev.next = ciq_toMove
            
        if ciq_destination is self.firstCommand:
            self.firstCommand = ciq_toMove
        
    def enableLoop(self):
        if self.firstCommand is None:
            return
            
        self.firstCommand.prev = self.lastCommand
        self.lastCommand.next = self.firstCommand
        
    def disableLoop(self):
        if self.firstCommand is None:
            return
            
        self.firstCommand.prev = None
        self.lastCommand.next = None
        
    def isLoop(self):
        return self.firstCommand.prev is not None
        
    def enableCommand(self, key):
        ciq = self._raiseIfInvalidKey(key, "enableCommand")
        ciq.enabled = True
        
    def disableCommand(self, key):
        ciq = self._raiseIfInvalidKey(key, "disableCommand")
        ciq.enabled = False
        
    def isCommandDisabled(self, key):
        ciq = self._raiseIfInvalidKey(key, "isCommandDisabled")
        return ciq.isEnabled()
        
    def clone(self, From=None):
        #TODO clone what ?
            #executing queue
            #parent class
            #loaders queue (? not needed for an execution, and will be really hard to clone)
            #next key (?)
    
        pass #TODO
        
    def __hash__(self):
        #TODO each loader need a hash with its command
            #settings are only part of the system loader hash
            
            #three hash: hash_file, hash_default (static), current_hash
            #if hash_file is None and current_hash == hash_default => not a candidate to be saved
            #if hash_file is not None
                #if current_hash == hash_file => candidate to be save + does not trigger file regeneration
                #if current_hash == hash_default => need to be remove of the file + trigger file regeneration
                #else => need to be saved + trigger file regeneration
    
        #TODO hashing what ?
            #executing order (for each loader)
            #command instruction (for each loader)
            #parent (settings)(only for system loader)
            
        #TODO prblm, so need to know the execution order in loader to compute hash...
            
        pass #TODO
        
        
