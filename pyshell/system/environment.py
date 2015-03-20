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

## internal modules ##
from pyshell.arg.argchecker   import ArgChecker, defaultInstanceArgChecker, listArgChecker
from pyshell.utils.exception  import ParameterException
from pyshell.system.parameter import Parameter,ParameterManager
from pyshell.system.settings  import GlobalSettings, LocalSettings

## external modules ##
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
            param.getLock().acquire(True) #blocking=True
        
        return self
            
    def __exit__(self, type, value, traceback):
        for param in self.parametersList:
            param.getLock().release()

class EnvironmentParameter(Parameter):
    _internalLock = Lock()
    _internalLockCounter = 0

    @staticmethod
    def getInitSettings():
        return LocalSettings()

    def __init__(self, value, typ=None, settings=None):
        if settings is not None:
            if not isinstance(settings, LocalSettings):
                raise ParameterException("(EnvironmentParameter) __init__, a LocalSettings was expected for settings, got '"+str(type(settings))+"'")

            self.settings = settings
        else:
            self.settings = self.getInitSettings()
            
        readOnly = self.settings.isReadOnly()
        self.settings.setReadOnly(False)

        Parameter.__init__(self)
        if typ is None:
            typ = DEFAULT_CHECKER
        elif not isinstance(typ,ArgChecker):#typ must be argChecker
            raise ParameterException("(EnvironmentParameter) __init__, an ArgChecker instance was expected for argument typ, got '"+str(type(typ))+"'")

        self.isListType = isinstance(typ, listArgChecker)
        self.typ = typ
        self.setValue(value)
        
        self.lock     = None
        self.lockID   = -1
        self.settings.setReadOnly(readOnly)

    def _initLock(self):
        if not self.isLockEnable():
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
        return isinstance(self.settings, GlobalSettings)
    
    def isAListType(self):
        return self.isListType
    
    def addValues(self, values):
        #must be "not readonly"
        self.settings._raiseIfReadOnly(self.__class__.__name__,"addValues")
    
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
        self.settings._raiseIfReadOnly(self.__class__.__name__,"removeValues")
    
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
        self.settings._raiseIfReadOnly(self.__class__.__name__,"setValue")
        self.value = self.typ.getValue(value)

    def enableGlobal(self):
        if isinstance(self.settings, GlobalSettings):
            return
        
        self.settings = GlobalSettings(readOnly = self.settings.isReadOnly(), removable = self.settings.isRemovable())

    def enableLocal(self):
        if isinstance(self.settings, LocalSettings):
            return

        self.settings = LocalSettings(readOnly = self.settings.isReadOnly(), removable = self.settings.isRemovable())

    def __repr__(self):
        return "Environment, value:"+str(self.value)

    def __str__(self):
        return str(self.value)
        
    def __hash__(self):
        return hash( str(Parameter.__hash__(self)) + str(hash(self.settings)))
