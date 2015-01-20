#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject,net>

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

#BNF GRAMMAR OF A COMMAND
# 
## RULE 1 ## <commands>  ::= <command> <threading> <EOL> | <command> "|" <commands>
## RULE 2 ## <threading> ::= " &" | ""
## RULE 3 ## <command>   ::= <token> | <token> " " <command>
## RULE 4 ## <token>     ::= <string> | "$" <string> | "\$" <string> | "-" <text> | "-" <text> <string> | "\-" <string>
## RULE 5 ## <string>    ::= <text> | <text> "\ " <string> #TODO conflict with command rule
#
#

#TODO
    #finish the grammar then refactor the parsing system

    #firing/executing system
        #for piped command
            #with a "&" at the end of a script line
            #with a "fire" at the beginning of a script line

        #with only an alias name
            #with one of the two solution above
            #with a specific command from alias addon 

    #keep track of running event and be able to kill one or all of them
        #manage it in alias object with a static list
            #an alias add itself in the list before to start then remove itself from the list at the end of its execution

class Parser(list):
    "This object will parse a command line withou any resolution of process, argument, or parameter"
    
    def __init__(self,string):
        list.__init__(self)
        self.currentToken    = None
        self.currentCommand  = []
        self.argSpotted      = [] #TODO
        self.paramSpotted    = [] #TODO
        self._innerParser    = self._subParseNoToken
        self.string          = string
        self.escapeChar      = False
        self.runInBackground = False
        self.isParsed        = False #TODO

    def _pushCommandInList(self):
        if len(self.currentCommand) > 0:
            self.append(self.currentCommand)
            self.currentCommand = []
    
    def _pushTokenInCommand(self):
        if self.currentToken is not None:
            if len(self.currentToken) > 0:
                self.currentCommand.append(self.currentToken)
            
            self.currentToken = None
            self._innerParser = self._subParseNoToken

    def _subParseNoToken(self,char):
        if char == ' ':
            return
            
        if char == '|':
            self._pushCommandInList()
            return
            
        self.currentToken = ""
        
        if char == '"':
            self._innerParser = self._subParseWrappedToken
            return
            
        self._innerParser = self._subParseToken

        if char == '\\':
            self.escapeChar = True
        else:
            self.currentToken += char
        
        if char == '$':
            argSpotted.append(len(currentCommand))
        elif char == '-':
            paramSpotted.append(len(currentCommand))
        
    def _subParseWrappedToken(self,char):
        if self.escapeChar:
            self.currentToken += char
            self.escapeChar    = False
            return
    
        if char == '\\':
            self.escapeChar = True
        elif char == '"':
            self._innerParser = self._subParseWrappedTokenEnd
        else:
            self.currentToken += char
            
    def _subParseWrappedTokenEnd(self, char):
        if char in (' ','|',):
            self._pushTokenInCommand()
            self._innerParser = self._subParseNoToken
            self._subParseNoToken(char)
        else:
            self._innerParser = self._subParseToken
            self._subParseToken(char)
        
    def _subParseToken(self,char):
        if self.escapeChar:
            self.currentToken += char
            self.escapeChar    = False
            return
            
        if char == '\\':
            self.escapeChar    = True
        elif char == '"':
            self._innerParser = self._subParseWrappedToken
        elif char == ' ' or char == '|':
            self._pushTokenInCommand()
                
            if char == '|':
                self._pushCommandInList()
        else:
            self.currentToken += char

    def parse(self):
        del self[:]
    
        if self.string is None:
            return
            
        if type(self.string) != str and type(self.string) != unicode:
            pass #raise
            
        self.string = self.string.strip(' \t\n\r')
        
        if len(self.string) == 0:
            return
                
        for i in xrange(0,len(self.string)):
            char = self.string[i]
            self._innerParser(char)    
            
        #push intermediate data
        self._pushTokenInCommand()
        self._pushCommandInList()
        
        #compute runInBackground
        if len(self) > 0:
            if self[-1][-1] == '&':
                self.runInBackground = True
                del self[-1][-1]
            elif self[-1][-1][-1] == '&':
                self.runInBackground = True
                self[-1][-1] = self[-1][-1][:-1]
            
    def isToExecuteInAnotherThread(self):
        return self.runInBackground

class Solver(object):
    pass #TODO
    
class Executer(object):
    pass #TODO

        

