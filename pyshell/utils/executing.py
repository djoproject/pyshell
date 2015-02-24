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

def _generatePrefix(parameterContainer, prefix = None):

    #is is a shell execution ?
    isInShell = False
    if parameterContainer.context.hasParameter(CONTEXT_EXECUTION_KEY, perfectMatch = True):
        param = parameterContainer.context.getParameter(CONTEXT_EXECUTION_KEY, perfectMatch = True)
        with param.getLock():
            isInShell = param.getSelectedValue() == CONTEXT_EXECUTION_SHELL
            
    if not isInShell or not parameterContainer.isMainThread() or parameterContainer.getCurrentId()[1] > 0:
        pass
    
        #TODO build a prefix with "processName", "command name", "thread id", "level id", "file line", ...
            #processName => from argument (could be none)
            #command name => TODO ?
                #be carefull engine could be not available yet
                
                #IDEA 1: if we can get command index (from engine or from clone loop) AND if the command is stored byt the solver
                    #just get it from the solver
                    #--- need to store it in parser object
                    #+++ easy to implement
                    
                #IDEA 2: solve again the command from the parser to the solver
                    #+++ no need to store anything
                    #--- * 2 maybe it will not retrieve the same command name...
                    
                #IDEA 3: ?
                
            #thread id => parameterContainer.getCurrentId()[0]
            #level id => parameterContainer.getCurrentId()[1]
                    
    return prefix

def _execute(parser,parameterContainer, processName=None): 

    ## solving then execute ##
    ex     = None
    engine = None
    try:                
        #solve command, variable, and dashed parameters
        rawCommandList, rawArgList, mappedArgs = Solver().solve(parser, parameterContainer.environment.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY).getValue(), parameterContainer.variable)
        
        #clone command/alias to manage concurrency state
        newRawCommandList = []
        for i in xrange(0,len(rawCommandList)):
            c = rawCommandList[i].clone()
            
            if len(c) == 0:#check if there is at least one empty command, if yes, raise
                raise DefaultPyshellException(_generatePrefix(parameterContainer,"Empty command at index "+str(i)),CORE_WARNING) #TODO append command name, how to build it
        
            newRawCommandList.append(c)

        #prepare an engine
        engine = engineV3(newRawCommandList, rawArgList, mappedArgs, parameterContainer)
        
        #execute 
        engine.execute()

    except executionInitException as ex:
        printException(ex,_generatePrefix(parameterContainer,"Fail to init an execution object: "))
    except executionException as ex:
        printException(ex, _generatePrefix(parameterContainer,"Fail to execute: "))
    except commandException as ex:
        printException(ex, _generatePrefix(parameterContainer,"Error in command method: "))
    except engineInterruptionException as ex:
        if ex.abnormal:
            printException(ex, _generatePrefix(parameterContainer,"Abnormal execution abort, reason: "))
        else:
            printException(ex, _generatePrefix(parameterContainer,"Normal execution abort, reason: "))
    except argException as ex:
        printException(ex, _generatePrefix(parameterContainer,"Error while parsing argument: "))
    except ListOfException as ex:
        printException(ex,_generatePrefix(parameterContainer,"List of exception(s): "))
    except Exception as ex:
        printException(ex,_generatePrefix(parameterContainer))

    return ex, engine



