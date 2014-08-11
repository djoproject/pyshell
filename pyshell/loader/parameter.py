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

#TODO
    #quid:
        #si on ajoute une valeur qui existe deja
        #lorsqu'on unload, on ne devrait pas la retirer
        #impliquerai d'avoir un etat du loadeur par rapport a son chargement

from utils import getAndInitCallerModule, AbstractLoader
from pyshell.utils.parameter import EnvironmentParameter, ContextParameter
from exception import LoadException

def _local_getAndInitCallerModule(subLoaderName = None)
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



#TODO for the following one, value should be an instance of parameter
    #so an instance ov env ? or just a string
        #just a string and convert it to env in the register

#TODO register properties (?)
    #need the end of brainstorming in addon.parameter
"""def registerSetParameterValue(paramKey, value, noErrorIfKeyExist = False, override = False, parent = None, subLoaderName = None):
    #test key
    if type(paramKey) != str and type(paramKey) != unicode:
        raise LoadException("(Loader) registerSetParameterValue, only string or unicode key are allowed")

    if parent != None and parent in FORBIDEN_SECTION_NAME:
        raise LoadException("(Loader) registerSetParameterValue, <"+str(parent)+"> is not an allowed parent name")

    #test value
    try:
        value = str(value)
    except Exception as ex:
        raise LoadException("(Loader) registerSetParameterValue, fail to convert value to string")

    #append
    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.params.append( (paramKey, value, noErrorIfKeyExist, override, parent) )"""


    
class ParamaterLoader(AbstractLoader):
    def __init__(self, prefix=()):
        self.valueToAddTo = [] #TODO unload
        self.valueToSet   = [] #TODO unload
        
        #self.params     = [] #TODO ??? wait
        
    def _addValueTo(self, parameterManager, keyName, valueToAdd, parentName, listOfExceptions):
        if not parameterManager.hasParameter(contextKey,CONTEXT_NAME):
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value <"+str(valueToAdd)+"> to "+str(parentName)+" <"+str(keyName)+">: unknow key name"))
            return
        
        envObject = parameterManager.getParameter(contextKey, parentName)

        if not isinstance(envObject.typ, listArgChecker):
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value <"+str(valueToAdd)+"> to "+str(parentName)+" <"+str(keyName)+">: not a list parameter"))
            return

        #value must be a list
        if not hasattr(value, "__iter__"):
            value = (value,)

        #object is readonly ?
        if envObject.isReadOnly():
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value <"+str(valueToAdd)+"> to "+str(parentName)+" <"+str(keyName)+">: object is readonly"))
        
        #check values
        ValuesToAdd = []
        for v in value:
            if v in context.value:
                listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value <"+str(v)+"> to "+str(parentName)+" <"+str(keyName)+">: value already exists"))
                continue

            #check value validity
            try:
                context.typ.checker.getValue(v,None,"Context "+contextKey)
            except argException as argE:
                listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value <"+str(valueToAdd)+"> to "+str(parentName)+" <"+str(keyName)+">: invalid value type, "+str(argE)))
                continue
                
            ValuesToAdd.append(v)
        
        oldValues = envobject.getValue()[:]
        oldValues.extend(ValuesToAdd)
            
        try:
            envobject.setValue(oldValues)
        except argException as argE:
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value <"+str(v)+"> to "+str(parentName)+" <"+str(keyName)+">: invalid values, "+str(argE)))
        except ParameterException as pe:
            listOfExceptions.addException(LoadException("(ParamaterLoader) addValueTo, fail to add value <"+str(v)+"> to "+str(parentName)+" <"+str(keyName)+">: "+str(pe)))
    
    def _setValueTo(self, parameterManager, keyName, value, noErrorIfKeyExist, override, parentName, listOfExceptions):
        if parameterManager.hasParameter(keyName, ENVIRONMENT_NAME) and not override:
            if not noErrorIfKeyExist:
                listOfExceptions.addException(LoadException("(ParamaterLoader) setValueTo, fail to set "+str(parentName)+" value with key <"+str(keyName)+">: key already exists"))
            
            return

        try:
            parameterManager.setParameter(keyName, value,parentName)
        except ParameterException as pe:
            listOfExceptions.addException(LoadException("(ParamaterLoader) setValueTo, fail to set "+str(parentName)+" value with key <"+str(keyName)+">: "+str(pe)))
    
    def load(self, parameterManager = None):
        if parameterManager == None:
            return

        exceptions = ListOfException()
        #errorList = []

        ## ADD VALUE TO CONTEXT/ENV ##
        for contextKey, value, parent in self.valueToAddTo:
            self._addValueTo(parameterManager, contextKey, value, parent, exceptions)

        for key, instance, noErrorIfKeyExist, override,ENVIRONMENT_NAME in self.valueToSet:
            self._setValueTo(parameterManager, key, instance, noErrorIfKeyExist, override,ENVIRONMENT_NAME, exceptions)

######################

        #TODO
        """## SET PARAMS ##
        for paramKey, value, noErrorIfKeyExist, override, parent in self.params:
            if parameterManager.hasParameter(paramKey,parent):
                if override:
                    parameterManager.setParameter(paramKey, EnvironmentParameter(value),parent)
                elif not noErrorIfKeyExist:
                    print("fail to create parameter <"+paramKey+">, already exists and override not allowed")

            else:
                parameterManager.setParameter(paramKey, EnvironmentParameter(value),parent)"""

        #print error list
        if exceptions.isThrowable():
            raise exceptions

    def unload(self, mltries):
        #TODO remove values added
        
        #TODO remove object set
    
        pass #TODO        

