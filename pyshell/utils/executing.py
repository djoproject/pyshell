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
from pyshell.utils.constants   import ENVIRONMENT_LEVEL_TRIES_KEY, CONTEXT_EXECUTION_KEY, CONTEXT_EXECUTION_SHELL, DEBUG_ENVIRONMENT_NAME
from pyshell.utils.exception   import DefaultPyshellException, ListOfException, USER_WARNING, PARSE_ERROR, CORE_WARNING,CORE_ERROR
from pyshell.utils.parsing     import Parser
from pyshell.utils.printing    import printException
from pyshell.utils.solving     import Solver
from pyshell.system.parameter  import VarParameter
import threading

#execute return engine and lastException to the calling alias
    #engine to retrieve any output
    #exception, to check granularity and eventually stop the execution

def execute(string, parameterContainer, processName=None, processArg=None):
    
    #add external parameters at the end of the command
    if hasattr(processArg, "__iter__"):
        string += " " + ' '.join(str(x) for x in processArg)
    elif type(processArg) == str or type(processArg) == unicode:
        string += " "+processArg
    elif processArg is not None:
        raise DefaultPyshellException("unknown type or process args, expect a list or a string, got '"+type(processArg)+"'",CORE_ERROR)
        
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
        parameterContainer.variable.setParameter("$!", VarParameter(str(t.ident)), localParam = True)
        return None,None #not possible to retrieve exception or engine, it is another thread
    else:
        return _execute(parser,parameterContainer, processName)

def _generateSuffix(parameterContainer, commandNameList=None, engine=None, processName=None):

    #print if in debug ? 
    param = parameterContainer.context.getParameter(DEBUG_ENVIRONMENT_NAME, perfectMatch = True)
    showAdvancedResult= (param is not None and param.getSelectedValue() > 0)

    if not showAdvancedResult:
        #is is a shell execution ?
        param = parameterContainer.context.getParameter(CONTEXT_EXECUTION_KEY, perfectMatch = True)
        showAdvancedResult = (param is None or param.getSelectedValue() != CONTEXT_EXECUTION_SHELL)
            
    if showAdvancedResult or not parameterContainer.isMainThread() or parameterContainer.getCurrentId()[1] > 0:
        threadId, levelId = parameterContainer.getCurrentId()
        message = " (threadId="+str(threadId)+", level="+str(levelId)
        
        if processName is not None:
            message += ", process='"+str(processName)+"'"
        
        if commandNameList is not None and engine is not None and not engine.stack.isEmpty():
            commandIndex = engine.stack.cmdIndexOnTop()
            message += ", command='"+" ".join(commandNameList[commandIndex]) + "'"
        
        message += ")"

        return message
    return None

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
        printException(ex,prefix="Fail to init an execution object: ", suffix=_generateSuffix(parameterContainer, commandNameList=commandNameList, engine=engine,processName=processName))
    except executionException as ex:
        printException(ex,prefix="Fail to execute: ", suffix=_generateSuffix(parameterContainer, commandNameList=commandNameList, engine=engine,processName=processName))
    except commandException as ex:
        printException(ex,prefix="Error in command method: ", suffix=_generateSuffix(parameterContainer, commandNameList=commandNameList, engine=engine,processName=processName))
    except engineInterruptionException as ex:
        if ex.abnormal:
            printException(ex, prefix="Abnormal execution abort, reason: ", suffix=_generateSuffix(parameterContainer, commandNameList=commandNameList, engine=engine,processName=processName))
        else:
            printException(ex,prefix="Normal execution abort, reason: ", suffix=_generateSuffix(parameterContainer, commandNameList=commandNameList, engine=engine,processName=processName))
    except argException as ex:
        printException(ex, prefix="Error while parsing argument: ", suffix=_generateSuffix(parameterContainer, commandNameList=commandNameList, engine=engine,processName=processName))
    except ListOfException as ex:
        printException(ex, prefix="List of exception(s): ", suffix=_generateSuffix(parameterContainer, commandNameList=commandNameList, engine=engine,processName=processName))
    except Exception as ex:
        printException(ex,suffix=_generateSuffix(parameterContainer, commandNameList=commandNameList, engine=engine,processName=processName))

    return ex, engine



