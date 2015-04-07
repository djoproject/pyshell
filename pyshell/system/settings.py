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

from pyshell.utils.constants import EMPTY_STRING
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

    def addLoader(self, loaderSignature):
        pass

    def mergeFromPreviousSettings(self, parameter):
        pass
        
    def getLoaderSet(self):
        return None

    def getProperties(self):
        return ( ("removable", self.isRemovable(), ), ("readOnly", self.isReadOnly(), ), ("transient", self.isTransient(), ) ) 
        
    def __hash__(self):
        return hash(self.getProperties())

class LocalSettings(Settings):
    def __init__(self, readOnly = False, removable = True):
        self.readOnly = False
        self.setRemovable(removable)
        self.setReadOnly(readOnly)

    def setReadOnly(self, state):
        if type(state) != bool:
            raise ParameterException("(LocalSettings) setReadOnly, expected a bool type as state, got '"+str(type(state))+"'")
            
        self.readOnly = state

    def isReadOnly(self):
        return self.readOnly

    def _raiseIfReadOnly(self, className = None, methName = None):
        if self.isReadOnly():
            if methName is not None:
                methName = str(methName)+", "
            else:
                methName = EMPTY_STRING
                
            if className is not None:
                className = "("+str(className)+") "
            else:
                className = EMPTY_STRING
                
            raise ParameterException(className+methName+"read only parameter")

    def setRemovable(self, state):
        self._raiseIfReadOnly(self.__class__.__name__,"setRemovable")
    
        if type(state) != bool:
            raise ParameterException("(LocalSettings) setRemovable, expected a bool type as state, got '"+str(type(state))+"'")
            
        self.removable = state

    def isRemovable(self):
        return self.removable

class GlobalSettings(LocalSettings):
    def __init__(self, readOnly = False, removable = True, transient = False):
        LocalSettings.__init__(self, False, removable)
        
        self.setTransient(transient)
        self.loaderSet    = None
        #self.origin       = None
        #self.originArg    = None
        self.startingHash = None
        self.setReadOnly(readOnly)

    def setTransient(self,state):
        self._raiseIfReadOnly(self.__class__.__name__,"setTransient")
        
        if type(state) != bool:
            raise ParameterException("(GlobalSettings) setTransient, expected a bool type as state, got '"+str(type(state))+"'")
            
        self.transient = state

    def isTransient(self):
        return self.transient

    def addLoader(self, loaderSignature):
        if self.loaderSet is None:
            self.loaderSet = set()
            
        self.loaderSet.add(loaderSignature)
        
    def getLoaderSet(self):
        return self.loaderSet
    
    def mergeFromPreviousSettings(self, settings):
        if settings is None:
            return

        if not isinstance(settings, GlobalSettings):
            raise ParameterException("(GlobalSettings) mergeFromPreviousSettings, a GlobalSettings object was expected, got '"+str(type(settings))+"'") 
        
        #manage loader
        otherLoaders = settings.getLoaderSet()
        if self.loaderSet is None:
            if otherLoaders is not None:
                self.loaderSet = set(otherLoaders)
        elif otherLoaders is not None:
            self.loaderSet = self.loaderSet.union(otherLoaders)
    
        #manage origin
        
        #TODO the first tuple (origin,originProfile,) of the current settings has to stay in first position
        
        self.startingHash = settings.startingHash
        
    def setStartingPoint(self, hashi, origin, originProfile = None):
        if self.startingHash is not None:
            raise ParameterException("(GlobalSettings) setStartingPoint, a starting point was already defined for this parameter") 
            
        self.startingHash = hashi
        
        #TODO 
            #(origin,originProfile,) become first in loaderSet AND should always stay first
        
        
    def isEqualToStartingHash(self, hashi):
        return hashi == self.startingHash

    def getStartingPoint(self):
        pass #TODO return origin point of this settings, first items in the list
                
