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

#from pyshell.system.context     import ContextParameterManager
#from pyshell.system.environment import EnvironmentParameterManager
#from pyshell.system.key         import CryptographicKeyParameterManager
#from pyshell.system.variable    import VariableParameterManager
from pyshell.utils.constants    import ORIGIN_PROCESS, AVAILABLE_ORIGIN
from pyshell.utils.exception    import DefaultPyshellException

from threading import current_thread

class _ThreadInfo(object):
    def __init__(self):
        self.level          = -1
        self.procedureStack = []
        self.origin         = ORIGIN_PROCESS
        self.originArg      = None

    def canBeDeleted(self):
        return self.level == 1 and self.origin == ORIGIN_PROCESS

class AbstractParameterContainer(object):
    def getCurrentId(self):
        pass #TO OVERRIDE

    def getOrigin(self):
        pass #TO OVERRIDE

    def setOrigin(self, origin):
        pass #TO OVERRIDE

class ParameterContainer(AbstractParameterContainer):
    #SUBCONTAINER_LIST = ["environment", "context", "variable", "key"] #TODO update addon/parameters

    def __init__(self):
        self.threadInfo = {} #hold the level of the current thread
        #self.environment = EnvironmentParameterManager(self)
        #self.context     = ContextParameterManager(self)
        #self.variable    = VariableParameterManager(self)
        #self.key         = CryptographicKeyParameterManager(self)
        self.mainThread  = current_thread().ident
        self.parameterManagerList = []

    def registerParameterManager(self, name, obj):
        #TODO should check the object, only need to be flushable (create an interface in utils)
    
        setattr(self, name, obj)
        self.parameterManagerList.append(name)

    def getThreadInfo(self):
        tid = current_thread().ident

        if tid in self.threadInfo:
            return self.threadInfo[tid]
        
        ti = _ThreadInfo()
        self.threadInfo[tid] = ti
        return ti

    def isThreadRegistered(self):
        return current_thread().ident in self.threadInfo

    def pushVariableLevelForThisThread(self, procedure = None):
        info = self.getThreadInfo()
        info.procedureStack.append(procedure)
        info.level += 1

    def popVariableLevelForThisThread(self):        
        if not self.isThreadRegistered():
            return 

        info = self.getThreadInfo()
                
        if info.level == -1: #this info only hold the origin
            return

        #flush parameter manager
        for name in self.parameterManagerList:
            pm = getattr(self, name)
            pm.flushVariableLevelForThisThread() #TODO rename this call to flush()
        
        #self.environment.flushVariableLevelForThisThread()
        #self.context.flushVariableLevelForThisThread()
        #self.variable.flushVariableLevelForThisThread()
        #self.key.flushVariableLevelForThisThread()
        
        #update level map
        info.level -= 1

        if info.canBeDeleted():
            del self.threadInfo[current_thread().ident]
        
    def getCurrentId(self):        
        if not self.isThreadRegistered():
            self.pushVariableLevelForThisThread()

        info = self.getThreadInfo()

        if info.level == -1:
            self.pushVariableLevelForThisThread()
    
        return (current_thread().ident,info.level,)
        
    def isMainThread(self):
        return self.mainThread == current_thread().ident

    def getCurrentProcedure(self):
        if not self.isThreadRegistered():
            return None

        info = self.getThreadInfo()

        if len(info.procedureStack) == 0:
            return None

        return info.procedureStack[-1]

    def getOrigin(self):
        if not self.isThreadRegistered():
            return ORIGIN_PROCESS, None

        info = self.getThreadInfo()
        return info.origin, info.originArg

    def setOrigin(self, origin, originArg=None):
        if origin not in ORIGIN_PROCESS:
            raise DefaultPyshellException("(ParameterContainer) setOrigin, not a valid origin, got '"+str(origin)+"', expect one of these: "+",".join(AVAILABLE_ORIGIN))

        if origin == ORIGIN_PROCESS:
            if self.isThreadRegistered():
                info = self.getThreadInfo()
                info.origin = ORIGIN_PROCESS
                info.originArg = originArg

                if info.canBeDeleted():
                    del self.threadInfo[current_thread().ident]
        else:
            info = self.getThreadInfo()
            info.origin = origin
            info.originArg = originArg
            
            
