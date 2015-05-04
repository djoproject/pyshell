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

if sys.version_info[0] < 2 or (sys.version_info[0] < 3 and sys.version_info[0] < 7):
    from pyshell.utils.ordereddict import OrderedDict #TODO get from pipy, so the path will change
else:
    from collections import OrderedDict 
                
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
        
        #clone call must block update

#TODO BRAINSTORMING about false branching
    #goto can only work FROM and TO instruction of the same loader
    #what about command move ?
    
    #SOLUTION 1: goto hold the string key
    
    #SOLUTION 2: goto hold reference node
    
    #SOLUTION 3: goto is stored into node
    
    #SOLUTION 4: 
    
        
#CURRENT STRUCT: don't allow command merging from different loader XXX
    #it won't be saved, so why allow to merge command from different loader at running time ? just considere a loader group like a individual statement
    #but allow to order the loaders
    
    #PRBLM 1: how to save loader order ?
        #prblm, loader are not always loaded in the same order
        #in system, like fantom settings ?
            #uuuh, how to store that ? 
                #always before/after other loader ?
                #at least position x ?
                #store full loader list ?
                #...
        #no order, executed in front of loading order ? easiest one XXX
            #loaders are independant and execution order shouldn't have any impact on them
            #if a loader need to be executed after another one, just add a dependancy in the loader to require the other loader to be loaded before
    
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
        #only extra command are removable
        #registered command hold the x first key, no more, no less, the x is a constant
        #each key up to the x first is an extra key, no more need of boolean to identify extra command
        
        #on unload, iterate from the first command in list
            #if register at the correct place (compare key and position), do nothing
            #if register at the wrong place, add moveCommand
            #if extra before the last registered, addCommand + moveCommand
                #move what ? extra or registered ? extra.
                    #registered will always be added before extra, and a move occur in front of existing thing, so move extra
            #if extra after last registed, just addCommand
            
        #PRBLM 3.1: define move TODO
            #relative move ? absolute move ? in front of key ? in front of zero ?
            #key can move
            
    #PRBLM 4: what about goto/false jump with this structure ? TODO
        

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
                
        self.enabled    = True
        
    def isEnabled():
        return self.enabled

    def __hash__(self):
        pass #TODO
            #value to hash: key, parser, enabled

class _LoaderInfo(object):
    def __init__(self):
        self.commandMap       = {}
        self.firstCommand     = None
        self.lastCommand      = None
        self.nextAvailableKey = 0
        self.registeredCount  = 0

    def __hash__(self):
        return object.__hash__(self)
        #TODO each loader need a hash with its command
            #settings are only part of the system loader hash
            
            #three hash: hash_file, hash_default (static), current_hash
            #if hash_file is None and current_hash == hash_default => not a candidate to be saved
            #if hash_file is not None
                #if current_hash == hash_file => candidate to be save + does not trigger file regeneration
                #if current_hash == hash_default => need to be remove of the file + trigger file regeneration
                #else => need to be saved + trigger file regeneration
    
        #TODO value to hash: command list, 

class ProcedureInQueue(Procedure):
    def __init__(self, name, settings = None):
        Procedure.__init__(self, name, settings)
        self.size               = 0
        self.nextCommand        = None
        self.loopEnabled        = False
        self.currentLoader      = None
        self.currentLoaderState = None
        
    def execute(self, parameters):
        engine = None

        while True:
            for self.currentLoader, self.currentLoaderState in self.settings.getLoaders().items():
                currentCommand = self.currentLoaderState.firstCommand
                while currentCommand is not None:
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
                
    #### business method
    
    def getSize(self):
        return self.size
    
    def _checkOrigin(self, origin, methName, createIfDoesNotExist=False):
        if origin is None:
            origin = SYSTEM_VIRTUAL_LOADER

        if not self.settings.hasLoaderState(origin):
            if not createIfDoesNotExist:
                raise ParameterException("(ProcedureInQueue) "+str(methName)+", the loader '"+str(origin)+"' does not exist in this procedure")

            loaderInfo = self.settings.setLoaderState(origin,_LoaderInfo())
        else:
            loaderInfo = self.settings.getLoaderState(origin)

        return origin, loaderInfo

    def _checkKey(self, key, origin, loaderInfo, methName, keyName = DEFAULT_KEY_NAME):
        if key not in loaderInfo.commandMap:
            raise ParameterException("(ProcedureInQueue) "+str(methName)+", not existant "+str(keyName)+" '"+str(key)+"' for loader '"+str(origin)+"'")
            
        return loaderInfo.commandMap[key]

    def _checkCommandString(self, commandStringList, methName):
        if not isinstance(commandStringList, Parser):
            parser = commandStringList
        else:
            parser = Parser(commandString)

        if not parser.isParsed()
            parser.parse()

        if len(parser) == 0:
            raise ParameterException("(Procedure) '"+str(methName)+"', try to add a command string that does not hold any command")

        return parser

    def setNextCommandToExecute(self, key):
        if self.currentLoader is None:
            raise ParameterException("(ProcedureInQueue) setNextCommandToExecute, not possible to set next command to execute, the procedure is not running")

        self.nextCommand = self._checkKey(key, self.currentLoader, self.settings.getLoaderState(self.currentLoader), "setNextCommandToExecute")
    
    def _extractCommandFromQueue(self, cmd, loaderInfo):
        if cmd.prev is not None:
            cmd.prev.next = cmd.next

        if cmd.next is not None:
            cmd.next.prev = cmd.prev
            
        if cmd is loaderInfo.firstCommand:
            loaderInfo.firstCommand = cmd.next

        cmd.prev = cmd.next = None

        return cmd

    def _addCommandBefore(self, commandNode, parser, origin, loaderInfo):
        newNode = CommandInQueue(loaderInfo.nextAvailableKey,parser)
        loaderInfo.nextAvailableKey += 1
        self.size += 1

        #first insertion
        if commandNode is None: 
            loaderInfo.firstCommand = loaderInfo.lastCommand = newNode
            return newNode

        if commandNode.prev is not None:
            newNode.prev = commandNode.prev
            newNode.prev.next = newNode
            
        commandNode.prev = newNode
        newNode.next = commandNode
        
        if commandNode is loaderInfo.firstCommand:
            loaderInfo.firstCommand = newNode
                
        return newNode
        
    def _addCommandAfter(self, commandNode, parser, origin, loaderInfo):      
        newNode = CommandInQueue(loaderInfo.nextAvailableKey,parser)
        loaderInfo.nextAvailableKey += 1
        self.size += 1
        
        #first insertion
        if commandNode is None: 
            loaderInfo.firstCommand = loaderInfo.lastCommand = newNode
            return newNode

        if commandNode.next is not None:
            newNode.next = commandNode.next
            newNode.next.prev = newNode
            
        commandNode.next = newNode
        newNode.prev = commandNode
        
        if commandNode is loaderInfo.lastCommand:
            loaderInfo.lastCommand = newNode
        
        return newNode
        
    def removeCommand(self, key, origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "removeCommand", createIfDoesNotExist=False)
        ciq = self._checkKey(key, origin, loaderInfo, "removeCommand")
        
        #is a command registered ? call disabling then return.  removing not allowed
        if ciq.key < loaderInfo.registeredCount:
            ciq.enabled = False
            return
        
        #remove from executing queue
        self._extractCommandFromQueue(ciq)      
        self.size -= 1

    def addCommandBefore(self, key, commandStringList, origin=None):
        parser = self._checkCommandString(commandStringList, "addCommandBefore")
        origin, loaderInfo = self._checkOrigin(origin, "addCommandBefore", createIfDoesNotExist=False)
        ciq = self._checkKey(key, origin, loaderInfo, "addCommandBefore")
        return self._addCommandBefore(self, ciq, parser, origin, loaderInfo)
        
    def addCommandAfter(self, key, commandStringList, origin=None):
        parser = self._checkCommandString(commandStringList, "addCommandAfter")
        origin, loaderInfo = self._checkOrigin(origin, "addCommandAfter", createIfDoesNotExist=False)
        ciq = self._checkKey(key, origin, loaderInfo, "addCommandAfter")
        return self._addCommandAfter(self, ciq, parser, origin, loaderInfo)
        
    def addCommandFirst(self, commandString, origin=None):
        parser = self._checkCommandString(commandStringList, "addCommandFirst")
        origin, loaderInfo = self._checkOrigin(origin, "addCommandFirst", createIfDoesNotExist=True)
        return self._addCommandBefore(self, loaderInfo.firstCommand, parser, origin, loaderInfo)
        
    def addCommandLast(self, commandString, origin=None):
        parser = self._checkCommandString(commandStringList, "addCommandLast")
        origin, loaderInfo = self._checkOrigin(origin, "addCommandLast", createIfDoesNotExist=True)
        return self._addCommandAfter(self, loaderInfo.lastCommand, parser, origin, loaderInfo)
    
    ####

    def _exchangeCommand(self, firstCommand, secondCommand, loaderInfo):
        firstNext = firstCommand.next
        firstPrev = firstCommand.prev
        
        firstCommand.next = secondCommand.next
        firstCommand.prev = secondCommand.prev
        
        if secondCommand is loaderInfo.firstCommand:
            loaderInfo.firstCommand = firstCommand
            
        if secondCommand is loaderInfo.lastCommand:
            loaderInfo.lastCommand = firstCommand
            
        secondCommand.next = firstNext
        secondCommand.prev = firstPrev
        
        if firstCommand is loaderInfo.firstCommand:
            loaderInfo.firstCommand = secondCommand
            
        if firstCommand is loaderInfo.lastCommand:
            loaderInfo.lastCommand = secondCommand
                
    def exchangeCommand(self,firstKey, secondKey, origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "exchangeCommand", createIfDoesNotExist=False)
        ciq1 = self._checkKey(firstKey, origin, loaderInfo, "exchangeCommand",FIRST_KEY_NAME)
        ciq2 = self._checkKey(secondKey, origin, loaderInfo, "exchangeCommand",SECOND_KEY_NAME)
        self._exchangeCommand(ciq1, ciq2, loaderInfo)
            
    def upCommand(self,key, origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "upCommand", createIfDoesNotExist=False)
        ciq = self._checkKey(firstKey, origin, loaderInfo, "upCommand")
        
        if ciq.prev is None:
            return
            
        self._exchangeCommand(ciq.prev, ciq, loaderInfo)
        
    def downCommand(self,key, origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "downCommand", createIfDoesNotExist=False)
        ciq = self._checkKey(firstKey, origin, loaderInfo, "downCommand")
        
        if ciq.next is None:
            return
            
        self._exchangeCommand(ciq.next, ciq, loaderInfo)
                
    def moveCommandAfter(self, key, destinationKey, origin=None):
        if key == destinationKey: #can not move a command on itself
            return
    
        origin, loaderInfo = self._checkOrigin(origin, "moveCommandBefore", createIfDoesNotExist=False)
        ciq_toMove = self._checkKey(key, origin, loaderInfo, "moveCommandAfter")
        ciq_destination = self._checkKey(destinationKey, origin, loaderInfo, "moveCommandAfter",DESTINATION_KEY_NAME)
                
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
            loaderInfo.lastCommand = ciq_toMove
        
    def moveCommandBefore(self, key, destinationKey, origin=None): 
        if key == destinationKey: #can not move a command on itself
            return
        
        origin, loaderInfo = self._checkOrigin(origin, "moveCommandBefore", createIfDoesNotExist=False)
        ciq_toMove = self._checkKey(key, origin, loaderInfo, "moveCommandBefore")
        ciq_destination = self._checkKey(destinationKey, origin, loaderInfo, "moveCommandBefore",DESTINATION_KEY_NAME)
                
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
            loaderInfo.firstCommand = ciq_toMove
        
    def enableLoop(self):
        self.loopEnabled = True
        
    def disableLoop(self):
        self.loopEnabled = False
        
    def isLoop(self):
        return self.loopEnabled
        
    def enableCommand(self, key,origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "enableCommand")
        ciq = self._checkKey(key, origin, loaderInfo, "enableCommand")
        ciq.enabled = True
        
    def disableCommand(self, key,origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "disableCommand")
        ciq = self._checkKey(key, origin, loaderInfo, "disableCommand")
        ciq.enabled = False
        
    def isCommandDisabled(self, key,origin=None):
        origin, loaderInfo = self._checkOrigin(origin, "isCommandDisabled")
        ciq = self._checkKey(key, origin, loaderInfo, "isCommandDisabled")
        return ciq.isEnabled()
        
    def clone(self, From=None): #TODO the method name should change, cloneForExecution
        #TODO clone what ?
            #executing queue
            #parent class
            #loaders queue (? not needed for an execution, and will be really hard to clone)
            #next key (?)
    
        pass #TODO
                
