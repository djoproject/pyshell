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
    #don't save property that still have default value
        #do it in addon/parameter

    #get/set readonly/transient/removable/...  update call in software
    #update env/con constructor everywhere

from pyshell.utils.exception import ParameterException
from pyshell.utils.valuable  import Valuable, SelectableValuable
from pyshell.system.container import DEFAULT_DUMMY_PARAMETER_CONTAINER, AbstractParameterContainer
from pyshell.utils.constants import ORIGIN_PROCESS
from pyshell.utils.flushable import Flushable
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
    
    path = stringPath.split(".")
    finalPath = []

    for index in xrange(0, len(path)):
        if len(path[index]) == 0:
            continue

        finalPath.append(path[index])

    return True, tuple(finalPath)

class ParameterManager(Flushable):                    
    def __init__(self, parent = None):
        self._internalLock  = Lock()
        self.mltries        = multiLevelTries() 
        self.threadLocalVar = {}                #hold the paths for the current level of the current thread
    
        if parent is None:
            self.parentContainer = DEFAULT_DUMMY_PARAMETER_CONTAINER
        else:
            if not isinstance(parent, AbstractParameterContainer):
                raise ParameterException("(ParameterManager) __init__, expect an instance of AbstractParameterContainer, got '"+str(type(parent))+"'")

            self.parentContainer = parent
    
    def _buildExistingPathFromError(self, wrongPath, advancedResult):
        pathToReturn = list(advancedResult.getFoundCompletePath())
        pathToReturn.extend(wrongPath[advancedResult.getTokenFoundCount():])
        return pathToReturn

    def _getAdvanceResult(self, methName, stringPath, raiseIfNotFound = True, raiseIfAmbiguous = True, perfectMatch = False):

        #prepare and check path
        state, result = isAValidStringPath(stringPath)

        if not state:
            raise ParameterException("(ParameterManager) "+str(methName)+", "+result)

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
    
    def getAllowedType(self):#XXX to override if needed
        return Parameter
    
    def isAnAllowedType(self,value): #XXX to override if needed
        return isinstance(value,self.getAllowedType()) and value.__class__.__name__ == self.getAllowedType().__name__ #second condition is to forbidde child class
    
    def generateNewGlobalSettings(self):
        return GlobalParameterSettings()

    def generateNewLocalSettings(self):
        return LocalParameterSettings()

    def isDefaultSettings(self,value):
        return value is DEFAULT_LOCAL_PARAMETER_SETTINGS

    def extractParameter(self, value):
        if self.isAnAllowedType(value):
            return value
                
        if isinstance(value, Parameter):
            raise ParameterException("(ParameterManager) extractParameter, can not use an object of type '"+str(type(value))+"' in this manager")
            
        return self.getAllowedType()(value) #try to instanciate parameter, may raise if invalid type
    
    @synchronous()
    def setParameter(self,stringPath, param, localParam = True):
        param = self.extractParameter(param)

        if not self.isDefaultSettings(param.settings):
            if localParam:
                if not isinstance(param.settings,LocalParameterSettings) or isinstance(param.settings,GlobalParameterSettings):
                    raise ParameterException("(ParameterManager) setParameter, expect a parameter with LocalParameterSettings settings, got '"+str(type(param.settings))+"'")
            else:
                if not isinstance(param.settings,GlobalParameterSettings):
                    raise ParameterException("(ParameterManager) setParameter, expect a parameter with GlobalParameterSettings settings, got '"+str(type(param.settings))+"'")

        #check safety and existing
        advancedResult = self._getAdvanceResult("setParameter",stringPath, False, False, True)
        if advancedResult.isValueFound():
            (global_var, local_var, ) = advancedResult.getValue()
            
            if localParam:
                key            = self.parentContainer.getCurrentId()
                param.lockable = False #this parameter will be only used in a single thread, no more need to lock it

                if key in local_var:
                    if local_var[key].isReadOnly():
                        raise ParameterException("(ParameterManager) setParameter, can not set the parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' because a parameter with this name already exist and is not editable")
                else:
                    if key not in self.threadLocalVar:
                        self.threadLocalVar[key] = set()

                    self.threadLocalVar[key].add( '.'.join(str(x) for x in advancedResult.getFoundCompletePath()) )

                if self.isDefaultSettings(param.settings):
                    param.settings = self.generateNewLocalSettings()

                local_var[key] = param
            else:
                if global_var is not None:
                    if global_var.isReadOnly():
                        raise ParameterException("(ParameterManager) setParameter, can not set the parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' because a parameter with this name already exist and is not editable")

                    previous_setting = global_var.settings
                else:
                    previous_setting = None

                if self.isDefaultSettings(param.settings):
                    param.settings = self.generateNewGlobalSettings()

                param.settings.mergeLoaderSet(previous_setting)
                param.settings.setOriginProvider(self.parentContainer)
                param.settings.updateOrigin()

                self.mltries.update( stringPath.split("."), (param, local_var, ) )
        else:
            local_var = {}
            if localParam:
                global_var     = None
                key            = self.parentContainer.getCurrentId()
                local_var[key] = param
                param.lockable = False #this parameter will be only used in a single thread, no more need to lock it #TODO should disappear

                if self.isDefaultSettings(param.settings):
                    param.settings = self.generateNewLocalSettings()

            else:
                global_var = param

                if self.isDefaultSettings(param.settings):
                    param.settings = self.generateNewGlobalSettings()

                param.settings.setOriginProvider(self.parentContainer)
                param.settings.updateOrigin()

            self.mltries.insert( stringPath.split("."), (global_var, local_var, ) )
        
        return param
            
    @synchronous()
    def getParameter(self, stringPath, perfectMatch = False, localParam = True, exploreOtherLevel=True):
        advancedResult = self._getAdvanceResult("getParameter",stringPath, perfectMatch=perfectMatch, raiseIfNotFound=False) #this call will raise if value not found or ambiguous
        
        if advancedResult.isValueFound():
            (global_var, local_var, ) = advancedResult.getValue()

            for case in xrange(0,2): #simple loop to explore the both statment of this condition if needed, without ordering
                if localParam:
                    key = self.parentContainer.getCurrentId()
                    if key in local_var:
                        return local_var[key]

                    if not exploreOtherLevel:
                        break
                else:
                    if global_var is not None:
                        return global_var

                    if not exploreOtherLevel:
                        break

                localParam = not localParam

        return None
    
    @synchronous()
    def hasParameter(self, stringPath, raiseIfAmbiguous = True, perfectMatch = False, localParam = True, exploreOtherLevel=True):
        advancedResult = self._getAdvanceResult("hasParameter",stringPath, False,raiseIfAmbiguous, perfectMatch) #this call will raise if ambiguous
        
        if advancedResult.isValueFound():
            (global_var, local_var, ) = advancedResult.getValue()

            for case in xrange(0,2): #simple loop to explore the both statment of this condition if needed, without any order
                if localParam:
                    key = self.parentContainer.getCurrentId()

                    if key in local_var:
                        return True

                    if not exploreOtherLevel:
                        return False
                else:
                    if global_var is not None:
                        return True

                    if not exploreOtherLevel:
                        return False

                localParam = not localParam

        return False

    @synchronous()
    def unsetParameter(self, stringPath, localParam = True, exploreOtherLevel=True, force=False):
        advancedResult = self._getAdvanceResult("unsetParameter", stringPath, perfectMatch=True) #this call will raise if value not found or ambiguous
        
        if advancedResult.isValueFound():
            (global_var, local_var, ) = advancedResult.getValue()
            for case in xrange(0,2): #simple loop to explore the both statment of this condition if needed, without any order
                if localParam:
                    key = self.parentContainer.getCurrentId()  

                    if key not in local_var:
                        if not exploreOtherLevel:
                            raise ParameterException("(ParameterManager) unsetParameter, unknown local parameter '"+" ".join(advancedResult.getFoundCompletePath())+"'")
                        
                        localParam = not localParam
                        continue
                    
                    if not force:
                        if not local_var[key].isRemovable():
                            raise ParameterException("(ParameterManager) unsetParameter, local parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' is not removable")
                    
                    if len(local_var) == 1 and global_var is None:
                        self.mltries.remove( advancedResult.getFoundCompletePath() )
                    else:
                        del local_var[key]

                    #remove from thread local list
                    self.threadLocalVar[key].remove('.'.join(str(x) for x in advancedResult.getFoundCompletePath()))
                    if len(self.threadLocalVar[key]) == 0:
                        del self.threadLocalVar[key]
                        
                    return

                else:
                    if global_var is None:
                        if not exploreOtherLevel:
                            raise ParameterException("(ParameterManager) unsetParameter, unknown global parameter '"+" ".join(advancedResult.getFoundCompletePath())+"'")
                        
                        localParam = not localParam
                        continue

                    if not force:
                        if not global_var.isRemovable():
                            raise ParameterException("(ParameterManager) unsetParameter, parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' is not removable")
                    
                        if hasattr(global_var.settings, "loaderSet") and global_var.settings.loaderSet is not None and len(global_var.settings.loaderSet) > 0:
                            raise ParameterException("(ParameterManager) unsetParameter, parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' can be removed, at least on loader is registered on this parameter")

                    if len(local_var) == 0:
                        self.mltries.remove( advancedResult.getFoundCompletePath() )
                        
                    return
                        
    @synchronous()    
    def flush(self): #flush the Variable at this Level For This Thread
        key = self.parentContainer.getCurrentId()

        #clean level
        if key in self.threadLocalVar: #do we have recorded some variables for this thread at this level ?
            for path in self.threadLocalVar[key]: #no error possible, missing value or invalid type is possible here, because of the process in set/unset
                advancedResult = self._getAdvanceResult("popVariableLevelForThisThread",path, False, False)
                (global_var_value, local_var_dic,) = advancedResult.getValue()
                del local_var_dic[key]
                    
                if global_var_value is None and len(local_var_dic) == 0:
                    mltries.remove( path ) #can not raise, because every path exist

            del self.threadLocalVar[key]
    
    @synchronous()
    def buildDictionnary(self, stringPath, localParam = True, exploreOtherLevel=True):
        state, result = isAValidStringPath(stringPath)
        
        if not state:
            raise ParameterException("(ParameterManager) buildDictionnary, "+result)
        
        result = self.mltries.buildDictionnary(result, True, True, False)
        
        to_ret = {}
        key = None
        
        for var_key, (global_var, local_var) in result.items():
            localParam_tmp = localParam
            for case in xrange(0,2): #simple loop to explore the both statment of this condition if needed, without any order
                if localParam_tmp:
                    if key is None:
                        key = self.parentContainer.getCurrentId()
                        
                    if key in local_var:
                        to_ret[var_key] = local_var[key]
                        break
                        
                    if not exploreOtherLevel:
                        break
                else:
                    if global_var is not None:
                        to_ret[var_key] = global_var
                        break
                        
                    if not exploreOtherLevel:
                        break
                    
                localParam_tmp = not localParam_tmp
        
        return to_ret

class Parameter(Valuable): #abstract
    def __init__(self, transient = False):
        pass

    def getValue(self):
        pass #TO OVERRIDE

    def setValue(self,value):
        pass #TO OVERRIDE

    def __str__(self):
        return str(self.getValue())

    def __repr__(self):
        return str(self.getValue())

    def getProperties(self):
        return ()
        
class LocalParameterSettings(object):
    def __init__(self):
        self.readOnly  = False
        self.removable = True

    def setTransient(self,state):
        pass

    def isTransient(self):
        return True

    def setReadOnly(self, state):
        if type(state) != bool:
            raise ParameterException("(EnvironmentParameter) setReadOnly, expected a bool type as state, got '"+str(type(state))+"'") #TODO
            
        self.readOnly = state
        self.updateOrigin()

    def isReadOnly(self):
        return self.readOnly

    def _raiseIfReadOnly(self, methName = None):
        if self.isReadOnly():
            if methName is not None:
                methName = " "+methName+", "
            else:
                methName = ""
                
            raise ParameterException("("+self.__class__.__name__+") "+methName+"read only parameter") #TODO no more current class but parent class

    def setRemovable(self, state):
        self._raiseIfReadOnly("setRemovable")
    
        if type(state) != bool:
            raise ParameterException("(EnvironmentParameter) setRemovable, expected a bool type as state, got '"+str(type(state))+"'") #TODO
            
        self.removable = state
        self.updateOrigin()

    def isRemovable(self):
        return self.removable

    def setOriginProvider(self, provider):
        pass

    def updateOrigin(self):
        pass

    def addLoader(self, loaderSignature):
        pass

    def mergeLoaderSet(self, parameter):
        pass

    def getProperties(self):
        return ( ("removable", self.isRemovable(), ), ("readonly", self.isReadOnly(), ), ) 

DEFAULT_LOCAL_PARAMETER_SETTINGS = LocalParameterSettings() #TODO should be immutable

class GlobalParameterSettings(LocalParameterSettings):
    def __init__(self):
        LocalParameterSettings.__init__(self)
        self.transient = True
        self.originProvider = None
        self.origin = ORIGIN_PROCESS
        self.originArg = None
        self.loaderSet = None

    def setTransient(self,state):
        if type(state) != bool:
            raise ParameterException("(GlobalParameterSettings) setTransient, expected a bool type as state, got '"+str(type(state))+"'")
            
        self.transient = state
        self.updateOrigin()

    def isTransient(self):
        return self.transient

    def setOriginProvider(self, provider):
        if provider is not None and not isinstance(provider, AbstractParameterContainer):
            raise ParameterException("(GlobalParameterSettings) setOriginProvider, an AbstractParameterContainer object was expected, got '"+str(type(provider))+"'") 
        
        self.originProvider = provider
        
    def updateOrigin(self):
        if self.originProvider == None:
            self.origin = ORIGIN_PROCESS
            self.originArg = None
        else:
            self.origin, self.originArg = self.originProvider.getOrigin()

    def addLoader(self, loaderSignature):
        if self.loaderSet is None:
            self.loaderSet = set()
            
        self.loaderSet.add(loaderSignature)
        
    def mergeLoaderSet(self, parameterSettings):
        if not isinstance(parameterSettings, ParameterSettings):
            raise ParameterException("(GlobalParameterSettings) mergeLoaderSet, an ParameterSettings object was expected, got '"+str(type(parameterSettings))+"'") 
            
        if self.loaderSet is None:
            if parameterSettings.loaderSet is not None:
                self.loaderSet = set(parameterSettings.loaderSet)
        elif parameterSettings.loaderSet is not None:
            self.loaderSet = self.loaderSet.union(parameterSettings.loaderSet)
            
