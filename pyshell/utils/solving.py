#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.arg.argchecker  import booleanValueArgChecker,defaultInstanceArgChecker
from pyshell.command.engine  import EMPTY_MAPPED_ARGS
from pyshell.utils.exception import DefaultPyshellException, SYSTEM_ERROR, USER_WARNING
from pyshell.utils.parameter import ParameterManagerV3
from pyshell.utils.parsing   import Parser
from tries                   import multiLevelTries

class Solver(object):
    def __init__(self):
        pass
            
    def solve(self, parser, mltries, variablesContainer):
        if not isinstance(parser, Parser):
            raise DefaultPyshellException("Fail to init solver, a parser object was expected, got '"+str(type(parser))+"'",SYSTEM_ERROR)
            
        if not parser.isParsed:
            raise DefaultPyshellException("Fail to init solver, parser object is not yet parsed",SYSTEM_ERROR)
            
        if not isinstance(variablesContainer,ParameterManagerV3):
            raise DefaultPyshellException("Fail to init solver, a ParameterManager object was expected, got '"+str(type(variablesContainer))+"'",SYSTEM_ERROR)
            
        if not isinstance(mltries, multiLevelTries):
            raise DefaultPyshellException("Fail to init solver, a multiLevelTries object was expected, got '"+str(type(mltries))+"'",SYSTEM_ERROR)
            
        self.parser             = parser
        self.mltries            = mltries
        self.variablesContainer = variablesContainer

        commandList    = []
        argList        = []
        mappedArgsList = []

        for tokenList, argSpotted, paramSpotted in self.parser:
            if len(paramSpotted) > 0:
                paramSpotted = list(paramSpotted)

            tokenList                        = self._solveVariables(tokenList,argSpotted,paramSpotted)
            command, remainingTokenList      = self._solveCommands(tokenList)
            
            _removeEveryIndexUnder(paramSpotted, len(tokenList) - len(remainingTokenList) )
            _addValueToIndex(paramSpotted, 0, len(remainingTokenList) - len(tokenList))
                                    
            mappedParams, remainingTokenList = self._solveDashedParameters(command, remainingTokenList, paramSpotted)
            
            commandList.append(    command            )
            argList.append(        remainingTokenList )
            mappedArgsList.append( mappedParams       )
            
        return commandList, argList, mappedArgsList
        
    def _solveVariables(self,tokenList,argSpotted, paramSpotted):
        "replace argument like `$toto` into their value in parameter, the input must come from the output of the method parseArgument"

        #no arg spotted
        if len(argSpotted) == 0:
            return tokenList

        tokenList = list(tokenList)
        indexCorrection = 0
        
        for argIndex in argSpotted:
            argIndex += indexCorrection
        
            #get the token and remove $
            stringToken = tokenList[argIndex][1:]

            #remove old key from token list
            del tokenList[argIndex]

            #if not existing var, act as an empty var
            if not self.variablesContainer.hasParameter(stringToken):
                varSize = 0
            else:
                #insert the var list at the correct place (var is always a list)
                values = self.variablesContainer.getParameter(stringToken).getValue()
                tokenList = tokenList[0:argIndex] + values + tokenList[argIndex:]
                varSize = len(values)
            
            #update every spotted param index with an index bigger than the var if the value of the var is different of 1
            if varSize != 1:
                indexCorrection += varSize-1
                _addValueToIndex(paramSpotted, argIndex+1, indexCorrection)
                
        return tokenList

    def _solveCommands(self, tokenList):
        "indentify command name and args from output of method parseArgument"

        #search the command with advanced seach
        searchResult = None
        try:
            searchResult = self.mltries.advancedSearch(tokenList, False)
        except triesException as te:
            raise DefaultPyshellException("failed to find the command '"+str(tokenList)+"', reason: "+str(te), USER_WARNING)
        
        #ambiguity on the last token used
        if searchResult.isAmbiguous():                    
            tokenIndex = len(searchResult.existingPath) - 1
            tries = searchResult.existingPath[tokenIndex][1].localTries
            keylist = tries.getKeyList(tokenList[tokenIndex])
            
            raise DefaultPyshellException("ambiguity on command '"+" ".join(tokenList)+"', token '"+str(tokenList[tokenIndex])+"', possible value: "+ ", ".join(keylist), USER_WARNING)
        
        #no value on the last token found OR no token found
        elif not searchResult.isAvalueOnTheLastTokenFound():
            if searchResult.getTokenFoundCount() == len(tokenList):
                raise DefaultPyshellException("uncomplete command '"+" ".join(tokenList)+"', type 'help "+" ".join(tokenList)+"' to get the next available parts of this command", USER_WARNING)
                
            if len(tokenList) == 1:
                raise DefaultPyshellException("unknown command '"+" ".join(tokenList)+"', type 'help' to get the list of commands", USER_WARNING)
                
            raise DefaultPyshellException("unknown command '"+" ".join(tokenList)+"', token '"+str(tokenList[searchResult.getTokenFoundCount()])+"' is unknown, type 'help' to get the list of commands", USER_WARNING)

        #return the command found and the not found token
        return searchResult.getLastTokenFoundValue(), list(searchResult.getNotFoundTokenList())
        
    def _solveDashedParameters(self, command, remainingTokenList, paramSpotted):
        #empty command list, nothing to map
        if len(command) == 0 or len(paramSpotted) == 0:
            return (EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS, ), remainingTokenList 

        #get multi-command entry command, the first command
        firstSingleCommand,useArgs,enabled = command[0]

        #extract arfeeder
        if (  (not hasattr(firstSingleCommand.preProcess, "isDefault") or not firstSingleCommand.preProcess.isDefault)) and hasattr(firstSingleCommand.preProcess, "checker"):
            feeder = firstSingleCommand.preProcess.checker
            indexToSet = 0
        elif ( (not hasattr(firstSingleCommand.process, "isDefault") or not firstSingleCommand.process.isDefault)) and hasattr(firstSingleCommand.process, "checker"):
            feeder = firstSingleCommand.process.checker
            indexToSet = 1
        elif ( (not hasattr(firstSingleCommand.postProcess, "isDefault") or not firstSingleCommand.postProcess.isDefault)) and hasattr(firstSingleCommand.postProcess, "checker"):
            feeder = firstSingleCommand.postProcess.checker
            indexToSet = 2
        else:
            return (EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS, ), remainingTokenList                

        #compute arg mapping for this command
        localMappedArgs = [EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS]
        paramFound, remainingArgs = _mapDashedParams(remainingTokenList, feeder.argTypeList,paramSpotted)
        localMappedArgs[indexToSet] = paramFound
        
        return localMappedArgs, remainingArgs
        
def _removeEveryIndexUnder(indexList, endIndex):
    for i in xrange(0,len(indexList)):
        if indexList[i] < endIndex:
            continue
        
        del indexList[:i]
        return

def _addValueToIndex(indexList, startingIndex, valueToAdd=1):
    for i in xrange(0,len(indexList)):
        if indexList[i] < startingIndex:
            continue
        
        indexList[i] += valueToAdd

def _mapDashedParams(inputArgs, argTypeMap,paramSpotted):  
    if len(paramSpotted) == 0:
        return {}, inputArgs
    
    notUsedArgs   = []
    paramFound    = {}
    
    currentName   = None
    currentParam  = None
    currentIndex  = 0 

    for index in paramSpotted:
        paramName = inputArgs[index][1:]
    
        #remove false param
        if paramName not in argTypeMap:
            continue
        
        #manage last met param
        if currentParam is not None:
            _mapDashedParamsManageParam(inputArgs, currentName, currentParam, currentIndex, paramFound, notUsedArgs, index)
        else:
            #base case, process the first param index, need to flush available arg before this index
            notUsedArgs.extend(inputArgs[0:index])
        
        currentName  = paramName
        currentParam = argTypeMap[paramName]
        currentIndex = index
    
    if currentParam is None:
        return {}, inputArgs
    
    #manage last param
    _mapDashedParamsManageParam(inputArgs, currentName, currentParam, currentIndex, paramFound, notUsedArgs, len(inputArgs))
    
    return paramFound,notUsedArgs
    
def _mapDashedParamsManageParam(inputArgs, currentName, currentParam, currentIndex, paramFound, notUsedArgs, lastIndex):
    argAvailableCount = lastIndex - currentIndex - 1

    #special case for boolean, parameter alone is equivalent to true
    if isinstance(currentParam, booleanValueArgChecker):
        if argAvailableCount == 0:
            paramFound[currentName] = ("true",)
        elif _isValidBooleanValueForChecker(inputArgs[currentIndex+1]):
            paramFound[currentName] = (inputArgs[currentIndex+1],)
            notUsedArgs.extend( inputArgs[currentIndex+2:lastIndex] )
        else:
            paramFound[currentName] = ("true",)
            notUsedArgs.extend( inputArgs[currentIndex+1:lastIndex] )
    else:
        #did we reach max size ?
        #don't care about minimum size, it will be check during execution phase
        if currentParam.maximumSize < argAvailableCount:
            paramFound[currentName] = tuple( inputArgs[currentIndex+1:currentIndex+1+currentParam.maximumSize] )
            notUsedArgs.extend(inputArgs[currentIndex+1+currentParam.maximumSize:lastIndex])
        else:
            paramFound[currentName] = tuple( inputArgs[currentIndex+1:lastIndex] )

def _isValidBooleanValueForChecker(value):
    try:
        defaultInstanceArgChecker.getbooleanValueArgCheckerInstance().getValue(value)
        return True
    except Exception:
        return False
