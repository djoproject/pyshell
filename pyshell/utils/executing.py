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
from pyshell.command.engine    import engineV3
from pyshell.command.exception import *
from pyshell.utils.constants   import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.exception   import DefaultPyshellException, ListOfException, USER_WARNING, PARSE_ERROR
from pyshell.utils.parsing     import Parser
from pyshell.utils.parameter   import VarParameter
from pyshell.utils.printing    import printException
from pyshell.utils.solving     import Solver
import threading, thread

#TODO 
    #why do we still need to return ex and engine
        #does not have any sense in background mode

    #keep track of running event and be able to kill one or all of them
        #manage it in alias object with a static list
            #an alias add itself in the list before to start then remove itself from the list at the end of its execution
            

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
        rawCommandList, rawArgList, mappedArgs = Solver().solve(parser, parameterContainer.environment.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY).getValue(), parameterContainer.variable)
        
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



