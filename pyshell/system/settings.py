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

from pyshell.utils.constants import EMPTY_STRING, ORIGIN_PROCESS
from pyshell.utils.exception import ParameterException
from pyshell.system.container import AbstractParameterContainer

class Settings(object):
    def __init__(self, readOnly = False, removable = True):
        pass
    
    def setTransient(self,state):
        pass

    def isTransient(self):
        return True

    def setReadOnly(self, state):
        pass

    def isReadOnly(self):
        return False        

    def setRemovable(self, state):
        pass

    def isRemovable(self):
        return True

    def setOriginProvider(self, provider):
        pass

    def updateOrigin(self):
        pass

    def addLoader(self, loaderSignature):
        pass

    def mergeLoaderSet(self, parameter):
        pass
        
    def getLoaderSet(self):
        return None

    def getProperties(self):
        return ( ("removable", self.isRemovable(), ), ("readonly", self.isReadOnly(), ), ) 

class LocalSettings(Settings):
    def __init__(self, readOnly = False, removable = True):
        self.readOnly = False
        self.setRemovable(removable)
        self.setReadOnly(readOnly)

    def setReadOnly(self, state):
        if type(state) != bool:
            raise ParameterException("(LocalSettings) setReadOnly, expected a bool type as state, got '"+str(type(state))+"'")
            
        self.readOnly = state
        self.updateOrigin()

    def isReadOnly(self):
        return self.readOnly

    def _raiseIfReadOnly(self, className = None, methName = None):
        if self.isReadOnly():
            if methName is not None:
                methName = methName+", "
            else:
                methName = EMPTY_STRING
                
            if className is not None:
                className = "("+className+") "
            else:
                className = EMPTY_STRING
                
            raise ParameterException(className+methName+"read only parameter")

    def setRemovable(self, state):
        self._raiseIfReadOnly(self.__class__.__name__,"setRemovable")
    
        if type(state) != bool:
            raise ParameterException("(LocalSettings) setRemovable, expected a bool type as state, got '"+str(type(state))+"'")
            
        self.removable = state
        self.updateOrigin()

    def isRemovable(self):
        return self.removable

class GlobalSettings(LocalSettings):
    def __init__(self, readOnly = False, removable = True, transient = False, originProvider = None):
        self.setOriginProvider(originProvider)
        
        LocalSettings.__init__(self, False, removable)
        
        self.setTransient(transient)
        self.loaderSet = None
        self.updateOrigin()
        self.setReadOnly(readOnly)

    def setTransient(self,state):
        if type(state) != bool:
            raise ParameterException("(GlobalSettings) setTransient, expected a bool type as state, got '"+str(type(state))+"'")
            
        self.transient = state
        self.updateOrigin()

    def isTransient(self):
        return self.transient

    def setOriginProvider(self, provider):
        if provider is not None and not isinstance(provider, AbstractParameterContainer):
            raise ParameterException("(GlobalSettings) setOriginProvider, an AbstractParameterContainer object was expected, got '"+str(type(provider))+"'") 
        
        self.originProvider = provider
        
    def updateOrigin(self):    
        if self.originProvider == None:
            self.origin = ORIGIN_PROCESS
            self.originArg = None
        else:
            self.origin, self.originArg = self.originProvider.getOrigin()

    def addLoader(self, loaderSignature):
        if self.loaderSet is None:
            self.loaderSet = set()
            
        self.loaderSet.add(loaderSignature)
        
    def getLoaderSet(self):
        return self.loaderSet
        
    def mergeLoaderSet(self, settings):
        if not isinstance(settings, Settings):
            raise ParameterException("(GlobalSettings) mergeLoaderSet, a Settings object was expected, got '"+str(type(settings))+"'") 
        
        otherLoaders = settings.getLoaderSet()
        if self.loaderSet is None:
            if otherLoaders is not None:
                self.loaderSet = set(otherLoaders)
        elif otherLoaders is not None:
            self.loaderSet = self.loaderSet.union(otherLoaders)
