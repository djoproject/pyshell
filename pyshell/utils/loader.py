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

from pyshell.command.command import MultiCommand, UniCommand
from exception import LoadException
from tries.exception import triesException
import inspect
from pyshell.utils.parameter import CONTEXT_NAME, ENVIRONMENT_NAME, FORBIDEN_SECTION_NAME, EnvironmentParameter, GenericParameter, ContextParameter
from pyshell.arg.exception import argException
from pyshell.arg.argchecker import ArgChecker

def _raiseIfInvalidKeyList(keyList, methName):
    if not hasattr(keyList,"__iter__"):
        raise LoadException("(Loader) "+methName+", keyList is not iterable")

    for key in keyList:
        if type(key) != str and type(key) != unicode:
            raise LoadException("(Loader) "+methName+", only string or unicode key are allowed")

        if len(key) == 0:
            raise LoadException("(Loader) "+methName+", empty key is not allowed")

def _getAndInitCallerModule(loaderName = None):
    frm = inspect.stack()[2]
    mod = inspect.getmodule(frm[0])

    loaderDict = None
    if hasattr(mod,"_loader"):
        loaderDict = mod._loader
    else:
        loaderDict = {}
        mod._loader = loaderDict
        
    if loaderName == "":
        loaderName = None
    
    if loaderName in loaderDict:
        return loaderDict[loaderName]

    loader = Loader()
    loaderDict[loaderName] = loader
    return loader

def registerSetGlobalPrefix(keyList, subLoaderName = None):
    _raiseIfInvalidKeyList(keyList, "registerSetGlobalPrefix")
    loader = _getAndInitCallerModule(subLoaderName)
    loader.prefix = keyList

def registerSetTempPrefix(keyList, subLoaderName = None):
    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "registerSetTempPrefix")

    loader = _getAndInitCallerModule(subLoaderName)
    loader.TempPrefix = keyList
    
def registerResetTempPrefix(subLoaderName = None):
    loader = _getAndInitCallerModule(subLoaderName)
    loader.TempPrefix = None

def registerAnInstanciatedCommand(keyList, cmd, subLoaderName = None):
    #must be a multiCmd
    if not isinstance(cmd, MultiCommand):
        raise LoadException("(Loader) addInstanciatedCommand, cmd must be an instance of MultiCommand")

    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "registerAnInstanciatedCommand")

    loader = _getAndInitCallerModule(subLoaderName)
    loader._addCmd(" ".join(keyList), keyList, cmd)
    return cmd

def registerCommand(keyList, pre=None,pro=None,post=None, showInHelp=True, subLoaderName = None):
    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "registerCommand")
    loader = _getAndInitCallerModule(subLoaderName)
    
    if loader.TempPrefix != None:
        name = " ".join(loader.TempPrefix) + " " + " ".join(keyList)
    else:
        name = " ".join(keyList)
        
    cmd = UniCommand(name, pre,pro,post, showInHelp)
    
    loader._addCmd(name, keyList, cmd)
    return cmd

def registerCreateMultiCommand(keyList, showInHelp=True, subLoaderName = None):
    loader = _getAndInitCallerModule(subLoaderName)

    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "registerCreateMultiCommand")
    
    if loader.TempPrefix != None:
        name = " ".join(loader.TempPrefix) + " " + " ".join(keyList)
    else:
        name = " ".join(keyList)
    
    cmd = MultiCommand(name, showInHelp)
    loader._addCmd(name, keyList, cmd)

    return cmd

def registerAddActionOnEvent(eventType, action, subLoaderName = None):
    pass #TODO XXX need to have event manager, later

def registerDependOnAddon(name, subLoaderName = None):
    if type(name) != str and type(name) != unicode:
        raise LoadException("(Loader) registerDependOnAddon, only string or unicode addon name are allowed")

    loader = _getAndInitCallerModule(subLoaderName)
    loader.dep.append(name)

#TODO if value is a list, must have more than one element

def registerAddValueToContext(contextKey, value, typ = None, subLoaderName = None):
    #test key
    if type(contextKey) != str and type(contextKey) != unicode:
        raise LoadException("(Loader) registerSetParameterValue, only string or unicode key are allowed")

    #check typ si different de None
    if typ != None and not isinstance(typ, ArgChecker):
        raise LoadException("(Loader) registerSetParameterValue, type must be None or an instance of ArgChecker")

    loader = _getAndInitCallerModule(subLoaderName)
    loader.context.append( (contextKey, value, typ) )
    
def registerAddValueToEnvironment(envKey, value, typ = None, subLoaderName = None):
    #test key
    if type(envKey) != str and type(envKey) != unicode:
        raise LoadException("(Loader) registerAddValueToEnvironment, only string or unicode key are allowed")

    #check typ si different de None
    if typ != None and not isinstance(typ, ArgChecker):
        raise LoadException("(Loader) registerAddValueToEnvironment, type must be None or an instance of ArgChecker")

    loader = _getAndInitCallerModule(subLoaderName)
    loader.env.append( (envKey, value, typ) )
    
def registerSetEnvironmentValue(envKey, value, typ = None, noErrorIfKeyExist = False, override = False, subLoaderName = None):
    ##test key
    if type(envKey) != str and type(envKey) != unicode:
        raise LoadException("(Loader) registerSetEnvironmentValue, only string or unicode key are allowed")

    #check typ si different de None
    if typ != None and not isinstance(typ, ArgChecker):
            raise LoadException("(Loader) registerSetEnvironmentValue, type must be None or an instance of ArgChecker")

    loader = _getAndInitCallerModule(subLoaderName)
    loader.env_set.append( (envKey, value, typ, noErrorIfKeyExist, override) )
    
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
    loader = _getAndInitCallerModule(subLoaderName)
    loader.params.append( (paramKey, value, noErrorIfKeyExist, override, parent) )
    
def registerStopHelpTraversalAt(keyList,subLoaderName = None):
    loader = _getAndInitCallerModule(subLoaderName)

    #check cmd and keylist
    _raiseIfInvalidKeyList(keyList, "registerCreateMultiCommand")
    loader.stoplist.append(keyList)

class Loader(object):
    def __init__(self, prefix=()):
        self.prefix     = prefix
        self.cmdDict    = {}
        self.TempPrefix = None
        self.stoplist   = []

        self.context    = [] 
        self.env        = [] 
        self.env_set    = [] 
        self.params     = [] 
        self.dep        = [] #TODO
    
    def _load(self, mltries, parameterManager= None):
        #add command
        for k,v in self.cmdDict.iteritems():
            keyList, cmd = v
            key = list(self.prefix)
            key.extend(keyList)
            try:
                mltries.insert(key, cmd)
            except triesException as te:
                print "fail to insert key <"+str(" ".join(key))+"> in multi tries: "+str(te)

        #stop traversal
        for stop in self.stoplist:
            key = list(self.prefix)
            key.extend(stop)
        
            try:
                mltries.setStopTraversal(key, True)
            except triesException as te:
                print "fail to disable traversal for key list <"+str(" ".join(stop))+"> in multi tries: "+str(te)

        self._loadParams(parameterManager)

    def _loadParams(self, parameterManager = None):

        #TODO chaque appel a parameterManager peut déclencher une exception ParameterException, les catcher !!!
            #les appels au sous object aussi, context, env, ...

        if parameterManager == None:
            return

        #context
        for contextKey, value, typ in self.context:
            if parameterManager.hasParameter(contextKey,CONTEXT_NAME):
                context = parameterManager.getContext(contextKey)

                if not hasattr(value, "__iter__"):
                    value = (value,)

                for v in value:
                    if v not in context.value:
                        try:
                            context.value.append( context.typ.checker.getValue(v) )
                        except argException as argE:
                            print("fail to add value <"+str(v)+"> in context <"+contextKey+"> beacause: "+str(argE))
            else:
                if typ == None:
                    print("the context <"+contextKey+"> does not exist and no type defined to create it")
                    continue

                if not hasattr(value, "__iter__"):
                    value = (value,)

                try:
                    parameterManager.setContext(contextKey, ContextParameter(value, typ)) #TODO may throw an exception
                except argException as argE:
                    print("fail to create context <"+contextKey+">, because invalid value: "+str(argE))
                    continue

        for envKey, value, typ in self.env:
            if parameterManager.hasParameter(envKey, ENVIRONMENT_NAME):
                envobject = parameterManager.getEnvironment(envKey)

                if not isinstance(envobject.typ, listArgChecker):
                    print("fail to add environment value on <"+envKey+">, because the existing one is not a list environment")
                    continue

                oldValue = envobject.getValue()[:]
                if not hasattr(value, "__iter__"):
                    oldValue.append(value)
                else:
                    oldValue.extend(value)

                envobject.setValue(oldValue) #TODO may raise an exception

            else:
                if typ == None:
                    print("fail to add environment value on <"+envKey+">, because the environment does not exist and no type is defined")
                    continue

                if not hasattr(value, "__iter__"):
                    value = (value,)

                if not isinstance(typ, listArgChecker):
                    typ = listArgChecker(typ)

                parameterManager.setEnvironement(envKey, EnvironmentParameter(value, typ)) #TODO may throw an exception


        for envKey, value, typ, noErrorIfKeyExist, override in self.env_set:
            if parameterManager.hasParameter(envKey, ENVIRONMENT_NAME):
                if not override:
                    continue

                envobject = parameterManager.getEnvironment(envKey)

                if not hasattr(value, "__iter__") and isinstance(envobject.typ, listArgChecker):
                    value = (value, )

                if hasattr(value, "__iter__") and not isinstance(envobject.typ, listArgChecker):
                    value = value[0]

                envobject.setValue(value) #TODO may throw an exception

            else:
                if typ == None:
                    if not noErrorIfKeyExist:
                        print("fail to add environment value on <"+envKey+">, because the environment does not exist and no type is defined")

                    continue

                if not hasattr(value, "__iter__") and isinstance(typ, listArgChecker):
                    value = (value, )

                if hasattr(value, "__iter__") and not isinstance(typ, listArgChecker):
                    typ = listArgChecker(typ)

                parameterManager.setParameter(paramKey, GenericParameter(value),parent) #TODO may throw an exception

        for paramKey, value, noErrorIfKeyExist, override, parent in self.params:
            if parameterManager.hasParameter(paramKey,parent):
                if override:
                    parameterManager.setParameter(paramKey, GenericParameter(value),parent) #TODO may throw an exception
                elif not noErrorIfKeyExist:
                    print("fail to create parameter <"+paramKey+">, already exists and override not allowed")

            else:
                parameterManager.setParameter(paramKey, GenericParameter(value),parent) #TODO may throw an exception


    def _unload(self, mltries):
        for k,v in self.cmdDict.iteritems():
            keyList, cmd = v
            key = list(self.prefix)
            key.extend(keyList)
            
            try:
                mltries.remove(key)
            except triesException as te:
                print("fail to remove key <"+str(" ".join(key))+"> in multi tries: "+str(te))
        
        #don't unload params on unload

    def _unloadParams(self, parameterManager):
        pass #TODO
        
    def _reload(self, mltries):
        self.unload(mltries)
        self.load(mltries)
        
    def _addCmd(self, name, keyList, cmd):
        if self.TempPrefix != None:
            prefix = list(self.TempPrefix)
            prefix.extend(keyList)
        else:
            prefix = keyList
    
        self.cmdDict[name] = (prefix, cmd,)
        
        
        
        
