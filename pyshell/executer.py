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

#TODO
    #-add argument
        #-d start as daemon
            #by default, a daemon must be a loop
            #think to a system able to stop it easily          
        
    #manage daemon system

#system library
import readline
import os
import sys
import atexit
import getopt
import traceback

#tries library
from tries import multiLevelTries
from tries.exception import triesException, pathNotExistsTriesException

#local library
from pyshell.command.exception import *
from pyshell.command.engine    import engineV3
from pyshell.arg.exception     import *
from pyshell.arg.argchecker    import defaultInstanceArgChecker, listArgChecker, filePathArgChecker, IntegerArgChecker
from pyshell.addons            import addon
from pyshell.utils.parameter   import ParameterManager, EnvironmentParameter, ContextParameter
from pyshell.utils.keystore    import KeyStore
from pyshell.utils.exception   import ListOfException
from pyshell.utils.constants   import DEFAULT_KEYSTORE_FILE, KEYSTORE_SECTION_NAME, DEFAULT_PARAMETER_FILE, CONTEXT_NAME, ENVIRONMENT_NAME
from pyshell.utils.coloration  import red, orange, nocolor

class writer :
    def __init__(self, out):
    	self.out = out

    def write(self, text):
        self.out.write("    "+str(text))

def _parseLine(line, args):
    line = line.split("|")
    toret = []

    for partline in line:
        #remove blank char
        partline = partline.strip(' \t\n\r')
        if len(partline) == 0:
            continue
        
        #split on space
        partline = partline.split(" ")

        #fo each token
        finalCmd = []
        for cmd in partline:
            cmd = cmd.strip(' \t\n\r')
            if len(cmd) == 0 :
                continue
            
            if args is not None:
                if cmd.startswith("$") and len(cmd) > 1:
                    if cmd[1:] not in args:
                        print("Unknown var '"+cmd[1:]+"'")
                        return ()

                    finalCmd.extend(args[cmd[1:]])

                elif cmd.startswith("\$"):
                    finalCmd.append(cmd[1:])
                else:
                    finalCmd.append(cmd)
            else:
                finalCmd.append(cmd)

        if len(finalCmd) == 0:
            continue

        toret.append(finalCmd)

    return toret

class CommandExecuter():
    def __init__(self, paramFile = None):
        #create param manager
        self.params = ParameterManager(paramFile)

        #init original params
        self.params.setParameter("prompt",              EnvironmentParameter(value="pyshell:>", typ=defaultInstanceArgChecker.getStringArgCheckerInstance(),transient=False,readonly=False, removable=False), ENVIRONMENT_NAME)
        self.params.setParameter("tabsize",             EnvironmentParameter(value=4, typ=IntegerArgChecker(0),transient=False,readonly=False, removable=False), ENVIRONMENT_NAME)

        #TODO update "vars" to ... (remove it?)
        self.params.setParameter("vars",                EnvironmentParameter(value={},transient=True,readonly=True, removable=False), ENVIRONMENT_NAME)
        
        self.params.setParameter("levelTries",          EnvironmentParameter(value=multiLevelTries(),transient=True,readonly=True, removable=False), ENVIRONMENT_NAME)
        keyStorePath = EnvironmentParameter(value=DEFAULT_KEYSTORE_FILE, typ=filePathArgChecker(exist=None, readable=True, writtable=None, isFile=True),transient=False,readonly=False, removable=False)
        self.params.setParameter("keystoreFile",        keyStorePath, ENVIRONMENT_NAME)
        self.keystore = KeyStore(keyStorePath)
        self.params.setParameter(KEYSTORE_SECTION_NAME, EnvironmentParameter(value=self.keystore,transient=True,readonly=True, removable=False), ENVIRONMENT_NAME) 
        self.params.setParameter("saveKeys",            EnvironmentParameter(value=True, typ=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),transient=False,readonly=False, removable=False), ENVIRONMENT_NAME)
        self.params.setParameter("debug",               ContextParameter(value=(0,1,2,3,4,), typ=defaultInstanceArgChecker.getIntegerArgCheckerInstance(), transient = False, transientIndex = False, defaultIndex = 0, removable=False), CONTEXT_NAME)
        self.params.setParameter("historyFile",         EnvironmentParameter(value=os.path.join(os.path.expanduser("~"), ".pyshell_history"), typ=filePathArgChecker(exist=None, readable=True, writtable=None, isFile=True),transient=False,readonly=False, removable=False), ENVIRONMENT_NAME)
        self.params.setParameter("useHistory",          EnvironmentParameter(value=True, typ=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),transient=False,readonly=False, removable=False), ENVIRONMENT_NAME)
        self.params.setParameter("execution",           ContextParameter(value=("shell", "script", "daemon",), typ=defaultInstanceArgChecker.getStringArgCheckerInstance(), transient = True, transientIndex = True, defaultIndex = 0, removable=False), CONTEXT_NAME)
        self.params.setParameter("addonToLoad",         EnvironmentParameter(value=("pyshell.addons.std",), typ=listArgChecker(defaultInstanceArgChecker.getStringArgCheckerInstance()),transient=False,readonly=False, removable=False), ENVIRONMENT_NAME)
        
        #redirect output
        real_out    = sys.stdout
        self.writer = writer(real_out)
        sys.stdout  = self.writer
        
        #try to load parameter file
        try:
            self.params.load()
        except Exception as ex:
            print "Fail to load parameters file: "+str(ex)

        #try to load standard shell function
        #TODO try to remove addon loading from here and move it to the loop to load addon
            #just import loadAddonFun from addon
        try:
            addon._loaders.load(self.params)
        except ListOfException as loe:
            if len(loe.exceptions) > 0:
                print("LOADING FATAL ERROR:")
                for e in loe.exceptions:
                    print("    "+str(e))
        #except Exception as ex:
        #    print "LOADING FATAL ERROR, an unexpected error occured during the default addon loading: "+str(ex)

            if self.params.getParameter("debug",CONTEXT_NAME).getSelectedValue() > 0:
                traceback.print_exc()

        #load and manage history file
        #FIXME move on start'up
        if self.params.getParameter("useHistory",ENVIRONMENT_NAME).getValue():
            try:
                readline.read_history_file(self.params.getParameter("historyFile",ENVIRONMENT_NAME).getValue())
            except IOError:
                pass
        
        #try to load keystore
        #FIXME move on start'up
        if self.params.getParameter("saveKeys",ENVIRONMENT_NAME).getValue():
            try:
                self.keystore.load()
            except Exception as ex:
                print "Fail to load keystore file: "+str(ex)
        
        #load other addon
        #FIXME move to onStartUp event when the event manager will be ready
        for addonName in self.params.getParameter("addonToLoad",ENVIRONMENT_NAME).getValue():
            try:
                addon.loadAddonFun(addonName, self.params)
            except ListOfException as loe:
                if len(loe.exceptions) > 0:
                    print("fail to load addon '"+str(addonName)+"': ")
                    for e in loe.exceptions:
                        print("    "+str(e))
            except Exception as ex:
                print("fail to load addon '"+str(addonName)+"': "+str(ex))

                if self.params.getParameter("debug",CONTEXT_NAME).getSelectedValue() > 0:
                    traceback.print_exc()
                
        #save at exit
        #FIXME move to atExit when the event manager will be ready
        atexit.register(self.saveParams)
        atexit.register(self.saveKeyStore)
        atexit.register(self.saveHistory)
    
    def saveHistory(self):
        if self.params.getParameter("useHistory",ENVIRONMENT_NAME).getValue():
            readline.write_history_file(self.params.getParameter("historyFile",ENVIRONMENT_NAME).getValue())
    
    def saveParams(self):
        if self.params.getParameter("useHistory",ENVIRONMENT_NAME).getValue():
            self.params.save()
            
    def saveKeyStore(self):
        if self.params.getParameter("saveKeys",ENVIRONMENT_NAME).getValue():
            self.keystore.save()
        
    #
    #
    # @return, true if no severe error or correct process, false if severe error
    #
    def executeCommand(self,cmd):
        ## init, parse and check the string list ##
        
        #TODO update vars, if exist use it, otherelse, put a None value or something like that
        cmdStringList = _parseLine(cmd,self.params.getParameter("vars", ENVIRONMENT_NAME).getValue())

        #if empty list after parsing, nothing to execute
        if len(cmdStringList) == 0:
            return False

        #define console coloration function
        if self.params.getParameter("execution",CONTEXT_NAME).getSelectedValue() == "shell":
            _severe = red
            _warning = orange
        else:
            _severe = nocolor
            _warning = nocolor

        ## look after command in tries ##
        rawCommandList = []   
        rawArgList     = []
        for finalCmd in cmdStringList:            
            #search the command with advanced seach
            searchResult = None
            try:
                searchResult = self.params.getParameter("levelTries",ENVIRONMENT_NAME).getValue().advancedSearch(finalCmd, False)
            except triesException as te:
                print(_warning("failed to find the command '"+str(finalCmd)+"', reason: "+str(te)))
                return False
            
            if searchResult.isAmbiguous():                    
                tokenIndex = len(searchResult.existingPath) - 1
                tries = searchResult.existingPath[tokenIndex][1].localTries
                keylist = tries.getKeyList(finalCmd[tokenIndex])

                print(_warning("ambiguity on command '"+" ".join(finalCmd)+"', token '"+str(finalCmd[tokenIndex])+"', possible value: "+ ", ".join(keylist)))

                return False
            elif not searchResult.isAvalueOnTheLastTokenFound():
                if searchResult.getTokenFoundCount() == len(finalCmd):
                    print(_warning("uncomplete command '"+" ".join(finalCmd)+"', type 'help "+" ".join(finalCmd)+"' to get the next available parts of this command"))
                else:
                    if len(finalCmd) == 1:
                        print(_warning("unknown command '"+" ".join(finalCmd)+"', type 'help' to get the list of commands"))
                    else:
                        print(_warning("unknown command '"+" ".join(finalCmd)+"', token '"+str(finalCmd[searchResult.getTokenFoundCount()])+"' is unknown, type 'help' to get the list of commands"))
                
                return False

            #append in list
            rawCommandList.append(searchResult.getLastTokenFoundValue())
            rawArgList.append(searchResult.getNotFoundTokenList())
        
        ## execute the engine object ##
        try:
            engine = engineV3(rawCommandList, rawArgList, self.params)
            engine.execute()
            return True
            
        except executionInitException as eie:
            print(_severe("Fail to init an execution object: "+str(eie.value)))
        except executionException as ee:
            print(_severe("Fail to execute: "+str(eie.value)))
        except commandException as ce:
            print(_severe("Error in command method: "+str(ce.value)))
        except engineInterruptionException as eien:
            if eien.abnormal:
                print(_severe("Abnormal execution abort, reason: "+str(eien.value)))
            else:
                print(_warning("Normal execution abort, reason: "+str(eien.value)))
        except argException as ae:
            print(_warning("Error in parsing argument: "+str(ae.value)))
        except ListOfException as loe:
            if len(loe.exceptions) > 0:
                print(_severe("List of exception:"))
                for e in loe.exceptions:
                    print(_warning("    "+str(e)))
        except Exception as e:
            print(_severe(str(e)))

        #print stack trace if debug is enabled
        if self.params.getParameter("debug",CONTEXT_NAME).getSelectedValue() > 0:
            traceback.print_exc()

        return False
    
    def mainLoop(self):
        #enable autocompletion
        if 'libedit' in readline.__doc__:
            import rlcompleter
            readline.parse_and_bind ("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")

        readline.set_completer(self.complete)
        
        self.params.getParameter("execution", CONTEXT_NAME).setIndexValue("shell")
        
        #mainloop
        while True:
            #read prompt
            try:
                sys.stdout = self.writer.out
                cmd = raw_input(self.params.getParameter("prompt",ENVIRONMENT_NAME).getValue())
            except SyntaxError:
                print "   syntax error"
                continue
            except EOFError:
                print "\n   end of stream"
                break
            finally:
                sys.stdout = self.writer    
            
            
            #execute command
            self.executeCommand(cmd)        
    
    ###############################################################################################
    ##### Readline REPL ###########################################################################
    ###############################################################################################
    def printAsynchronousOnShell(self,EventToPrint):
        print ""
        print "   "+EventToPrint

        #this is needed because after an input, the readline buffer isn't always empty
        if len(readline.get_line_buffer()) == 0 or readline.get_line_buffer()[-1] == '\n':
            sys.stdout.write(self.params.getParameter("prompt",ENVIRONMENT_NAME).getValue())
        else:
            sys.stdout.write(self.params.getParameter("prompt",ENVIRONMENT_NAME).getValue() + readline.get_line_buffer())

        sys.stdout.flush()
        
    def complete(self,suffix,index):
        cmdStringList = _parseLine(readline.get_line_buffer(),None)

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
            
        #TODO is it normal to catch exception like this here ?
        except Exception as ex:
            import traceback,sys
            print traceback.format_exc()

        return None

    def executeFile(self,filename):
        shellOnExit = False
        self.params.getParameter("execution", CONTEXT_NAME).setIndexValue("script")
        
        try:
            with open(filename, 'wb') as f:
                config.write(configfile)
                
                for line in f:
                    if line.trim() == "noexit":
                        shellOnExit = True
                
                    self.executeCommand(line)
        except Exception as ex:
            print("An error occured during the script execution: "+str(ex))
        
        return shellOnExit

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

