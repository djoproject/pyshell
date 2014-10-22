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

#TODO use that (or remove them)
EVENT_ON_STARTUP      = "onstartup" #at application launch
EVENT_AT_EXIT         = "atexit" #at application exit
EVENT_AT_ADDON_LOAD   = "onaddonload" #at addon load (args=addon name)
EVENT_AT_ADDON_UNLOAD = "onaddonunload" #at addon unload (args=addon name)

import threading, sys
from pyshell.utils.exception   import DefaultPyshellException, USER_ERROR, ListOfException, ParameterException, ParameterLoadingException
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

#TODO
    #BUG piping does not work

    # "removable" boolean is not checked if event is removed from tries...
            
    #find a new name, not really an alias, and not really an event
        #an event is just an alias running in backgroun, so we can keep alias
    
    #rename all variable like stringCmdList, it is difficult to understand what is what

#TODO somewhere else
    #firing/executing system (not in this module anymore)
        #for piped command
            #with a "&" at the end of a script line
            #with a "fire" at the beginning of a script line

        #with only an alias name
            #with one of the two solution above
            #with a specific command from alias addon 

    #keep track of running event and be able to kill one or all of them (not in this module anymore)    

### UTILS COMMAND ###
    
def getAbsoluteIndex(index, listSize):
    if index > 0:
        return index
    
    index = listSize + index
    
    #python work like that
    if index < 0:
        return 0
    
    return index

class Event(UniCommand):
    def __init__(self, name, showInHelp = True, readonly = False, removable = True, transient = False):
        UniCommand.__init__(self, name, self._pre, None, self._post, showInHelp)

        self.stringCmdList = [] 
        self.stopOnError                     = True
        self.argFromEventOnlyForFirstCommand = False
        self.useArgFromEvent                 = True
        self.executeOnPre                    = True
        
        #global lock system
        self.setReadOnly(readonly)
        self.setRemovable(removable)
        self.setTransient(transient)
        
        #specific command system
        self.lockedTo = -1
    
    ### PRE/POST process ###
    @shellMethod(args       = listArgChecker(ArgChecker()),
                 parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
    def _pre(self, args, parameters):
        if not self.executeOnPre:
            return args

        return self._execute(args, parameters)

    @shellMethod(args       = listArgChecker(ArgChecker()),
                 parameters = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
    def _post(self, args, parameters):
        if self.executeOnPre:
            return args

        return self._execute(args, parameters)

    def _execute(self, args, parameters):
        #make a copy of the current event
        e = self.clone() #could be updated during its execution in another thread
        engine = None
        
        for cmd in e.stringCmdList:
            if e.useArgFromEvent:
                if e.argFromEventOnlyForFirstCommand:
                    e.useArgFromEvent = False
                
                cmd[0].extend(args)
            
            state, engine = executeCommand(cmd, parameters, False)  
            if not state and e.stopOnError:
                raise engineInterruptionException("internal command has been interrupted")
            
        #return the result of last command in the alias
        if engine == None:
            return ()
            
        lastResult = engine.getLastResult()
        
        if lastResult == None: #FIXME pas sur, on devrait pouvoir renvoyer None
            return ()
            
        return lastResult
        
    ###### get/set method
        
    def setReadOnly(self, value):
        if type(value) != bool:
            raise ParameterException("(Event) setReadOnly, expected a bool type as state, got '"+str(type(value))+"'")
            
        self.readonly = value
        
    def setRemovable(self, value):
        if type(value) != bool:
            raise ParameterException("(Event) setRemovable, expected a bool type as state, got '"+str(type(value))+"'")
            
        self.removable = value
        
    def setTransient(self, value):
        if type(value) != bool:
            raise ParameterException("(Event) setTransient, expected a bool type as state, got '"+str(type(value))+"'")
            
        self.transient = value  
    
    def setStopOnError(self, value):
        if type(value) != bool:
            raise ParameterException("(Event) setStopOnError, expected a boolean value as parameter, got '"+str(type(value))+"'")
    
        self.stopOnError = value
        
    def setArgFromEventOnlyForFirstCommand(self, value):
        if type(value) != bool:
            raise ParameterException("(Event) setStopOnError, expected a boolean value as parameter, got '"+str(type(value))+"'")
    
        self.argFromEventOnlyForFirstCommand = value
        
    def setUseArgFromEvent(self, value):
        if type(value) != bool:
            raise ParameterException("(Event) setStopOnError, expected a boolean value as parameter, got '"+str(type(value))+"'")
    
        self.useArgFromEvent = value
        
    def setExecuteOnPre (self, value):
        if type(value) != bool:
            raise ParameterException("(Event) setExecuteOnPre, expected a boolean value as parameter, got '"+str(type(value))+"'")
    
        self.executeOnPre = value
        
    def setLockedTo(self, value):
        try:
            value = int(value)
        except ValueError as va:
            raise ParameterException("(Event) setLockedTo, expected an integer value as parameter: "+str(va))
    
        if value < -1 or value >= len(self.stringCmdList):
            if len(self.stringCmdList) == 0:
                raise ParameterException("(Event) setLockedTo, only -1 is allowed because event list is empty, got '"+str(value)+"'")
            else:
                raise ParameterException("(Event) setLockedTo, only a value from -1 to '"+str(len(self.stringCmdList) - 1)+"' is allowed, got '"+str(value)+"'")
            
        self.lockedTo = value
        
    def isStopOnError(self):
        return self.stopOnError
        
    def isArgFromEventOnlyForFirstCommand(self):
        return self.argFromEventOnlyForFirstCommand
        
    def isUseArgFromEvent(self):
        return self.useArgFromEvent
        
    def isExecuteOnPre(self):
        return self.executeOnPre
        
    def isReadOnly(self):
        return self.readonly
        
    def isRemovable(self):
        return self.removable
        
    def isTransient(self):
        return self.transient
        
    def getLockedTo(self):
        return self.lockedTo
        
    #### business method
    
    def setCommand(self, index, commandStringList):
        self._checkAccess("setCommand", (index,), False)
        raiseIfInvalidKeyList(commandStringList, ParameterException,"Event", "setCommand")
        index = getAbsoluteIndex(index, len(self.stringCmdList))
        
        if index >= len(self.stringCmdList):
            self.stringCmdList.append( [commandStringList] )
            return len(self.stringCmdList) - 1
        else:
            self.stringCmdList[index] = [commandStringList] 
        
        return index

    def addCommand(self, commandStringList):
        self._checkAccess("addCommand")
        raiseIfInvalidKeyList(commandStringList, ParameterException,"Event", "addCommand") 
        self.stringCmdList.append( commandStringList )
        return len(self.stringCmdList) - 1
        
    def addPipeCommand(self, index, commandStringList):
        self._checkAccess("addPipeCommand", (index,))
        raiseIfInvalidKeyList(commandStringList, ParameterException,"Event", "addPipeCommand")
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
            raise ParameterException("(Event) "+methName+", this event is readonly, can not do any update on its content")
            
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
                
                    raise ParameterException("(Event) "+methName+", index out of bound. "+message+", got '"+str(index)+"'")
            except TypeError as te:
                raise ParameterException("(Event) "+methName+", invalid index: "+str(te))
        
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
            
                raise ParameterException("(Event) "+methName+", invalid index. "+message+", got '"+str(index)+"'")
        
    def upCommand(self,index):
        self.moveCommand(index,index-1)
        
    def downCommand(self,index):
        self.moveCommand(index,index+1)
        
    def clone(self):
        e = Event(self.name)
    
        e.stringCmdList                   = self.stringCmdList[:]
        e.stopOnError                     = self.stopOnError
        e.argFromEventOnlyForFirstCommand = self.argFromEventOnlyForFirstCommand
        e.useArgFromEvent                 = self.useArgFromEvent
        e.executeOnPre                    = self.executeOnPre
        e.readonly                        = self.readonly
        e.removable                       = self.removable
        e.transient                       = self.transient
        e.lockedTo                        = self.lockedTo
        
        return e
