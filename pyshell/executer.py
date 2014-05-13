#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2012  Jonathan Delvaux <jonathan.delvaux@uclouvain.be>

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
#import traceback

#custom library
from tries import multiLevelTries
from tries.exception import triesException
from command.exception import *
from command.engine import engineV3
from arg.exception import *
from addons import stdaddons

##history file
#load history file
histfile = os.path.join(os.path.expanduser("~"), ".pyshell") #TODO le file name devrait etre parametrable
try:
    readline.read_history_file(histfile)
except IOError:
    pass

#save history file at exit
import atexit
atexit.register(readline.write_history_file, histfile)
del os, histfile      

class CommandExecuter():
    def __init__(self):
        self.environment               = {}
        self.environment["prompt"]     = "pyshell:>"
        self.environment["printer"]    = self
        self.environment["executer"]   = self
        self.levelTries                = multiLevelTries()
        self.environment["levelTries"] = self.levelTries
        self.environment["debug"]      = False
        
        #try to load standard shell function
        try:
            stdaddons._loader._load(self.environment["levelTries"])
        except Exception as ex:
            print "failed to load standard addon: "+str(ex)
    #
    #
    # @return, true if no severe error or correct process, false if severe error
    #
    def executeCommand(self,cmd):
        ### STEP 1: split on pipe ### 
        cmd = cmd.split("|")
        if len(cmd) < 0 :
            print "   split command error (pipe)"
            return False
        
        ### STEP 2: split on space AND look for command ###
        rawCommandList = []   
        rawArgList     = []
        for inner in cmd:
            #remove blank char
            inner = inner.strip(' \t\n\r')
            if len(inner) == 0:
                continue
            
            #split on space
            inner = inner.split(" ")
            if len(inner) < 0 :
                print "   split command error (space)"
                return False
            
            #fo each token
            finalCmd = []
            for cmd in inner:
                cmd = cmd.strip(' \t\n\r')
                if len(cmd) == 0 :
                    continue
                
                finalCmd.append(cmd)
            
            #is there a non empty token list ?
            if len(finalCmd) > 0:
                #search the command with advanced seach
                searchResult = None
                try:
                    searchResult = self.levelTries.advancedSearch(finalCmd, False)
                except triesException as te:
                    print "failed to find the command <"+str(finalCmd)+">, reason: "+str(te)
                    return False
                
                if searchResult.isAmbiguous():
                    print "ambiguity"#TODO show the different possibility
                    
                    #TODO get tries index in result and get corresponding advancedTriesResult
                    advancedTriesResult = searchResult.getAdvancedTriesResult(searchResult.getTokenUsed() - 1)
                    
                    #TODO generate corresponding value
                    
                    #TODO print them
                    
                    return False
                elif not searchResult.isAvalueOnTheLastTokenFound():
                    self.printOnShell("unknown command <"+" ".join(finalCmd)+">")
                    return False

                #append in list
                rawCommandList.append(searchResult.getLastTokenFoundValue())
                rawArgList.append(searchResult.getNotFoundTokenList())
        
        #if the command list is empty, nothing to execute, stop here
        if len(rawCommandList) == 0 or len(rawArgList) == 0:
            return False
        
        #execute the engine object
        try:
            engine = engineV3(rawCommandList, rawArgList, self.environment)
            engine.execute()
            return True
        except executionInitException as eie:
            self.printOnShell("Fail to init an execution object: "+str(eie.value))
        except executionException as ee:
            self.printOnShell("Fail to execute: "+str(eie.value))
        except commandException as ce:
            self.printOnShell("Error in command method: "+str(ce.value))
        except engineInterruptionException as eien:
            if eien.abnormal:
                self.printOnShell("Abnormal execution abort, reason: "+str(eien.value))
            else:
                self.printOnShell("Normal execution abort, reason: "+str(eien.value))
        except argException as ae:
            self.printOnShell("Error in parsing argument: "+str(ae.value))
        except Exception as e:
            self.printOnShell("Unknown error: "+str(e))
            
        return False
    
    def mainLoop(self):
        while True:
            #enable autocompletion
                #TODO need to do that at every iteration ???
            if(sys.platform == 'darwin'):
                import rlcompleter
                readline.parse_and_bind ("bind ^I rl_complete")
            else:
                readline.parse_and_bind("tab: complete")
            readline.set_completer(self.complete)
            
            #read prompt
            try:
                cmd = raw_input(self.environment["prompt"])
            except SyntaxError:
                print "   syntax error"
                continue
            except EOFError:
                print "\n   end of stream"
                break
            
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
            sys.stdout.write(environment["prompt"])
        else:
            sys.stdout.write(environment["prompt"] + readline.get_line_buffer())

        sys.stdout.flush()
    
    #TODO convert into write function from output
        #to be able to output on any output stream
    def printOnShell(self,toPrint):
        print "   "+str(toPrint)
        
    def complete(self,prefix,index):
        #TODO pas encore au point
        
        args = prefix.split(" ")
        if len(args) < 0 :
            print "   split command error"
            return None
        StartNode = None
        if len(args) > 0:
            try:
                #TODO, la methode searchEntryFromMultiplePrefix ne semble pas adaptee pour ici
                
                StartNode,args = environment["levelTries"].searchEntryFromMultiplePrefix(args,True)
                print StartNode.getCompleteName()
            except triesException as e:
                print "   "+str(e)
                return None
        if StartNode == None:
            StartNode = environment["levelTries"].levelOneTries
    
        key = StartNode.getAllPossibilities().keys()
        #print key
        try:
            return key[index]
        except IndexError:
            return None

    def executeFile(self,filename):
        f = open(filename, "r")
        exitOnEnd = True
        for line in f:
            print environment["prompt"]+line.strip('\n\r')
            if line.startswith("noexit"):
                exitOnEnd = False
            elif not self.executeCommand(line):
                break
                
        return exitOnEnd

if __name__ == "__main__":
    executer = CommandExecuter()
    executer.mainLoop()

