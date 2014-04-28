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
from arg.exception import *

##history file
#load history file
histfile = os.path.join(os.path.expanduser("~"), ".rfidShell") #TODO devrait etre parametrable
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
        self.environment["prompt"]     = ":>"
        self.environment["printer"]    = self
        self.environment["executer"]   = self
        self.levelTries                = multiLevelTries()
        self.environment["levelTries"] = self.levelTries
        self.environment["debug"]      = False
        
        #TODO try to load standard shell function
   
   #TODO ces methodes doivent se retrouver dans le module standardShell (il faut le créer)
    """def addCommand(self,CommandStrings,preProcess=None,process=None,postProcess=None,showInHelp=True):
        #build the command name
        name = " ".join(CommandStrings)
        
        #the helping message will be the message of the starting point
        if preProcess != None :
            helpMsg = preProcess.__doc__
        elif process != None:
            helpMsg = process.__doc__
        elif postProcess != None:
            helpMsg = postProcess.__doc__
        else:
            helpMsg = "this command do nothing"
        
        #build the command
        c = UniCommand(name,helpMsg,preProcess,process,postProcess,showInHelp)
        
        #add the command into the tries
        try:
            self.levelTries.insert(CommandStrings,c)
            return c
        except triesException as e:
            print self.printOnShell(str(e))
            return None"""
            
    """def addMultiCommand(self,CommandStrings,helpMessage,showInHelp=True):
        #build the command name
        name = " ".join(CommandStrings)
        
        #create the command 
        c = MultiCommand(name,helpMessage,showInHelp)
        
        #add the command into the tries
        try:
            self.levelTries.insert(CommandStrings,c)
            return c
        except triesException as e:
            print self.printOnShell(str(e))
            return None"""
            
    """def addAlias(self,CommandStrings,AliasCommandStrings):
        #pas aussi simple
            #on doit pouvoir gerer des alias avec des arguments fixe
        
        #commande speciale
            #contient le path vers la commande
            #les arguments ou une partie des arguments
        
        #TODO CommandStrings can't contain special token : >, >>, |, ...
        
        #TODO find the command in the tree
        
        #TODO build alias command
        
        #TODO insert in tree
        
        pass #TODO"""
    
    #
    #
    # @return, true if no severe error or correct process, false if severe error
    #
    def executeCommand(self,cmd):
        ### STEP 1: split on pipe ### 
        cmd = cmd.split("|")
        if len(cmd) < 0 :
            print "   split command error"
            return False
        
        ### STEP 2: split on space AND look for command ###
        rawCommandList = []   
        for inner in cmd:
            #remove blank char
            inner = inner.strip(' \t\n\r')
            if len(inner) == 0:
                continue
            
            #split on space
            inner = inner.split(" ")
            if len(inner) < 0 :
                print "   split command error"
                rawCommandList = []
                break
            
            #fo each token
            finalCmd = []
            for cmd in inner:
                cmd = cmd.strip(' \t\n\r')
                if len(cmd) == 0 :
                    continue
                
                finalCmd.append(cmd)
            
            #is there a non empty token list ?
            if len(finalCmd) > 0:
                #TODO search the command with advanced seach
                
                #TODO manage exception
                
                #TODO set the args to the function
                
                #TODO append in rawCommandList
                
                pass
                
                """try:
                    #TODO search will fail, need to make an advanced mltries search
                
                    triesNode,args = self.levelTries.search(finalCmd) #args est une liste
                    rawCommandList.append((triesNode.value,args))
                except triesException as e:
                    self.printOnShell(str(e))
                    return True"""
        
        #if the command list is empty, nothing to execute, stop here
        if len(rawCommandList) == 0:
            return False
        
        #TODO execute command engine
        
        #TODO create engine object
        
        #TODO execute engine object
        
        #TODO manage the exception
        
        pass
    
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

