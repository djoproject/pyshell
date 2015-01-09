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
from pyshell.utils.parameter    import EnvironmentParameter, ContextParameter, VarParameter, ParameterContainer
from pyshell.utils.keystore     import KeyStore
from pyshell.utils.exception    import ListOfException
from pyshell.utils.constants    import *
from pyshell.utils.utils        import getTerminalSize
from pyshell.utils.printing     import Printer, warning, error, printException
from pyshell.utils.valuable     import SimpleValuable
from pyshell.utils.executing    import executeCommand, preParseLine
from pyshell.utils.aliasManager import AliasFromList, AliasFromFile

class CommandExecuter():
    def __init__(self, paramFile = None):
        self._initParams(paramFile)
        self._initPrinter()
        
        #load addon addon (if not loaded, can't do anything)
        loaded = False
        with self.ExceptionManager("fail to load addon 'pyshell.addons.addon'"):
            addon.loadAddonFun("pyshell.addons.addon", self.params)
            loaded = True
        
        if not loaded:
            print("fail to load addon loader, can not do anything with the application without this loader")
            exit(-1)
        
        #TODO create default event here (see list of event in constant file)
        
        self._initStartUpEvent()
        self._initExitEvent()
        
        ## execute atStartUp ##
        #TODO provide args from outside
            #nope, arg from outside must be mapped as global var in environment
            #give an empty 
        executeCommand(EVENT__ON_STARTUP,self.params, "__startup__") 

    def _initParams(self, paramFile):
        #create param manager
        self.params = ParameterContainer()
        self.promptWaitingValuable = SimpleValuable(False)

        ## init original params ##
        self.params.environment.setParameter(ENVIRONMENT_PARAMETER_FILE_KEY,    EnvironmentParameter(value=paramFile, typ=filePathArgChecker(exist=None, readable=True, writtable=None, isFile=True),transient=True,readonly=False, removable=False), localParam = False)
        self.params.environment.setParameter(ENVIRONMENT_PROMPT_KEY,            EnvironmentParameter(value=ENVIRONMENT_PROMPT_DEFAULT, typ=defaultInstanceArgChecker.getStringArgCheckerInstance(),transient=False,readonly=False, removable=False), localParam = False)
        self.params.environment.setParameter(ENVIRONMENT_TAB_SIZE_KEY,          EnvironmentParameter(value=TAB_SIZE, typ=IntegerArgChecker(0),transient=False,readonly=False, removable=False), localParam = False)
        self.params.environment.setParameter(ENVIRONMENT_LEVEL_TRIES_KEY,       EnvironmentParameter(value=multiLevelTries(),transient=True,readonly=True, removable=False), localParam = False)
        self.params.environment.setParameter(ENVIRONMENT_KEY_STORE_FILE_KEY,    EnvironmentParameter(value=DEFAULT_KEYSTORE_FILE, typ=filePathArgChecker(exist=None, readable=True, writtable=None, isFile=True),transient=False,readonly=False, removable=False), localParam = False)
        self.params.environment.setParameter(KEYSTORE_SECTION_NAME,             EnvironmentParameter(value=KeyStore(),transient=True,readonly=True, removable=False), localParam = False) 
        self.params.environment.setParameter(ENVIRONMENT_SAVE_KEYS_KEY,         EnvironmentParameter(value=ENVIRONMENT_SAVE_KEYS_DEFAULT, typ=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),transient=False,readonly=False, removable=False), localParam = False)
        self.params.environment.setParameter(ENVIRONMENT_HISTORY_FILE_NAME_KEY, EnvironmentParameter(value=ENVIRONMENT_HISTORY_FILE_NAME_VALUE, typ=filePathArgChecker(exist=None, readable=True, writtable=None, isFile=True),transient=False,readonly=False, removable=False), localParam = False)
        self.params.environment.setParameter(ENVIRONMENT_USE_HISTORY_KEY,       EnvironmentParameter(value=ENVIRONMENT_USE_HISTORY_VALUE, typ=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),transient=False,readonly=False, removable=False), localParam = False)
        self.params.environment.setParameter(ENVIRONMENT_ADDON_TO_LOAD_KEY,     EnvironmentParameter(value=ENVIRONMENT_ADDON_TO_LOAD_DEFAULT, typ=listArgChecker(defaultInstanceArgChecker.getStringArgCheckerInstance()),transient=False,readonly=False, removable=False), localParam = False)
        self.params.environment.setParameter(ADDONLIST_KEY,                     EnvironmentParameter(value = {}, typ=defaultInstanceArgChecker.getArgCheckerInstance(), transient = True, readonly = True, removable = False), localParam = False)
        
        self.params.context.setParameter(DEBUG_ENVIRONMENT_NAME,ContextParameter(value=tuple(range(0,5)), typ=defaultInstanceArgChecker.getIntegerArgCheckerInstance(), transient = False, transientIndex = False, defaultIndex = 0, removable=False, readonly=True), localParam = False)
        self.params.context.setParameter(CONTEXT_EXECUTION_KEY, ContextParameter(value=(CONTEXT_EXECUTION_SHELL, CONTEXT_EXECUTION_SCRIPT, CONTEXT_EXECUTION_DAEMON,), typ=defaultInstanceArgChecker.getStringArgCheckerInstance(), transient = True, transientIndex = True, defaultIndex = 0, removable=False, readonly=True), localParam = False)
        self.params.context.setParameter(CONTEXT_COLORATION_KEY,ContextParameter(value=(CONTEXT_COLORATION_LIGHT,CONTEXT_COLORATION_DARK,CONTEXT_COLORATION_NONE,), typ=defaultInstanceArgChecker.getStringArgCheckerInstance(), transient = False, transientIndex = False, defaultIndex = 0, removable=False, readonly=True), localParam = False)
    
    def _initPrinter(self):
        ## prepare the printing system ##
        printer = Printer.getInstance()
        printer.setREPLFunction(self.printAsynchronousOnShellV2)
        printer.setPromptShowedContext(self.promptWaitingValuable)
        printer.configureFromParameters(self.params)

    def _initStartUpEvent(self):
        ## prepare atStartUp ##
        mltries = self.params.environment.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY, perfectMatch=True).getValue()
        _atstartup = AliasFromList(EVENT__ON_STARTUP, showInHelp = False, readonly = False, removable = False, transient = True)
        _atstartup.setErrorGranularity(None) #never stop, don't care about error
        
        _atstartup.addCommand( ("addon",     "load", "pyshell.addons.parameter", ) )
        _atstartup.addCommand( ("parameter", "load", ) )
        _atstartup.addCommand( ("addon",     "unload", "pyshell.addons.parameter", ) ) #TODO don't unload it if in addon to load on startup
        _atstartup.addCommand( ("addon",     "onstartup", "load", ) ) #TODO don't load parameter if already loaded
        _atstartup.addCommand( (EVENT_ON_STARTUP, ) )
        
        _atstartup.setReadOnly(True)
        mltries.insert( (EVENT__ON_STARTUP, ), _atstartup )
        
        atstartup = AliasFromList(EVENT_ON_STARTUP, showInHelp = False, readonly = False, removable = False, transient = True)
        atstartup.setErrorGranularity(None) #never stop, don't care about error
        atstartup.addCommand( ("history","load", ) )
        atstartup.addCommand( ("key",    "load", ) )
        mltries.insert( (EVENT_ON_STARTUP, ), atstartup )

    def _initExitEvent(self):
        mltries = self.params.environment.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY, perfectMatch=True).getValue()
    
        ## prepare atExit ##
        atExit = AliasFromList(EVENT_AT_EXIT, showInHelp = False, readonly = False, removable = False, transient = True)
        atExit.setErrorGranularity(None) #never stop, don't care about error
        
        atExit.addCommand( ("parameter", "save",) ) #TODO need to have parameters addons parameter loaded before to save
            #TODO load parameter addon but do not print any error if already loaded, add a parameter to addon load
        atExit.addCommand( ("history",   "save",) )
        atExit.addCommand( ("key",       "save",) )
        
        atExit.setReadOnly(True)
        mltries.insert( (EVENT_AT_EXIT, ), atExit )
        atexit.register(self.AtExit)
        
    def AtExit(self):
        executeCommand(EVENT_AT_EXIT,self.params, "__atexit__") #TODO provide args from outside
            
    def mainLoop(self):
        #enable autocompletion
        if 'libedit' in readline.__doc__:
            import rlcompleter
            readline.parse_and_bind ("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")

        readline.set_completer(self.complete)
        
        self.params.context.getParameter(CONTEXT_EXECUTION_KEY, perfectMatch=True).setIndexValue(CONTEXT_EXECUTION_SHELL)
        
        #mainloop
        while True:
            #read prompt
            self.promptWaitingValuable.setValue(True)
            try:
                cmd = raw_input(self.params.environment.getParameter(ENVIRONMENT_PROMPT_KEY, perfectMatch=True).getValue())
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
            executeCommand(cmd, self.params, "__shell__") #TODO provide processName AND processArg from the outside of the sofware
    
    def printAsynchronousOnShellV2(self,message):
        prompt = self.params.environment.getParameter(ENVIRONMENT_PROMPT_KEY, perfectMatch=True).getValue()
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
                dic = self.params.environment.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY, perfectMatch=True).getValue().buildDictionnary(fullline, True, True, False)

                toret = {}
                for k in dic.keys():
                    toret[k[0]] = None

                toret = toret.keys()[:]
                toret.append(None)
                return toret[index]

            fullline = cmdStringList[-1]

            ## manage ambiguity ##
            advancedResult = self.params.environment.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY, perfectMatch=True).getValue().advancedSearch(fullline, False)
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
                    dic = self.params.environment.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY, perfectMatch=True).getValue().buildDictionnary(fullline, True, True, False)
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
            if self.params.context.getParameter(DEBUG_ENVIRONMENT_NAME, perfectMatch=True).getSelectedValue() > 0:
                printException(ex)

        return None

    @contextmanager
    def ExceptionManager(self, msg_prefix = None):
        try:
            yield
        except ListOfException as loe:
            if msg_prefix is None:
                msg_prefix = "List of exception: "

            printException(loe, msg_prefix)
                        
        except Exception as pex:
            if msg_prefix is not None:
                msg_prefix += ": "

            printException(pex, msg_prefix)

    def executeFile(self,filename, granularity = None):            
        self.params.context.getParameter(CONTEXT_EXECUTION_KEY, perfectMatch=True).setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        afile = AliasFromFile(filename)
        afile.setErrorGranularity(granularity)
        
        with self.ExceptionManager("An error occured during the script execution: "):
            afile.execute(args = (), parameters=self.params)

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
    print("-h, --help:        print this help message")
    print("-p, --parameter:   define a custom parameter file")
    print("-s, --script:      define a script to execute")
    print("-n, --no-exit:     start the shell after the script")
    print("-g, --granularity: set the error granularity for file script")
    print("")

if __name__ == "__main__":
    #manage args
    opts = ()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:s:ng:", ["help", "parameter=", "script=", "no-exit", "granularity="])
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
    Granularity     = sys.maxint
    
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
        elif o in ("-g", "--granularity"):
            try:
                Granularity = int(a)
            except ValueError as ve:
                print("invalid value for granularity: "+str(ve))
                usage()
                exit(-1)
        else:
            print("unknown parameter: "+str(o))
    
    if ParameterFile is None:
        ParameterFile = DEFAULT_PARAMETER_FILE
    
    #run basic instance
    executer = CommandExecuter(ParameterFile)
    
    if ScriptFile != None:
        executer.executeFile(ScriptFile, Granularity)
    else:
        ExitAfterScript = False
    
    if not ExitAfterScript:
        executer.mainLoop()

