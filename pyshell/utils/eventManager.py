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

EVENT_ON_STARTUP      = "onstartup" #at application launch
EVENT_AT_EXIT         = "atexit" #at application exit
EVENT_AT_ADDON_LOAD   = "onaddonload" #at addon load (args=addon name)
EVENT_AT_ADDON_UNLOAD = "onaddonunload" #at addon unload (args=addon name)

import threading, sys
from pyshell.utils.exception   import DefaultPyshellException, USER_ERROR, ListOfException, ParameterException, ParameterLoadingException
from pyshell.utils.utils       import raiseIfInvalidKeyList
from pyshell.command.command   import UniCommand
from pyshell.arg.decorator     import shellMethod
from pyshell.arg.argchecker    import ArgChecker,listArgChecker

try:
    pyrev = sys.version_info.major
except AttributeError:
    pyrev = sys.version_info[0]

if pyrev == 2:
    import ConfigParser 
else:
    import configparser as ConfigParser

#TODO TODO TODO TODO TODO
    #check whole security, is everything used ?
        #readonlye, transient, removable, ...
        #lockable index, not removable command, etc.

    #firing/executing system
        #for piped command
            #with a "&" at the end of a script line
            #with a "fire" at the beginning of a script line

        #with only an alias name
            #with one of the two solution above
            #with a specific command from alias addon 

    #keep track of running event and be able to kill one or all of them
            
    #find a new name, not really an alias, and not really an event
        #an event is just an alias running in backgroun, so we can keep alias
    
    #rename all variable like stringCmdList, it is difficult to understand what is what

### UTILS COMMAND ###

def isInt(value):
    try:
        i = int(value) 
        return True, i 
    except ValueError:
        pass
    
    return False, None
    
def isBool(value):
    if type(value) != str and type(value) != unicode:
        return False, None
        
    if value.lower() == "true":
        return True,True
        
    if value.lower() == "false":
        return True,False
        
    return False,None

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
        self.lockedTo = -1 #TODO can't update command bellow and at this index
            #TODO make setter/getter
                #set must check the size of the list, can not set a number bigger than the list
    
    ### PRE/POST process ###
    @shellMethod(args=listArgChecker(ArgChecker()))
    def _pre(self, args):
        if not self.executeOnPre:
            return args

        return self._execute(args)

    @shellMethod(args=listArgChecker(ArgChecker()))
    def _post(self, args):
        if self.executeOnPre:
            return args

        return self._execute(args)

    def _execute(self, args):
        #TODO make a copy of the current event
            #could be updated during its execution in another thread

        #TODO manage stopOnError, useArgFromEvent

        #TODO execute commands
            #create new engine for each command
        
        #TODO return the result of last command in the alias
            #need to update engine to be able to do that
        
        pass #TODO

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
        
    #### business method
    
    def setCommand(self, index, commandStringList):
        #TODO event is readonly ?
    
        #TODO is bellow locked index ?
        
        #TODO add commad at index
        
        #TODO return real index
            #if list containt 5 and we try to insert at 7, real index will be 5 
        
        pass #TODO

    def addCommand(self, commandStringList):
        raiseIfInvalidKeyList(commandStringList, ParameterException,"Event", "addCommand") 

        #TODO event is readonly ?

        self.stringCmdList.append( commandStringList )
        
        #TODO return real index
        
    def addPipeCommand(self, index, commandStringList):
        #TODO event is readonly ?
        
        #TODO is bellow locked index ?
        
        #TODO is valid commandString ?
        
        pass #TODO
        
    def removePipeCommand(self, index):
        #TODO event is readonly ?
        
        #TODO is bellow locked index ?
        
        #TODO remove the last part of a command is equal to remove it
            #so the command is removable ?
    
        pass #TODO
        
    def removeCommand(self, index):
        #TODO event is readonly ?
    
        #TODO is bellow locked index ?
    
        try:
            del self.stringCmdList[index]
        except IndexError:
            pass #do nothing
        
    def moveCommand(self,fromIndex, toIndex):
        #TODO event is readonly ?
    
        #TODO is bellow locked index ?
    
        try:
            self.stringCmdList[fromIndex]
        except IndexError:
            if len(self.stringCmdList) == 0:
                message = "command list is empty"
            elif len(self.stringCmdList) == 1:
                message = "only index 0 is available"
            else:
                message = "a value between 0 and "+str(len(self.stringCmdList)-1) + " was expected"
        
            raise ParameterException("(Event) moveCommand, invalid index 'from',"+message+" , got '"+str(fromIndex)+"'")
        
        #transforme to positive index if needed
        if fromIndex < 0:
            fromIndex = len(self.stringCmdList) + fromIndex
        
        try:
            self.stringCmdList[toIndex]
        except IndexError:
            if len(self.stringCmdList) == 0:
                message = "command list is empty"
            elif len(self.stringCmdList) == 1:
                message = "only index 0 is available"
            else:
                message = "a value between 0 and "+str(len(self.stringCmdList)-1) + " was expected"
        
            raise ParameterException("(Event) moveCommand, invalid index 'to',"+message+" , got '"+str(fromIndex)+"'")
            
        #transforme to positive index if needed
        if toIndex < 0:
            toIndex = len(self.stringCmdList) + toIndex
            
        if fromIndex == toIndex:
            return
        
        #manage the case when we try to insert after the existing index
        if fromIndex < toIndex:
            toIndex -= 1
            
        self.stringCmdList.insert(toIndex, self.stringCmdList.pop(fromIndex))
        
    def upCommand(self,index):
        self.moveCommand(index,index-1)
        
    def downCommand(self,index):
        self.moveCommand(index,index+1)
        
    def clone(self):
        e = Event()
    
        e.stringCmdList                   = self.stringCmdList[:]
        e.stopOnError                     = self.stopOnError
        e.argFromEventOnlyForFirstCommand = self.argFromEventOnlyForFirstCommand
        e.useArgFromEvent                 = self.useArgFromEvent
        e.executeOnPre                    = self.executeOnPre
        
        return e
