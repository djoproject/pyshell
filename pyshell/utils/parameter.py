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
from pyshell.utils.exception import ParameterException, ParameterLoadingException
from pyshell.utils.valuable  import Valuable, SelectableValuable
from pyshell.utils.constants import CONTEXT_NAME, ENVIRONMENT_NAME, MAIN_CATEGORY, PARAMETER_NAME, DEFAULT_SEPARATOR
from threading import Lock, current_thread
from functools import wraps
from tries import multiLevelTries

def synchronous():
    def _synched(func):
        @wraps(func)
        def _synchronizer(self,*args, **kwargs):
            self._internalLock.acquire()
            try:
                return func(self, *args, **kwargs)
            finally:
                self._internalLock.release()
        return _synchronizer
    return _synched


#TODO
    #split context/envir/variabl in separate data structure
        #no need to store them in the same dico
        #store in three separate files ? XXX brainstorming needed
    
    #store in mltries
            

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

class ParameterManager2(object):
    #TODO
        #when to use perfect match or not ?
            #perfect in:
                #insertion
                    #otherelse, risk to overwrite existing parameter with prefix insertion
                    
                #unsetParameter, same problem as insertion
                #flushThreadLocal
                
            #not perfect in :
                #getParameter
                
            #can choose for :
                #hasParameter

    def __init__(self):
        self._internalLock = Lock()
        self.mltries = multiLevelTries()
        self.threadLocalVar = {}
    
    def _getAdvanceResult(self, methName, name, parent, raiseIfNotFound = True, raiseIfAmbiguous = True):
        if parent == None:
            parent = MAIN_CATEGORY
        
        path           = (parent, name,)
        advancedResult =  self.mltries.advancedSearch(path, False)
        
        if raiseIfAmbiguous and advancedResult.isAmbiguous():
            pass #TODO raise ambiguous path, say which token is ambiguous and which are the possibilities
        
        if raiseIfNotFound and not advancedResult.isValueFound():
            pass #TODO raise path does not exist, say which token is not found
        
        return advancedResult
        
    @synchronous()
    def setParameter(self,name, param, parent = None, uniqueForThread = False):
    
        #check category
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
        
            #parent can not be a name of a child of FORBIDEN_SECTION_NAME (because of the struct of the file)
            for forbidenName in FORBIDEN_SECTION_NAME:
                if name in self.params[forbidenName]:
                    raise ParameterException("(ParameterManager) setParameter, invalid parameter name '"+name+"', a similar '"+forbidenName+"' object already has this name")
            
        #check safety and existing
        advancedResult = self._getAdvanceResult("getParameter",name, parent, False, False)
        if advancedResult.isValueFound():
            value = advancedResult.getValue()
            
            if isinstance(value, dict):
                if not uniqueForThread:
                    pass #TODO raise, can not inject not unique, some unique value already exist
            
                tid = current_thread().ident
                
                if tid not in value:
                    value[tid] = param
                    
                    if tid not in self.threadLocalVar:
                        self.threadLocalVar[tid] = []
                    self.threadLocalVar[tid].append( (parent, name, ) )
                else:
                    if value[tid].isReadOnly() or not value[tid].isRemovable():
                        pass #TODO raise, not editable
                        
                    value[tid] = param
            else:  
                if uniqueForThread:
                    pass #TODO raise, can not inject unique, a not unique already exist 
            
                if value.isReadOnly() or not value.isRemovable():
                    pass #TODO raise, not editable
                    
                self.mltries.update( (parent, name, ), param )
        else:
            if uniqueForThread:
                dic = {}
                tid = current_thread().ident
                dic[tid] = param
                param = dic
                
            self.mltries.insert( (parent, name, ), param )
            
    @synchronous()
    def getParameter(self, name, parent = None):
        advancedResult = self._getAdvanceResult("getParameter",name, parent)
        value = advancedResult.getValue()
        
        if isinstance(value, dict):
            tid = current_thread().ident
            
            if tid not in value:
                pass #TODO raise path does not exist
                
            return value[tid]
        else:
            return value
    
    @synchronous()
    def hasParameter(self, name, parent = None, raiseIfAmbiguous = True):
        advancedResult = self._getAdvanceResult("hasParameter",name, parent, False,raiseIfAmbiguous)
                
        if advancedResult.isValueFound():
            value = advancedResult.getValue()
            if isinstance(value, dict):
                return current_thread().ident in value
            return True
        return False

    @synchronous()
    def unsetParameter(self, name, parent = None):
        advancedResult = self._getAdvanceResult("unsetParameter", name, parent)
        
        if advancedResult.isValueFound():
            value = advancedResult.getValue()
            if isinstance(value, dict):
                tid = current_thread().ident
                if tid not in value:
                    pass #TODO raise, not found for this thread
                
                if not value[tid].isRemovable():
                    pass #TODO raise, object not removable
                
                #remove value from dic or remove dic if empty
                if len(value) > 1:
                    del value[tid]
                else:
                    mltries.remove( advancedResult.getFoundCompletePath() )
                #TODO remove from thread local list
                
            else:
                if not value.isRemovable():
                    pass #TODO raise, object not removable
            
                mltries.remove( advancedResult.getFoundCompletePath() )
    
    @synchronous()
    def flushThreadLocal(self):
        tid = current_thread().ident
        
        if tid not in self.threadLocalVar:
            return
            
        for path in self.threadLocalVar[tid]:
        
            #XXX this check is not usefull, shouldn't occur
            if not self.hasParameter(path[0], path[1]): #TODO must be perfect match, no raise
                continue
                
            advancedResult = self._getAdvanceResult("hasParameter",path[0], path[1], False, False)
            value = advancedResult.getValue()
            
            #XXX this check is not usefull, shouldn't occur
            if isinstance(value, dict):
                pass #TODO raise, should always be a dict
                
            if len(value) > 1:
                del value[tid]
            else:
                mltries.remove( path ) #TODO could raise ? don't think it could occur, at this point we know the path exist
                    
        del self.threadLocalVar[tid]
    
    """@synchronous()
    def unMarkUnique(self, name, parent = None):
        advancedResult = self._getAdvanceResult("unMarkUnique",name, parent)
        value = advancedResult.getValue()
        
        if not isinstance(value, dict):
            pass #TODO raise, not a marked path
        
        tid = current_thread().ident
        if len(value) > 1 and (len(value) == 1 and tid not in value):
            pass #TODO raise others thread still using this mark
        
        self.mltries.remove(advancedResult.getFoundCompletePath())"""
            

class ParameterManager(object):
    #TODO
        #this object should be synchronized
        #convert to MULTILEVELTRIES
            #only two level: parent and key
            #be carefull to uptade .params usage in others place (like addons/parameter.py, loader/paramete.py)

    def __init__(self):
        self.params = {} #TODO should be tries
        self.params[CONTEXT_NAME] = {} #TODO should be tries and not in params
        self.params[ENVIRONMENT_NAME] = {} #TODO should be tries and not in params

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
        
            #parent can not be a name of a child of FORBIDEN_SECTION_NAME (because of the struct of the file)
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
        
    #UNIQUE BY THREAD TODO implement it
        #update setParameter
            #if key exist and is not unique => raise
            #if parameter is transient => raise
            #remove/disable lock for the parameter
            #add it in the current thread list, to be able to remove it easily when the thread will die
        
        #update unsetParameter
            #if unique, only remove for the current thread
            #otherelse, remove for the whole app
        
        #create flushThread
            #remove every value created for the current thread
                #overwrite readonly
        
        #create unMarkUnique, remove the tuple parent/key from the Unique system 
            #raise if mark is in use
            #otherelse remove mark
            
        #what about data structure ? TODO check that
            #to mark an empty key
                #inject a special empty parameter into the tries, or just an empty list
                
            #to keep several value for a parameter ?
                #each thread can define its parameter type, etc.
            
            #to keep a list of key for an specific thread
                #just a dictionnary of list
                    #one list for each thread

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
            param.getLock().acquire(True)
        
        return self
            
    def __exit__(self, type, value, traceback):
        for param in self.parametersList:
            param.getLock().release()

class EnvironmentParameter(Parameter):
    _internalLock = Lock()
    _internalLockCounter = 0

    def __init__(self, value, typ=None, transient = False, readonly = False, removable = True, sep = DEFAULT_SEPARATOR):
        Parameter.__init__(self, transient)
        self.readonly = False
        self.setRemovable(removable)

        #typ must be argChecker
        if typ is not None and not isinstance(typ,ArgChecker):
            raise ParameterException("(EnvironmentParameter) __init__, invalid type instance, must be an ArgChecker instance")

        self.isListType = isinstance(typ, listArgChecker)
        self.setListSeparator(sep)
        self.typ = typ
        self.setValue(value)
        
        self.lock   = None
        self.lockID = -1
        self.setReadOnly(readonly)

    def _raiseIfReadOnly(self, methName = None):
        if self.readonly:
            if methName is not None:
                methName = " "+methName+", "
            else:
                methName = ""
                
            raise ParameterException("("+self.__name__+") "+methName+"read only parameter")

    def _initLock(self):
        if self.lock is None:
            with EnvironmentParameter._internalLock:
                if self.lock is None:
                    self.lockID = EnvironmentParameter._internalLockCounter
                    EnvironmentParameter._internalLockCounter += 1
                    self.lock = Lock()
    
    def getLock(self):
        self._initLock()
        return self.lock
        
    def getLockID(self):
        self._initLock()
        return self.lockID
        
    def isLockEnable(self):
        return True #TODO be able to disable it ? yes for uniqueBytThread
    
    def isAListType(self):
        return self.isListType
    
    def addValues(self, values):
        #must be "not readonly"
        self._raiseIfReadOnly("addValues")
    
        #typ must be list
        if not self.isAListType():
            raise ParameterException("(EnvironmentParameter) addValues, can only add value to a list parameter")
    
        #values must be iterable
        if not hasattr(values, "__iter__"):
            values = (values, )
        
        #each value must be a valid element from checker
        values = self.typ.getValue(values)
    
        #append values
        self.value.extend(values)
    
    def removeValues(self, values):
        #must be "not readonly"
        self._raiseIfReadOnly("removeValues")
    
        #typ must be list
        if not self.isAListType():
            raise ParameterException("(EnvironmentParameter) removeValues, can only remove value to a list parameter")
        
        #values must be iterable
        if not hasattr(values, "__iter__"):
            values = (values, )
        
        #remove first occurence of each value
        values = self.typ.getValue(values)
        for v in values:
            if v in self.value:
                self.value.remove(v)
        
    def setListSeparator(self, sep):
        self._raiseIfReadOnly("setListSeparator")
    
        if sep == None or (type(sep) != str and type(sep) != unicode):
            raise ParameterException("(EnvironmentParameter) setListSeparator, separator must be a string, get "+str(type(sep)))
            
        if len(sep) != 1:
            raise ParameterException("(EnvironmentParameter) setListSeparator, separator must have a length of 1, get <"+str(len(sep))+">")
            
        self.sep = sep

    def getValue(self):
        return self.value

    def setValue(self, value):
        self._raiseIfReadOnly("setValue")
        
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
        self._raiseIfReadOnly("setRemovable")
    
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
        self._raiseIfReadOnly("setFromFile")
    
        Parameter.setFromFile(self, valuesDictionary)
        
        if "value" in valuesDictionary:
            self.setValue(valuesDictionary["value"])
            
        if "removable" in valuesDictionary:
            self.setRemovable(valuesDictionary["removable"])
            
        if "readonly" in valuesDictionary:
            self.setReadOnly(valuesDictionary["readonly"])
            
    def __repr__(self):
        return "Environment, value:"+str(self.value)

def _convertToSetList(orig):
    seen = set()
    seen_add = seen.add
    return [ x for x in orig if not (x in seen or seen_add(x))]

class ContextParameter(EnvironmentParameter, SelectableValuable):
    def __init__(self, value, typ, transient = False, transientIndex = False, index=0, defaultIndex = 0, readonly = False, removable = True, sep=","):

        if not isinstance(typ,listArgChecker):
            typ = listArgChecker(typ,1)
        
        self.defaultIndex = 0
        self.index = 0
        
        EnvironmentParameter.__init__(self, value, typ, transient, readonly, removable, sep)
        self.tryToSetDefaultIndex(defaultIndex)
        self.tryToSetIndex(index)
        self.setTransientIndex(transientIndex)
                
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
        self._raiseIfReadOnly("setTransientIndex")
    
        if type(state) != bool:
            raise ParameterException("(ContextParameter) setTransientIndex, expected a bool type as state, got '"+str(type(state))+"'")
            
        self.transientIndex = state
        
    def isTransientIndex(self):
        return self.transientIndex
        
    def setDefaultIndex(self,defaultIndex):
        self._raiseIfReadOnly("setDefaultIndex")
    
        try:
            self.value[defaultIndex]
        except IndexError:
            raise ParameterException("(ContextParameter) setDefaultIndex, invalid index value, a value between 0 and "+str(len(self.value))+" was expected, got "+str(defaultIndex))
        except TypeError:
            raise ParameterException("(ContextParameter) setDefaultIndex, invalid index value, a value between 0 and "+str(len(self.value))+" was expected, got "+str(defaultIndex))
            
        self.defaultIndex = defaultIndex
        
    def tryToSetDefaultIndex(self,defaultIndex):
        self._raiseIfReadOnly("tryToSetDefaultIndex")
            
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

    def addValues(self, values):
        EnvironmentParameter.addValues(self,values)
        self.value = _convertToSetList(self.value)
                
    def removeValues(self, values):
        #must stay at least one item in list
        if len(self.value) == 1:
            raise ParameterException("(ContextParameter) removeValues, can remove more value from this context, at least one value must stay in the list")
        
        #remove
        EnvironmentParameter.removeValues(self, values)
        
        #recompute index if needed
        self.tryToSetDefaultIndex(self.defaultIndex)
        self.tryToSetIndex(self.index)

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
        if "defaultIndex" in valuesDictionary:
            self.setDefaultIndex(valuesDictionary["defaultIndex"])
            
        if "transientIndex" in valuesDictionary:
            self.setTransientIndex(valuesDictionary["transientIndex"])
            
        if "index" in valuesDictionary:
            self.setIndex(valuesDictionary["index"])
        else:
            self.setIndex(self.defaultIndex)
            
        EnvironmentParameter.setFromFile(self, valuesDictionary)
            
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

        EnvironmentParameter.__init__(self,parsed_value, typ=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()), transient = False, readonly = False, removable = True)    
    
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




