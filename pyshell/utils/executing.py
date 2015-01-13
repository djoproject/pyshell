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

#BNF GRAMMAR OF A COMMAND
# 
## RULE 1 ## <commands>  ::= <command> <threading> <EOL> | <command> "|" <commands>
## RULE 2 ## <threading> ::= " &" | ""
## RULE 3 ## <command>   ::= <token> | <token> " " <command>
## RULE 4 ## <token>     ::= <string> | "$" <string> | "\$" <string> | "-" <text> | "-" <text> <string> | "\-" <string>
## RULE 5 ## <string>    ::= <text> | <text> "\ " <string> #TODO conflict with command rule
#
#

from pyshell.utils.exception   import *
from pyshell.command.exception import *
from pyshell.arg.exception     import *
from pyshell.arg.argchecker    import booleanValueArgChecker, defaultInstanceArgChecker
from pyshell.utils.constants   import DEBUG_ENVIRONMENT_NAME, ENVIRONMENT_TAB_SIZE_KEY, ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.printing    import warning, error, printException
from pyshell.utils.parameter   import VarParameter
from pyshell.command.engine    import engineV3, EMPTY_MAPPED_ARGS
from tries.exception import triesException
#from shlex import split
import sys, threading, thread

if sys.version_info[0] < 2 or (sys.version_info[0] < 3 and sys.version_info[0] < 7):
    from pyshell.utils.ordereddict import OrderedDict #TODO get from pipy, so the path will change
else:
    from collections import OrderedDict 

#TODO
    #finish the grammar then refactor the parsing system

    #refactore parsing method, see 
        #manage space escape like ‘\ ‘
        #manage "&"

    #firing/executing system
        #for piped command
            #with a "&" at the end of a script line
            #with a "fire" at the beginning of a script line

        #with only an alias name
            #with one of the two solution above
            #with a specific command from alias addon 

    #keep track of running event and be able to kill one or all of them
        #manage it in alias object with a static list
            #an alias add itself in the list before to start then remove itself from the list at the end of its execution

class Parser(object):
    #TODO
        #exclusion char //
        
        #two mode
            #1) only check grammar
            #2) check grammar + bind args + bind command
                #what about parameter binding ?

    def __init__(self,string):
        self.currentToken   = None
        self.currentCommand = []
        self.commandList    = []
        self.argSpotted     = []
        self.paramSpotted   = []
        self._innerParser   = self._subParseNoToken
        self.string = string
        
    def _subParseNoToken(self,char):
        if char == ' ':
            return
            
        if char == '|':
            if len(self.currentCommand) > 0:
                self.commandList.append(self.currentCommand)
                self.currentCommand = []
                
            return
            
        self.currentToken = ""
        
        if char == '"':
            self._innerParser = self._subParseWrappedToken
            return
            
        self._innerParser = self._subParseToken
        self.currentToken += char
        
        if char == '$':
            argSpotted.append(len(currentCommand))
        elif char == '-':
            paramSpotted.append(len(currentCommand))
        
    def _subParseWrappedToken(self,char):
        if char == '"':
            currentCommand.append(currentToken)
            currentToken = None
            self._innerParser = self._subParseNoToken
        else:
            self.currentToken += char
        
    def _subParseToken(self,char):
        if char == ' ' or char == '|':
            self.currentCommand.append(self.currentToken)
            self.currentToken = None
            self._innerParser = self._subParseNoToken
            
            if char == '|':
                commandList.append(currentCommand)
                currentCommand = []
        else:
            self.currentToken += char

    def parse(self):
        if self.string is None:
            return
            
        if type(self.string) != str and type(self.string) != unicode:
            pass #raise
            
        self.string = self.string.strip(' \t\n\r')
        
        if len(self.string) == 0:
            return
                
        for i in xrange(0,len(self.string)):
            char = self.string[i]
            self._innerParser(char)    
            
        if self.currentToken is not None:
            self.currentCommand.append(self.currentToken)
            self.currentToken = None
            
        if len(self.currentCommand) > 0:
            self.commandList.append(self.currentCommand)
            self.currentCommand = []

def _isValidBooleanValueForChecker(value):
    try:
        defaultInstanceArgChecker.getbooleanValueArgCheckerInstance().getValue(value)
        return True
    except Exception:
        return False

def parseDashedParams(inputArgs, argTypeList, prefix= "-", exclusion = "\\"):
    paramFound           = {}
    remainingArgs        = []
    whereToStore         = []
    
    lastParamFoundName    = None
    lastParamFoundChecker = None

    for i in xrange(0, len(inputArgs)):
        ### manage parameter ###
        if lastParamFoundChecker != None and lastParamFoundChecker.maximumSize != None and len(whereToStore) == lastParamFoundChecker.maximumSize:
            #no need to check booleanchecker, whereToStore is not empty if the code reach this stateent with booleanchecker
            
            if isinstance(lastParamFoundChecker, booleanValueArgChecker):
                if not _isValidBooleanValueForChecker(whereToStore[0]):
                    remainingArgs.append(whereToStore[0])
                    whereToStore = ("true",)

            paramFound[lastParamFoundName] = tuple(whereToStore)
            lastParamFoundChecker = lastParamFoundName = None
            whereToStore = []
    
        ### standard management ###
        #exclusion character
        if inputArgs[i].startswith(exclusion + prefix):
            whereToStore.append(inputArgs[i][len(exclusion):])
            continue
        
        #not a param token
        if not inputArgs[i].startswith(prefix):
            whereToStore.append(inputArgs[i])
            continue

        paramName = inputArgs[i][len(prefix):]

        #prefix string only
        if len(paramName) == 0:
            whereToStore.append(prefix)
            continue
        
        #is it a negative number ?
        number = True
        try:
            float(inputArgs[i])
        except ValueError:
            number = False
            
        if number:
            whereToStore.append(inputArgs[i])
            continue

        #not a param key, manage it like a string
        if paramName not in argTypeList:
            whereToStore.append(inputArgs[i])
            continue

        ### params token found ###
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

def preParseNotPipedCommand(line):
    "parse line that looks like 'aaa bbb ccc'"

    #remove blank char at the ends
    #print "BEFORE", "<"+str(line)+">"
    line = line.strip(' \t\n\r')
    #print "AFTER", "<"+str(line)+">"

    if len(line) == 0:
        return ()

    #split on space
    line = line.split(" ")

    #fo each token
    parsedLine = []
    for token in line:

        #clean token
        clearedToken = token.strip(' \t\n\r')

        #remove empty token
        if len(clearedToken) == 0:
            continue

        parsedLine.append(clearedToken)

    return parsedLine

def preParseLine(line):
    "parse line that looks like 'aaa bbb ccc | ddd eee fff | ggg hhh iii'"

    line = line.split("|")
    toret = []
    
    for partline in line:
        finalCmd = preParseNotPipedCommand(partline)

        #remove empty command
        if len(finalCmd) == 0:
            continue

        toret.append(finalCmd)

    return toret

def parseArgument(preParsedCmd, params, commandName = None):#, commandArg = None):
    "replace argument like `$toto` into their value in parameter, the input must come from the output of the method parseArgument"

    parsedCmd = []
    unknowVarError = set()

    for rawCmd in preParsedCmd:
        newRawCmd = []

        for stringToken in rawCmd:

            if stringToken.startswith("$") and len(stringToken) > 1:
                #remove $
                stringToken = stringToken[1:]

                if not params.variable.hasParameter(stringToken):                    
                    unknowVarError.add("Unknown var '"+stringToken+"'")
                    continue
                
                else:
                    param = params.variable.getParameter(stringToken)
                    
                    #because it is a VarParameter, it is always a list type
                    newRawCmd.extend(param.getValue())   
                
            elif stringToken.startswith("\$"):
                #remove "\"
                newRawCmd.append(stringToken[1:])

            else:
                newRawCmd.append(stringToken)

        parsedCmd.append(newRawCmd)

    if len(unknowVarError) > 0:
        toRaise = ListOfException()
        for uniqueError in unknowVarError:
            toRaise.addException( DefaultPyshellException(uniqueError, USER_WARNING) )

        raise toRaise

    return parsedCmd

def parseCommand(parsedCmd, mltries):
    "indentify command name and args from output of method parseArgument"

    ## look after command in tries ##
    rawCommandList = []   
    rawArgList     = []

    for finalCmd in parsedCmd:            
        #search the command with advanced seach
        searchResult = None
        try:
            searchResult = mltries.advancedSearch(finalCmd, False)
        except triesException as te:
            raise DefaultPyshellException("failed to find the command '"+str(finalCmd)+"', reason: "+str(te), USER_WARNING)
        
        if searchResult.isAmbiguous():                    
            tokenIndex = len(searchResult.existingPath) - 1
            tries = searchResult.existingPath[tokenIndex][1].localTries
            keylist = tries.getKeyList(finalCmd[tokenIndex])
            #print keylist, finalCmd[tokenIndex]
            
            raise DefaultPyshellException("ambiguity on command '"+" ".join(finalCmd)+"', token '"+str(finalCmd[tokenIndex])+"', possible value: "+ ", ".join(keylist), USER_WARNING)

        elif not searchResult.isAvalueOnTheLastTokenFound():
            if searchResult.getTokenFoundCount() == len(finalCmd):
                raise DefaultPyshellException("uncomplete command '"+" ".join(finalCmd)+"', type 'help "+" ".join(finalCmd)+"' to get the next available parts of this command", USER_WARNING)
                
            if len(finalCmd) == 1:
                raise DefaultPyshellException("unknown command '"+" ".join(finalCmd)+"', type 'help' to get the list of commands", USER_WARNING)
                
            raise DefaultPyshellException("unknown command '"+" ".join(finalCmd)+"', token '"+str(finalCmd[searchResult.getTokenFoundCount()])+"' is unknown, type 'help' to get the list of commands", USER_WARNING)

        #append in list
        rawCommandList.append(searchResult.getLastTokenFoundValue())
        rawArgList.append(searchResult.getNotFoundTokenList())
    
    return rawCommandList, rawArgList

def extractDashedParams(rawCommandList, rawArgList):
    newRawArgList = []
    mappedArgs = []
    for i in range(0, len(rawCommandList)):
        multiCmd = rawCommandList[i]

        #empty command list
        if len(multiCmd) == 0:
            continue

        #get multi-command entry command
        firstSingleCommand,useArgs,enabled = multiCmd[0]

        #extract arfeeder
        if ((hasattr(firstSingleCommand.preProcess, "isDefault") and firstSingleCommand.preProcess.isDefault)) or not hasattr(firstSingleCommand.preProcess, "checker"):
            if ((hasattr(firstSingleCommand.process, "isDefault") and firstSingleCommand.process.isDefault)) or not hasattr(firstSingleCommand.process, "checker"):
                if ((hasattr(firstSingleCommand.postProcess, "isDefault") and firstSingleCommand.postProcess.isDefault)) or not hasattr(firstSingleCommand.postProcess, "checker"):
                    mappedArgs.append( (EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS, ) )
                    newRawArgList.append( [] )
                    continue
                else:
                    feeder = firstSingleCommand.postProcess.checker
                    indexToSet = 2
            else:
                feeder = firstSingleCommand.process.checker
                indexToSet = 1
        else:
            feeder = firstSingleCommand.preProcess.checker
            indexToSet = 0

        localMappedArgs = [EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS,EMPTY_MAPPED_ARGS]
        paramFound, remainingArgs = parseDashedParams(rawArgList[i], feeder.argTypeList)
        localMappedArgs[indexToSet] = paramFound

        newRawArgList.append(remainingArgs)
        mappedArgs.append( tuple(localMappedArgs) )

    return newRawArgList, mappedArgs

def fireCommand(cmd, params, preParse = True , processName=None, processArg=None):
    t = threading.Thread(None, executeCommand, None, (cmd,params,preParse,processName,processArg,))
    t.start()

# TODO add processName at the error message
#      Except if (in main (main thread + level 0) AND in shell mode) OR None name
#      OR add cmd name (or both)
#
#     possible to get cmd in progress with the engine stack
#         even possible to know if it is in pre/pro/post
#
#     if (in shell mode AND main) OR processName is None
#           don't print processName
#     else: #in alias, script, daemon, ...
#           if processName is None
#               print cmd name
#           else:
#               print process name + cmd name
#
# @return, true if no severe error or correct process, false if severe error
#
def executeCommand(cmd, params, preParse = True , processName=None, processArg=None):
    "execute the engine object"
        
    stackTraceColor = error
    ex              = None
    engine          = None
    try:
        params.pushVariableLevelForThisThread()
        
        if preParse:
            cmdPreParsed = preParseLine(cmd)
        else:
            cmdPreParsed = cmd
        
        if processArg is not None: 
            #TODO PROBABLY BUG... if it is a alias, the call of the inner command will call another push and these local variable will not be available...
            #TODO BUG (?) script execution will cause a lot of this statement, why ?
                #check with the startup script
                   
            params.variable.setParameter("*", VarParameter(' '.join(str(x) for x in processArg)), localParam = True) #all in one string
            params.variable.setParameter("#", VarParameter(len(processArg)), localParam = True)                      #arg count
            params.variable.setParameter("@", VarParameter(processArg), localParam = True)                            #all args
            #TODO params.variable.setParameter("?", VarParameter(processArg, localParam = True)                            #value from last command
            #TODO params.variable.setParameter("!", VarParameter(processArg, localParam = True)                            #last pid started in background
            params.variable.setParameter("$", VarParameter(thread.get_ident()), localParam = True)                    #current process id #TODO id is not enought, need level
        
        #parse and check the string list
        cmdStringList = parseArgument(cmdPreParsed, params, processName)
        
        #if empty list after parsing, nothing to execute
        if len(cmdStringList) == 0:
            return None, None
        
        #convert token string to command objects and argument strings
        rawCommandList, rawArgList = parseCommand(cmdStringList, params.environment.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY).getValue()) #parameter will raise if leveltries does not exist
        rawArgList, mappedArgs = extractDashedParams(rawCommandList, rawArgList)

        #clone command/alias to manage concurrency state
        newRawCommandList = []
        for c in rawCommandList:
            newRawCommandList.append(c.clone())

        #prepare an engine
        engine = engineV3(newRawCommandList, rawArgList, mappedArgs, params)
        
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
        params.popVariableLevelForThisThread()

    return ex, engine






