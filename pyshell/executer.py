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

#system library
import readline, os, sys, atexit, getopt, traceback
from contextlib import contextmanager

#tries library
from tries import multiLevelTries
from tries.exception import triesException, pathNotExistsTriesException

#local library
from pyshell.arg.argchecker     import defaultInstanceArgChecker, listArgChecker, filePathArgChecker, IntegerArgChecker
from pyshell.addons             import addon
from pyshell.utils.parameter    import ParameterManager, EnvironmentParameter, ContextParameter, VarParameter
from pyshell.utils.keystore     import KeyStore
from pyshell.utils.exception    import ListOfException
from pyshell.utils.constants    import *
from pyshell.utils.utils        import getTerminalSize
from pyshell.utils.printing     import Printer, warning, error, printException
from pyshell.utils.valuable     import SimpleValuable
from pyshell.utils.executing    import executeCommand, preParseLine
from pyshell.utils.aliasManager import Alias

class CommandExecuter():
    def __init__(self, paramFile = None):
        #create param manager
        self.params = ParameterManager()

        ## init original params ##
        self.params.setParameter("parameterFile",       EnvironmentParameter(value=paramFile, typ=filePathArgChecker(exist=None, readable=True, writtable=None, isFile=True),transient=True,readonly=False, removable=False), ENVIRONMENT_NAME)
        self.params.setParameter("prompt",              EnvironmentParameter(value="pyshell:>", typ=defaultInstanceArgChecker.getStringArgCheckerInstance(),transient=False,readonly=False, removable=False), ENVIRONMENT_NAME)
        self.params.setParameter("tabsize",             EnvironmentParameter(value=TAB_SIZE, typ=IntegerArgChecker(0),transient=False,readonly=False, removable=False), ENVIRONMENT_NAME)
        mltries = multiLevelTries()
        self.params.setParameter("levelTries",          EnvironmentParameter(value=mltries,transient=True,readonly=True, removable=False), ENVIRONMENT_NAME)
        keyStorePath = EnvironmentParameter(value=DEFAULT_KEYSTORE_FILE, typ=filePathArgChecker(exist=None, readable=True, writtable=None, isFile=True),transient=False,readonly=False, removable=False)
        self.params.setParameter("keystoreFile",        keyStorePath, ENVIRONMENT_NAME)
        self.keystore = KeyStore(keyStorePath)
        self.params.setParameter(KEYSTORE_SECTION_NAME, EnvironmentParameter(value=self.keystore,transient=True,readonly=True, removable=False), ENVIRONMENT_NAME) 
        self.params.setParameter("saveKeys",            EnvironmentParameter(value=True, typ=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),transient=False,readonly=False, removable=False), ENVIRONMENT_NAME)
        self.params.setParameter("historyFile",         EnvironmentParameter(value=os.path.join(DEFAULT_CONFIG_DIRECTORY, ".pyshell_history"), typ=filePathArgChecker(exist=None, readable=True, writtable=None, isFile=True),transient=False,readonly=False, removable=False), ENVIRONMENT_NAME)
        self.params.setParameter("useHistory",          EnvironmentParameter(value=True, typ=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),transient=False,readonly=False, removable=False), ENVIRONMENT_NAME)
        self.params.setParameter("addonToLoad",         EnvironmentParameter(value=("pyshell.addons.std","pyshell.addons.keystore",), typ=listArgChecker(defaultInstanceArgChecker.getStringArgCheckerInstance()),transient=False,readonly=False, removable=False), ENVIRONMENT_NAME)
        self.params.setParameter(ADDONLIST_KEY,         EnvironmentParameter(value = {}, typ=defaultInstanceArgChecker.getArgCheckerInstance(), transient = True, readonly = True, removable = False), ENVIRONMENT_NAME)
        
        self.params.setParameter("debug",               ContextParameter(value=tuple(range(0,5)), typ=defaultInstanceArgChecker.getIntegerArgCheckerInstance(), transient = False, transientIndex = False, defaultIndex = 0, removable=False), CONTEXT_NAME)
        self.params.setParameter("execution",           ContextParameter(value=(CONTEXT_EXECUTION_SHELL, CONTEXT_EXECUTION_SCRIPT, CONTEXT_EXECUTION_DAEMON,), typ=defaultInstanceArgChecker.getStringArgCheckerInstance(), transient = True, transientIndex = True, defaultIndex = 0, removable=False), CONTEXT_NAME)
        self.params.setParameter("coloration",          ContextParameter(value=(CONTEXT_COLORATION_LIGHT,CONTEXT_COLORATION_DARK,CONTEXT_COLORATION_NONE,), typ=defaultInstanceArgChecker.getStringArgCheckerInstance(), transient = False, transientIndex = False, defaultIndex = 0, removable=False), CONTEXT_NAME)
        
        ## prepare the printing system ##
        printer = Printer.getInstance()
        printer.setShellContext(self.params.getParameter("execution",CONTEXT_NAME))
        printer.setREPLFunction(self.printAsynchronousOnShellV2)
        self.promptWaitingValuable = SimpleValuable(False)
        printer.setPromptShowedContext(self.promptWaitingValuable)
        printer.setSpacingContext(self.params.getParameter("tabsize",ENVIRONMENT_NAME))
        printer.setBakcgroundContext(self.params.getParameter("coloration",CONTEXT_NAME))
        
        #load addon addon (if not loaded, can't do anything)
        with self.ExceptionManager("fail to load addon 'pyshell.addons.addon'"):
            addon.loadAddonFun("pyshell.addons.addon", self.params)
            #TODO should exit if faillure, no ?
                    
        ## prepare atStartUp ##
        _atstartup = Alias(EVENT__ON_STARTUP, showInHelp = False, readonly = False, removable = False, transient = True)
        _atstartup.setErrorGranularity(None) #never stop, don't care about error
        
        _atstartup.addCommand( ("addon",     "load", "pyshell.addons.parameter", ) )
        _atstartup.addCommand( ("parameter", "load", ) )
        _atstartup.addCommand( ("addon",     "unload", "pyshell.addons.parameter", ) )
        _atstartup.addCommand( ("addon",     "onstartup", "load", ) )
        _atstartup.addCommand( ("atstartup", ) )
        
        _atstartup.setReadOnly(True)
        mltries.insert( (EVENT__ON_STARTUP, ), _atstartup )
        
        atstartup = Alias(EVENT_ON_STARTUP, showInHelp = False, readonly = False, removable = False, transient = True)
        atstartup.setErrorGranularity(None) #never stop, don't care about error
        atstartup.addCommand( ("history","load", ) )
        atstartup.addCommand( ("key",    "load", ) )
        mltries.insert( (EVENT_ON_STARTUP, ), atstartup )
        
        ## prepare atExit ##
        atExit = Alias(EVENT_AT_EXIT, showInHelp = False, readonly = False, removable = False, transient = True)
        atExit.setErrorGranularity(None) #never stop, don't care about error
        
        atExit.addCommand( ("parameter", "save",) )
        atExit.addCommand( ("history",   "save",) )
        atExit.addCommand( ("key",       "save",) )
        
        atExit.setReadOnly(True)
        mltries.insert( (EVENT_AT_EXIT, ), atExit )
        atexit.register(self.AtExit)
        
        ## execute atStartUp ##
        executeCommand(EVENT__ON_STARTUP,self.params)
    
    def AtExit(self):
        executeCommand(EVENT_AT_EXIT,self.params)
            
    def mainLoop(self):
        #enable autocompletion
        if 'libedit' in readline.__doc__:
            import rlcompleter
            readline.parse_and_bind ("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")

        readline.set_completer(self.complete)
        
        self.params.getParameter("execution", CONTEXT_NAME).setIndexValue(CONTEXT_EXECUTION_SHELL)
        
        #mainloop
        while True:
            #read prompt
            self.promptWaitingValuable.setValue(True)
            try:
                cmd = raw_input(self.params.getParameter("prompt",ENVIRONMENT_NAME).getValue())
            except SyntaxError as se:
                self.promptWaitingValuable.setValue(False)
                error(se, "syntax error")
                continue
            except EOFError:
                self.promptWaitingValuable.setValue(False)
                warning("\n   end of stream")
                break
 
            #execute command
            self.promptWaitingValuable.setValue(False)
            executeCommand(cmd, self.params)        
    
    def printAsynchronousOnShellV2(self,message):
        prompt = self.params.getParameter("prompt",ENVIRONMENT_NAME).getValue()
        #this is needed because after an input, the readline buffer isn't always empty
        if len(readline.get_line_buffer()) == 0 or readline.get_line_buffer()[-1] == '\n':
            size = len(prompt)
            toprint = prompt
            
        else:
            size = len(prompt) + len(readline.get_line_buffer())
            toprint = prompt + readline.get_line_buffer()
        
        width, height = getTerminalSize()
        offset = int(size/width)
        
        #http://ascii-table.com/ansi-escape-sequences-vt-100.php
        #message = EventToPrint +" "+str(width)+" "+str(size)+" "+str(offset)
        if offset > 0:
            message = "\r\033["+str(offset)+"A\033[2K" + message# + "\033[s"
        else:
            message = "\r\033[K" + message# + "\033[s"
        
        sys.stdout.write(message + "\n" + toprint)
        sys.stdout.flush()
        
    def complete(self,suffix,index):
        cmdStringList = preParseLine(readline.get_line_buffer())

        try:
            ## special case, empty line ##
                #only print root tokens
            if len(cmdStringList) == 0:
                fullline = ()
                dic = self.params.getParameter("levelTries",ENVIRONMENT_NAME).getValue().buildDictionnary(fullline, True, True, False)

                toret = {}
                for k in dic.keys():
                    toret[k[0]] = None

                toret = toret.keys()[:]
                toret.append(None)
                return toret[index]

            fullline = cmdStringList[-1]

            ## manage ambiguity ##
            advancedResult = self.params.getParameter("levelTries",ENVIRONMENT_NAME).getValue().advancedSearch(fullline, False)
            if advancedResult.isAmbiguous():
                tokenIndex = len(advancedResult.existingPath) - 1

                if tokenIndex != (len(fullline)-1):
                    return None #ambiguity on an inner level

                tries = advancedResult.existingPath[tokenIndex][1].localTries
                keylist = tries.getKeyList(fullline[tokenIndex])

                keys = []
                for key in keylist:
                    tmp = list(fullline[:])
                    tmp.append(key)
                    keys.append(tmp)
            else:
                try:
                    dic = self.params.getParameter("levelTries",ENVIRONMENT_NAME).getValue().buildDictionnary(fullline, True, True, False)
                except pathNotExistsTriesException as pnete:
                    return None

                keys = dic.keys()

            #build final result
            finalKeys = []
            for k in keys:
            
                #special case to complete the last token if needed
                if len(k) >= len(fullline) and len(k[len(fullline)-1]) > len(fullline[-1]):
                    toappend = k[len(fullline)-1]

                    if len(k) > len(fullline):
                        toappend += " "

                    finalKeys.append(toappend)
                    break

                #normal case, the last token on the line is complete, only add its child tokens
                finalKeys.append(" ".join(k[len(fullline):]))
            
            #if no other choice than the current value, return the current value
            if "" in finalKeys and len(finalKeys) == 1:
                return (fullline[-1],None,)[index]

            finalKeys.append(None)
            return finalKeys[index]
            
        except Exception as ex:
            if self.params.getParameter("debug",CONTEXT_NAME).getSelectedValue() > 0:
                printException(ex,None, traceback.format_exc())

        return None

    @contextmanager
    def ExceptionManager(self, msg_prefix = None):
        try:
            yield
        except ListOfException as loe:
            if msg_prefix is None:
                msg_prefix = "List of exception"
            
            error(msg_prefix+": ")
            for e in loe.exceptions:
                printException(e,"    ")
            
        except Exception as pex:
            if msg_prefix is not None:
                msg_prefix += ": "

            st = None
            if self.params.getParameter("debug",CONTEXT_NAME).getSelectedValue() > 0:
                st = traceback.format_exc()
                
            printException(pex, msg_prefix, st)

    def executeFile(self,filename):
        #TODO load the file into an alias manager
            #load the whole file ???
                #or load part after part, create an extended class of alias to manage aliasFile
                
            #then execute it
            
        #TODO be able to set granularity error with args
    
        shellOnExit = False
        self.params.getParameter("execution", CONTEXT_NAME).setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        
        try:
            with open(filename, 'wb') as f:
                config.write(configfile)
                
                for line in f:
                    if line.trim() == "noexit":
                        shellOnExit = True
                    
                    #TODO stop on error (see alias manager)
                    lastException, engine = executeCommand(line,self.params)
                    
        except Exception as ex:
            st = None
            if self.params.getParameter("debug",CONTEXT_NAME).getSelectedValue() > 0:
                st = traceback.format_exc()
                
            printException(ex, "An error occured during the script execution: ", st)
        
        return shellOnExit

####################################################################################################
#no need to use printing system on the following function because shell is not yet running

def usage():
    print("")
    print("executer.py [-h -p <parameter file> -i <script file> -s]")
    
def help():
    usage()
    print("")
    print("Python Custom Shell Executer v1.0")
    print("")
    print("-h, --help:      print this help message")
    print("-p, --parameter: define a custom parameter file")
    print("-s, --script:    define a script to execute")
    print("-n, --no-exit:   start the shell after the script")
    print("")

if __name__ == "__main__":
    #manage args
    opts = ()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:s:n", ["help", "parameter=", "script=", "no-exit"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(str(err)) # will print something like "option -a not recognized"
        usage()
        print("")
        print("to get help: executer.py -h")
        print("")
        sys.exit(2)
        
    ParameterFile   = None
    ScriptFile      = None
    ExitAfterScript = True
    
    for o, a in opts:
        if o in ("-h", "--help"):
            help()
            exit()
        elif o in ("-p", "--parameter"):
            ParameterFile = a
        elif o in ("-s", "--script"):
            ScriptFile = a
        elif o in ("-n", "--no-exit"):
            ExitAfterScript = False
        else:
            print("unknown parameter: "+str(o))
    
    if ParameterFile is None:
        ParameterFile = DEFAULT_PARAMETER_FILE
    
    #run basic instance
    executer = CommandExecuter(ParameterFile)
    
    if ScriptFile != None:
        ExitAfterScript = not self.executeFile(ScriptFile)
    else:
        ExitAfterScript = False
    
    if not ExitAfterScript:
        executer.mainLoop()

