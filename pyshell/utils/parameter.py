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

from pyshell.arg.argchecker  import ArgChecker, defaultInstanceArgChecker, listArgChecker
from pyshell.utils.exception import ParameterException
from pyshell.utils.valuable  import Valuable, SelectableValuable
from threading import Lock, current_thread
from functools import wraps
from tries import multiLevelTries
from shlex import shlex

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

def isAValidStringPath(stringPath):
    if type(stringPath) != str and type(stringPath) != unicode:
        return False, "invalid stringPath, a string was expected, got '"+str(type(stringPath))+"'"

    if len(stringPath) == 0:
        return False, "stringPath can not have a length of 0"
    
    path = stringPath.split(".")

    for index in xrange(0, len(path)):
        if len(path[index]) == 0:
            return False, "key at index '"+str(index)+"' has a length of 0"

    return True, path

class ParameterContainer(object):
    SUBCONTAINER_LIST = ["environment", "context", "variable"]

    def __init__(self):
        self.environment = ParameterManagerV2()
        self.context     = ParameterManagerV2()
        self.variable    = ParameterManagerV2()

    def flushVariableForCurrentThread(): #TODO call it at the end of each execution, prblm with inner call...
        self.environment.flushThreadLocal()
        self.context.flushThreadLocal()
        self.variable.flushThreadLocal()

class ParameterManagerV3(object):
    #TODO
        #be carefull to uptade .params usage in others place (like addons/parameter.py, loader/paramete.py)
        #be carefull to use boolean perfectMatch for hasParameter and getParameter
                
    def __init__(self):
        self._internalLock  = Lock()
        self.mltries        = multiLevelTries() 
        self.threadLocalVar = {}                #hold the paths for the current level of the current thread
        self.threadLevel    = {}                #hold the level of the current thread
    
    def _buildExistingPathFromError(self, wrongPath, advancedResult):
        pathToReturn = list(advancedResult.getFoundCompletePath())
        pathToReturn.extend(wrongPath[advancedResult.getTokenFoundCount():])
        return pathToReturn

    def _getAdvanceResult(self, methName, stringPath, raiseIfNotFound = True, raiseIfAmbiguous = True, perfectMatch = False):

        #prepare and check path
        state, result = isAValidStringPath(stringPath)

        if not state:
            raise ParameterException("(ParameterManager) "+str(methName)+","+result)

        path = result

        #explore mltries
        advancedResult =  self.mltries.advancedSearch(path, perfectMatch)
        
        if raiseIfAmbiguous and advancedResult.isAmbiguous(): 
            indexOfAmbiguousKey = advancedResult.getTokenFoundCount()
            possiblePath = self.mltries.buildDictionnary(path[:indexOfAmbiguousKey], ignoreStopTraversal=True, addPrexix=True, onlyPerfectMatch=False)
            possibleValue = []
            for k,v in possiblePath.items():
                possibleKey.append(k[indexOfPossibleValue])
            
            raise ParameterException("(ParameterManager) "+str(methName)+", key '"+str(path[indexOfAmbiguousKey])+"' is ambiguous for path '"+".".join(self._buildExistingPathFromError(path, advancedResult))+"', possible value are: '"+",".join(possibleValue)+"'")
        
        if raiseIfNotFound and not advancedResult.isValueFound():
            indexNotFound = advancedResult.getTokenFoundCount()
            raise ParameterException("(ParameterManager) "+str(methName)+", key '"+str(path[indexNotFound])+"' is unknown for path '"+".".join(self._buildExistingPathFromError(path, advancedResult))+"'")
                        
        return advancedResult
        
    @synchronous()
    def setParameter(self,stringPath, param, localParam = True):

        #must be an instance of Parameter
        if not isinstance(param, Parameter):
            raise ParameterException("(ParameterManager) setParameter, invalid parameter '"+str(stringPath)+"', an instance of Parameter was expected, got "+str(type(param)))

        #check safety and existing
        advancedResult = self._getAdvanceResult("getParameter",stringPath, False, False, True)
        if advancedResult.isValueFound():
            (global_var, local_var, ) = advancedResult.getValue()
            
            if localParam:
                tid            = current_thread().ident
                key            = (tid, self.threadLevel[tid]) #TODO could raise if no starting push
                param.lockable = False #this parameter will be only used in a single thread, no more need to lock it

                if key in local_var:
                    if local_var[key].isReadOnly() or not local_var[key].isRemovable():
                        raise ParameterException("(ParameterManager) setParameter, can not set the parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' because a parameter with this name already exist and is not editable")
                else:
                    if key not in self.threadLocalVar:
                        self.threadLocalVar[key] = set()

                    self.threadLocalVar[key].add( advancedResult.getFoundCompletePath() )

                local_var[key] = param

            else:
                if global_var is not None and (global_var.isReadOnly() or not global_var.isRemovable()):
                    raise ParameterException("(ParameterManager) setParameter, can not set the parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' because a parameter with this name already exist and is not editable")

                self.mltries.update( stringPath.split("."), (param, local_var, ) )
        else:
            local_var = {}
            if localParam:
                global_var     = None
                tid            = current_thread().ident
                key            = (tid, self.threadLevel[tid]) #TODO could raise if no starting push
                local_var[key] = param
                param.lockable = False #this parameter will be only used in a single thread, no more need to lock it
            else:
                global_var = param
                
            self.mltries.insert( stringPath.split("."), (global_var, local_var, ) )
            
    @synchronous()
    def getParameter(self, stringPath, perfectMatch = False, localParam = True): #TODO
        advancedResult = self._getAdvanceResult("getParameter",stringPath, perfectMatch=perfectMatch) #this call will raise if value not found or ambiguous
        (global_var, local_var, ) = advancedResult.getValue()
        
        #TODO boolean localParam is not enough, we need to know if we have to explore local and global, or only local, or only global

        #TODO update from here
        if isinstance(value, dict):
            tid = current_thread().ident
            
            if tid not in value:
                raise ParameterException("(ParameterManager) getParameter, unknown parameter '"+stringPath+"'")
                
            return value[tid]
        else:
            return value
    
    @synchronous()
    def hasParameter(self, stringPath, raiseIfAmbiguous = True, perfectMatch = False, localParam = True): #TODO
        advancedResult = self._getAdvanceResult("hasParameter",stringPath, False,raiseIfAmbiguous, perfectMatch) #this call will raise if ambiguous
        
        #TODO boolean localParam is not enough, we need to know if we have to explore local and global, or only local, or only global

        if advancedResult.isValueFound():
            value = advancedResult.getValue()
            if isinstance(value, dict):
                return current_thread().ident in value
            return True
        return False

    @synchronous()
    def unsetParameter(self, stringPath, localParam = True): #TODO
        advancedResult = self._getAdvanceResult("unsetParameter", stringPath, perfectMatch=True) #this call will raise if value not found or ambiguous
        
        #TODO boolean localParam is not enough, we need to know if we have to explore local and global, or only local, or only global
            #not sure about unset

        if advancedResult.isValueFound():
            value = advancedResult.getValue()
            if isinstance(value, dict):
                tid = current_thread().ident
                if tid not in value:
                    raise ParameterException("(ParameterManager) unsetParameter, unknown parameter '"+" ".join(advancedResult.getFoundCompletePath())+"'")
                
                if not value[tid].isRemovable():
                    raise ParameterException("(ParameterManager) unsetParameter, parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' is not removable")
                
                #remove value from dic or remove dic if empty
                if len(value) > 1:
                    del value[tid]
                else:
                    self.mltries.remove( advancedResult.getFoundCompletePath() )
                
                #remove from thread local list
                self.threadLocalVar[tid].remove(advancedResult.getFoundCompletePath())
                if len(self.threadLocalVar[tid]) == 0:
                    del self.threadLocalVar[tid]
                
            else:
                if not value.isRemovable():
                    raise ParameterException("(ParameterManager) unsetParameter, parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' is not removable")
            
                self.mltries.remove( advancedResult.getFoundCompletePath() )
    
    @synchronous()    
    def pushVariableLevelForThisThread():
        tid = current_thread().ident

        if tid not in self.threadLevel:
            self.threadLevel[tid] = 0
        else:
            self.threadLevel[tid] += 1

    @synchronous()    
    def popVariableLevelForThisThread():
        tid = current_thread().ident

        if tid in self.threadLevel: #do we have at least a default level for this thread ?
            key = (tid, self.threadLevel[tid])

            #clean level
            if key in self.threadLocalVar: #do we have recorded some variables for this thread at this level ?
                for path in self.threadLocalVar[key]: #no error possible, missing value or invalid type is possible here, because of the process in set/unset
                    advancedResult = self._getAdvanceResult("popVariableLevelForThisThread",path, False, False)
                    (global_var_value, local_var_dic,) = advancedResult.getValue()
                    del local_var_dic[key]
                        
                    if global_var_value is None and len(local_var_dic) == 0:
                        mltries.remove( path ) #can not raise, because every path exist

                del self.threadLocalVar[key]

            #remove level
            if self.threadLevel[tid] <= 0: #if root level, end of this thread
                del self.threadLevel[tid]
            else:
                self.threadLevel[tid] -= 1

class ParameterManagerV2(object):
    #TODO
        #be carefull to uptade .params usage in others place (like addons/parameter.py, loader/paramete.py)
        #be carefull to use boolean perfectMatch for hasParameter and getParameter
                
    def __init__(self):
        self._internalLock = Lock()
        self.mltries = multiLevelTries()
        self.threadLocalVar = {}
    
    def _buildExistingPathFromError(self, wrongPath, advancedResult):
        pathToReturn = list(advancedResult.getFoundCompletePath())
        pathToReturn.extend(wrongPath[advancedResult.getTokenFoundCount():])

        print wrongPath, advancedResult.getFoundCompletePath(), advancedResult.getTokenFoundCount()

        return pathToReturn

    def _getAdvanceResult(self, methName, stringPath, raiseIfNotFound = True, raiseIfAmbiguous = True, perfectMatch = False):

        #prepare and check path
        state, result = isAValidStringPath(stringPath)

        if not state:
            raise ParameterException("(ParameterManager) "+str(methName)+","+result)

        path = result

        #explore mltries
        advancedResult =  self.mltries.advancedSearch(path, perfectMatch)
        
        if raiseIfAmbiguous and advancedResult.isAmbiguous(): 
            indexOfAmbiguousKey = advancedResult.getTokenFoundCount()
            possiblePath = self.mltries.buildDictionnary(path[:indexOfAmbiguousKey], ignoreStopTraversal=True, addPrexix=True, onlyPerfectMatch=False)
            possibleValue = []
            for k,v in possiblePath.items():
                possibleKey.append(k[indexOfPossibleValue])
            
            raise ParameterException("(ParameterManager) "+str(methName)+", key '"+str(path[indexOfAmbiguousKey])+"' is ambiguous for path '"+".".join(self._buildExistingPathFromError(path, advancedResult))+"', possible value are: '"+",".join(possibleValue)+"'")
        
        if raiseIfNotFound and not advancedResult.isValueFound():
            indexNotFound = advancedResult.getTokenFoundCount()
            raise ParameterException("(ParameterManager) "+str(methName)+", key '"+str(path[indexNotFound])+"' is unknown for path '"+".".join(self._buildExistingPathFromError(path, advancedResult))+"'")
                        
        return advancedResult
        
    @synchronous()
    def setParameter(self,stringPath, param, uniqueForThread = False):

        #must be an instance of Parameter
        if not isinstance(param, Parameter):
            raise ParameterException("(ParameterManager) setParameter, invalid parameter '"+str(stringPath)+"', an instance of Parameter was expected, got "+str(type(param)))

        #check safety and existing
        advancedResult = self._getAdvanceResult("getParameter",stringPath, False, False, True)
        if advancedResult.isValueFound():
            value = advancedResult.getValue()
            
            if isinstance(value, dict):
                if not uniqueForThread:
                    raise ParameterException("(ParameterManager) setParameter, can not set the parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' with not unique by thread because this parameter is already used in other thread as unique by thread")
            
                tid = current_thread().ident
                param.lockable = False #this parameter will be only used in a single thread, no more need to lock it

                if tid not in value:
                    value[tid] = param
                    
                    if tid not in self.threadLocalVar:
                        self.threadLocalVar[tid] = set()
                    self.threadLocalVar[tid].add( advancedResult.getFoundCompletePath() )
                else:
                    if value[tid].isReadOnly() or not value[tid].isRemovable():
                        raise ParameterException("(ParameterManager) setParameter, can not set the parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' because a parameter with this name already exist and is not editable")
                        
                    value[tid] = param
            else:  
                if uniqueForThread:
                    raise ParameterException("(ParameterManager) setParameter, can not set the parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' with unique by thread because this parameter is already used as not unique by thread")
            
                if value.isReadOnly() or not value.isRemovable():
                    raise ParameterException("(ParameterManager) setParameter, can not set the parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' because a parameter with this name already exist and is not editable")
                    
                self.mltries.update( advancedResult.getFoundCompletePath(), param )
        else:
            if uniqueForThread:
                dic            = {}
                tid            = current_thread().ident
                dic[tid]       = param
                param.lockable = False #this parameter will be only used in a single thread, no more need to lock it
                param          = dic
                
            self.mltries.insert( stringPath.split("."), param )
            
    @synchronous()
    def getParameter(self, stringPath, perfectMatch = False):
        advancedResult = self._getAdvanceResult("getParameter",stringPath, perfectMatch=perfectMatch) #this call will raise if value not found or ambiguous
        value = advancedResult.getValue()
        
        if isinstance(value, dict):
            tid = current_thread().ident
            
            if tid not in value:
                raise ParameterException("(ParameterManager) getParameter, unknown parameter '"+stringPath+"'")
                
            return value[tid]
        else:
            return value
    
    @synchronous()
    def hasParameter(self, stringPath, raiseIfAmbiguous = True, perfectMatch = False):
        advancedResult = self._getAdvanceResult("hasParameter",stringPath, False,raiseIfAmbiguous, perfectMatch) #this call will raise if ambiguous
                
        if advancedResult.isValueFound():
            value = advancedResult.getValue()
            if isinstance(value, dict):
                return current_thread().ident in value
            return True
        return False

    @synchronous()
    def unsetParameter(self, stringPath):
        advancedResult = self._getAdvanceResult("unsetParameter", stringPath, perfectMatch=True) #this call will raise if value not found or ambiguous
        
        if advancedResult.isValueFound():
            value = advancedResult.getValue()
            if isinstance(value, dict):
                tid = current_thread().ident
                if tid not in value:
                    raise ParameterException("(ParameterManager) unsetParameter, unknown parameter '"+" ".join(advancedResult.getFoundCompletePath())+"'")
                
                if not value[tid].isRemovable():
                    raise ParameterException("(ParameterManager) unsetParameter, parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' is not removable")
                
                #remove value from dic or remove dic if empty
                if len(value) > 1:
                    del value[tid]
                else:
                    self.mltries.remove( advancedResult.getFoundCompletePath() )
                
                #remove from thread local list
                self.threadLocalVar[tid].remove(advancedResult.getFoundCompletePath())
                if len(self.threadLocalVar[tid]) == 0:
                    del self.threadLocalVar[tid]
                
            else:
                if not value.isRemovable():
                    raise ParameterException("(ParameterManager) unsetParameter, parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' is not removable")
            
                self.mltries.remove( advancedResult.getFoundCompletePath() )
    
    @synchronous()
    def flushThreadLocal(self):
        tid = current_thread().ident
        
        if tid not in self.threadLocalVar:
            return
            
        for path in self.threadLocalVar[tid]: #no error possible, missing value or invalid type is possible here, because of the process in set/unset
            advancedResult = self._getAdvanceResult("hasParameter",path, False, False)
            value = advancedResult.getValue()

            if len(value) > 1:
                del value[tid]
            else:
                mltries.remove( path ) #can not raise, because every path exist
                    
        del self.threadLocalVar[tid]            

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

    def __str__(self):
        return str(self.getValue())

    def __repr__(self):
        return str(self.getValue())

    def getProperties(self):
        return ()

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

    def __init__(self, value, typ=None, transient = False, readonly = False, removable = True):
        Parameter.__init__(self, transient)
        self.readonly = False #need to be false at the beginning to define the different class fields
        self.setRemovable(removable)

        #typ must be argChecker
        if typ is not None and not isinstance(typ,ArgChecker):
            raise ParameterException("(EnvironmentParameter) __init__, invalid type instance, must be an ArgChecker instance")

        self.isListType = isinstance(typ, listArgChecker)
        self.typ = typ
        self.setValue(value)
        
        self.lock     = None
        self.lockID   = -1
        self.lockable = True
        self.setReadOnly(readonly)
        
    def getProperties(self):
        return ( ("removable", self.removable, ), ("readonly", self.readonly, ), ) 

    def _raiseIfReadOnly(self, methName = None):
        if self.readonly:
            if methName is not None:
                methName = " "+methName+", "
            else:
                methName = ""
                
            raise ParameterException("("+self.__class__.__name__+") "+methName+"read only parameter")

    def _initLock(self):
        if not self.lockable:
            return

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
        return self.lockable
    
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

    def __repr__(self):
        return "Environment, value:"+str(self.value)

def _convertToSetList(orig):
    seen = set()
    seen_add = seen.add
    return [ x for x in orig if not (x in seen or seen_add(x))]

class ContextParameter(EnvironmentParameter, SelectableValuable):
    def __init__(self, value, typ, transient = False, transientIndex = False, index=0, defaultIndex = 0, readonly = False, removable = True):

        if not isinstance(typ,listArgChecker):            
            typ = listArgChecker(typ,1)
        else:        
            typ.setSize(1,None)
            
        if typ.checker.maximumSize != 1:
            raise ParameterException("(ContextParameter) __init__, inner checker must have a maximum length of 1, got '"+str(typ.checker.maximumSize)+"'")
        
        self.defaultIndex = 0
        self.index = 0
        
        EnvironmentParameter.__init__(self, value, typ, transient, False, removable)#, sep)
        self.tryToSetDefaultIndex(defaultIndex)
        self.tryToSetIndex(index)
        self.setTransientIndex(transientIndex)
        self.setReadOnly(readonly)
    
    def getProperties(self):
        return  ( ("defaultIndex", self.defaultIndex,), ("index", self.index,), ("removable", self.removable, ), ("readonly", self.readonly, ), )

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
            
    def __repr__(self):
        return "Context, available values: "+str(self.value)+", selected index: "+str(self.index)+", selected value: "+str(self.value[self.index])
    
    def __str__(self):
        return str(self.value[self.index])
        
class VarParameter(EnvironmentParameter):
    def __init__(self,value):
        tmp_value_parsed = [value]
        parsed_value = []
        
        while len(tmp_value_parsed) > 0:
            value_to_parse = tmp_value_parsed
            tmp_value_parsed = []
            
            for v in value_to_parse:
                if type(v) == str or type(v) == unicode:
                    v = split(v)

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
