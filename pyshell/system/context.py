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

from pyshell.system.parameter import ParameterManager, LocalParameterSettings, GlobalParameterSettings
from pyshell.system.environment import EnvironmentParameter
from pyshell.utils.valuable  import SelectableValuable
from pyshell.utils.exception import ParameterException
from pyshell.arg.argchecker  import listArgChecker, defaultInstanceArgChecker

CONTEXT_DEFAULT_CHECKER = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance())
CONTEXT_DEFAULT_CHECKER.setSize(1,None)

class ContextParameterManager(ParameterManager):
    def getAllowedType(self):
        return ContextParameter

def _convertToSetList(orig):
    seen = set()
    seen_add = seen.add
    return [ x for x in orig if not (x in seen or seen_add(x))]


class LocalContextParameterSettings(LocalParameterSettings):
    def __init__(self, readOnly = False, removable = True):
        LocalParameterSettings.__init__(self,readOnly,removable)

    def setTransientIndex(self,state):
        pass
        
    def isTransientIndex(self):
        return True

class GlobalContextParameterSettings(GlobalParameterSettings, LocalContextParameterSettings): #inheritance in this order will ignore setTransientIndex and isTransientIndex from LocalContextParameterSettings and use those from GlobalParameterSettings
    def __init__(self, readOnly = False, removable = True, transient = False, originProvider = None, transientIndex = False):
        GlobalParameterSettings.__init__(self,False,removable,transient,originProvider)
        self.setTransientIndex(transientIndex)
        self.setReadOnly(readOnly)

    def setTransientIndex(self,state):
        self._raiseIfReadOnly(self.__class__.__name__,"setTransientIndex")
    
        if type(state) != bool:
            raise ParameterException("(GlobalContextParameterSettings) setTransientIndex, expected a bool type as state, got '"+str(type(state))+"'")
            
        self.transientIndex = state
        self.updateOrigin()
        
    def isTransientIndex(self):
        return self.transientIndex

class ContextParameter(EnvironmentParameter, SelectableValuable):
    @staticmethod
    def getInitSettings():
        return LocalContextParameterSettings()

    def __init__(self, value, typ=None, transientIndex = False, index=0, defaultIndex = 0, settings=None):

        if typ is None:
            typ = CONTEXT_DEFAULT_CHECKER
        else:
            if not isinstance(typ,listArgChecker):            
                typ = listArgChecker(typ,minimumSize=1,maximumSize=None) #minimal size = 1, because we need at least one element to have a context
            else:
                typ.setSize(1,typ.maximumSize)
                
            if typ.checker.maximumSize != 1:
                raise ParameterException("(ContextParameter) __init__, inner checker must have a maximum length of 1, got '"+str(typ.checker.maximumSize)+"'")
        
        self.defaultIndex = 0
        self.index = 0
        
        EnvironmentParameter.__init__(self, value, typ)
        self.tryToSetDefaultIndex(defaultIndex)
        self.tryToSetIndex(index)

        #set and check settings
        if settings is not None:
            if not isinstance(settings, LocalContextParameterSettings):
                raise ParameterException("(ContextParameter) __init__, a LocalContextParameterSettings was expected for settings, got '"+str(type(settings))+"'")

            self.settings = settings
    
    def getProperties(self):
        prop = list(self.settings.getProperties())
        prop.append( ("defaultIndex", self.defaultIndex,) )

        if not self.settings.isTransientIndex():
            prop.append( ("index", self.index,) )

        return tuple(prop)

    def setValue(self,value):
        EnvironmentParameter.setValue(self,value)
        self.value = _convertToSetList(self.value)
        self.tryToSetDefaultIndex(self.defaultIndex)
        self.tryToSetIndex(self.index)

    def setIndex(self, index):
        try:
            self.value[index]
        except IndexError:
            raise ParameterException("(ContextParameter) setIndex, invalid index value, a value between 0 and "+str(len(self.value))+" was expected, got "+str(index))
        except TypeError:
            raise ParameterException("(ContextParameter) setIndex, invalid index value, a value between 0 and "+str(len(self.value))+" was expected, got "+str(index))
            
        self.index = index
        if not self.settings.isTransientIndex():
            self.settings.updateOrigin()
        
    def tryToSetIndex(self, index):
        #try new index
        try:
            self.value[index]
            self.index = index
            if not self.settings.isTransientIndex():
                self.settings.updateOrigin()
            return
        except IndexError:
            pass
        except TypeError:
            pass

        #try old index, is it still valid?
        try:
            self.value[self.index]
            return #no update on the object
        except IndexError:
            pass
        
        #old index is no more valid, try defaultIndex
        self.tryToSetDefaultIndex(self.defaultIndex) #default index is still valid ?
        self.index = self.defaultIndex 
        if not self.settings.isTransientIndex():
            self.settings.updateOrigin()

    def setIndexValue(self,value):
        try:
            self.index = self.value.index(self.typ.checker.getValue(value))
        except ValueError:
            raise ParameterException("(ContextParameter) setIndexValue, unexisting value '"+str(value)+"', the value must exist in the context")
            
        if not self.settings.isTransientIndex():
            self.settings.updateOrigin()
            
    def getIndex(self):
        return self.index

    def getSelectedValue(self):
        return self.value[self.index]
                
    def setDefaultIndex(self,defaultIndex):
        self.settings._raiseIfReadOnly(self.__class__.__name__,"setDefaultIndex")
    
        try:
            self.value[defaultIndex]
        except IndexError:
            raise ParameterException("(ContextParameter) setDefaultIndex, invalid index value, a value between 0 and "+str(len(self.value))+" was expected, got "+str(defaultIndex))
        except TypeError:
            raise ParameterException("(ContextParameter) setDefaultIndex, invalid index value, a value between 0 and "+str(len(self.value))+" was expected, got "+str(defaultIndex))
            
        self.defaultIndex = defaultIndex
        self.settings.updateOrigin()
        
    def tryToSetDefaultIndex(self,defaultIndex):
        self.settings._raiseIfReadOnly(self.__class__.__name__,"tryToSetDefaultIndex")
        
        #try new default index
        try:
            self.value[defaultIndex]
            self.defaultIndex = defaultIndex
            self.settings.updateOrigin()
            return
        except IndexError:
            pass
        except TypeError:
            pass
        
        #try old default index, is it still valid ?
        try:
            self.value[self.defaultIndex]
            return #no update on the object
        except IndexError:
            pass
        
        #if old default index is invalid, set default as 0, there is always at least one element in context, index 0 will always be valid
        self.defaultIndex = 0
        self.settings.updateOrigin()
        
    def getDefaultIndex(self):
        return self.defaultIndex
        
    def reset(self):
        self.index = self.defaultIndex
        
        if not self.settings.isTransientIndex():
            self.settings.updateOrigin()

    def addValues(self, values):
        EnvironmentParameter.addValues(self,values)
        self.value = _convertToSetList(self.value)
                
    def removeValues(self, values):
        self.settings._raiseIfReadOnly(self.__class__.__name__,"removeValues")
        
        values = _convertToSetList(values)
        
        newValues = []
        for v in values:
            if v in self.value:
                newValues.append(v)
                
        if len(newValues) == 0:
            return
    
        #must stay at least one item in list
        if (len(self.value) - len(newValues)) == 0:
            raise ParameterException("(ContextParameter) removeValues, can remove all the value in this context, at least one value must stay in the list")
        
        #remove
        EnvironmentParameter.removeValues(self, newValues)
        
        #recompute index if needed
        self.tryToSetDefaultIndex(self.defaultIndex)
        self.tryToSetIndex(self.index)
            
    def __repr__(self):
        return "Context, available values: "+str(self.value)+", selected index: "+str(self.index)+", selected value: "+str(self.value[self.index])
    
    def __str__(self):
        return str(self.value[self.index])
        
    def enableGlobal(self):
        if isinstance(self.settings, GlobalContextParameterSettings):
            return
        
        readOnly = self.settings.isReadOnly()
        removable = self.settings.isRemovable()
        self.settings.__class__ = GlobalContextParameterSettings
        GlobalContextParameterSettings.__init__(self.settings, readOnly=readOnly, removable=removable)
        self.settings.setRemovable(removable)
        self.settings.setReadOnly(readOnly)
