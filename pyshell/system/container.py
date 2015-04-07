#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.utils.constants import DEFAULT_PROFILE_NAME, SYSTEM_VIRTUAL_LOADER
from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.flushable import Flushable

from threading import current_thread

class _ThreadInfo(object):
    def __init__(self):
        self.procedureStack = []
        self.origin         = SYSTEM_VIRTUAL_LOADER
        self.originProfile  = DEFAULT_PROFILE_NAME

    def canBeDeleted(self):
        return len(self.procedureStack) == 0 and self.origin == SYSTEM_VIRTUAL_LOADER and self.originProfile == DEFAULT_PROFILE_NAME

class AbstractParameterContainer(object):
    def getCurrentId(self):
        pass #TO OVERRIDE

    def getOrigin(self):
        pass #TO OVERRIDE

    def setOrigin(self, origin, originProfile=None):
        pass #TO OVERRIDE

class DummyParameterContainer(AbstractParameterContainer):
    def __init__(self):
        self.origin = SYSTEM_VIRTUAL_LOADER
        self.originProfile = DEFAULT_PROFILE_NAME

    def getCurrentId(self):
        return current_thread().ident, None

    def getOrigin(self):
        return self.origin, self.originProfile

    def setOrigin(self, origin, originProfile=None):
        self.origin = origin
        
        if originProfile is None:
            self.originProfile = DEFAULT_PROFILE_NAME
        else:
            self.originProfile = originProfile
        
DEFAULT_DUMMY_PARAMETER_CONTAINER = DummyParameterContainer()

class ParameterContainer(AbstractParameterContainer):
    def __init__(self):
        self.threadInfo = {} #hold the level of the current thread
        self.mainThread  = current_thread().ident
        self.parameterManagerList = []

    def registerParameterManager(self, name, obj):
        if not isinstance(obj,Flushable):
            raise DefaultPyshellException("(ParameterContainer) registerParameterManager, an instance of Flushable object was expected, got '"+str(type(obj))+"'")
    
        if hasattr(self, name):
            raise DefaultPyshellException("(ParameterContainer) registerParameterManager, an attribute is already registered with this name: '"+str(name)+"'")
    
        setattr(self, name, obj)
        self.parameterManagerList.append(name)

    def getThreadInfo(self):
        tid = current_thread().ident

        if tid in self.threadInfo:
            return self.threadInfo[tid]
        
        ti = _ThreadInfo()
        self.threadInfo[tid] = ti
        return ti

    def pushVariableLevelForThisThread(self, procedure = None):
        info = self.getThreadInfo() #get or create
        info.procedureStack.append(procedure)

    def popVariableLevelForThisThread(self):        
        if current_thread().ident not in self.threadInfo:
            return 

        info = self.getThreadInfo() #only get, never create thread info
                
        if len(info.procedureStack) > 0: #this info only hold the origin
            #flush parameter manager
            for name in self.parameterManagerList:
                pm = getattr(self, name)
                pm.flush()
            
            #update level map
            info.procedureStack = info.procedureStack[:-1]

        if info.canBeDeleted():
            del self.threadInfo[current_thread().ident]
        
    def getCurrentId(self):        
        if current_thread().ident not in self.threadInfo:
            return current_thread().ident, -1

        info = self.getThreadInfo() #only get, never create thread info
        return current_thread().ident,len(info.procedureStack)-1,
        
    def isMainThread(self):
        return self.mainThread == current_thread().ident

    def getCurrentProcedure(self):
        if current_thread().ident not in self.threadInfo:
            return None

        info = self.getThreadInfo() #only get, never create thread info

        if len(info.procedureStack) == 0:
            return None

        return info.procedureStack[-1]

    def getOrigin(self):
        if current_thread().ident not in self.threadInfo:
            return SYSTEM_VIRTUAL_LOADER, DEFAULT_PROFILE_NAME

        info = self.getThreadInfo() #only get, never create thread info
        return info.origin, info.originProfile

    def setOrigin(self, origin, originProfile=None):

        if originProfile is None:
            originProfile = DEFAULT_PROFILE_NAME

        if origin == SYSTEM_VIRTUAL_LOADER and originProfile == DEFAULT_PROFILE_NAME:
            if current_thread().ident in self.threadInfo: #no need to store origin if not registered and new origin is SYSTEM_VIRTUAL_LOADER, because for unregistered, the default origin is ORIGIN_PROCESS
                info = self.getThreadInfo()
                info.origin = SYSTEM_VIRTUAL_LOADER
                info.originProfile = DEFAULT_PROFILE_NAME

                if info.canBeDeleted():
                    del self.threadInfo[current_thread().ident]
        else:
            info = self.getThreadInfo()
            info.origin = origin
            info.originProfile = originProfile
            
