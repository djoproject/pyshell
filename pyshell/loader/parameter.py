#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject,net>

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
        
from pyshell.loader.exception import LoadException
from pyshell.loader.utils     import getAndInitCallerModule, AbstractLoader
from pyshell.utils.parameter  import EnvironmentParameter, ContextParameter, VarParameter
from pyshell.arg.argchecker   import defaultInstanceArgChecker
from pyshell.utils.constants  import ENVIRONMENT_NAME, CONTEXT_NAME
from pyshell.utils.exception  import ListOfException, ParameterException

def _local_getAndInitCallerModule(subLoaderName = None):
    return getAndInitCallerModule(ParamaterLoader.__module__+"."+ParamaterLoader.__name__,ParamaterLoader, 3, subLoaderName)

def registerAddValuesToContext(contextKey, value, subLoaderName = None):
    #test key
    if type(contextKey) != str and type(contextKey) != unicode:
        raise LoadException("(Loader) registerAddValueToContext, only string or unicode key are allowed")

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.valueToAddTo.append( (contextKey, value,CONTEXT_NAME, ) )
    
def registerAddValuesToEnvironment(envKey, value, subLoaderName = None):
    #test key
    if type(envKey) != str and type(envKey) != unicode:
        raise LoadException("(Loader) registerAddValueToEnvironment, only string or unicode key are allowed")

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.valueToAddTo.append( (envKey, value, ENVIRONMENT_NAME,) )

def registerSetEnvironment(envKey, env, noErrorIfKeyExist = False, override = False, subLoaderName = None):
    ##test key
    if type(envKey) != str and type(envKey) != unicode:
        raise LoadException("(Loader) registerSetEnvironmentValue, only string or unicode key are allowed")

    #check typ si different de None
    if not isinstance(env, EnvironmentParameter):
        raise LoadException("(Loader) registerSetEnvironmentValue, env must be an instance of EnvironmentParameter")

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.valueToSet.append( (envKey, env, noErrorIfKeyExist, override,ENVIRONMENT_NAME,) )
    
def registerSetContext(contextKey, context, noErrorIfKeyExist = False, override = False, subLoaderName = None):
    ##test key
    if type(contextKey) != str and type(contextKey) != unicode:
        raise LoadException("(Loader) registerSetEnvironmentValue, only string or unicode key are allowed")

    #check typ si different de None
    if not isinstance(context, ContextParameter):
        raise LoadException("(Loader) registerSetEnvironmentValue, env must be an instance of EnvironmentParameter")

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.valueToSet.append( (contextKey, context, noErrorIfKeyExist, override,CONTEXT_NAME,) )

def registerSetVar(varKey, stringValue, noErrorIfKeyExist = False, override = False, parent = None, subLoaderName = None):
    ##test key
    if type(varKey) != str and type(varKey) != unicode:
        raise LoadException("(Loader) registerSetVar, only string or unicode key are allowed")

    #check parent
    if parent != None and parent in FORBIDEN_SECTION_NAME:
        raise LoadException("(Loader) registerSetVar, '"+str(parent)+"' is not an allowed parent name")
    
    parameter = VarParameter(stringValue)

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.valueToSet.append( (varKey, parameter, noErrorIfKeyExist, override,parent,) )
    
class ParamaterLoader(AbstractLoader):
    def __init__(self, prefix=()):
        AbstractLoader.__init__(self)
        self.valueToAddTo = []
        self.valueToSet   = []
        
        self.valueToUnset  = None
        self.valueToRemove = None

    #TODO a part of this logic has moves into utils/parameter, adapt this code
    def _removeValueTo(self, parameterManager, keyName, valueToAdd, parentName, listOfExceptions):
        if not parameterManager.hasParameter(keyName,parentName):
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value '"+str(valueToAdd)+"' to "+str(parentName)+" '"+str(keyName)+"': unknow key name"))
            return
        
        envObject = parameterManager.getParameter(keyName, parentName)

        try:
            envObject.removeValues(valueToAdd)
        except Exception as ex:
            listOfExceptions.addException(ex)

        """if not envObject.isAListType():
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value '"+str(valueToAdd)+"' to "+str(parentName)+" '"+str(keyName)+"': not a list parameter"))
            return

        #value must be a list
        if not hasattr(value, "__iter__"):
            value = (value,)

        #object is readonly ?
        if envObject.isReadOnly():
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value '"+str(valueToAdd)+"' to "+str(parentName)+" '"+str(keyName)+"': object is readonly"))
        
        #check values
        for v in value:
            if v not in envObject.value:
                listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value '"+str(v)+"' to "+str(parentName)+" '"+str(keyName)+"': value does not exist"))
                continue

            #remove value
            envObject.value.remove(v)

        #force to rebuilt index for context
        if isinstance(envObject, ContextParameter):
            envObject.setIndex(envObject.index)"""
    
    def _addValueTo(self, parameterManager, keyName, valueToAdd, parentName, listOfExceptions):
        if not parameterManager.hasParameter(keyName,parentName):
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value '"+str(valueToAdd)+"' to "+str(parentName)+" '"+str(keyName)+"': unknow key name"))
            return
        
        envObject = parameterManager.getParameter(keyName, parentName)

        try:
            envObject.addValues(valueToAdd)
        except Exception as ex:
            listOfExceptions.addException(ex)

        """if not listArgChecker.isAListType():
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value '"+str(valueToAdd)+"' to "+str(parentName)+" '"+str(keyName)+"': not a list parameter"))
            return

        #value must be a list
        if not hasattr(value, "__iter__"):
            value = (value,)

        #object is readonly ?
        if envObject.isReadOnly():
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value '"+str(valueToAdd)+"' to "+str(parentName)+" '"+str(keyName)+"': object is readonly"))
        
        #check values
        ValuesToAdd = []
        for v in value:
            if v in envObject.value:
                listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value '"+str(v)+"' to "+str(parentName)+" '"+str(keyName)+"': value already exists"))
                continue

            #check value validity
            try:
                envObject.typ.checker.getValue(v,None,"Context "+keyName)
            except argException as argE:
                listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value '"+str(valueToAdd)+"' to "+str(parentName)+" '"+str(keyName)+"': invalid value type, "+str(argE)))
                continue
                
            ValuesToAdd.append(v)
        
        oldValues = envobject.getValue()[:]
        oldValues.extend(ValuesToAdd)
            
        try:
            envobject.setValue(oldValues)
            self.valueToRemove.append(  (keyName, ValuesToAdd, parentName, )  )
        except argException as argE:
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value '"+str(v)+"' to "+str(parentName)+" '"+str(keyName)+"': invalid values, "+str(argE)))
        except ParameterException as pe:
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value '"+str(v)+"' to "+str(parentName)+" '"+str(keyName)+"': "+str(pe)))
        """

    def _unsetValueTo(self, parameterManager, exist,oldValue,keyName,parentName,value, listOfExceptions):
        
        #still exist ?
        if not parameterManager.hasParameter(keyName,parentName):
            listOfExceptions.addException(LoadException("(ParamaterLoader) unsetValueTo, fail to unset "+str(parentName)+" value with key '"+str(keyName)+"': key does not exist"))
        
        if exist:
            envItem = parameterManager.getParameter(keyName,parentName)
            
            #if current value is still the value loaded with this addon, restore the old value
            if envItem.getValue() == value:
                envItem.setValue(oldValue)
            #otherwise, the value has been updated and the item already exist before the loading of this module, so do nothing
        else: 
            try:
                parameterManager.unsetParameter(keyName, parentName)
            except ParameterException as pe:
                listOfExceptions.addException(LoadException("(ParamaterLoader) unsetValueTo, fail to unset "+str(parentName)+" value with key '"+str(keyName)+"': "+str(pe)))
    
    
    def _setValueTo(self, parameterManager, keyName, value, noErrorIfKeyExist, override, parentName, listOfExceptions):
        exist = parameterManager.hasParameter(keyName, parentName)
        oldValue = None
        if exist:
            oldValue = parameterManager.getParameter(keyName, parentName).getValue()
            if not override:
                if not noErrorIfKeyExist:
                    listOfExceptions.addException(LoadException("(ParamaterLoader) setValueTo, fail to set "+str(parentName)+" value with key '"+str(keyName)+"': key already exists"))
                
                return

        try:
            parameterManager.setParameter(keyName, value,parentName)
            self.valueToUnset.append(  (exist,oldValue,keyName,parentName,value, )  )
        except ParameterException as pe:
            listOfExceptions.addException(LoadException("(ParamaterLoader) setValueTo, fail to set "+str(parentName)+" value with key '"+str(keyName)+"': "+str(pe)))
    
    def load(self, parameterManager = None, subLoaderName = None):
        self.valueToUnset = []
        self.valueToRemove = []
        AbstractLoader.load(self, parameterManager, subLoaderName)
    
        if parameterManager == None:
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
    
        if parameterManager == None:
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

