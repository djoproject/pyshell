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

import threading, sys, re, os
from pyshell.utils.valuable   import Valuable, DefaultValuable, SelectableValuable
from pyshell.utils.exception  import NOTICE, WARNING, PyshellException
from pyshell.utils.constants  import CONTEXT_EXECUTION_SHELL, CONTEXT_COLORATION_DARK, CONTEXT_COLORATION_LIGHT

_EMPTYSTRING = ""

#http://misc.flogisoft.com/bash/tip_colors_and_formatting
LIGHTMAUVE     = '\033[95m'
LIGHTBLUE      = '\033[94m'
LIGHTGREEN     = '\033[92m'
LIGHTORANGE    = '\033[93m'
LIGHTRED       = '\033[91m'

DARKMAUVE      = '\033[35m'
DARKBLUE       = '\033[34m'
DARKGREEN      = '\033[32m'
DARKORANGE     = '\033[33m'
DARKRED        = '\033[31m'

ENDC           = '\033[0m'
BOLT           = '\033[1m'
UNDERLINE      = '\033[4m'

ANSI_ESCAPE = re.compile(r'\x1b[^m]*m')

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
        self.backgroundContext   = DefaultValuable(None)
    
    def __enter__(self):
        return Printer._printerLock.__enter__()
        
    def __exit__(self, type, value, traceback):
        return Printer._printerLock.__exit__(type, value, traceback)
    
    def setREPLFunction(self, fun):
        if not hasattr(fun, "__call__"):
            raise Exception("(Printer) setREPLFunction, invalid repl function, must be a callable object")
            
        self.replWriteFunction = fun
    
    def setShellContext(self, context):    
        if not isinstance(context, SelectableValuable):
            raise Exception("(Printer) setShellContext, invalid shell context, must be an instance of SelectableValuable")
    
        self.shellContext = context
    
    def setPromptShowedContext(self, context):    
        if not isinstance(context, Valuable):
            raise Exception("(Printer) setPromptShowedContext, invalid running context, must be an instance of Valuable")
    
        self.promptShowedContext = context
        
    def setSpacingContext(self, context):    
        if not isinstance(context, Valuable):
            raise Exception("(Printer) setSpacingContext, invalid spacing context, must be an instance of Valuable")
    
        self.spacingContext = context
        
    def setBakcgroundContext(self, context):
        if not isinstance(context, SelectableValuable):
            raise Exception("(Printer) setBakcgroundContext, invalid background context, must be an instance of SelectableValuable")
    
        self.backgroundContext = context
    
    def isDarkBackGround(self):
        return self.backgroundContext.getSelectedValue() == CONTEXT_COLORATION_DARK
        
    def isLightBackGround(self):
        return self.backgroundContext.getSelectedValue() == CONTEXT_COLORATION_LIGHT
    
    def isInShell(self):
        return self.shellContext.getSelectedValue() == CONTEXT_EXECUTION_SHELL
    
    def isPromptShowed(self):
        return self.promptShowedContext.getValue()
    
    @staticmethod
    def getInstance():
        if Printer._instance is None:
            with Printer._printerLock:
                if Printer._instance is None:
                    Printer._instance = Printer()
                    
        return Printer._instance

    def cprint(self, out):
        if out is None:
            return
        
        #remove ansi annotation if not in shell mode or if stdout is redirected to a file
        if not self.isInShell() or ( not self.isDarkBackGround() and not self.isLightBackGround()) or not (os.fstat(0) == os.fstat(1)):
            out = ANSI_ESCAPE.sub('', str(out))
        
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
    
    def _formatColor(self, text, light, dark):
        if not self.isInShell():
            return text

        if self.isLightBackGround():
            return light+text+ENDC
        
        if self.isDarkBackGround():
            return dark+text+ENDC
            
        return text

    def _format(self, text, effect):
        if not self.isInShell():
            return text
            
        return effect+text+ENDC

    def formatRed(self, text):
        return self._formatColor(text, LIGHTRED, DARKRED)
        
    def formatBlue(self, text):
        return self._formatColor(text, LIGHTBLUE, DARKBLUE)
        
    def formatGreen(self, text):
        return self._formatColor(text, LIGHTGREEN, DARKGREEN)
        
    def formatOrange(self, text):
        return self._formatColor(text, LIGHTORANGE, DARKORANGE)
        
    def formatMauve(self, text):
        return self._formatColor(text, LIGHTMAUVE, DARKMAUVE)
        
    def formatBolt(self, text):
        return self._format(text, BOLT)
        
    def formatUnderline(self, text):
        return self._format(text, UNDERLINE)
        
    def info(self, string):
        self.cprint(string)
    
    def notice(self, string):
        self.cprint(self.formatGreen(string))
        
    def warning(self, string):
        self.cprint(self.formatOrange(string))
        
    def error(self, string):
        self.cprint(self.formatRed(string))
        
    def debug(self, string):
        self.cprint(self.formatOrange(string))
    
def _toLineString(args, kwargs):
    s = ' '.join(str(x) for x in args)
    s2 = ', '.join(str(k)+"="+str(v) for k,v in kwargs.items())
    
    if len(s) > 0:
        if len(s2) > 0:
            return s + " " + s2
        return s
    return s2 

def formatRed(text):
    printer = Printer.getInstance()
    return printer.formatRed(text)

def formatBlue(text):
    printer = Printer.getInstance()
    return printer.formatBlue(text)
    
def formatGreen(text):
    printer = Printer.getInstance()
    return printer.formatGreen(text)
    
def formatOrange(text):
    printer = Printer.getInstance()
    return printer.formatOrange(text)
    
def formatMauve(text):
    printer = Printer.getInstance()
    return printer.formatMauve(text)
    
def formatBolt(text):
    printer = Printer.getInstance()
    return printer.formatBolt(text)
    
def formatUnderline(text):
    printer = Printer.getInstance()
    return printer.formatUnderline(text)

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
            return notice
        elif exception.severity >= WARNING:
            warning(prefix + str(exception) + stackTrace)
            return warning

    error(prefix + str(exception) + stackTrace)
    return error

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
    return len(ANSI_ESCAPE.sub('', str(string)))


