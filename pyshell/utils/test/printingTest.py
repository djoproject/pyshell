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

import unittest, sys
from pyshell.utils.printing  import Printer, LIGHTRED, ENDC, DARKRED, BOLT, _toLineString, formatException, LIGHTORANGE, LIGHTGREEN
from pyshell.utils.valuable  import SimpleValuable
from pyshell.utils.constants import CONTEXT_EXECUTION_SHELL,CONTEXT_EXECUTION_SCRIPT, CONTEXT_EXECUTION_DAEMON, CONTEXT_COLORATION_LIGHT, CONTEXT_COLORATION_DARK, CONTEXT_COLORATION_NONE
from pyshell.utils.exception import DefaultPyshellException, WARNING, NOTICE

class NewOutput(object):
    def __init__(self):
        self.lastOutPut = ""
        sys.stdout = self
        
    def write(self, data):
        self.lastOutPut += data
        
    def restore(self):
        sys.stdout = sys.__stdout__
        
    def flush(self):
        self.lastOutPut = ""

class PrintingTest(unittest.TestCase):
    def setUp(self):
        p = Printer.getInstance()
        
        self.shellContext = SimpleValuable(CONTEXT_EXECUTION_SHELL) #CONTEXT_EXECUTION_SHELL, CONTEXT_EXECUTION_SCRIPT, CONTEXT_EXECUTION_DAEMON
        p.setShellContext(self.shellContext)
        
        self.promptShowedContext = SimpleValuable(True) #True or False
        p.setPromptShowedContext(self.promptShowedContext)
        
        self.spacingContext = SimpleValuable(5) #an integer bigger than 0
        p.setSpacingContext(self.spacingContext)
        
        self.backgroundContext = SimpleValuable(CONTEXT_COLORATION_LIGHT) #CONTEXT_COLORATION_LIGHT, CONTEXT_COLORATION_DARK, CONTEXT_COLORATION_NONE
        p.setBakcgroundContext(self.backgroundContext)
        
        self.debugContext = SimpleValuable(0) #an integer between [0,5]
        p.setDebugContext(self.debugContext)
    
    def test_getInstance(self):
        p = Printer.getInstance()
        p2 = Printer.getInstance()
        self.assertEqual(p,p2)
    
    def test_setShellContext(self):
        self.assertRaises(Exception, Printer.getInstance().setShellContext, ("plop",))
    
    def test_setPromptShowedContext(self):
        self.assertRaises(Exception, Printer.getInstance().setPromptShowedContext, ("plop",))
        
    def test_setSpacingContext(self):
        self.assertRaises(Exception, Printer.getInstance().setSpacingContext, ("plop",))
        
    def test_setBakcgroundContext(self):
        self.assertRaises(Exception, Printer.getInstance().setBakcgroundContext, ("plop",))
        
    def test_setDebugContext(self):
        self.assertRaises(Exception, Printer.getInstance().setDebugContext, ("plop",))
    
    def test_isDarkBackGround(self):
        p = Printer.getInstance()
        self.backgroundContext.setValue(CONTEXT_COLORATION_DARK)
        self.assertTrue(p.isDarkBackGround())
    
        self.backgroundContext.setValue(CONTEXT_COLORATION_LIGHT)
        self.assertFalse(p.isDarkBackGround())
        
        self.backgroundContext.setValue(CONTEXT_COLORATION_NONE)
        self.assertFalse(p.isDarkBackGround())
        
    def test_isLightBackGround(self):
        p = Printer.getInstance()
        self.backgroundContext.setValue(CONTEXT_COLORATION_DARK)
        self.assertFalse(p.isLightBackGround())
        
        self.backgroundContext.setValue(CONTEXT_COLORATION_LIGHT)
        self.assertTrue(p.isLightBackGround())
        
        self.backgroundContext.setValue(CONTEXT_COLORATION_NONE)
        self.assertFalse(p.isLightBackGround())
        
    def test_shellContext(self):
        p = Printer.getInstance()
        self.shellContext.setValue(CONTEXT_EXECUTION_SHELL)
        self.assertTrue(p.isInShell())
        
        self.shellContext.setValue(CONTEXT_EXECUTION_SCRIPT)
        self.assertFalse(p.isInShell())
        
        self.shellContext.setValue(CONTEXT_EXECUTION_DAEMON)
        self.assertFalse(p.isInShell())
        
    def test_promptShowedContext(self):
        p = Printer.getInstance()
        self.promptShowedContext.setValue(True)
        self.assertTrue(p.isPromptShowed())
        
        self.promptShowedContext.setValue(False)
        self.assertFalse(p.isPromptShowed())
        
    def test_debugContext(self):
        p = Printer.getInstance()
        self.debugContext.setValue(0)
        self.assertFalse(p.isDebugEnabled())
        self.assertEqual(p.getDebugLevel(), 0)
        
        self.debugContext.setValue(1)
        self.assertTrue(p.isDebugEnabled())
        self.assertEqual(p.getDebugLevel(), 1)
        
        self.debugContext.setValue(90)
        self.assertTrue(p.isDebugEnabled())
        self.assertEqual(p.getDebugLevel(), 90)
    
    def test_formatColor(self):
        p = Printer.getInstance()
        
        self.shellContext.setValue(CONTEXT_EXECUTION_SHELL)
        self.assertEqual(p.formatRed("plop"), LIGHTRED + "plop" + ENDC)
        
        self.shellContext.setValue(CONTEXT_EXECUTION_SCRIPT)
        self.assertEqual(p.formatRed("plop"), "plop")
        
        self.shellContext.setValue(CONTEXT_EXECUTION_SHELL)
        self.backgroundContext.setValue(CONTEXT_COLORATION_DARK)
        self.assertEqual(p.formatRed("plop"), DARKRED + "plop" + ENDC)
        
        self.shellContext.setValue(CONTEXT_EXECUTION_SCRIPT)
        self.assertEqual(p.formatRed("plop"), "plop")
        
        self.shellContext.setValue(CONTEXT_EXECUTION_SHELL)
        self.backgroundContext.setValue(CONTEXT_COLORATION_NONE)
        self.assertEqual(p.formatRed("plop"), "plop")
        
        self.shellContext.setValue(CONTEXT_EXECUTION_SCRIPT)
        self.assertEqual(p.formatRed("plop"), "plop")
        
    def test_format(self):
        p = Printer.getInstance()
        
        self.shellContext.setValue(CONTEXT_EXECUTION_SHELL)
        self.assertEqual(p.formatBolt("plop"), BOLT + "plop" + ENDC)
        
        self.shellContext.setValue(CONTEXT_EXECUTION_SCRIPT)
        self.assertEqual(p.formatBolt("plop"), "plop")
        
    def test_cprint(self):
        p = Printer.getInstance()
        no = NewOutput()
        
        p.cprint(None)
        self.assertEqual(no.lastOutPut, "")
        
        self.shellContext.setValue(CONTEXT_EXECUTION_SHELL)
        txt = p.formatRed("plop")
        p.cprint(txt)
        self.assertEqual(no.lastOutPut, "     "+LIGHTRED + "plop" + ENDC+"\n")
        
        no.flush()
        self.shellContext.setValue(CONTEXT_EXECUTION_SHELL)
        txt = p.formatRed("plop")
        self.shellContext.setValue(CONTEXT_EXECUTION_SCRIPT)
        p.cprint(txt)
        self.assertEqual(no.lastOutPut, "     plop\n")
        
        no.flush()
        self.shellContext.setValue(CONTEXT_EXECUTION_SHELL)
        txt = p.formatRed("plop\nplop")
        p.cprint(txt)
        self.assertEqual(no.lastOutPut, "     "+LIGHTRED + "plop"+"\n     " + "plop" + ENDC+"\n")
        
        no.flush()
        self.shellContext.setValue(CONTEXT_EXECUTION_SHELL)
        txt = p.formatRed("plop")
        self.backgroundContext.setValue(CONTEXT_COLORATION_NONE)
        p.cprint(txt)
        self.assertEqual(no.lastOutPut, "     plop\n")
        
        no.restore()
        
    def test_toLineString(self):
        self.assertEqual(_toLineString((),{}),"")
        self.assertEqual(_toLineString(("a",),{}),"a")
        self.assertEqual(_toLineString((),{"b":"42"}),"b=42")
        self.assertEqual(_toLineString(("a",),{"b":"42"}),"a b=42")
        self.assertEqual(_toLineString(("a","b","c",),{"e":"42", "f":23, "g":96}),"a b c e=42 g=96 f=23")
    
    def test_formatException(self):
        self.assertEqual(formatException(Exception("toto")), LIGHTRED + "toto" + ENDC)
        
        self.assertEqual(formatException(DefaultPyshellException("toto")), LIGHTRED + "toto" + ENDC)
        self.assertEqual(formatException(DefaultPyshellException("toto", WARNING)), LIGHTORANGE + "toto" + ENDC)
        self.assertEqual(formatException(DefaultPyshellException("toto", NOTICE)), LIGHTGREEN + "toto" + ENDC)
        
        #TODO listOfException
        
        #TODO what use of space to print the stacktrace ? (not sure)
        
        #TODO what about the printing of stacktrace in the lower exception, should be in upper
            #because it only retains the last one...
            
if __name__ == '__main__':
    unittest.main()
