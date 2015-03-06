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

from pyshell.system.parameter import Parameter,ParameterManager
from pyshell.arg.argchecker   import ArgChecker, listArgChecker, defaultInstanceArgChecker

from threading import Lock

DEFAULT_CHECKER = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance())

class EnvironmentParameterManager(ParameterManager):
    def getAllowedType(self):
        return EnvironmentParameter

def _lockSorter(param1, param2):
    return param1.getLockID() - param2.getLockID()

class ParametersLocker(object):
    def __init__(self, parametersList):
        self.parametersList = sorted(parametersList, cmp=_lockSorter)
                
    def __enter__(self):
        for param in self.parametersList:
            param.getLock().acquire(True)
        
        return self
            
    def __exit__(self, type, value, traceback):
        for param in self.parametersList:
            param.getLock().release()

class EnvironmentParameter(Parameter):
    _internalLock = Lock()
    _internalLockCounter = 0

    def __init__(self, value, typ=None, transient = False, readonly = False, removable = True):
        Parameter.__init__(self, transient)
        self.readonly = False #need to be false at the beginning to define the different class fields
        self.setRemovable(removable)
        
        if typ is None:
            typ = DEFAULT_CHECKER
        else:
            #typ must be argChecker
            if not isinstance(typ,ArgChecker):
                raise ParameterException("(EnvironmentParameter) __init__, invalid type instance, must be an ArgChecker instance")

        self.isListType = isinstance(typ, listArgChecker)
        self.typ = typ
        self.setValue(value)
        
        self.lock     = None
        self.lockID   = -1
        self.lockable = True
        self.setReadOnly(readonly)
        
    def getProperties(self):
        return ( ("removable", self.removable, ), ("readonly", self.readonly, ), ) 

    def _raiseIfReadOnly(self, methName = None):
        if self.readonly:
            if methName is not None:
                methName = " "+methName+", "
            else:
                methName = ""
                
            raise ParameterException("("+self.__class__.__name__+") "+methName+"read only parameter")

    def _initLock(self):
        if not self.lockable:
            return

        if self.lock is None:
            with EnvironmentParameter._internalLock:
                if self.lock is None:
                    self.lockID = EnvironmentParameter._internalLockCounter
                    EnvironmentParameter._internalLockCounter += 1
                    self.lock = Lock()
    
    def getLock(self):
        self._initLock()
        return self.lock
        
    def getLockID(self):
        self._initLock()
        return self.lockID
        
    def isLockEnable(self):
        return self.lockable
    
    def isAListType(self):
        return self.isListType
    
    def addValues(self, values):
        #must be "not readonly"
        self._raiseIfReadOnly("addValues")
    
        #typ must be list
        if not self.isAListType():
            raise ParameterException("(EnvironmentParameter) addValues, can only add value to a list parameter")
    
        #values must be iterable
        if not hasattr(values, "__iter__"):
            values = (values, )
        
        #each value must be a valid element from checker
        values = self.typ.getValue(values)
    
        #append values
        self.value.extend(values)
    
    def removeValues(self, values):
        #must be "not readonly"
        self._raiseIfReadOnly("removeValues")
    
        #typ must be list
        if not self.isAListType():
            raise ParameterException("(EnvironmentParameter) removeValues, can only remove value to a list parameter")
        
        #values must be iterable
        if not hasattr(values, "__iter__"):
            values = (values, )
        
        #remove first occurence of each value
        values = self.typ.getValue(values)
        for v in values:
            if v in self.value:
                self.value.remove(v)

    def getValue(self):
        return self.value

    def setValue(self, value):
        self._raiseIfReadOnly("setValue")
        self.value = self.typ.getValue(value)

    def isReadOnly(self):
        return self.readonly

    def isRemovable(self):
        return self.removable

    def setReadOnly(self, state):
        if type(state) != bool:
            raise ParameterException("(EnvironmentParameter) setReadOnly, expected a bool type as state, got '"+str(type(state))+"'")
            
        self.readonly = state

    def setRemovable(self, state):
        self._raiseIfReadOnly("setRemovable")
    
        if type(state) != bool:
            raise ParameterException("(EnvironmentParameter) setRemovable, expected a bool type as state, got '"+str(type(state))+"'")
            
        self.removable = state

    def __repr__(self):
        return "Environment, value:"+str(self.value)
