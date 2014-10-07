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

from pyshell.arg.argchecker  import defaultInstanceArgChecker, listArgChecker, ArgChecker, IntegerArgChecker, stringArgChecker, booleanValueArgChecker, floatTokenArgChecker
from pyshell.utils.exception import ListOfException, AbstractListableException
from pyshell.utils.exception import ParameterException, ParameterLoadingException
from pyshell.utils.valuable  import Valuable
from pyshell.utils.constants import CONTEXT_NAME, ENVIRONMENT_NAME, MAIN_CATEGORY, PARAMETER_NAME, DEFAULT_SEPARATOR
import os, sys
from threading import Lock

#TODO
    #context/env manager ?
        #how to manage concurrency?
        
    #convert parent dico and subelement dico in tries
        #and manage every consequences (ambiguity)
        
    #split context/envir/variabl in separate data structure
        #no need to store them in the same dico
        #store in three separate files ?

    #implement "add value" method to context/envi list
        #used and implemented in addon/parameter.py
        #used in ?
    
try:
    pyrev = sys.version_info.major
except AttributeError:
    pyrev = sys.version_info[0]

if pyrev == 2:
    import ConfigParser 
else:
    import configparser as ConfigParser

INSTANCE_TYPE          = {"string": defaultInstanceArgChecker.getStringArgCheckerInstance,
                          "int"   : defaultInstanceArgChecker.getIntegerArgCheckerInstance,
                          "bool"  : defaultInstanceArgChecker.getbooleanValueArgCheckerInstance,
                          "float" : defaultInstanceArgChecker.getFloatTokenArgCheckerInstance}

#XXX FORBIDEN_SECTION_NAME is difined at the end of this module XXX

def getInstanceType(typ):
    if typ in INSTANCE_TYPE:
        return INSTANCE_TYPE[typ]()
    else:
        return ArgChecker()

def getTypeFromInstance(instance):
    #XXX can't use a dico here because the order is significant
    
    if isinstance(instance, booleanValueArgChecker):
        return "bool"
    elif isinstance(instance, stringArgChecker):
        return "string"
    elif isinstance(instance, IntegerArgChecker):
        return "int"
    elif isinstance(instance, floatTokenArgChecker):
        return "float"
    else:
        return "any"
        
def _getInt(config, section, option, defaultValue):
    ret = defaultValue
    if config.has_option(section, option):
        try:
            ret = int(config.get(section, option))
        except ValueError as ve:
            raise ParameterLoadingException("(ParameterManager) _getInt, fail to load '"+option+"' for section '"+str(section)+"' : "+str(ve))

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
        if self.filePath is None:
            return
    
        #load params
        config = None
        if os.path.exists(self.filePath):
            config = ConfigParser.RawConfigParser()
            try:
                config.read(self.filePath)
            except Exception as ex:
                raise ParameterLoadingException("(ParameterManager) load, fail to read parameter file : "+str(ex))
                return
        else:
        
            emptyParameter = True
            for k,v in self.params:
                if len(self.params[k]) > 0:
                    emptyParameter = False
                    break
            
            if not emptyParameter:
                #if no parameter file, try to create it, then return
                try:
                    self.save()
                except Exception as ex:
                    raise ParameterLoadingException("(ParameterManager) load, parameter file does not exist, fail to create it"+str(ex))
                return

        #read and parse, for each section
        errorList = ListOfException()
        for section in config.sections():
            specialSectionClassToUse = None
            for specialSectionClass in RESOLVE_SPECIAL_SECTION_ORDER:
                if not specialSectionClass.isParsable(config, section):
                    continue
                    
                specialSectionClassToUse = specialSectionClass
                break
            if specialSectionClassToUse != None:
            
                #a parent category with a similar name can not already exist (because of the structure of the parameter file)
                if section in self.params:
                    errorList.addException(ParameterLoadingException("Section '"+str(section)+"', a parent category with this name already exist, can not create a "+specialSectionClassToUse.getStaticName()+" with this name"))
                    continue
                
                #try to parse the parameter
                try:
                    argument_dico = specialSectionClassToUse.parse(config, section)
                except AbstractListableException as ale:
                    errorList.addException(ale)
                    continue
                
                if section in self.params[specialSectionClassToUse.getStaticName()]:
                    try:
                        self.params[specialSectionClassToUse.getStaticName()][section].setFromFile(argument_dico)
                    except Exception as ex:
                        errorList.addException(ParameterLoadingException("(ParameterManager) load, fail to set information on "+specialSectionClassToUse.getStaticName()+" '"+str(section)+"' : "+str(ex)))
                        
                else:
                    try:
                        self.params[specialSectionClassToUse.getStaticName()][section] = specialSectionClassToUse(**argument_dico)
                    except Exception as ex:
                        errorList.addException(ParameterLoadingException("(ParameterManager) load, fail to create new "+specialSectionClassToUse.getStaticName()+" '"+str(section)+"' : "+str(ex)))
                        continue
        
            ### GENERIC ### 
            else:
                if section in FORBIDEN_SECTION_NAME:
                    errorList.addException(ParameterLoadingException( "(ParameterManager) load, parent section name '"+str(section)+"' not allowed"))
                    continue
            
                #if section in 

                for option in config.options(section):
                    if section not in self.params:
                        self.params[section] = {}
                    
                    self.params[section][option] = VarParameter(config.get(section, option))
                    
                    """if option in self.params[section]:
                        if isinstance(self.params[section][option], Parameter):
                            self.params[section][option].setValue(config.get(section, option))
                            continue        
                            
                    self.params[section][option] = EnvironmentParameter(value=config.get(section, option))"""
        
        #manage errorList
        if errorList.isThrowable():
            raise errorList

    def save(self):
        if self.filePath is None:
            return
    
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
                """
                    value = str(childValue.getValue())
                else:"""
                
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

    def setParameter(self,name, param, parent = None):
        if parent == None:
            parent = MAIN_CATEGORY
        
        if parent in FORBIDEN_SECTION_NAME:
            #is context instance
            if not isinstance(param, FORBIDEN_SECTION_NAME[parent]):
                raise ParameterException("(ParameterManager) setParameter, invalid "+parent+", an instance of "+str(FORBIDEN_SECTION_NAME[parent].__name__)+" was expected, got "+str(type(param)))
            
            #name can't be an existing section name (because of the struct of the file)
            if name in self.params:
                raise ParameterException("(ParameterManager) setParameter, invalid "+parent+" name '"+str(name)+"', a similar item already has this name")
        else:
            #is generic instance 
            if not isinstance(param, VarParameter):
                raise ParameterException("(ParameterManager) setParameter, invalid parameter, an instance of VarParameter was expected, got "+str(type(param)))
        
            #parent can not be a name of a child of FORBIDEN_SECTION_NAME
            for forbidenName in FORBIDEN_SECTION_NAME:
                if name in self.params[forbidenName]:
                    raise ParameterException("(ParameterManager) setParameter, invalid parameter name '"+name+"', a similar '"+forbidenName+"' object already has this name")
            
        if parent not in self.params:
            self.params[parent] = {}

        if name in self.params[parent]:
            if self.params[parent][name].isReadOnly() or not self.params[parent][name].isRemovable():
                raise ParameterException("(ParameterManager) setParameter, this parameter name already exist and is readonly or not removable")

        self.params[parent][name] = param

    def getParameter(self, name, parent = None):
        if parent == None:
            parent = MAIN_CATEGORY

        #name exists ?
        if name not in self.params[parent]:
            raise ParameterException("(ParameterManager) getParameter, parameter '"+str(name)+"'  does not exist")

        return self.params[parent][name]

    def hasParameter(self, name, parent = None):
        if parent == None:
            parent = MAIN_CATEGORY

        return parent in self.params and name in self.params[parent]

    def unsetParameter(self, name, parent = None):
        if parent == None:
            parent = MAIN_CATEGORY

        if parent not in self.params or name not in self.params[parent]:
            raise ParameterException("(ParameterManager) unsetParameter, parameter name '"+str(name)+"'  does not exist")

        if not self.params[parent][name].isRemovable():
            raise ParameterException("(ParameterManager) setParameter, this parameter is not removable")

        del self.params[parent][name]

        if len(self.params[parent]) == 0:
            del self.params[parent] 

class Parameter(Valuable): #abstract
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
        return {} #TO OVERRIDE

    def __str__(self):
        return str(self.getValue())

    def __repr__(self):
        return str(self.getValue())
        
    @staticmethod
    def isParsable(config, section):
        return True #TO OVERRIDE
        
    @staticmethod
    def parse(config, section):
        return {} #TO OVERRIDE
    
    @staticmethod
    def getStaticName():
        return PARAMETER_NAME #TO OVERRIDE
        
    def setFromFile(self,valuesDictionary):
        pass #TO OVERRIDE

def _lockSorter(param1, param2):
    return param1.getLockID() - param2.getLockID()

class ParametersLocker(object):
    def __init__(self, parametersList):
        self.parametersList = sorted(parametersList, cmp=_lockSorter)
                
    def __enter__(self):
        for param in self.parametersList:
            param.getLock().acquire(blocking=True)
        
        return self
            
    def __exit__(self, type, value, traceback):
        for param in self.parametersList:
            param.getLock().release()

class EnvironmentParameter(Parameter):
    _internalLock = Lock()
    _internalLockCounter = 0

    def __init__(self, value, typ=None, transient = False, readonly = False, removable = True, sep = DEFAULT_SEPARATOR):
        Parameter.__init__(self, transient)
        self.setReadOnly(readonly)
        self.setRemovable(removable)

        #typ must be argChecker
        if typ is not None and not isinstance(typ,ArgChecker):
            raise ParameterException("(EnvironmentParameter) __init__, invalid type instance, must be an ArgChecker instance")

        self.isListType = isinstance(typ, listArgChecker)
        self.setListSeparator(sep)
        self.typ = typ
        self._setValue(value)
        
        self.lock   = None
        self.lockID = -1

    def _initLock(self):
        if self.lock is None:
            with EnvironmentParameter._internalLock:
                if self.lock is None:
                    self.lockID = _internalLockCounter
                    _internalLockCounter += 1
                    self.lock = Lock()
    
    def getLock(self):
        self._initLock()
        return self.lock
        
    def getLockID(self):
        self._initLock()
        return elf.lockID
    
    #TODO replace in all code part, the test isinstance(typ, listArgChecker) 
    def isAListType(self):
        return self.isListType
    
    #TODO replace brutal add value everywhere in the code
    def addValues(self, values):
        pass #TODO
        
    #TODO replace brutal remove value everywhere in the code
    def removeValue(self, value):
        pass #TODO remove a value if list type
            #TODO be carefull, need to recompute index in context class
    
    def setListSeparator(self, sep):
        if sep == None or (type(sep) != str and type(sep) != unicode):
            raise ParameterException("(EnvironmentParameter) setListSeparator, separator must be a string, get "+str(type(sep)))
            
        if len(sep) != 1:
            raise ParameterException("(EnvironmentParameter) setListSeparator, separator must have a length of 1, get <"+str(len(sep))+">")
            
        self.sep = sep

    def getValue(self):
        return self.value

    def setValue(self, value):
        if self.readonly:
            raise ParameterException("(EnvironmentParameter) setValue, read only parameter")

        self._setValue(value)

    def _setValue(self,value):
        if self.typ is None:
            self.value = value
        else:
            self.value = self.typ.getValue(value)

    def isReadOnly(self):
        return self.readonly

    def isRemovable(self):
        return self.removable

    def setReadOnly(self, state):
        if type(state) != bool:
            raise ParameterException("(EnvironmentParameter) setReadOnly, expected a bool type as state, got '"+str(type(state))+"'")
            
        self.readonly = state

    def setRemovable(self, state):
        if type(state) != bool:
            raise ParameterException("(EnvironmentParameter) setRemovable, expected a bool type as state, got '"+str(type(state))+"'")
            
        self.removable = state

    def getParameterSerializableField(self):
        toret = Parameter.getParameterSerializableField(self)
        toret["readonly"]  = str(self.readonly)
        toret["removable"] = str(self.removable)
        
        if self.isListType:
            #toret["listType"] = str(True)
            toret["separator"] = self.sep
            if self.typ is not None:
                toret["type"]     = getTypeFromInstance(self.typ.checker)
            toret["value"]    = self.sep.join(str(x) for x in self.value) #concat on ascii unit separator character

        else:
            #toret["listType"] = str(False)
            if self.typ is not None:
                toret["type"]     = getTypeFromInstance(self.typ)
            toret["value"]    = str(self.value)

        return toret
        
    @staticmethod
    def isParsable(config, section):
        return Parameter.isParsable(config, section) and config.has_option(section, "value")
        
    @staticmethod
    def parse(config,section):
        dic = {}

        value            = config.get(section, "value")
        dic["readonly"]  = _getBool(config, section, "readonly", False)
        dic["removable"] = _getBool(config, section, "removable", False)

        #manage type
        if config.has_option(section, "type"):
            dic["typ"] = getInstanceType(config.get(section, "type"))
        else:
            dic["typ"] = ArgChecker()

        #has a separator? is a list ?
        if config.has_option(section, "separator"):
            sep = config.get(section, "separator")
            
            if sep == None or (type(sep) != str and type(sep) != unicode):
                raise ParameterLoadingException("(EnvironmentParameter) parse, section '"+str(section)+"', separator must be a string, get '"+str(type(sep))+"'")
                
            if len(sep) != 1:
                raise ParameterLoadingException("(EnvironmentParameter) parse, section '"+str(section)+"', separator must have a length of 1, get <"+str(len(sep))+">")
        
            value = value.strip()
            if len(value) == 0:
                dic["value"] = ()
            else:
                dic["value"] = value.split(sep)
            
            dic["sep"] = sep
            dic["typ"] = listArgChecker(dic["typ"])
        else:
            dic["value"] = value
       
        dic["transient"] = False
        return dic
        
    @staticmethod
    def getStaticName():
        return ENVIRONMENT_NAME
        
    def setFromFile(self,valuesDictionary):
        Parameter.setFromFile(self, valuesDictionary)
        
        if "value" in valuesDictionary:
            self._setValue(valuesDictionary["value"])
            
        if "readonly" in valuesDictionary:
            self.setReadOnly(valuesDictionary["readonly"])
            
        if "removable" in valuesDictionary:
            self.setRemovable(valuesDictionary["removable"])
            
    def __repr__(self):
        return "Environment, value:"+str(self.value)
            

class ContextParameter(EnvironmentParameter):
    def __init__(self, value, typ, transient = False, transientIndex = False, index=0, defaultIndex = 0, readonly = False, removable = True, sep=","):

        if not isinstance(typ,listArgChecker):
            typ = listArgChecker(typ,1)
        
        self.defaultIndex = 0
        self.index = 0
        
        EnvironmentParameter.__init__(self, value, typ, transient, readonly, removable, sep)
        self.tryToSetDefaultIndex(defaultIndex)
        self.tryToSetIndex(index)
        self.setTransientIndex(transientIndex)
                
    def _setValue(self,value):
        EnvironmentParameter._setValue(self,value)
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
        
    def tryToSetIndex(self, index):
        try:
            self.value[index]
            self.index = index
            return
        except IndexError:
            pass
        except TypeError:
            pass
            
        self.index = self.defaultIndex

    def setIndexValue(self,value):
        try:
            self.index = self.value.index(self.typ.checker.getValue(value))
        except IndexError:
            raise ParameterException("(ContextParameter) setIndexValue, invalid index value")
        except TypeError:
            raise ParameterException("(ContextParameter) setIndexValue, invalid index value, the value must exist in the context")
            
    def getIndex(self):
        return self.index

    def getSelectedValue(self):
        return self.value[self.index]
        
    def setTransientIndex(self,state):
        if type(state) != bool:
            raise ParameterException("(ContextParameter) setTransientIndex, expected a bool type as state, got '"+str(type(state))+"'")
            
        self.transientIndex = state
        
    def isTransientIndex(self):
        return self.transientIndex
        
    def setDefaultIndex(self,defaultIndex):
        try:
            self.value[defaultIndex]
        except IndexError:
            raise ParameterException("(ContextParameter) setDefaultIndex, invalid index value, a value between 0 and "+str(len(self.value))+" was expected, got "+str(defaultIndex))
        except TypeError:
            raise ParameterException("(ContextParameter) setDefaultIndex, invalid index value, a value between 0 and "+str(len(self.value))+" was expected, got "+str(defaultIndex))
            
        self.defaultIndex = defaultIndex
        
    def tryToSetDefaultIndex(self,defaultIndex):
        try:
            self.value[defaultIndex]
            self.defaultIndex = defaultIndex
            return
        except IndexError:
            pass
        except TypeError:
            pass
            
        self.defaultIndex = 0
        
    def getDefaultIndex(self):
        return self.defaultIndex

    def getParameterSerializableField(self):
        toret = EnvironmentParameter.getParameterSerializableField(self)
        
        if not self.transientIndex:
            toret["index"] = str(self.index)
            
        toret["defaultIndex"] = str(self.defaultIndex)

        return toret
        
    def reset(self):
        self.index = self.defaultIndex

    @staticmethod
    def isParsable(config, section):
        return EnvironmentParameter.isParsable(config, section) and config.has_option(section, "defaultIndex")
        
    @staticmethod
    def parse(config, section):
        dic = EnvironmentParameter.parse(config, section)
    
        #is it context type ?
        dic["defaultIndex"] = _getInt(config, section, "defaultIndex", 0)
            
        #manage selected index
        if config.has_option(section, "index"):
            dic["transientIndex"] = False
            dic["index"] = _getInt(config, section, "index", 0)
        else:
            dic["transientIndex"] = True
            
        return dic
        
    @staticmethod
    def getStaticName():
        return CONTEXT_NAME
        
    def setFromFile(self,valuesDictionary):
        EnvironmentParameter.setFromFile(self, valuesDictionary)
        
        if "defaultIndex" in valuesDictionary:
            self.setDefaultIndex(valuesDictionary["defaultIndex"])
            
        if "transientIndex" in valuesDictionary:
            self.setTransientIndex(valuesDictionary["transientIndex"])
            
        if "index" in valuesDictionary:
            self.setIndex(valuesDictionary["index"])
        else:
            self.setIndex(self.defaultIndex)
            
    def __repr__(self):
        return "Context, available values: "+str(self.value)+", selected index: "+str(self.index)+", selected value: "+str(self.value[self.index])
    
    def __str__(self):
        return str(self.value[self.index])
        
class VarParameter(EnvironmentParameter):
    def __init__(self,value):
        tmp_value_parsed = [value] #TODO what occur if it is a list or not ?
        parsed_value = []
        
        while len(tmp_value_parsed) > 0:
            value_to_parse = tmp_value_parsed
            tmp_value_parsed = []
            
            for v in value_to_parse:
                if type(v) == str or type(v) == unicode:
                    v = v.strip()
                    v = v.split(" ")

                    for subv in v:
                        if len(subv) == 0:
                            continue
                    
                        parsed_value.append(subv)
                        
                elif hasattr(v, "__iter__"):
                    tmp_value_parsed.extend(v)
                else:
                    tmp_value_parsed.append(str(v))

        EnvironmentParameter.__init__(self,parsed_value, typ=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance(),1), transient = False, readonly = False, removable = True)    
    
    def __str__(self):
        to_ret = ""
        
        for v in self.value:
            to_ret += str(v)+" "
            
        return to_ret
    
    def __repr__(self):
        return "Variable, value:"+str(self.value)

RESOLVE_SPECIAL_SECTION_ORDER    = [ContextParameter, EnvironmentParameter]
FORBIDEN_SECTION_NAME            = {CONTEXT_NAME:ContextParameter,
                                    ENVIRONMENT_NAME:EnvironmentParameter}




