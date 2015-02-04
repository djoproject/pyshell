#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.utils.exception   import DefaultPyshellException, PARSE_ERROR

#BNF GRAMMAR OF A COMMAND
# 
## RULE 1 ## <commands>  ::= <command> <threading> <EOL> | <command> "|" <commands>
## RULE 2 ## <threading> ::= "&" | ""
## RULE 3 ## <command>   ::= <token> | <token> " " <command>
## RULE 4 ## <token>     ::= <text> | "$" <text> | "-" <text>
#

#TODO create escaping method
    #with wrapping or not
    #use it in parameter saving

def escapeString(string, wrapped = True):

    string.replace("\"","\\$")
    if wrapped:
    
    else:

    string.replace("$","\\$")
    string.replace("&","\\&")
    string.replace("|","\\|")
    string.replace("-","\\$")
    
    string.replace(" ","\\ ")
    string.replace("\t","\\\t")
    string.replace("\n","\\\n")
    string.replace("\r","\\\r")
    
    string.replace("\\","\\\\")
    return string

class Parser(list):
    "This object will parse a command line withou any resolution of process, argument, or parameter"
    
    def __init__(self,string):
        
        if type(string) != str and type(string) != unicode:
            raise DefaultPyshellException("fail to init parser object, a string was expected, got '"+str(type(string))+"'",PARSE_ERROR)
    
        list.__init__(self)
        self.currentToken    = None
        self.currentCommand  = []
        self.argSpotted      = []
        self.paramSpotted    = []
        self.string          = string
        self.wrapped         = False

    def _pushCommandInList(self):
        if len(self.currentCommand) > 0:
            self.append(  (tuple(self.currentCommand),tuple(self.argSpotted),tuple(self.paramSpotted),)  )
            del self.currentCommand[:]
            del self.argSpotted[:]
            del self.paramSpotted[:]
    
    def _pushTokenInCommand(self):
        if self.currentToken is not None:
            if len(self.currentToken) > 0:
                self.currentCommand.append(self.currentToken)
            
                index = len(self.currentCommand) -1

                if index in self.argSpotted and (' ' in self.currentToken or len(self.currentToken) == 1):
                    self.argSpotted.remove(index)

                elif index in self.paramSpotted:
                    if (' ' in self.currentToken or len(self.currentToken) == 1):
                        self.paramSpotted.remove(index)
                    else:
                        try:
                            float(self.currentToken)
                            self.paramSpotted.remove(index)
                        except ValueError:
                            pass
            
            self.currentToken = None
            self.wrapped = False

    def _parse(self,char):
        if self.currentToken is None:
            if char in (' ','\t','\n','\r',):
                return
                
            if char == '|':
                self._pushCommandInList()
                return
                
            self.currentToken = ""

        if self.escapeChar:
            self.currentToken += char
            self.escapeChar    = False

        elif char == '\\':
            self.escapeChar    = True
        elif char == '"':
            self.wrapped = not self.wrapped
        elif not self.wrapped and char in (' ','|','\t','\n','\r',):
            self._pushTokenInCommand()
                
            if char == '|':
                self._pushCommandInList()
        elif char == '$' and len(self.currentToken) == 0:
            self.argSpotted.append(len(self.currentCommand))
            self.currentToken += char
        elif char == '-' and len(self.currentToken) == 0:
            self.paramSpotted.append(len(self.currentCommand))
            self.currentToken += char
        elif char == '&':
            self.lastBackground = (len(self), len(self.currentCommand), len(self.currentToken))
            self.currentToken += char
        else:
            self.currentToken += char

    def parse(self):
        del self[:]
        self.escapeChar      = False
        self.runInBackground = False
        self.parsed          = False
        self.lastBackground  = None
    
        self.string = self.string.strip(' \t\n\r')
        
        if len(self.string) == 0:
            return
                
        for i in xrange(0,len(self.string)):
            char = self.string[i]
            self._parse(char)    
            
        #push intermediate data
        self._pushTokenInCommand()
        self._pushCommandInList()
        
        #compute runInBackground
        if self.lastBackground is not None and len(self)-1 == self.lastBackground[0] and len(self[-1][0])-1 == self.lastBackground[1] and len(self[-1][0][-1])-1 == self.lastBackground[2]:
            self.runInBackground = True
            if len(self[-1][0][-1]) == 1:
                if len(self[-1][0]) == 1:
                    del self[-1] #remove command
                else:
                    del self[-1][0][-1] #remove token
            else:
                self[-1][0][-1] = self[-1][0][-1][:-1] #remove char
                
        self.parsed = True
            
    def isToRunInBackground(self):
        return self.runInBackground
        
    def isParsed(self):
        return self.parsed



