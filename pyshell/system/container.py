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

from pyshell.system.context     import ContextParameterManager
from pyshell.system.environment import EnvironmentParameterManager
from pyshell.system.key         import CryptographicKeyParameterManager
from pyshell.system.variable    import VariableParameterManager

from threading import current_thread

class ParameterContainer(object):
    SUBCONTAINER_LIST = ["environment", "context", "variable", "key"]

    def __init__(self):
        self.threadLevel = {} #hold the level of the current thread
        self.environment = EnvironmentParameterManager()
        self.context     = ContextParameterManager()
        self.variable    = VariableParameterManager()
        self.key         = CryptographicKeyParameterManager()
        self.mainThread  = current_thread().ident

    def pushVariableLevelForThisThread(self, procedure = None):
        tid = current_thread().ident
        
        #manage first call to this container with this thread
        if tid not in self.threadLevel:
            level = -1
            procedureStack = []
        else:
            level, procedureStack = self.threadLevel[tid]
        
        #add level
        procedureStack.append(procedure)
        self.threadLevel[tid] = level+1, procedureStack

    def popVariableLevelForThisThread(self):
        tid = current_thread().ident
        
        #manage first call to this container with this thread
        if tid not in self.threadLevel:
            return 
        else:
            level, procedureStack = self.threadLevel[tid]
        
        #flush parameter manager
        self.environment.flushVariableLevelForThisThread()
        self.context.flushVariableLevelForThisThread()
        self.variable.flushVariableLevelForThisThread()
        
        #update level map
        level -= 1
        if level == -1:
            del self.threadLevel[tid]
        else:
            del procedureStack[-1]
            self.threadLevel[tid] = level, procedureStack
        
    def getCurrentId(self):
        tid = current_thread().ident
        
        if tid not in self.threadLevel:
            self.pushVariableLevelForThisThread()
    
        return (tid,self.threadLevel[tid][0],)
        
    def isMainThread(self):
        return self.mainThread == current_thread().ident

    def getCurrentProcedure(self):
        tid = current_thread().ident
        return self.threadLevel[tid][1]
