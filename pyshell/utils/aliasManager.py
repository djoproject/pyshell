#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject,net>

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
    #use copy.copy in Command object in place of clone.

import threading, sys, copy
from pyshell.utils.exception   import DefaultPyshellException, PyshellException, ERROR, USER_ERROR, ListOfException, ParameterException, ParameterLoadingException
from pyshell.utils.utils       import raiseIfInvalidKeyList
from pyshell.utils.executing   import executeCommand
from pyshell.command.command   import UniCommand
from pyshell.command.exception import engineInterruptionException
from pyshell.arg.decorator     import shellMethod
from pyshell.arg.argchecker    import ArgChecker,listArgChecker, defaultInstanceArgChecker

try:
    pyrev = sys.version_info.major
except AttributeError:
    pyrev = sys.version_info[0]

if pyrev == 2:
    import ConfigParser 
else:
    import configparser as ConfigParser
                
### UTILS COMMAND ###
    
def getAbsoluteIndex(index, listSize):
    if index > 0:
        return index
    
    index = listSize + index
    
    #python work like that
    if index < 0:
        return 0
    
    return index

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
    @shellMethod(args       = listArgChecker(ArgChecker()),
                 parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
    def _pre(self, args, parameters):
        "this command is an alias"
        
        if not self.executeOnPre:
            return args

        return self.execute(args, parameters)

    @shellMethod(args       = listArgChecker(ArgChecker()),
                 parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
    def _post(self, args, parameters):
        if self.executeOnPre:
            return args

        return self.execute(args, parameters)
        
    def execute(self, args, parameters):
        pass #XXX TO OVERRIDE
        
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
    
    #TODO try to find a generic way to do that...
    def _innerExecute(self, cmd, args, parameters):
        lastException, engine = executeCommand(cmd, parameters, False, self.name, args)  
        
        if lastException != None: 
            if not isinstance(lastException, PyshellException):
                raise engineInterruptionException("internal command has been interrupted because of an enexpected exception")
            
            if self.errorGranularity is not None and lastException.severity <= self.errorGranularity:
                raise engineInterruptionException("internal command has been interrupted because an internal exception has a granularity bigger than allowed")               
        
        return lastException, engine
            
    def execute(self, args, parameters):
        #make a copy of the current alias       
        e = copy.deepcopy(self) #could be updated during its execution in another thread #TODO is it enough to use copy ?
            #TODO FIXME deepcopy is too much
            
        engine = None
        
        #for cmd in e.stringCmdList:
        for i in xrange(0,len(e.stringCmdList)):
            lastException, engine = e._innerExecute(e.stringCmdList[i], args, parameters)

        #return the result of last command in the alias
        if engine == None:
            return ()
            
        return engine.getLastResult()
                
    #### business method
    
    def setCommand(self, index, commandStringList):
        self._checkAccess("setCommand", (index,), False)
        raiseIfInvalidKeyList(commandStringList, ParameterException,"Alias", "setCommand")
        index = getAbsoluteIndex(index, len(self.stringCmdList))
        
        if index >= len(self.stringCmdList):
            self.stringCmdList.append( [commandStringList] )
            return len(self.stringCmdList) - 1
        else:
            self.stringCmdList[index] = [commandStringList] 
        
        return index

    def addCommand(self, commandStringList):
        self._checkAccess("addCommand")
        raiseIfInvalidKeyList(commandStringList, ParameterException,"Alias", "addCommand") 
        self.stringCmdList.append( [commandStringList] )
        return len(self.stringCmdList) - 1
        
    def addPipeCommand(self, index, commandStringList):
        self._checkAccess("addPipeCommand", (index,))
        raiseIfInvalidKeyList(commandStringList, ParameterException,"Alias", "addPipeCommand")
        self.stringCmdList[index].append(commandStringList)
        return getAbsoluteIndex(index, len(self.stringCmdList))
        
    def removePipeCommand(self, index):
        self._checkAccess("removePipeCommand", (index,))
        del self.stringCmdList[index][-1]
        if len(self.stringCmdList[index]) == 0:
            del self.stringCmdList[index]
        
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
        
class AliasFile(Alias):
    def __init__(self, filePath, showInHelp = True, readonly = False, removable = True, transient = False):
        Alias.__init__("execute "+str(filePath), showInHelp, readonly, removable, transient )
        self.filePath = filePath
    
    #TODO adapt, read command from file, not from list
    def _execute(self, args, parameters):
        #make a copy of the current alias
        e = self.clone()
        engine = None
        
        #for cmd in e.stringCmdList:
        for i in xrange(0,len(e.stringCmdList)):
            lastException, engine = self._innerExecute(e.stringCmdList[i]) #TODO more args

        #return the result of last command in the alias
        if engine == None:
            return ()
            
        return engine.getLastResult()
    
    def clone(self, From=None):
        if From is None:
            From = AliasFile(self.filePath)
            
        return Alias.clone(self,From)
    
