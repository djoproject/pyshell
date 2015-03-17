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
    #what about globalSettings if we try to add in local
        #forbidde that, because it will enable a Lock for this local parameter

## internal modules ##
from pyshell.utils.exception  import ParameterException
from pyshell.utils.flushable  import Flushable
from pyshell.utils.valuable   import Valuable
from pyshell.system.container import AbstractParameterContainer, DEFAULT_DUMMY_PARAMETER_CONTAINER

## external modules ##
from functools import wraps
from threading import Lock
from tries     import multiLevelTries

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
    
    def extractParameter(self, value):
        if self.isAnAllowedType(value):
            return value
                
        if isinstance(value, Parameter):
            raise ParameterException("(ParameterManager) extractParameter, can not use an object of type '"+str(type(value))+"' in this manager")
            
        return self.getAllowedType()(value) #try to instanciate parameter, may raise if invalid type
    
    @synchronous()
    def setParameter(self,stringPath, param, localParam = True):
        param = self.extractParameter(param)

        #check safety and existing
        advancedResult = self._getAdvanceResult("setParameter",stringPath, False, False, True)
        if advancedResult.isValueFound():
            (global_var, local_var, ) = advancedResult.getValue()
            
            if localParam:
                key            = self.parentContainer.getCurrentId()

                if key in local_var:
                    if local_var[key].isReadOnly():
                        raise ParameterException("(ParameterManager) setParameter, can not set the parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' because a parameter with this name already exist and is not editable")
                else:
                    if key not in self.threadLocalVar:
                        self.threadLocalVar[key] = set()

                    self.threadLocalVar[key].add( '.'.join(str(x) for x in advancedResult.getFoundCompletePath()) )

                local_var[key] = param
            else:
                if global_var is not None:
                    if global_var.isReadOnly():
                        raise ParameterException("(ParameterManager) setParameter, can not set the parameter '"+" ".join(advancedResult.getFoundCompletePath())+"' because a parameter with this name already exist and is not editable")

                    previous_setting = global_var.settings
                else:
                    previous_setting = None

                param.enableGlobal()
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
            else:
                global_var = param
                param.enableGlobal()
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
                    
                        loaderSet = global_var.settings.getLoaderSet()
                        if loaderSet is not None and len(loaderSet) > 0:
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

    def enableGlobal(self):
        pass

    def getProperties(self):
        return ()
            
