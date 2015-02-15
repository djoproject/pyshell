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

import threading, sys
from pyshell.utils.exception   import DefaultPyshellException, PyshellException, ERROR, USER_ERROR, ListOfException, ParameterException, ParameterLoadingException
from pyshell.utils.executing   import execute
from pyshell.command.command   import UniCommand
from pyshell.command.exception import engineInterruptionException
from pyshell.arg.decorator     import shellMethod
from pyshell.arg.argchecker    import ArgChecker,listArgChecker, defaultInstanceArgChecker
from pyshell.utils.parsing     import Parser
from pyshell.system.parameter  import VarParameter
import thread
                
### UTILS COMMAND ###
    
def getAbsoluteIndex(index, listSize):
    if index > 0:
        return index
    
    index = listSize + index
    
    #python work like that
    if index < 0:
        return 0
    
    return index

#TODO
    #should be able again to give args to the method execute

#TODO brainstorming
    #create a special endless alias for shell entry point ?
        #+++
        
        #---

class Alias(UniCommand):
    def __init__(self, name, showInHelp = True, readonly = False, removable = True, transient = False):
        UniCommand.__init__(self, name, self._pre, None, self._post, showInHelp)
        
        self.errorGranularity = sys.maxint
        self.executeOnPre     = True
        
        #global lock system
        self.setReadOnly(readonly)
        self.setRemovable(removable)
        self.setTransient(transient)
        
    ### PRE/POST process ###
    
    def _setArgs(self,parameterContainer, args):
        parameterContainer.variable.setParameter("*", VarParameter(' '.join(str(x) for x in args)), localParam = True) #all in one string
        parameterContainer.variable.setParameter("#", VarParameter(len(args)), localParam = True)                      #arg count
        parameterContainer.variable.setParameter("@", VarParameter(args), localParam = True)                           #all args
        #TODO parameterContainer.variable.setParameter("?", VarParameter(args, localParam = True)                            #value from last command
            #TODO set default as empty
        #TODO parameterContainer.variable.setParameter("!", VarParameter(args, localParam = True)                            #last pid started in background
            #should be global ? because thread list is global in the system...
        
        parameterContainer.variable.setParameter("$", VarParameter(thread.get_ident()), localParam = True)             #current process id #TODO id is not enought, need level
    
    @shellMethod(args       = listArgChecker(ArgChecker()),
                 parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
    def _pre(self, args, parameters):
        "this command is an alias"
        
        if not self.executeOnPre:
            return args
        
        parameters.pushVariableLevelForThisThread()
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
        
        parameters.pushVariableLevelForThisThread()
        self._setArgs(parameters, args)
        try:
            return self.execute(parameters)
        finally:
            parameters.popVariableLevelForThisThread()
        
    def execute(self, parameters):
        pass #XXX TO OVERRIDE and use _innerExecute
        
    def _innerExecute(self, cmd, name, parameters):
        #TODO set "$?"
            #if error from last execution, set empty
            #otherwise, set the result if any
    
        lastException, engine = execute(cmd, parameters, name)  

        if lastException != None: 
            if not isinstance(lastException, PyshellException):
                raise engineInterruptionException("internal command has been interrupted because of an enexpected exception", abnormal=True)
            
            if self.errorGranularity is not None and lastException.severity <= self.errorGranularity:
                raise engineInterruptionException("internal command has been interrupted because an internal exception has a granularity bigger than allowed", abnormal=False)               
        
        return lastException, engine
        
    ###### get/set method
    
    def setReadOnly(self, value):
        if type(value) != bool:
            raise ParameterException("(Alias) setReadOnly, expected a bool type as state, got '"+str(type(value))+"'")
            
        self.readonly = value
        
    def setRemovable(self, value):
        if type(value) != bool:
            raise ParameterException("(Alias) setRemovable, expected a bool type as state, got '"+str(type(value))+"'")
            
        self.removable = value
        
    def setTransient(self, value):
        if type(value) != bool:
            raise ParameterException("(Alias) setTransient, expected a bool type as state, got '"+str(type(value))+"'")
            
        self.transient = value  
    
    def setErrorGranularity(self, value):
        if value is not None and (type(value) != int or value < 0):
            raise ParameterException("(Alias) setErrorGranularity, expected a integer value bigger than 0, got '"+str(type(value))+"'")
    
        self.errorGranularity = value
        
    def setExecuteOnPre (self, value):
        if type(value) != bool:
            raise ParameterException("(Alias) setExecuteOnPre, expected a boolean value as parameter, got '"+str(type(value))+"'")
    
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
            From = Alias(self.name)
        
        From.errorGranularity = self.errorGranularity
        From.executeOnPre     = self.executeOnPre
        From.readonly         = self.readonly
        From.removable        = self.removable
        From.transient        = self.transient
        
        return UniCommand.clone(self,From)
            
class AliasFromList(Alias):
    def __init__(self, name, showInHelp = True, readonly = False, removable = True, transient = False):
        Alias.__init__(self, name, showInHelp, readonly, removable, transient)
        
        #specific command system
        self.stringCmdList    = [] 
        self.lockedTo = -1
    
    def setLockedTo(self, value):
        try:
            value = int(value)
        except ValueError as va:
            raise ParameterException("(Alias) setLockedTo, expected an integer value as parameter: "+str(va))
    
        if value < -1 or value >= len(self.stringCmdList):
            if len(self.stringCmdList) == 0:
                raise ParameterException("(Alias) setLockedTo, only -1 is allowed because alias list is empty, got '"+str(value)+"'")
            else:
                raise ParameterException("(Alias) setLockedTo, only a value from -1 to '"+str(len(self.stringCmdList) - 1)+"' is allowed, got '"+str(value)+"'")
            
        self.lockedTo = value
        
    def getLockedTo(self):
        return self.lockedTo
        
    def getStringCmdList(self):
        return self.stringCmdList
                
    def execute(self, parameters):
        #e = self.clone() #make a copy of the current alias      
        engine = None
        
        #for cmd in self.stringCmdList:
        for i in xrange(0,len(self.stringCmdList)):
            lastException, engine = self._innerExecute(self.stringCmdList[i], self.name + " (index: "+str(i)+")", parameters)

        #return the result of last command in the alias
        if engine == None:
            return ()
            
        return engine.getLastResult()
                
    #### business method
    
    def setCommand(self, index, commandStringList):
        self._checkAccess("setCommand", (index,), False)

        parser = Parser(commandString)
        parser.parse()

        if len(parser) == 0:
            raise ParameterException("(Alias) addCommand, try to add a command string that does not hold any command")

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
            raise ParameterException("(Alias) addCommand, try to add a command string that does not hold any command")

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
            raise ParameterException("(Alias) "+methName+", this alias is readonly, can not do any update on its content")
            
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
                
                    raise ParameterException("(Alias) "+methName+", index out of bound. "+message+", got '"+str(index)+"'")
            except TypeError as te:
                raise ParameterException("(Alias) "+methName+", invalid index: "+str(te))
        
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
            
                raise ParameterException("(Alias) "+methName+", invalid index. "+message+", got '"+str(index)+"'")
        
    def upCommand(self,index):
        self.moveCommand(index,index-1)
        
    def downCommand(self,index):
        self.moveCommand(index,index+1)
    
    def clone(self, From=None):
        if From is None:
            From = AliasFromList(self.name)
        
        From.stringCmdList = self.stringCmdList[:]
        From.lockedTo      = self.lockedTo
        
        return Alias.clone(self,From)       
        
class AliasFromFile(Alias):
    def __init__(self, filePath, showInHelp = True, readonly = False, removable = True, transient = False):
        Alias.__init__(self, "execute "+str(filePath), showInHelp, readonly, removable, transient )
        self.filePath = filePath
    
    def execute(self, parameters):
        #make a copy of the current alias
        engine = None
        
        #for cmd in self.stringCmdList:
        index = 0
        with open(self.filePath) as f:
            for line in f:
                lastException, engine = self._innerExecute(line, self.name + " (line: "+str(index)+")", parameters) 
                index += 1

        #return the result of last command in the alias
        if engine == None:
            return ()
            
        return engine.getLastResult()
    
    def clone(self, From=None):
        if From is None:
            From = AliasFile(self.filePath)
            
        return Alias.clone(self,From)
    
