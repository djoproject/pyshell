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

from pyshell.arg.argchecker import listArgChecker, ArgChecker, IntegerArgChecker, stringArgChecker, booleanValueArgChecker, floatTokenArgChecker
from exception import ParameterException
import os, sys

if sys.version_info.major == 2:
    import ConfigParser 
else:
    import configparser as ConfigParser
    
DEFAULT_PARAMETER_FILE = os.path.join(os.path.expanduser("~"), ".pyshellrc")
MAIN_CATEGORY          = "main"

CONTEXT_NAME           = "context"
ENVIRONMENT_NAME       = "environment"
FORBIDEN_SECTION_NAME  = (CONTEXT_NAME, ENVIRONMENT_NAME, ) 

def getInstanceType(typ):
    if typ == "string":
        return stringArgChecker()
    elif typ == "int":
        return IntegerArgChecker()
    elif typ == "bool":
        return booleanValueArgChecker()
    elif typ == "float":
        return floatTokenArgChecker()
    else:
        return ArgChecker()

def getTypeFromInstance(instance):
    if isinstance(instance, stringArgChecker):
        return "string"
    elif isinstance(instance, IntegerArgChecker):
        return "int"
    elif isinstance(instance, booleanValueArgChecker):
        return "bool"
    elif isinstance(instance, floatTokenArgChecker):
        return "float"
    else:
        return "any"

#TODO
    #manage readonly

    #gestion des erreurs dans le loader et un peu partout
        #gerer les appels de sous methodes qui génére des exception
            #genre le arg checker get value

        #pour le loader, tout charger même s'il y a des erreurs et afficher un recap'

    #executer command mapping
    #context/env manager ?
        #to manage concurrency for example ?
    #test

def _getInt(config, section, option, defaultValue):
    ret = defaultValue
    if config.has_option(section, option):
        try:
            ret = int(config.get(section, option))
        except ValueError as ve:
            print("(ParameterManager) _getInt, fail to load <"+option+"> for section <"+str(section)+"> : "+str(ve))

    return ret

def _getBool(config, section, option, defaultValue):
    ret = defaultValue
    if config.has_option(section, option):
        value = config.get(section,option)
        if value.upper() == "TRUE":
            ret = True
        else:
            ret = False

    return ret

class ParameterManager(object):
    def __init__(self, filePath = None):
        self.params = {}
        self.params[CONTEXT_NAME] = {}
        self.params[ENVIRONMENT_NAME] = {}
        self.filePath = filePath

    def load(self):
        #load params
        config = None
        if os.path.exists(self.filePath):
            config = ConfigParser.RawConfigParser()
            try:
                config.read(self.filePath)
            except Exception as ex:
                print("(ParameterManager) loadFile, fail to read parameter file : "+str(ex))
                return
        else:
            #if no parameter file, try to create it, then return
            self.save()
            return

        #read and parse, for each section
        for section in config.sections():

            #advanced section (context or env)
            if config.has_option(section, "value"):
                value = config.get(section, "value")

                #is it context type ?
                contextDefined = _getBool(config, section, "contextType", False)
                readonly       = _getBool(config, section, "readonly", False)
                removable      = _getBool(config, section, "removable", False)

                #manage type
                if config.has_option(section, "type"):
                    typ = getInstanceType(config.get(section, "type"))
                else:
                    typ = ArgChecker()

                isAList = contextDefined or _getBool(config, section, "listType", False)

                if isAList:
                    value = value.split(chr(31))

                ### CONTEXT ###
                if contextDefined:
                    if section in self.params[CONTEXT_NAME]:
                        context = self.params[CONTEXT_NAME][section]
                        try:
                            context.setValue(value)
                        except Exception as ex:
                            print("(ParameterManager) loadFile, fail to set value on context <"+str(section)+"> : "+str(ex))
                    else:
                        #get default index
                        defaultIndex = _getInt(config, section, "defaultIndex", 0)

                        if isAList:
                            typ = listArgChecker(typ)

                        context = ContextParameter(value, typ, False, False, defaultIndex, readonly, removable)
                        self.params[CONTEXT_NAME][section] = context

                    #manage selected index
                    transientIndex = not config.has_option(section, "index")
                    index = _getInt(config, section, "index", 0)
                    context.setIndex(index)
                    context.setTransientIndex(transientIndex)
                
                ### ENVIRONMENT ###
                else:
                    #manage existing
                    if section in self.params[ENVIRONMENT_NAME]:
                        self.params[ENVIRONMENT_NAME][section].setValue(config.get(section, "value"))
                    else:
                        if isAList:
                            typ = listArgChecker(typ)
                        
                        self.params[ENVIRONMENT_NAME][section] = EnvironmentParameter(config.get(section, "value"), typ,False, readonly, removable)
            
            ### GENERIC ### 
            else:
                if section in FORBIDEN_SECTION_NAME:
                    print("(ParameterManager) loadFile, parent section name not allowed")
                    continue
            
                #if section in 

                for option in config.options(section):
                    if section not in self.params:
                        self.params[section] = {}
                    
                    if option in self.params[section]:
                        if isinstance(self.params[section][option], Parameter):
                            self.params[section][option].setValue(config.get(section, option))
                            continue        
                            
                    self.params[section][option] = GenericParameter(value=config.get(section, option))
            
    def save(self):
        #manage standard parameter
        config = ConfigParser.RawConfigParser()
        for parent, childs in self.params.items():   
            if parent in FORBIDEN_SECTION_NAME:
                continue
            
            if parent == None:
                parent = MAIN_CATEGORY
            
            for childName, childValue in childs.items():
                if isinstance(childValue, Parameter):
                    if childValue.isTransient():
                        continue
                
                    value = str(childValue.getValue())
                else:
                    value = str(childValue)
            
                if not config.has_section(parent):
                    config.add_section(parent)

                config.set(parent, childName, value)
        
        #manage context and environment
        for s in FORBIDEN_SECTION_NAME:
            if s in self.params:
                for contextName, contextValue in self.params[s].items():
                    if contextValue.isTransient():
                        continue
                
                    if not config.has_section(contextName):
                        config.add_section(contextName)

                    for name, value in contextValue.getParameterSerializableField().items():
                        config.set(contextName, name, value)
        
        with open(self.filePath, 'wb') as configfile:
            config.write(configfile)

    def setContext(self, name, context): #ParameterException
        #is context instance
        if not isinstance(context, ContextParameter):
            raise ParameterException("(ParameterManager) setContext, invalid context, an instance of ContextParameter was expected, got "+str(type(context)))

        #name can't be an existing section name
        if name in self.params:
            raise ParameterException("(ParameterManager) setContext, invalid context name, a similar generic environment already has this name")

        self.params[CONTEXT_NAME][name] = context

    def getContext(self, name):
        #name exists ?
        if name not in self.params[CONTEXT_NAME]:
            raise ParameterException("(ParameterManager) getContext, unknown context name <"+str(name)+"> does not exist")

        return self.params[CONTEXT_NAME][name]

    def setEnvironement(self, name, environment):
        #is environment instance
        if not isinstance(environment, EnvironmentParameter) or isinstance(environment, GenericParameter):
            raise ParameterException("(ParameterManager) setEnvironement, invalid environment, an instance of EnvironmentParameter was expected, got "+str(type(environment)))

        #name can't be an existing section name
        if name in self.params:
            raise ParameterException("(ParameterManager) setEnvironement, invalid environment name, a similar generic environment already has this name")

        self.params[ENVIRONMENT_NAME][name] = environment

    def getEnvironment(self, name):
        #name exists ?
        if name not in self.params[ENVIRONMENT_NAME]:
            raise ParameterException("(ParameterManager) getEnvironment, environment name <"+str(name)+"> does not exist")

        return self.params[ENVIRONMENT_NAME][name]

    def setParameter(self,name, param, parent = None):
        if parent == None:
            parent = MAIN_CATEGORY

        #parent can not be a name of a child of FORBIDEN_SECTION_NAME
        for forbidenName in FORBIDEN_SECTION_NAME:
            if name in self.params[forbidenName]:
                raise ParameterException("(ParameterManager) setParameter, invalid parameter name, a similar "+forbidenName+" object already has this name")

        #is generic instance 
        if not isinstance(param, GenericParameter):
            raise ParameterException("(ParameterManager) setParameter, invalid parameter, an instance of GenericParameter was expected, got "+str(type(param)))

        if parent not in self.params:
            self.params[parent] = {}

        if name in self.params[parent]:
            if self.params[parent][name].isReadOnly() or not self.params[parent][name].isRemovable():
                raise ParameterException("(ParameterManager) setParameter, this parameter name already exist and is readonly or not removable")

        self.params[parent][name] = param

    def getParameter(self, name, parent = None):
        if parent == None:
            parent = MAIN_CATEGORY

        #if parent in FORBIDEN_SECTION_NAME:
        #    raise ParameterException("(ParameterManager) getParameter, can not directly access to <"+str(parent)+">, use the appropriate method")
        #XXX if this condition is enabled, could cause some problem in argchecker
            #Why: because there is no decorator to access to the FORBIDEN_SECTION_NAME and the generic decorator use this method
        #TODO ... pas classe
            #cette verif devrait etre egalement faite dans les autres methode Parameter

        #TODO plutôt rester générique et faire des vérifs quand ce sont du context ou du env

        #name exists ?
        if name not in self.params[parent]:
            raise ParameterException("(ParameterManager) getParameter, parameter name <"+str(name)+">  does not exist")

        return self.params[parent][name]

    def hasParameter(self, name, parent = None):
        if parent == None:
            parent = MAIN_CATEGORY

        return parent in self.params and name in self.params[parent]

    def unsetParameter(self, name, parent = None):
        if parent == None:
            parent = MAIN_CATEGORY

        if parent not in self.params or name not in self.params[parent]:
            raise ParameterException("(ParameterManager) unsetParameter, parameter name <"+str(name)+">  does not exist")

        if not self.params[parent][name].isRemovable():
            raise ParameterException("(ParameterManager) setParameter, this parameter is not removable")

        del self.params[parent][name]

        if len(self.params[parent]) == 0:
            del self.params[parent] 

class Parameter(object): #abstract
    def __init__(self, transient = False):
        self.transient = transient

    def getValue(self):
        pass #TO OVERRIDE

    def setValue(self,value):
        pass #TO OVERRIDE

    def setTransient(self,state):
        self.transient = state

    def isTransient(self):
        return self.transient

    def isReadOnly(self):
        return False

    def isRemovable(self):
        return self.transient
        
    def getParameterSerializableField(self):
        return {}

    def __str__(self):
        return str(self.getValue())

    def __repr__(self):
        return str(self.getValue())

class EnvironmentParameter(Parameter):
    def __init__(self, value, typ, transient = False, readonly = False, removable = True):
        Parameter.__init__(self, transient)
        self.readonly  = readonly
        self.removable = removable

        #typ must be argChecker
        if not isinstance(typ,ArgChecker):
            raise ParameterException("(EnvironmentParameter) __init__, invalid type instance, must be an ArgChecker instance")

        self.isListType = isinstance(typ, listArgChecker)
        self.typ = typ
        self.value = None
        self._setValue(value)

    def getValue(self):
        return self.value

    def setValue(self, value):
        if self.readonly:
            raise ParameterException("(EnvironmentParameter) setValue, read only parameter")

        self._setValue(value)

    def _setValue(self,value):
        self.value = self.typ.getValue(value)

    def isReadOnly(self):
        return self.readonly

    def isRemovable(self):
        return self.removable

    def setReadOnly(self, state):
        self.readonly = state

    def setRemovable(self, state):
        self.removable = state

    def getParameterSerializableField(self):
        toret = Parameter.getParameterSerializableField(self)
        toret["readonly"]  = str(self.readonly)
        toret["removable"] = str(self.removable)
        
        if self.isListType:
            toret["listType"] = str(True)
            toret["type"]     = getTypeFromInstance(self.typ.checker)
            toret["value"]    = chr(31).join(str(x) for x in self.value) #concat on ascii unit separator character

        else:
            toret["listType"] = str(False)
            toret["type"]     = getTypeFromInstance(self.typ)
            toret["value"]    = str(self.value)

        return toret

class GenericParameter(EnvironmentParameter):
    def __init__(self, value, transient = False, readonly = False, removable = True):
        EnvironmentParameter.__init__(self, value, ArgChecker(), transient, readonly, removable)
        
    def getParameterSerializableField(self):
        toret = EnvironmentParameter.getParameterSerializableField(self)
        
        if "type" in toret:
            del toret["type"]

        return toret

class ContextParameter(EnvironmentParameter):
    def __init__(self, value, typ, transient = False, transientIndex = False, defaultIndex = 0, readonly = False, removable = True):

        if not isinstance(typ,listArgChecker):
            typ = listArgChecker(typ)

        EnvironmentParameter.__init__(self, value, typ, transient, readonly, removable)
        self.index = defaultIndex
        self.defaultIndex = defaultIndex
        self.transientIndex = transientIndex

    def setIndex(self, index):
        try:
            self.value[index]
        except IndexError:
            raise Exception("(ContextParameter) setIndex, invalid index value, a value between 0 and "+str(len(self.value))+"was expected, got "+str(index))
        except TypeError:
            raise ParameterException("(ContextParameter) setIndex, invalid index value, a value between 0 and "+str(len(self.value))+"was expected, got "+str(index))
            
        self.index = index

    def setIndexValue(self,value):
        try:
            self.index = self.value.index(self.typ.checker.getValue(value))
        except IndexError:
            raise Exception("(ContextParameter) setIndexValue, invalid index value")
        except TypeError:
            raise ParameterException("(ContextParameter) setIndexValue, invalid index value, the value must exist in the context")
            
    def getIndex(self):
        return self.index

    def getSelectedValue(self):
        return self.value[self.index]
        
    def setTransientIndex(self,transientIndex):
        self.transientIndex = transientIndex
        
    def getTransientIndex(self):
        return self.transientIndex
        
    def setDefaultIndex(self,defaultIndex):
        try:
            self.value[defaultIndex]
        except IndexError:
            raise Exception("(ContextParameter) setDefaultIndex, invalid index value, a value between 0 and "+str(len(self.value))+"was expected, got "+str(defaultIndex))
        except TypeError:
            raise ParameterException("(ContextParameter) setDefaultIndex, invalid index value, a value between 0 and "+str(len(self.value))+"was expected, got "+str(defaultIndex))
            
        self.defaultIndex = defaultIndex
        
    def getDefaultIndex(self):
        return self.defaultIndex

    def getParameterSerializableField(self):
        toret = EnvironmentParameter.getParameterSerializableField(self)
        
        if not self.transientIndex:
            toret["index"] = str(self.index)
            
        toret["defaultIndex"] = str(self.defaultIndex)
        toret["contextType"]  = str(True)

        return toret
        
    def reset(self):
        self.index = self.defaultIndex


