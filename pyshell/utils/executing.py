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

from pyshell.utils.exception   import *
from pyshell.command.exception import *
from pyshell.arg.exception     import *
from pyshell.utils.constants   import ENVIRONMENT_NAME, CONTEXT_NAME
from pyshell.utils.printing    import warning, error, printException
from pyshell.command.engine    import engineV3

#TODO
    #TODO in preParseLine, manage space escape like ‘\ ‘

def preParseNotPipedCommand(line):

	#remove blank char at the ends
	line = line.strip(' \t\n\r')

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
    "parse a line to a list of list of string, without converting the arg element"

    line = line.split("|")
    toret = []
    
    for partline in line:
        finalCmd = preParseNotPipedCommand(partline)

        #remove empty command
        if len(finalCmd) == 0:
            continue

        toret.append(finalCmd)

    return toret

def parseArgument(preParsedCmd, params):
    "replace argument like `$toto` into their value in parameter"

    parsedCmd = []
    unknowVarError = set()

    for rawCmd in preParsedCmd:
        newRawCmd = []

        for stringToken in rawCmd:

            if stringToken.startswith("$") and len(stringToken) > 1:
                #remove $
                stringToken = stringToken[1:]

                if not params.hasParameter(stringToken):
                    unknowVarError.add("Unknown var '"+stringToken+"'")
                    continue
                    
                param = params.getParameter(stringToken)
                
                if not isinstance(param, VarParameter):
                    unknowVarError.add("specified key '"+stringToken+"' correspond to a type different of a var")
                    continue
                
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

        return toRaise

    return parsedCmd

def parseCommand(parsedCmd, mltries):

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

#
#
# @return, true if no severe error or correct process, false if severe error
#
def executeCommand(cmd, params):
    "execute the engine object"

    try:
        #parse and check the string list
        cmdStringList = parseArgument(preParseLine(cmd), params)

        #if empty list after parsing, nothing to execute
        if len(cmdStringList) == 0:
            return False

        #convert token string to command objects and argument strings
        rawCommandList, rawArgList = parseCommand(cmdStringList, params.getParameter("levelTries",ENVIRONMENT_NAME).getValue())
        
        #prepare an engine
        engine = engineV3(rawCommandList, rawArgList, params)
        
        #execute 
        engine.execute()
        return True
        
    except executionInitException as eie:
        error("Fail to init an execution object: "+str(eie.value))
    except executionException as ee:
        error("Fail to execute: "+str(eie.value))
    except commandException as ce:
        error("Error in command method: "+str(ce.value))
    except engineInterruptionException as eien:
        if eien.abnormal:
            error("Abnormal execution abort, reason: "+str(eien.value))
        else:
            warning("Normal execution abort, reason: "+str(eien.value))
    except argException as ae:
        warning("Error while parsing argument: "+str(ae.value))
    except ListOfException as loe:
        if len(loe.exceptions) > 0:
            error("List of exception:")
            for e in loe.exceptions:
                printException(e)
                
    except Exception as e:
        printException(e)

    #print stack trace if debug is enabled
    if params.getParameter("debug",CONTEXT_NAME).getSelectedValue() > 0:
        error(traceback.format_exc())

    return False






