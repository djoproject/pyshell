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
import readline
import os
import sys

#custom library
from tries import multiLevelTries
from tries.exception import triesException, pathNotExistsTriesException
from command.exception import *
from command.engine import engineV3
from arg.exception import *
from arg.argchecker import booleanValueArgChecker, stringArgChecker, IntegerArgChecker
from addons import stdaddons
from utils.parameter import ParameterManager, DEFAULT_PARAMETER_FILE, EnvironmentParameter, GenericParameter, ContextParameter

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

            if cmd.startswith("$") and len(cmd) > 1:
                if cmd[1:] not in args:
                    print("Unknown var <"+cmd[1:]+">")
                    return ()

                finalCmd.extend(args[cmd[1:]])

            elif cmd.startswith("\$"):
                finalCmd.append(cmd[1:])
            else:
                finalCmd.append(cmd)

        if len(finalCmd) == 0:
            continue

        toret.append(finalCmd)

    return toret

class CommandExecuter():
    def __init__(self, paramFile = None, useHistory = True):
        #create param manager
        self.params = ParameterManager(paramFile)

        #init original params
        self.params.setEnvironement("prompt", EnvironmentParameter(value="pyshell:>", typ=stringArgChecker(),transient=False,readonly=False, removable=False))
        self.params.setParameter("vars", GenericParameter(value={},transient=True,readonly=True, removable=False))
        self.params.setParameter("levelTries", GenericParameter(value=multiLevelTries(),transient=True,readonly=True, removable=False))
        self.params.setContext("debug", ContextParameter(value=(1,2,3,4,5,), typ=IntegerArgChecker(), transient = False, transientIndex = False, defaultIndex = 0))
        self.params.setEnvironement("historyFile", EnvironmentParameter(value=os.path.join(os.path.expanduser("~"), ".pyshell_history"), typ=stringArgChecker(),transient=False,readonly=False, removable=False))

        #TODO try to load parameter file

        #TODO save at exit

        #load and manage history file
        if useHistory:
            #TODO historyFile must be define and exist
        
            try:
                readline.read_history_file(self.params.getEnvironment("historyFile").getValue())
            except IOError:
                pass

            #save history file at exit
            import atexit
            atexit.register(readline.write_history_file, self.params.getEnvironment("historyFile").getValue())
            del atexit 
            
        #try to load standard shell function
        try:
            stdaddons._loader[None]._load(self.params.getParameter("levelTries").getValue())
        except Exception as ex:
            print "failed to load standard addon: "+str(ex)
        
        #redirect output
        real_out    = sys.stdout
        self.writer = writer(real_out)
        sys.stdout  = self.writer
    #
    #
    # @return, true if no severe error or correct process, false if severe error
    #
    def executeCommand(self,cmd):
        ### STEP 1: split 
        cmdStringList = _parseLine(cmd,self.params.getParameter("vars").getValue())

        #if empty list after parsing, nothing to execute
        if len(cmdStringList) == 0:
            return False

        rawCommandList = []   
        rawArgList     = []
        for finalCmd in cmdStringList:            
            #search the command with advanced seach
            searchResult = None
            try:
                searchResult = self.params.getParameter("levelTries").getValue().advancedSearch(finalCmd, False)
            except triesException as te:
                print "failed to find the command <"+str(finalCmd)+">, reason: "+str(te)
                return False
            
            if searchResult.isAmbiguous():                    
                tokenIndex = len(searchResult.existingPath) - 1
                tries = searchResult.existingPath[tokenIndex][1].localTries
                keylist = tries.getKeyList(finalCmd[tokenIndex])

                print("ambiguity on command <"+" ".join(finalCmd)+">, token <"+str(finalCmd[tokenIndex])+">, possible value: "+ ", ".join(keylist))

                return False
            elif not searchResult.isAvalueOnTheLastTokenFound():
                if searchResult.getTokenFoundCount() == len(finalCmd):
                    print("uncomplete command <"+" ".join(finalCmd)+">, type <help "+" ".join(finalCmd)+"> to get the next available parts of this command")
                else:
                    if len(finalCmd) == 1:
                        print("unknown command <"+" ".join(finalCmd)+">, type <help> to get the list of commands")
                    else:
                        print("unknown command <"+" ".join(finalCmd)+">, token <"+str(finalCmd[searchResult.getTokenFoundCount()])+"> is unknown, type <help> to get the list of commands")
                
                return False

            #append in list
            rawCommandList.append(searchResult.getLastTokenFoundValue())
            rawArgList.append(searchResult.getNotFoundTokenList())
        
        #execute the engine object
        try:
            engine = engineV3(rawCommandList, rawArgList, self.params)
            engine.execute()
            return True
            
        #TODO print stack trace if debug is enabled
        except executionInitException as eie:
            print("Fail to init an execution object: "+str(eie.value))
        except executionException as ee:
            print("Fail to execute: "+str(eie.value))
        except commandException as ce:
            print("Error in command method: "+str(ce.value))
        except engineInterruptionException as eien:
            if eien.abnormal:
                print("Abnormal execution abort, reason: "+str(eien.value))
            else:
                print("Normal execution abort, reason: "+str(eien.value))
        except argException as ae:
            print("Error in parsing argument: "+str(ae.value))
        #except Exception as e:
        #    print("Unknown error: "+str(e))

        return False
    
    def mainLoop(self):
        #enable autocompletion
        if 'libedit' in readline.__doc__:
            import rlcompleter
            readline.parse_and_bind ("bind ^I rl_complete")
        else:
            readline.parse_and_bind("tab: complete")

        readline.set_completer(self.complete)

        #mainloop
        while True:
            #read prompt
            try:
                sys.stdout = self.writer.out
                cmd = raw_input(self.params.getEnvironment("prompt").getValue())
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
            sys.stdout.write(self.params.getEnvironment("prompt").getValue())
        else:
            sys.stdout.write(self.params.getEnvironment("prompt").getValue() + readline.get_line_buffer())

        sys.stdout.flush()
        
    def complete(self,suffix,index):
        #TODO ça ne marche pas encore genial avec les $vars, voir fichier de bug
    
        cmdStringList = _parseLine(readline.get_line_buffer(),self.params.getParameter("vars").getValue())

        try:
            ## special case, empty line ##
                #only print root tokens
            if len(cmdStringList) == 0:
                fullline = ()
                dic = self.params.getParameter("levelTries").getValue().buildDictionnary(fullline, True, True, False)

                toret = {}
                for k in dic.keys():
                    toret[k[0]] = None

                toret = toret.keys()[:]
                toret.append(None)
                return toret[index]

            fullline = cmdStringList[-1]

            ## manage ambiguity ##
            advancedResult = self.params.getParameter("levelTries").getValue().advancedSearch(fullline, False)
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
                    dic = self.params.getParameter("levelTries").getValue().buildDictionnary(fullline, True, True, False)
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
            import traceback,sys
            print traceback.format_exc()

        return None

    #TODO
    """def executeFile(self,filename):
        f = open(filename, "r")
        exitOnEnd = True
        for line in f:
            print self.params.getEnvironment("prompt").getValue()+line.strip('\n\r')
            if line.startswith("noexit"):
                exitOnEnd = False
            elif not self.executeCommand(line):
                break
                
        return exitOnEnd"""

if __name__ == "__main__":
    #run basic instance
    executer = CommandExecuter(DEFAULT_PARAMETER_FILE)
    executer.mainLoop()

