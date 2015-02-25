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

from pyshell.arg.exception     import *
from pyshell.command.engine    import engineV3, FAKELOCK
from pyshell.command.exception import *
from pyshell.utils.constants   import ENVIRONMENT_LEVEL_TRIES_KEY, CONTEXT_EXECUTION_KEY, CONTEXT_EXECUTION_SHELL
from pyshell.utils.exception   import DefaultPyshellException, ListOfException, USER_WARNING, PARSE_ERROR, CORE_WARNING
from pyshell.utils.parsing     import Parser
from pyshell.utils.printing    import printException
from pyshell.utils.solving     import Solver
import threading

#execute return engine and lastException to the calling alias
    #engine to retrieve any output
    #exception, to check granularity and eventually stop the execution

def execute(string, parameterContainer, processName=None, processArg=None):
    
    #add external parameters at the end of the command
    if hasattr(processArg, "__iter__"):
        string += ' '.join(str(x) for x in processArg)
    elif type(processArg) == str or type(processArg) == unicode:
        string += processArg
            
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
        
        #no command to execute
        if len(parser) == 0:
            return None, None

    except Exception as ex:
        printException(ex, "Fail to parse command: ")
        return ex, None

    if parser.isToRunInBackground():
        t = threading.Thread(None, _execute, None, (parser,parameterContainer,processName,))
        t.start()
        return None,None #not possible to retrieve exception or engine, it is another thread
    else:
        return _execute(parser,parameterContainer, processName)

def _generatePrefix(parameterContainer, prefix = None, commandNameList=None, engine=None, processName=None):

    #TODO print if in debug ?
        #so no need to check if in shell if debug

    #is is a shell execution ?
    param = parameterContainer.context.getParameter(CONTEXT_EXECUTION_KEY, perfectMatch = True)
    isInShell= (param is not None and param.getSelectedValue() == CONTEXT_EXECUTION_SHELL)
            
    if not isInShell or not parameterContainer.isMainThread() or parameterContainer.getCurrentId()[1] > 0:
        threadId, levelId = parameterContainer.getCurrentId()
        message = "On thread "+str(threadId)+", level "+str(levelId)
        
        if processName is not None:
            message += ", process '"+str(processName)+"'"
            
        if commandNameList is not None and engine is not None and not engine.stack.isEmpty():
            commandIndex = engine.stack.cmdIndexOnTop()
            message += ", command '"+" ".join(commandNameList[commandIndex]) + "'"
            
        if prefix is not None:
            message += ": "+str(prefix)
            
        return message
    return prefix

def _execute(parser,parameterContainer, processName=None): 

    ## solving then execute ##
    ex              = None
    engine          = None
    commandNameList = None
    try:                
        #solve command, variable, and dashed parameters
        rawCommandList, rawArgList, mappedArgs, commandNameList = Solver().solve(parser, parameterContainer.environment.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY).getValue(), parameterContainer.variable)
        
        #clone command/alias to manage concurrency state
        newRawCommandList = []
        for i in xrange(0,len(rawCommandList)):
            c = rawCommandList[i].clone()
            
            if len(c) == 0:#check if there is at least one empty command, if yes, raise
                raise DefaultPyshellException("Command '"+" ".join(commandNameList[i])+"' is empty, not possible to execute",CORE_WARNING)
        
            newRawCommandList.append(c)

        #prepare an engine
        engine = engineV3(newRawCommandList, rawArgList, mappedArgs, parameterContainer)
        
        #execute 
        engine.execute()

    except executionInitException as ex:
        printException(ex,_generatePrefix(parameterContainer,prefix="Fail to init an execution object: ", commandNameList=commandNameList, engine=engine,processName=processName))
    except executionException as ex:
        printException(ex, _generatePrefix(parameterContainer,prefix="Fail to execute: ", commandNameList=commandNameList, engine=engine,processName=processName))
    except commandException as ex:
        printException(ex, _generatePrefix(parameterContainer,prefix="Error in command method: ", commandNameList=commandNameList, engine=engine,processName=processName))
    except engineInterruptionException as ex:
        if ex.abnormal:
            printException(ex, _generatePrefix(parameterContainer,prefix="Abnormal execution abort, reason: ", commandNameList=commandNameList, engine=engine,processName=processName))
        else:
            printException(ex, _generatePrefix(parameterContainer,prefix="Normal execution abort, reason: ", commandNameList=commandNameList, engine=engine,processName=processName))
    except argException as ex:
        printException(ex, _generatePrefix(parameterContainer,prefix="Error while parsing argument: ", commandNameList=commandNameList, engine=engine,processName=processName))
    except ListOfException as ex:
        printException(ex,_generatePrefix(parameterContainer,prefix="List of exception(s): ", commandNameList=commandNameList, engine=engine,processName=processName))
    except Exception as ex:
        printException(ex,_generatePrefix(parameterContainer, commandNameList=commandNameList, engine=engine,processName=processName))

    return ex, engine



