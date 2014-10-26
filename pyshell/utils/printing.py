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
    #disable coloration if redirect to file
        #os.fstat(0) == os.fstat(1)
        #http://stackoverflow.com/questions/1512457/determining-if-stdout-for-a-python-process-is-redirected

    #coloration system should be moved here and only used here
        #with a kind of formating method

import threading, sys
from pyshell.utils.valuable   import Valuable, DefaultValuable
from pyshell.utils.coloration import red, orange, green
from pyshell.utils.exception  import NOTICE, WARNING, PyshellException
import re

_EMPTYSTRING = ""

class Printer(object):
    _printerLock = threading.RLock()
    _instance = None

    def __init__(self):
        if Printer._instance is not None:
            raise Exception("(Printer) __init__, Try to create a new instance of printer, only one is allowed for a whole instance of this application, use getInstance method")
    
        self.replWriteFunction   = None
        self.shellContext        = DefaultValuable(None)
        self.promptShowedContext = DefaultValuable(False)
        self.spacingContext      = DefaultValuable(0)
    
    def __enter__(self):
        return Printer._printerLock.__enter__()
        
    def __exit__(self, type, value, traceback):
        return Printer._printerLock.__exit__(type, value, traceback)
    
    def setREPLFunction(self, fun):
        if not hasattr(fun, "__call__"):
            raise Exception("(Printer) setREPLFunction, invalid repl function, must be a callable object")
            
        self.replWriteFunction = fun
    
    def setShellContext(self, context):    
        if not isinstance(context, Valuable):
            raise Exception("(Printer) setShellContext, invalid shell context, must be an instance of valuable")
    
        self.shellContext = context
    
    def setPromptShowedContext(self, context):    
        if not isinstance(context, Valuable):
            raise Exception("(Printer) setPromptShowedContext, invalid running context, must be an instance of valuable")
    
        self.promptShowedContext = context
        
    def setSpacingContext(self, context):    
        if not isinstance(context, Valuable):
            raise Exception("(Printer) setSpacingContext, invalid spacing context, must be an instance of valuable")
    
        self.spacingContext = context
    
    def isInShell(self): #FIXME valuable does not have getSelectedValue method...
        return self.shellContext.getSelectedValue() == "shell"
    
    def isPromptShowed(self):
        return self.promptShowedContext.getValue()
    
    @staticmethod
    def getInstance():
        if Printer._instance is None:
            with Printer._printerLock:
                if Printer._instance is None:
                    Printer._instance = Printer()
                    
        return Printer._instance

    def _print(self, out):
        if out is None:
            return
        
        #TODO remove ansi annotation if not in shell mode or if stdout is redirected to a file
        
        outs = out.split("\n")
        out = ""
        space = " " * self.spacingContext.getValue()
        for o in outs:
            out += space + o + "\n"
            
        out = out[:-1]
        
        with Printer._printerLock:
            if self.isInShell() and self.isPromptShowed() and self.replWriteFunction is not None:
                self.replWriteFunction(out)
            else:
                print(out)
    
    def info(self, string):
        self._print(string)
    
    def notice(self, string):
        if self.isInShell():
            self._print(green(string))
        else:
            self._print(string)
        
    def warning(self, string):
        if self.isInShell():
            self._print(orange(string))
        else:
            self._print(string)
        
    def error(self, string):
        if self.isInShell():
            self._print(red(string))
        else:
            self._print(string)
        
    def debug(self, string):
        if self.isInShell():
            self._print(orange(string))
        else:
            self._print(string)
    
def _toLineString(args, kwargs):
    s = ' '.join(str(x) for x in args)
    s2 = ', '.join(str(k)+"="+str(v) for k,v in kwargs.items())
    
    if len(s) > 0:
        if len(s2) > 0:
            return s + " " + s2
        return s
    return s2 

def printShell(*args, **kwargs):
    printer = Printer.getInstance()
    printer.info(_toLineString(args, kwargs))

def info(*args, **kwargs):
    printShell(_toLineString(args, kwargs))

def notice(*args, **kwargs):
    printer = Printer.getInstance()
    printer.notice(_toLineString(args, kwargs))
    
def warning(*args, **kwargs):
    printer = Printer.getInstance()
    printer.warning(_toLineString(args, kwargs))
    
def error(*args, **kwargs):
    printer = Printer.getInstance()
    printer.error(_toLineString(args, kwargs))

def debug(*args, **kwargs):
    printer = Printer.getInstance()
    printer.debug(_toLineString(args, kwargs))
    
def printException(exception, prefix = None, stackTrace = None):
    if prefix is None:
        prefix = _EMPTYSTRING
        
    if stackTrace is None:
        stackTrace = _EMPTYSTRING
    else:
        stackTrace = "\n\n"+stackTrace

    if isinstance(exception, PyshellException):
        if exception.severity >= NOTICE:
            notice(prefix + str(exception) + stackTrace)
            return
        elif exception.severity >= WARNING:
            warning(prefix + str(exception) + stackTrace)
            return

    error(prefix + str(exception) + stackTrace)

def formatException(exception):
    printer = Printer.getInstance()
    if not self.isInShell():
        return str(exception)

    if isinstance(exception, PyshellException):
        if exception.severity >= NOTICE:
            return green(str(exception))
        elif exception.severity >= WARNING:
            return orange(str(exception))
        
        return red(str(exception))

def strLength(string):
    ansi_escape = re.compile(r'\x1b[^m]*m')
    return len(ansi_escape.sub('', str(string)))


