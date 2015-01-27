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

from pyshell.command.exception import *
from pyshell.arg.exception     import *
from pyshell.utils.parameter   import ParameterManagerV3
from pyshell.utils.exception   import ListOfException, DefaultPyshellException, USER_WARNING, PARSE_ERROR
from pyshell.command.engine    import EMPTY_MAPPED_ARGS
from pyshell.utils.printing    import printException
from pyshell.utils.constants   import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.command.engine    import engineV3, EMPTY_MAPPED_ARGS
from pyshell.arg.argchecker    import defaultInstanceArgChecker, booleanValueArgChecker
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
    #move solver to solving.py
    #move execute to executing.py
    #finish to refactor addons/alias.py

    #finish the grammar then refactor the parsing system

    #keep track of running event and be able to kill one or all of them
        #manage it in alias object with a static list
            #an alias add itself in the list before to start then remove itself from the list at the end of its execution
            
    #create an addon "background" to
        #fire a command on background
            #like the '&' but the parsing of the command occur later
        #kill a command on background with an id
            #hard kill
            #light kill (stop on next command)
        #list all command executing on background

class Parser(list):
    "This object will parse a command line withou any resolution of process, argument, or parameter"
    
    #TODO
        #be able to escape '&'
    
    def __init__(self,string):
        
        if type(string) != str and type(string) != unicode:
            raise DefaultPyshellException("fail to init parser object, a string was expected, got '"+str(type(string))+"'",PARSE_ERROR)
    
        list.__init__(self)
        self.currentToken    = None
        self.currentCommand  = []
        self.argSpotted      = []
        self.paramSpotted    = []
        self._innerParser    = self._parse
        self.string          = string
        self.escapeChar      = False
        self.runInBackground = False
        self.isParsed        = False
        self.wrapped         = False

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
            
                index = len(self.currentCommand) -1

                if index in self.argSpotted and (' ' in self.currentToken or len(self.currentToken) == 1):
                    self.argSpotted.remove(index)

                elif index in self.paramSpotted:
                    if (' ' in self.currentToken or len(self.currentToken) == 1):
                        self.paramSpotted.remove(index)
                    else:
                        try:
                            float(self.currentToken)
                            self.paramSpotted.remove(index)
                        except ValueError:
                            pass
            
            self.currentToken = None
            self.wrapped = False

    def _parse(self,char):
        if self.currentToken is None:
            if char in (' ','\t','\n','\r',):
                return
                
            if char == '|':
                self._pushCommandInList()
                return
                
            self.currentToken = ""

        if self.escapeChar:
            self.currentToken += char
            self.escapeChar    = False

        elif char == '\\':
            self.escapeChar    = True
        elif char == '"':
            self.wrapped = not self.wrapped
        elif not self.wrapped and char in (' ','|','\t','\n','\r',):
            self._pushTokenInCommand()
                
            if char == '|':
                self._pushCommandInList()
        elif char == '$' and len(self.currentToken) == 0:
            self.argSpotted.append(len(self.currentCommand))
            self.currentToken += char
        elif char == '-' and len(self.currentToken) == 0:
            self.paramSpotted.append(len(self.currentCommand))
            self.currentToken += char
        else:
            self.currentToken += char

    def parse(self):
        del self[:]
    
        self.string = self.string.strip(' \t\n\r')
        
        if len(self.string) == 0:
            return
                
        for i in xrange(0,len(self.string)):
            char = self.string[i]
            self._parse(char)    
            
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
            
    def isToRunInBackground(self):
        return self.runInBackground
        
    def isParsed(self):
        return 

class Solver(object):
    def __init__(self, parser, mltries, variablesContainer):
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
        self.isSolved           = False
            
    def solve(self):
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
            
        self.isSolved = True #TODO not really needed if nothing is stored about the parsing...
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

                #print tokenList, argIndex, varSize, values
                #tokenList[argIndex:argIndex+varSize-1] = values #TODO bug, does not insert, replace value
                #print tokenList
            
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

#TODO 
    #deploy in executer and alias
    #why do we still need to return ex and engine
        #does not have any sense in background mode

def execute(string, parameterContainer, processName=None, processArg=None):
    
    ## parsing ##
    parser = None
    try:
        #parsing
        if isinstance(string, Parser):
            parser = string
            
            if not parser.isParsed():
                parser.parse()
        else:
            parser = Parser(string)
            parser.parse()
            
        if len(parser) == 0:
            return None, None

    except Exception as ex:
        printException(ex)
        return ex, None

    if parser.isToRunInBackground():
        t = threading.Thread(None, _execute, None, (parser,parameterContainer,processName,processArg,))
        t.start()
        return None,None
    else:
        return _execute(parser,parameterContainer, processName, processArg)

def _execute(parser,parameterContainer, processName=None, processArg=None):    

    ## solving then execute ##
    ex     = None
    engine = None
    try:        
        parameterContainer.pushVariableLevelForThisThread()
        
        if processArg is not None: 
            #TODO PROBABLY BUG... if it is a alias, the call of the inner command will call another push and these local variable will not be available...
            #TODO BUG (?) script execution will cause a lot of this statement, why ?
                #check with the startup script
                   
            parameterContainer.variable.setParameter("*", VarParameter(' '.join(str(x) for x in processArg)), localParam = True) #all in one string
            parameterContainer.variable.setParameter("#", VarParameter(len(processArg)), localParam = True)                      #arg count
            parameterContainer.variable.setParameter("@", VarParameter(processArg), localParam = True)                            #all args
            #TODO parameterContainer.variable.setParameter("?", VarParameter(processArg, localParam = True)                            #value from last command
            #TODO parameterContainer.variable.setParameter("!", VarParameter(processArg, localParam = True)                            #last pid started in background
            parameterContainer.variable.setParameter("$", VarParameter(thread.get_ident()), localParam = True)                    #current process id #TODO id is not enought, need level
        
        #solve command, variable, and dashed parameters
        solver = Solver(parser, parameterContainer.environment.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY).getValue(), parameterContainer.variable)
        rawCommandList, rawArgList, mappedArgs = solver.solve()
        
        #clone command/alias to manage concurrency state
        newRawCommandList = []
        for c in rawCommandList:
            newRawCommandList.append(c.clone())

        #prepare an engine
        engine = engineV3(newRawCommandList, rawArgList, mappedArgs, parameterContainer)
        
        #execute 
        engine.execute()

    except executionInitException as ex:
        printException(ex,"Fail to init an execution object: ")
    except executionException as ex:
        printException(ex, "Fail to execute: ")
    except commandException as ex:
        printException(ex, "Error in command method: ")
    except engineInterruptionException as ex:
        if ex.abnormal:
            printException(ex, "Abnormal execution abort, reason: ")
        else:
            printException(ex, "Normal execution abort, reason: ")
    except argException as ex:
        printException(ex, "Error while parsing argument: ")
    except ListOfException as ex:
        printException(ex,"List of exception(s): ")
    except Exception as ex:
        printException(ex)
    finally:
        parameterContainer.popVariableLevelForThisThread()

    return ex, engine

