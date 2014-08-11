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

from utils import getAndInitCallerModule, AbstractLoader
from pyshell.utils.parameter import EnvironmentParameter, ContextParameter

def _local_getAndInitCallerModule(subLoaderName = None)
    return getAndInitCallerModule(ParamaterLoader.__module__+"."+ParamaterLoader.__name__,ParamaterLoader, 3, subLoaderName)

def registerAddValueToContext(contextKey, value, subLoaderName = None):
    #test key
    if type(contextKey) != str and type(contextKey) != unicode:
        raise LoadException("(Loader) registerSetParameterValue, only string or unicode key are allowed")

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.valueToAddToContext.append( (contextKey, value, ) )
    
def registerAddValueToEnvironment(envKey, value, subLoaderName = None):
    #test key
    if type(envKey) != str and type(envKey) != unicode:
        raise LoadException("(Loader) registerAddValueToEnvironment, only string or unicode key are allowed")

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.valueToAddToEnv.append( (envKey, value,) )

def registerSetEnvironment(envKey, env, noErrorIfKeyExist = False, override = False, subLoaderName = None):
    ##test key
    if type(envKey) != str and type(envKey) != unicode:
        raise LoadException("(Loader) registerSetEnvironmentValue, only string or unicode key are allowed")

    #check typ si different de None
    if not isinstance(env, EnvironmentParameter):
        raise LoadException("(Loader) registerSetEnvironmentValue, env must be an instance of EnvironmentParameter")

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.env.append( (envKey, env, noErrorIfKeyExist, override) )
    
def registerSetContext(contextKey, context, noErrorIfKeyExist = False, override = False, subLoaderName = None):
    ##test key
    if type(contextKey) != str and type(contextKey) != unicode:
        raise LoadException("(Loader) registerSetEnvironmentValue, only string or unicode key are allowed")

    #check typ si different de None
    if not isinstance(context, ContextParameter):
        raise LoadException("(Loader) registerSetEnvironmentValue, env must be an instance of EnvironmentParameter")

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.context.append( (contextKey, context, noErrorIfKeyExist, override) )



#TODO for the following one, value should be an instance of parameter
    #so an instance ov env ? or just a string

#TODO register properties (?)
    #need the end of brainstorming in addon.parameter
def registerSetParameterValue(paramKey, value, noErrorIfKeyExist = False, override = False, parent = None, subLoaderName = None):
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
    loader.params.append( (paramKey, value, noErrorIfKeyExist, override, parent) )


    
class ParamaterLoader(AbstractLoader):
    def __init__(self, prefix=()):
        self.valueToAddToContext = [] #TODO load/unload
        self.valueToAddToEnv     = [] #TODO load/unload
    
        self.context    = [] #TODO refactor load/unload
        self.env        = [] #TODO refactor load/unload
        
        #self.params     = [] #TODO ??? wait
        
    def load(self, parameterManager = None):
        #TODO refactor

        #TODO chaque appel a parameterManager peut déclencher une exception ParameterException, les catcher !!!
            #les appels au sous object aussi, context, env, ...

        #TODO does it still work ?

        if parameterManager == None:
            return

        errorList = []

        ## ADD VALUE TO CONTEXT ##
        for contextKey, value, typ in self.context:
            if parameterManager.hasParameter(contextKey,CONTEXT_NAME):
                context = parameterManager.getParameter(contextKey, CONTEXT_NAME)

                #value must be a list in context
                if not hasattr(value, "__iter__"):
                    value = (value,)

                for v in value:
                    if v not in context.value:
                        try:
                            context.value.append( context.typ.checker.getValue(v,None,"Context "+contextKey) )
                        except argException as argE:
                            errorList.append("fail to add value <"+str(v)+"> in context <"+contextKey+"> beacause: "+str(argE))
            else:
                if typ == None:
                    print("the context <"+contextKey+"> does not exist and no type defined to create it")
                    continue

                if not hasattr(value, "__iter__"):
                    value = (value,)

                try:
                    parameterManager.setParameter(contextKey, ContextParameter(value, typ), CONTEXT_NAME)
                except argException as argE:
                    errorList.append("fail to create context <"+contextKey+">, because invalid value: "+str(argE))
                except ParameterException as ex:
                    errorList.append("fail to create context <"+contextKey+">: "+str(ex))

        ## ADD VALUE TO ENV ##
        for envKey, value, typ in self.env:
            if parameterManager.hasParameter(envKey, ENVIRONMENT_NAME):
                envobject = parameterManager.getParameter(envKey, ENVIRONMENT_NAME)

                if not isinstance(envobject.typ, listArgChecker):
                    errorList.append("fail to add environment value on <"+envKey+">, because the existing one is not a list environment")
                    continue

                oldValue = envobject.getValue()[:]
                if not hasattr(value, "__iter__"):
                    oldValue.append(value)
                else:
                    oldValue.extend(value)

                try:
                    envobject.setValue(oldValue)
                except argException as argE:
                    errorList.append("fail to add new items to environment <"+contextKey+">, because invalid value: "+str(argE))
                except ParameterException as pe:
                    errorList.append("fail to add new items to environment <"+contextKey+">: "+str(pe))
            else:
                if typ == None:
                    errorList.append("fail to add new items to environment <"+envKey+">, because the environment does not exist and no type is defined")
                    continue

                if not hasattr(value, "__iter__"):
                    value = (value,)

                if not isinstance(typ, listArgChecker):
                    typ = listArgChecker(typ)

                try:
                    parameterManager.setParameter(envKey, EnvironmentParameter(value, typ), ENVIRONMENT_NAME)
                except argException as argE:
                    errorList.append("fail to create new environment <"+envKey+">, because invalid value: "+str(argE))
                except ParameterException as pe:
                    errorList.append("fail to create new environment <"+envKey+">: "+str(pe))

        ## SET ENV ##
        for envKey, value, typ, noErrorIfKeyExist, override in self.env_set:
            if parameterManager.hasParameter(envKey, ENVIRONMENT_NAME):
                if not override:
                    continue

                envobject = parameterManager.getParameter(envKey, ENVIRONMENT_NAME)

                if not hasattr(value, "__iter__") and isinstance(envobject.typ, listArgChecker):
                    value = (value, )

                if hasattr(value, "__iter__") and not isinstance(envobject.typ, listArgChecker):
                    value = value[0]

                try:
                    envobject.setValue(value)
                except argException as argE:
                    errorList.append("fail to set value to environment <"+envKey+">, because invalid value: "+str(argE))
                except ParameterException as pe:
                    errorList.append("fail to set value to environment <"+envKey+">: "+str(pe))

            else:
                #TODO this statement looks weird...
                    #try to understand what does it need to do
                    #then compare with the existing code

                if typ == None:
                    if not noErrorIfKeyExist:
                        print("fail to add environment value on <"+envKey+">, because the environment does not exist and no type is defined")

                    continue

                if not hasattr(value, "__iter__") and isinstance(typ, listArgChecker):
                    value = (value, )

                if hasattr(value, "__iter__") and not isinstance(typ, listArgChecker):
                    typ = listArgChecker(typ)

                try:
                    parameterManager.setParameter(paramKey, EnvironmentParameter(value, typ),ENVIRONMENT_NAME)
                except argException as argE:
                    errorList.append("fail to create new environment <"+envKey+">, because invalid value: "+str(argE))
                except ParameterException as pe:
                    errorList.append("fail to create new environment <"+envKey+">: "+str(pe))

        ## SET PARAMS ##
        for paramKey, value, noErrorIfKeyExist, override, parent in self.params:
            if parameterManager.hasParameter(paramKey,parent):
                if override:
                    parameterManager.setParameter(paramKey, EnvironmentParameter(value),parent)
                elif not noErrorIfKeyExist:
                    print("fail to create parameter <"+paramKey+">, already exists and override not allowed")

            else:
                parameterManager.setParameter(paramKey, EnvironmentParameter(value),parent)

        #print error list
        for error in errorList:
            print(error)

    def unload(self, mltries):
        pass #TODO
        
    def reload(self, mltries):
        self.unload(mltries)
        self.load(mltries)
        

