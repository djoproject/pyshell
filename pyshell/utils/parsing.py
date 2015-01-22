#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject,net>

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

from pyshell.utils.parameter import ParameterManagerV3
from pyshell.utils.exception import DefaultPyshellException, USER_WARNING
from pyshell.command.engine  import EMPTY_MAPPED_ARGS
from tries import multiLevelTries


#BNF GRAMMAR OF A COMMAND
# 
## RULE 1 ## <commands>  ::= <command> <threading> <EOL> | <command> "|" <commands>
## RULE 2 ## <threading> ::= " &" | ""
## RULE 3 ## <command>   ::= <token> | <token> " " <command>
## RULE 4 ## <token>     ::= <string> | "$" <string> | "\$" <string> | "-" <text> | "-" <text> <string> | "\-" <string>
## RULE 5 ## <string>    ::= <text> | <text> "\ " <string> #TODO conflict with command rule
#
#

#TODO

    #finish the grammar then refactor the parsing system

    #firing/executing system
        #for piped command
            #with a "&" at the end of a script line DONE
            #with a "fire" at the beginning of a script line TODO create a command to do it, it should be easy

    #keep track of running event and be able to kill one or all of them
        #manage it in alias object with a static list
            #an alias add itself in the list before to start then remove itself from the list at the end of its execution
            
    #create an addon "background" to
        #fire a command on background
        #kill a command on background with an id
            #hard kill
            #light kill (stop on next command)
        #list all command executing on background

class Parser(list):
    "This object will parse a command line withou any resolution of process, argument, or parameter"
    
    #TODO
        #remove $ char if var spotted
        #if $ alone, not a var
        #if $ is followed by escape char, not a var
        
        #remove '-' on spotted parameter
        #if - alone, not a parameter
        
        #be able to escape '&'
    
    def __init__(self,string):
        list.__init__(self)
        self.currentToken    = None
        self.currentCommand  = []
        self.argSpotted      = []
        self.paramSpotted    = []
        self._innerParser    = self._subParseNoToken
        self.string          = string
        self.escapeChar      = False
        self.runInBackground = False
        self.isParsed        = False

    def _pushCommandInList(self):
        if len(self.currentCommand) > 0:
            self.append(  (tuple(self.currentCommand),tuple(self.argSpotted),tuple(self.paramSpotted),)  )
            del self.currentCommand[:]
            del self.argSpotted[:]
            del self.paramSpotted[:]
    
    def _pushTokenInCommand(self):
        if self.currentToken is not None:
            if len(self.currentToken) > 0:
                self.currentCommand.append(self.currentToken)
            
            self.currentToken = None
            self._innerParser = self._subParseNoToken

    def _subParseNoToken(self,char):
        if char in (' ','\t','\n','\r',):
            return
            
        if char == '|':
            self._pushCommandInList()
            return
            
        self.currentToken = ""
        
        if char == '"':
            self._innerParser = self._subParseWrappedToken
            return
            
        self._innerParser = self._subParseToken

        if char == '\\':
            self.escapeChar = True
            return
            
        if char == '$':
            argSpotted.append(len(currentCommand))
        elif char == '-':
            paramSpotted.append(len(currentCommand))
            
        self.currentToken += char
        
    def _subParseWrappedToken(self,char):
        if self.escapeChar:
            self.currentToken += char
            self.escapeChar    = False
            return
    
        if char == '\\':
            self.escapeChar = True
        elif char == '"':
            self._innerParser = self._subParseWrappedTokenEnd
        else:
            self.currentToken += char
            
    def _subParseWrappedTokenEnd(self, char):
        if char in (' ','|','\t','\n','\r',):
            self._pushTokenInCommand()
            self._innerParser = self._subParseNoToken
            self._subParseNoToken(char)
        else:
            self._innerParser = self._subParseToken
            self._subParseToken(char)
        
    def _subParseToken(self,char):
        if self.escapeChar:
            self.currentToken += char
            self.escapeChar    = False
            return
            
        if char == '\\':
            self.escapeChar    = True
        elif char == '"':
            self._innerParser = self._subParseWrappedToken
        elif char in (' ','|','\t','\n','\r',):
            self._pushTokenInCommand()
                
            if char == '|':
                self._pushCommandInList()
        else:
            self.currentToken += char

    def parse(self):
        del self[:]
    
        if self.string is None:
            return
            
        if type(self.string) != str and type(self.string) != unicode:
            pass #TODO raise
            
        self.string = self.string.strip(' \t\n\r')
        
        if len(self.string) == 0:
            return
                
        for i in xrange(0,len(self.string)):
            char = self.string[i]
            self._innerParser(char)    
            
        #push intermediate data
        self._pushTokenInCommand()
        self._pushCommandInList()
        
        #compute runInBackground
        if len(self) > 0:
            if self[-1][0][-1] == '&':
                self.runInBackground = True
                del self[-1][0][-1]
            elif self[-1][0][-1][-1] == '&':
                self.runInBackground = True
                self[-1][0][-1] = self[-1][0][-1][:-1]
                
        self.isParsed = True
            
    def isToExecuteInAnotherThread(self):
        return self.runInBackground
        
    def isParsed(self):
        return 

class Solver(list):
    def __init__(self, parser, mltries, variablesContainer):
        if not isinstance(parser, Parser):
            pass #TODO raise
            
        if not self.isParsed:
            pass #TODO raise
            
        if not isinstance(variablesContainer,ParameterManagerV3):
            pass #TODO raise
            
        if not isinstance(mltries, multiLevelTries):
            pass #TODO raise
            
        self.parser             = parser
        self.mltries            = mltries
        self.variablesContainer = variablesContainer
        self.isSolved           = False
            
    def solve(self):
        for tokenList, argSpotted, paramSpotted in self.parser:
    
            tokenList                        = self._solveVariables(tokenList,argSpotted,paramSpotted)
            command, remainingTokenList      = self._solveCommands(tokenList)
            
            _removeEveryIndexUnder(paramSpotted, len(tokenList) - len(remainingTokenList) )
            _addValueToIndex(paramSpotted, 0, len(remainingTokenList) - len(tokenList))
                                    
            mappedParams, remainingTokenList = self._solveDashedParameters(command, remainingTokenList, paramSpotted)
            
            self.append( (command, mappedParams, remainingTokenList) )
            
        self.isSolved = True
        
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
                varSize = len(values)
                tokenList[argIndex:argIndex] =  varSize
            
            #update every spotted param index with an index bigger than the var if the value of the var is different of 1
            if varSize != 1:
                indexCorrection += varSize-1
                _addValueToIndex(paramSpotted, argIndex+1, indexCorrection)
                
        return tuple(tokenList)

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
        return searchResult.getLastTokenFoundValue(), tuple(searchResult.getNotFoundTokenList())
        
    def _solveDashedParameters(self, command, remainingTokenList, paramSpotted):
        #empty command list, nothing to map
        if len(command) == 0 or len(paramSpotted) == 0:
            return (EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS, ), remainingTokenList 

        #get multi-command entry command, the first command
        firstSingleCommand,useArgs,enabled = command[0]

        #extract arfeeder
        if ( not (hasattr(firstSingleCommand.preProcess, "isDefault") or not firstSingleCommand.preProcess.isDefault)) and hasattr(firstSingleCommand.preProcess, "checker"):
            feeder = firstSingleCommand.preProcess.checker
            indexToSet = 0
        elif (not (hasattr(firstSingleCommand.process, "isDefault") or not firstSingleCommand.process.isDefault)) and hasattr(firstSingleCommand.process, "checker"):
            feeder = firstSingleCommand.process.checker
            indexToSet = 1
        elif (not (hasattr(firstSingleCommand.postProcess, "isDefault") or not firstSingleCommand.postProcess.isDefault)) and hasattr(firstSingleCommand.postProcess, "checker"):
            feeder = firstSingleCommand.postProcess.checker
            indexToSet = 2
        else:
            return (EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS, ), remainingTokenList                

        #compute arg mapping for this command
        localMappedArgs = [EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS]
        paramFound, remainingArgs = _parseDashedParams(remainingTokenList, feeder.argTypeList,paramSpotted)
        localMappedArgs[indexToSet] = paramFound
        
        return tuple(localMappedArgs), tuple(localMappedArgs)

def _removeEveryIndexUnder(indexList, endIndex):
    for i in xrange(0,indexList):
        if indexList[i] < startingIndex:
            continue
        
        del indexList[:i]
        return

def _addValueToIndex(indexList, startingIndex, valueToAdd=1):
    for i in xrange(0,indexList):
        if indexList[i] < startingIndex:
            continue
        
        indexList[i] += valueToAdd

def _mapDashedParams(inputArgs, argTypeList,paramSpotted):
    
    #TODO remove false param

    for index in paramSpotted:
        #TODO param is bool ?
            #first token is a valid bool ?
        
        #TODO param has a max size ?
            #grab token until next param
    
        #TODO param has a min size ?
            #enought of token ?
                #if no, raise, or collect error
        
        #TODO where is the next param ?
            #do not forget to pipe the not used args
    
        pass #TODO
    
    
def _mapDashedParamsOLD(inputArgs, argTypeList,paramSpotted): #deprecated    
    ## init ##
    paramFound           = {} #map of found parameter with their values
    remainingArgs        = [] #list of args not used by any params
    whereToStore         = [] #temporary list of arg that will be used by the current parameter found
    
    lastParamFoundName    = None
    lastParamFoundChecker = None

    ## main loop ##
    for i in xrange(0, len(inputArgs)):
        
        ## CASE 1: a parameter was found and we reach the maximal amount of arg for this one ##
        if lastParamFoundChecker != None and lastParamFoundChecker.maximumSize != None and len(whereToStore) == lastParamFoundChecker.maximumSize:
            #no need to check booleanchecker, whereToStore is not empty if the code reach this stateent with booleanchecker
            
            if isinstance(lastParamFoundChecker, booleanValueArgChecker):
                if not _isValidBooleanValueForChecker(whereToStore[0]):
                    remainingArgs.append(whereToStore[0])
                    whereToStore = ("true",)

            paramFound[lastParamFoundName] = tuple(whereToStore)
            lastParamFoundChecker = lastParamFoundName = None
            whereToStore = []
    
        ## filtering the non candidate ##
        
        #STEP 1: is there a combination of escaping char at the beginning \-
        if inputArgs[i].startswith("\\-"):
            whereToStore.append(inputArgs[i][1:])
            continue
        
        #STEP 2: the string does not start with a dash
        if not inputArgs[i].startswith("-"):
            whereToStore.append(inputArgs[i])
            continue
        
        #STEP 3: is it a single dash ?
        if inputArgs[i] == "-":
            whereToStore.append("-")
            continue

        #STEP 4: is it a number ?
        try:
            float(inputArgs[i])
            whereToStore.append(inputArgs[i])
            continue
        except ValueError:
            pass
            
        #remove the dash
        paramName = inputArgs[i][1:]

        #not a param key, manage it like a string
        if paramName not in argTypeList:
            whereToStore.append(inputArgs[i])
            continue

        ## CASE 2: a new params is found, need to process the previous if exists ##
        if lastParamFoundChecker != None:
            if isinstance(lastParamFoundChecker, booleanValueArgChecker):
                if len(whereToStore) == 0:
                    whereToStore.append("true")
                else:
                    if not _isValidBooleanValueForChecker(whereToStore[0]):
                        remainingArgs.append(whereToStore[0])
                        whereToStore = ("true",)

            paramFound[lastParamFoundName] = tuple(whereToStore)
            lastParamFoundChecker = lastParamFoundName = None
        else:
            remainingArgs.extend(whereToStore)

        whereToStore = []
        argChecker   = argTypeList[paramName]
        
        #does not continue care about empty params (like engine, params, ...)
        if argTypeList[paramName].maximumSize == 0:
            continue
        
        lastParamFoundChecker = argChecker
        lastParamFoundName    = paramName

    ## CASE 3: mananage last checker found if exists ##
    if lastParamFoundChecker != None:
        if isinstance(lastParamFoundChecker, booleanValueArgChecker):
            if len(whereToStore) == 0:
                whereToStore.append("true")
            else:
                if not _isValidBooleanValueForChecker(whereToStore[0]):
                    remainingArgs.append(whereToStore[0])
                    whereToStore = ("true",)

        paramFound[lastParamFoundName] = tuple(whereToStore)
    else:
        remainingArgs.extend(whereToStore)

    return paramFound, remainingArgs
    
class Executer(object):
    def __init__(self,solver,runInBackground = False):
        pass #TODO
        
    def execute(self):
        pass #TODO

