#!/usr/bin/env python -t
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

from pyshell.utils.constants import EMPTY_STRING, SYSTEM_VIRTUAL_LOADER
from pyshell.utils.exception import ParameterException
from pyshell.system.container import AbstractParameterContainer
import collections

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

    def isFantom(self):
        return False

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
        
    def clone(self, From=None):
        if From is None:
            return Settings()
            
        return From

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
        
    def clone(self, From=None):
        if From is None:
            return LocalSettings(self.isReadOnly(), self.isRemovable())
        
        From.setReadOnly(False)
        From.setRemovable(self.isRemovable())
        From.setReadOnly(self.isReadOnly())
        
        return Settings.clone(From)

class GlobalSettings(LocalSettings):
    def __init__(self, readOnly = False, removable = True, transient = False):
        LocalSettings.__init__(self, False, removable)
        
        self.setTransient(transient)
        self.loaderSet    = {}
        self.startingHash = None
        self.setReadOnly(readOnly)

    def setTransient(self,state):
        self._raiseIfReadOnly(self.__class__.__name__,"setTransient")
        
        if type(state) != bool:
            raise ParameterException("(GlobalSettings) setTransient, expected a bool type as state, got '"+str(type(state))+"'")
            
        self.transient = state

    def isTransient(self):
        return self.transient

    def setLoaderState(self, loaderSignature, loaderState):
        #loaderState must be hashable
        if not isinstance(loaderSignature, collections.Hashable):
            raise ParameterException("(GlobalSettings) setLoaderState, loaderSignature has to be hashable") 

        self.loaderSet[loaderSignature] = loaderState
        return loaderState
        
    def getLoaderState(self, loaderSignature):
        return self.loaderSet[loaderSignature]
        
    def hasLoaderState(self, loaderSignature):
        return loaderSignature in self.loaderSet

    def hashForLoader(self, loaderSignature = None):
        if loaderSignature is None:
            SYSTEM_VIRTUAL_LOADER
            
        if loaderSignature is not SYSTEM_VIRTUAL_LOADER:
            return hash(self.loaderSet[loaderSignature])
            
        if SYSTEM_VIRTUAL_LOADER not in self.loaderSet:
            return hash(self)
            
        return hash( str(hash(self)) + str(hash(self.loaderSet[loaderSignature])))
        
    def getLoaders(self):
        return self.loaderSet.keys()
        
    def isFantom(self):
        return len(self.loaderSet) == 0
    
    ##### TODO remove method below, and update parameter/container
        #each loader will store two hash for each storable items (original hash, hash after file load)
        #merge does not exist anymore
        #create a method, setRegisteredHashForLoader, setFileHashForLoader (these methods will be called in loaders)
            #these methods only take the loaders signature as argument, the hash occurs on the information stored in the settings
    
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
        self.startingHash = settings.startingHash
        
    def setStartingPoint(self, hashi, origin, originProfile = None): 
        if self.startingHash is not None:
            raise ParameterException("(GlobalSettings) setStartingPoint, a starting point was already defined for this parameter") 
            
        self.startingHash = hashi        
        
    def isEqualToStartingHash(self, hashi):
        return hashi == self.startingHash   
    
    #XXX stop removing here ###############################################
    
    def clone(self, From=None):
        if From is None:
            From = GlobalSettings(self.isReadOnly(), self.isRemovable(), self.isTransient())
        else:
            From.setTransient(self.isTransient())
        
        #TODO clone loader state
            #if no clone method, use copy tools
                #simple or deep copy ?
        
        return LocalSettings.clone(From)
        
