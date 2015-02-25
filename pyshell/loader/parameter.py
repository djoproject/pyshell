#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

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

#TODO
    #pas convaincu de la maniere dont sont loadé/unloadé les valeurs/parametre
    #faire le point et voir si la solution est vraiment optimale
        
from pyshell.loader.exception import LoadException
from pyshell.loader.utils     import getAndInitCallerModule, AbstractLoader
from pyshell.arg.argchecker   import defaultInstanceArgChecker
from pyshell.utils.constants  import ENVIRONMENT_ATTRIBUTE_NAME, VARIABLE_ATTRIBUTE_NAME
from pyshell.utils.exception  import ListOfException, ParameterException
from pyshell.system.parameter import isAValidStringPath, EnvironmentParameter, ContextParameter, VarParameter

def _local_getAndInitCallerModule(subLoaderName = None):
    return getAndInitCallerModule(ParamaterLoader.__module__+"."+ParamaterLoader.__name__,ParamaterLoader, 3, subLoaderName)

def registerAddValuesToContext(contextKey, value, subLoaderName = None):
    #test key
    state, result = isAValidStringPath(contextKey)
    if not state:
        raise LoadException("(Loader) registerAddValueToContext, "+result)

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.valueToAddTo.append( (contextKey, value, CONTEXT_ATTRIBUTE_NAME, ) )
    
def registerAddValuesToEnvironment(envKey, value, subLoaderName = None):
    #test key
    state, result = isAValidStringPath(envKey)
    if not state:
        raise LoadException("(Loader) registerAddValuesToEnvironment, "+result)

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.valueToAddTo.append( (envKey, value, ENVIRONMENT_ATTRIBUTE_NAME,) )

def registerAddValuesToVariable(varKey, value, subLoaderName = None):
    #test key
    state, result = isAValidStringPath(varKey)
    if not state:
        raise LoadException("(Loader) registerAddValuesToVariable, "+result)

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.valueToAddTo.append( (varKey, value, VARIABLE_ATTRIBUTE_NAME,) )

def registerSetEnvironment(envKey, env, noErrorIfKeyExist = False, override = False, subLoaderName = None):
    ##test key
    state, result = isAValidStringPath(envKey)
    if not state:
        raise LoadException("(Loader) registerSetEnvironmentValue, "+result)

    #check typ si different de None
    if not isinstance(env, EnvironmentParameter):
        raise LoadException("(Loader) registerSetEnvironmentValue, env must be an instance of EnvironmentParameter")

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.valueToSet.append( (envKey, env, noErrorIfKeyExist, override,ENVIRONMENT_ATTRIBUTE_NAME,) )
    
def registerSetContext(contextKey, context, noErrorIfKeyExist = False, override = False, subLoaderName = None):
    ##test key
    state, result = isAValidStringPath(contextKey)
    if not state:
        raise LoadException("(Loader) registerSetContext, "+result)

    #check typ si different de None
    if not isinstance(context, ContextParameter):
        raise LoadException("(Loader) registerSetContext, env must be an instance of EnvironmentParameter")

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.valueToSet.append( (contextKey, context, noErrorIfKeyExist, override,CONTEXT_ATTRIBUTE_NAME,) )

def registerSetVar(varKey, stringValue, noErrorIfKeyExist = False, override = False, subLoaderName = None):
    ##test key
    state, result = isAValidStringPath(varKey)
    if not state:
        raise LoadException("(Loader) registerSetVar, "+result)
    
    parameter = VarParameter(stringValue)
    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.valueToSet.append( (varKey, parameter, noErrorIfKeyExist, override,VARIABLE_ATTRIBUTE_NAME,) )
    
class ParamaterLoader(AbstractLoader):
    def __init__(self, prefix=()):
        AbstractLoader.__init__(self)
        self.valueToAddTo = []
        self.valueToSet   = []
        
        self.valueToUnset  = None
        self.valueToRemove = None #TODO not used...

    def _removeValueTo(self, parameterManager, keyName, valueToRemove, attributeName, listOfExceptions):
        if not hasattr(parameterManager, attributeName):
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, environment container does not have the attribute '"+str(attributeName)+"'"))
            return

        container = getattr(parameterManager, attributeName)

        envObject = container.getParameter(keyName, perfectMatch = True, startWithLocal = False, exploreOtherLevel=False)
        if envObject is None:
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value '"+str(valueToRemove)+"' to '"+str(keyName)+"': unknow key name"))
            return

        try:
            envObject.removeValues(valueToRemove)
        except Exception as ex:
            listOfExceptions.addException(ex)
    
    def _addValueTo(self, parameterManager, keyName, valueToAdd, attributeName, listOfExceptions):
        if not hasattr(parameterManager, attributeName):
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, environment container does not have the attribute '"+str(attributeName)+"'"))
            return

        container = getattr(parameterManager, attributeName)

        envObject = container.getParameter(keyName, perfectMatch = True, startWithLocal = False, exploreOtherLevel=False)
        if envObject is None:
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value '"+str(valueToAdd)+"' to '"+str(keyName)+"': unknow key name"))
            return
        
        try:
            envObject.addValues(valueToAdd)
            self.valueToRemove.append(  (keyName, valueToAdd, attributeName)  )
        except Exception as ex:
            listOfExceptions.addException(ex)

    def _unsetValueTo(self, parameterManager, exist,oldValue,keyName,attributeName,value, listOfExceptions):
        if not hasattr(parameterManager, attributeName):
            listOfExceptions.addException(LoadException("(ParamaterLoader) unsetValueTo, environment container does not have the attribute '"+str(attributeName)+"'"))
            return

        container = getattr(parameterManager, attributeName)
        
        #still exist ?
        envItem = container.getParameter(keyName, perfectMatch = True, startWithLocal = False, exploreOtherLevel=False)
        if envItem is None:
            listOfExceptions.addException(LoadException("(ParamaterLoader) unsetValueTo, fail to unset value with key '"+str(keyName)+"': key does not exist"))
        
        if exist: #TODO could try to use envItem even if it is None, no ?
            #if current value is still the value loaded with this addon, restore the old value
            if envItem.getValue() == value:
                envItem.setValue(oldValue)
            #otherwise, the value has been updated and the item already exist before the loading of this module, so do nothing
        else: 
            try:
                container.unsetParameter(keyName, startWithLocal = False, exploreOtherLevel=False)
            except ParameterException as pe:
                listOfExceptions.addException(LoadException("(ParamaterLoader) unsetValueTo, fail to unset value with key '"+str(keyName)+"': "+str(pe)))
    
    def _setValueTo(self, parameterManager, keyName, value, noErrorIfKeyExist, override, attributeName, listOfExceptions):
        if not hasattr(parameterManager, attributeName):
            listOfExceptions.addException(LoadException("(ParamaterLoader) setValueTo, environment container does not have the attribute '"+str(attributeName)+"'"))
            return

        container = getattr(parameterManager, attributeName)
        param = container.getParameter(keyName, perfectMatch = True, startWithLocal = False, exploreOtherLevel=False)
        exist = param is not None
        oldValue = None
        if exist:
            oldValue = param.getValue()
            if not override:
                if not noErrorIfKeyExist:
                    listOfExceptions.addException(LoadException("(ParamaterLoader) setValueTo, fail to set value with key '"+str(keyName)+"': key already exists"))
                
                return
        try:
            container.setParameter(keyName, value, localParam=False)
            self.valueToUnset.append(  (exist,oldValue,keyName,attributeName,value, )  )
        except ParameterException as pe:
            listOfExceptions.addException(LoadException("(ParamaterLoader) setValueTo, fail to set value with key '"+str(keyName)+"': "+str(pe)))
    
    def load(self, parameterManager = None, subLoaderName = None):
        self.valueToUnset = []
        self.valueToRemove = []
        AbstractLoader.load(self, parameterManager, subLoaderName)
    
        if parameterManager is None:
            return

        exceptions = ListOfException()

        #add value
        for contextKey, value, parent in self.valueToAddTo:
            self._addValueTo(parameterManager, contextKey, value, parent, exceptions)

        #set value
        for key, instance, noErrorIfKeyExist, override,parent in self.valueToSet:
            self._setValueTo(parameterManager, key, instance, noErrorIfKeyExist, override,parent, exceptions)

        #raise error list
        if exceptions.isThrowable():
            raise exceptions

    def unload(self, parameterManager = None, subLoaderName = None):
        AbstractLoader.unload(self, parameterManager, subLoaderName)
    
        if parameterManager is None:
            return

        exceptions = ListOfException()

        #remove values added
        for contextKey, value, parent  in self.valueToRemove:
            self._removeValueTo(parameterManager, contextKey, value, parent, exceptions)

        #remove object set
        for exist,oldValue,keyName,parentName,value in self.valueToUnset:
            self._unsetValueTo(parameterManager, exist, oldValue, keyName, parentName, value, exceptions)

        #raise error list
        if exceptions.isThrowable():
            raise exceptions       

