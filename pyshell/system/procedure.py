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

#TODO in addon std
    #shift args
        #info in param.var
    #set args
        #info in param.var
    #goto (procedure line)
        #get procedure from parameterContainer
    #soft kill (thread id) (level or None)
        #get procedure from parameterContainer
    #hard kill
        #HOWTO ? is it reallistic to implement ?
            #just manage to kill the thread immediatelly
                #what about lock in this case ?
    #list process
        #get procedure list from parameterContainer
    #command to startreadline then execute
        #HOWTO ?

#TODO in executer
    #create an endless "shell" procedure
    #use object ProcedureFromList
        #need some new command before to do that
            #GOTO or LOOP
            #command to readline and execute

#TODO here
    #hard kill ? need brainstorming
    
    #special case, what append in procedure level 0
        #exception should never interrupt a procedure at level 0, because it could stop the application
            #default granularity = None, print a warning message if a procedure with lower granularity is executed at level 0
    
    #manage stack of process call
        #if an exception occur in a command of level X, the procedure of level X will raise an interrupting exception to the upper level
            #each procedure will raise an interrupting exception until the level 0 or until a procedure allowing the granularity
            #so if there is 5 level (and no granularity stop), 5 error message (and stacktrace if debug) will be printed
                #really ugly, only the first message and first stacktrace are relevant.
            
        #IDEA: raise exception from procedure to procedure with printing disabled
            #until we reach level 0 or a procedure that accept this level of granularity
            #then when we reach the last procedure, print a stacktrace of the procedure call
            #use the same exception
                #at procedure business code, catch exception, add information about current process, then re raise the exception
            #at the final level (0 or granularity stop), print procedure stack trace (even if debug disabled)

import threading, sys
from pyshell.utils.exception   import DefaultPyshellException, PyshellException, ERROR, USER_ERROR, ListOfException, ParameterException, ParameterLoadingException
from pyshell.utils.executing   import execute
from pyshell.command.command   import UniCommand
from pyshell.command.exception import engineInterruptionException
from pyshell.arg.decorator     import shellMethod
from pyshell.arg.argchecker    import ArgChecker,listArgChecker, defaultInstanceArgChecker
from pyshell.utils.parsing     import Parser
from pyshell.system.variable   import VarParameter
import thread
                
### UTILS COMMAND ###
    
def getAbsoluteIndex(index, listSize):
    if index > 0:
        return index
    
    index = listSize + index
    
    #python work like that (?)
    if index < 0:
        return 0
    
    return index

class Procedure(UniCommand):
    def __init__(self, name, showInHelp = True, readonly = False, removable = True, transient = False):
        UniCommand.__init__(self, name, self._pre, None, self._post, showInHelp)
        
        self.errorGranularity = sys.maxint
        self.executeOnPre     = True
        
        #global lock system
        self.setReadOnly(readonly)
        self.setRemovable(removable)
        self.setTransient(transient)

        self.interrupt       = False
        self.interruptReason = None
        
    ### PRE/POST process ###
    
    def _setArgs(self,parameters, args):
        parameters.variable.setParameter("*", VarParameter(' '.join(str(x) for x in args)), localParam = True)    #all in one string
        parameters.variable.setParameter("#", VarParameter(len(args)), localParam = True)                         #arg count
        parameters.variable.setParameter("@", VarParameter(args), localParam = True)                              #all args
        parameters.variable.setParameter("?", VarParameter( ()), localParam = True)                               #value from last command
        parameters.variable.setParameter("!", VarParameter( ()), localParam = True)                               #last pid started in background        
        parameters.variable.setParameter("$", VarParameter(parameters.getCurrentId()), localParam = True) #current process id 

    @shellMethod(args       = listArgChecker(ArgChecker()),
                 parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
    def _pre(self, args, parameters):
        "this command is a procedure"
        
        if not self.executeOnPre:
            return args
        
        parameters.pushVariableLevelForThisThread(self)
        self._setArgs(parameters, args)
        try:
            return self.execute(parameters)
        finally:
            parameters.popVariableLevelForThisThread()

    @shellMethod(args       = listArgChecker(ArgChecker()),
                 parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
    def _post(self, args, parameters):
        
        if self.executeOnPre:
            return args
        
        parameters.pushVariableLevelForThisThread(self)
        self._setArgs(parameters, args)
        try:
            return self.execute(parameters)
        finally:
            parameters.popVariableLevelForThisThread()
    
    def interrupt(self, reason=None):
        self.interrupt       = True
        self.interruptReason = reason

    def execute(self, parameters):
        pass #XXX TO OVERRIDE and use _innerExecute
        
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
            if not isinstance(lastException, PyshellException):
                raise engineInterruptionException("internal command has been interrupted because of an enexpected exception", abnormal=True)
            
            if self.errorGranularity is not None and lastException.severity <= self.errorGranularity:
                raise engineInterruptionException("internal command has been interrupted because an internal exception has a granularity bigger than allowed", abnormal=False)               
        else:
            if engine is not None and engine.getLastResult() is not None and len(engine.getLastResult()) > 0:
                param.setValue( engine.getLastResult() )
            else:
                param.setValue( () )

        return lastException, engine
        
    ###### get/set method
    
    def setNextCommandIndex(self, index):
        raise DefaultPyshellException("(Procedure) setNextCommandIndex, not possible to set next command index on this king of procedure")

    def setReadOnly(self, value):
        if type(value) != bool:
            raise ParameterException("(Procedure) setReadOnly, expected a bool type as state, got '"+str(type(value))+"'")
            
        self.readonly = value
        
    def setRemovable(self, value):
        if type(value) != bool:
            raise ParameterException("(Procedure) setRemovable, expected a bool type as state, got '"+str(type(value))+"'")
            
        self.removable = value
        
    def setTransient(self, value):
        if type(value) != bool:
            raise ParameterException("(Procedure) setTransient, expected a bool type as state, got '"+str(type(value))+"'")
            
        self.transient = value  
    
    #TODO not obvious, maximum level allowed ? or minimum level allowed ? bound included or not ?
        #update method name
    def setErrorGranularity(self, value):
        if value is not None and (type(value) != int or value < 0):
            raise ParameterException("(Procedure) setErrorGranularity, expected a integer value bigger than 0, got '"+str(type(value))+"'")
    
        self.errorGranularity = value
        
    def setExecuteOnPre (self, value):
        if type(value) != bool:
            raise ParameterException("(Procedure) setExecuteOnPre, expected a boolean value as parameter, got '"+str(type(value))+"'")
    
        self.executeOnPre = value
    
    def getErrorGranularity(self):
        return self.errorGranularity
        
    def isExecuteOnPre(self):
        return self.executeOnPre
        
    def isReadOnly(self):
        return self.readonly
        
    def isRemovable(self):
        return self.removable
        
    def isTransient(self):
        return self.transient
        
    def clone(self, From=None):
        if From is None:
            From = Procedure(self.name)
        
        From.errorGranularity = self.errorGranularity
        From.executeOnPre     = self.executeOnPre
        From.readonly         = self.readonly
        From.removable        = self.removable
        From.transient        = self.transient
        
        return UniCommand.clone(self,From)
            
class ProcedureFromList(Procedure):
    def __init__(self, name, showInHelp = True, readonly = False, removable = True, transient = False):
        Procedure.__init__(self, name, showInHelp, readonly, removable, transient)
        
        #specific command system
        self.stringCmdList    = [] 
        self.lockedTo         = -1
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
        if self.isReadOnly():
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
        
class ProcedureFromFile(Procedure):
    def __init__(self, filePath, showInHelp = True, readonly = False, removable = True, transient = False):
        Procedure.__init__(self, "execute "+str(filePath), showInHelp, readonly, removable, transient )
        self.filePath = filePath
    
    def execute(self, parameters):
        #make a copy of the current procedure
        engine = None
        
        #for cmd in self.stringCmdList:
        index = 0
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
    
