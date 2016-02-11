#!/usr/bin/env python -t
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

import unittest, sys, os
from pyshell.utils.printing   import Printer, LIGHTRED, ENDC, DARKRED, BOLT, _toLineString, formatException, LIGHTORANGE, LIGHTGREEN
from pyshell.utils.valuable   import SimpleValuable
from pyshell.utils.constants  import ENVIRONMENT_TAB_SIZE_KEY, CONTEXT_COLORATION_KEY, CONTEXT_EXECUTION_KEY, DEBUG_ENVIRONMENT_NAME, CONTEXT_EXECUTION_SHELL,CONTEXT_EXECUTION_SCRIPT, CONTEXT_EXECUTION_DAEMON, CONTEXT_COLORATION_LIGHT, CONTEXT_COLORATION_DARK, CONTEXT_COLORATION_NONE
from pyshell.utils.exception  import DefaultPyshellException, WARNING, NOTICE, ListOfException
from pyshell.system.container   import ParameterContainer
from pyshell.system.environment import EnvironmentParameter, EnvironmentParameterManager
from pyshell.system.context     import ContextParameter,ContextParameterManager
from pyshell.arg.argchecker   import defaultInstanceArgChecker, IntegerArgChecker

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
        
        self.promptShowedContext = SimpleValuable(True) #True or False
        p.setPromptShowedContext(self.promptShowedContext)
        
        self.params = ParameterContainer()
        self.params.registerParameterManager("environment", EnvironmentParameterManager(self.params))
        self.params.registerParameterManager("context", ContextParameterManager(self.params))
        
        self.debugContext = ContextParameter(value=tuple(range(0,91)), typ=defaultInstanceArgChecker.getIntegerArgCheckerInstance(), default_index = 0,index=0)
        self.params.context.setParameter(DEBUG_ENVIRONMENT_NAME, self.debugContext, local_param = False)
        self.debugContext.settings.setTransient(False)
        self.debugContext.settings.setTransientIndex(False)
        self.debugContext.settings.setRemovable(False)
        self.debugContext.settings.setReadOnly(True)
        
        self.shellContext = ContextParameter(value=(CONTEXT_EXECUTION_SHELL, CONTEXT_EXECUTION_SCRIPT, CONTEXT_EXECUTION_DAEMON,), typ=defaultInstanceArgChecker.getStringArgCheckerInstance(), default_index = 0)
        self.params.context.setParameter(CONTEXT_EXECUTION_KEY, self.shellContext, local_param = False)
        self.shellContext.settings.setTransient(True)
        self.shellContext.settings.setTransientIndex(True)
        self.shellContext.settings.setRemovable(False)
        self.shellContext.settings.setReadOnly(True)
        
        self.backgroundContext = ContextParameter(value=(CONTEXT_COLORATION_LIGHT,CONTEXT_COLORATION_DARK,CONTEXT_COLORATION_NONE,), typ=defaultInstanceArgChecker.getStringArgCheckerInstance(), default_index = 0)
        self.params.context.setParameter(CONTEXT_COLORATION_KEY, self.backgroundContext, local_param = False)
        self.backgroundContext.settings.setTransient(False)
        self.backgroundContext.settings.setTransientIndex(False)
        self.backgroundContext.settings.setRemovable(False)
        self.backgroundContext.settings.setReadOnly(True)
        
        self.spacingContext = EnvironmentParameter(value=5, typ=IntegerArgChecker(0))
        self.params.environment.setParameter(ENVIRONMENT_TAB_SIZE_KEY, self.spacingContext, local_param = False)
        self.spacingContext.settings.setTransient(False)
        self.spacingContext.settings.setRemovable(False)
        self.spacingContext.settings.setReadOnly(False)
                
        p.setParameters(self.params)
        ###
        
        """self.shellContext = SimpleValuable(CONTEXT_EXECUTION_SHELL) #CONTEXT_EXECUTION_SHELL, CONTEXT_EXECUTION_SCRIPT, CONTEXT_EXECUTION_DAEMON
        p.setShellContext(self.shellContext)
        
        self.spacingContext = SimpleValuable(5) #an integer bigger than 0
        p.setSpacingContext(self.spacingContext)
        
        self.backgroundContext = SimpleValuable(CONTEXT_COLORATION_LIGHT) #CONTEXT_COLORATION_LIGHT, CONTEXT_COLORATION_DARK, CONTEXT_COLORATION_NONE
        p.setBakcgroundContext(self.backgroundContext)
        
        self.debugContext = SimpleValuable(0) #an integer between [0,5]
        p.setDebugContext(self.debugContext)"""
    
    def test_getInstance(self):
        p = Printer.getInstance()
        p2 = Printer.getInstance()
        self.assertEqual(p,p2)
    
    #def test_setShellContext(self):
    #    self.assertRaises(Exception, Printer.getInstance().setShellContext, ("plop",))
    
    def test_setPromptShowedContext(self):
        self.assertRaises(Exception, Printer.getInstance().setPromptShowedContext, ("plop",))
        
    """def test_setSpacingContext(self):
        self.assertRaises(Exception, Printer.getInstance().setSpacingContext, ("plop",))
        
    def test_setBakcgroundContext(self):
        self.assertRaises(Exception, Printer.getInstance().setBakcgroundContext, ("plop",))
        
    def test_setDebugContext(self):
        self.assertRaises(Exception, Printer.getInstance().setDebugContext, ("plop",))"""
    
    def test_isDarkBackGround(self):
        p = Printer.getInstance()
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_DARK)
        self.assertTrue(p.isDarkBackGround())
    
    def test_isDarkBackGround2(self):
        p = Printer.getInstance()
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_LIGHT)
        self.assertFalse(p.isDarkBackGround())
        
    def test_isDarkBackGround3(self):
        p = Printer.getInstance()
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_NONE)
        self.assertFalse(p.isDarkBackGround())
        
    def test_isLightBackGround(self):
        p = Printer.getInstance()
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_DARK)
        self.assertFalse(p.isLightBackGround())
        
    def test_isLightBackGround2(self):
        p = Printer.getInstance()
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_LIGHT)
        self.assertTrue(p.isLightBackGround())

    def test_isLightBackGround3(self):
        p = Printer.getInstance()
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_NONE)
        self.assertFalse(p.isLightBackGround())
        
    def test_shellContext(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        self.assertTrue(p.isInShell())
        
    def test_shellContext2(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        self.assertFalse(p.isInShell())
        
    def test_shellContext3(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_DAEMON)
        self.assertFalse(p.isInShell())
        
    def test_promptShowedContext(self):
        p = Printer.getInstance()
        self.promptShowedContext.setValue(True)
        self.assertTrue(p.isPromptShowed())

    def test_promptShowedContext2(self):
        p = Printer.getInstance()
        self.promptShowedContext.setValue(False)
        self.assertFalse(p.isPromptShowed())
        
    def test_debugContext(self):
        p = Printer.getInstance()
        self.debugContext.settings.setIndexValue(0)
        self.assertFalse(p.isDebugEnabled())
        self.assertEqual(p.getDebugLevel(), 0)
        
    def test_debugContext2(self):
        p = Printer.getInstance()
        self.debugContext.settings.setIndexValue(1)
        self.assertTrue(p.isDebugEnabled())
        self.assertEqual(p.getDebugLevel(), 1)
        
    def test_debugContext3(self):
        p = Printer.getInstance()
        self.debugContext.settings.setIndexValue(90)
        self.assertTrue(p.isDebugEnabled())
        self.assertEqual(p.getDebugLevel(), 90)
    
    def test_formatColor(self):
        p = Printer.getInstance()
        
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        self.assertEqual(p.formatRed("plop"), LIGHTRED + "plop" + ENDC)
        
    def test_formatColor2(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        self.assertEqual(p.formatRed("plop"), "plop")
        
    def test_formatColor3(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_DARK)
        self.assertEqual(p.formatRed("plop"), DARKRED + "plop" + ENDC)
        
    def test_formatColor4(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        self.assertEqual(p.formatRed("plop"), "plop")
        
    def test_formatColor5(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_NONE)
        self.assertEqual(p.formatRed("plop"), "plop")
        
    def test_formatColor5(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        self.assertEqual(p.formatRed("plop"), "plop")
        
    def test_format(self):
        p = Printer.getInstance()
        
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        self.assertEqual(p.formatBolt("plop"), BOLT + "plop" + ENDC)
        
    def test_format2(self):
        p = Printer.getInstance()
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        self.assertEqual(p.formatBolt("plop"), "plop")
        
    def test_cprint(self):
        p = Printer.getInstance()
        no = NewOutput()
        
        p.cprint(None)
        self.assertEqual(no.lastOutPut, "")
        
    def test_cprint2(self):
        p = Printer.getInstance()
        no = NewOutput()
        
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        txt = p.formatRed("plop")
        p.cprint(txt)
        self.assertEqual(no.lastOutPut, "     "+LIGHTRED + "plop" + ENDC+"\n")
        
        no.restore()
        
    def test_cprint3(self):
        p = Printer.getInstance()
        no = NewOutput()
        
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        txt = p.formatRed("plop")
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        p.cprint(txt)
        self.assertEqual(no.lastOutPut, "     plop\n")
        
        no.restore()
        
    def test_cprint4(self):
        p = Printer.getInstance()
        no = NewOutput()
        
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        txt = p.formatRed("plop\nplop")
        p.cprint(txt)
        self.assertEqual(no.lastOutPut, "     "+LIGHTRED + "plop"+"\n     " + "plop" + ENDC+"\n")
        
        no.restore()
        
    def test_cprint5(self):
        p = Printer.getInstance()
        no = NewOutput()
        
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        txt = p.formatRed("plop")
        self.backgroundContext.settings.setIndexValue(CONTEXT_COLORATION_NONE)
        p.cprint(txt)
        self.assertEqual(no.lastOutPut, "     plop\n")
        
        no.restore()
        
    def test_toLineString(self):
        self.assertEqual(_toLineString((),{}),"")
        
    def test_toLineString2(self):
        self.assertEqual(_toLineString(("a",),{}),"a")
        
    def test_toLineString3(self):
        self.assertEqual(_toLineString((),{"b":"42"}),"b=42")
        
    def test_toLineString4(self):
        self.assertEqual(_toLineString(("a",),{"b":"42"}),"a b=42")
        
    def test_toLineString5(self):
        self.assertEqual(_toLineString(("a","b","c",),{"e":"42", "f":23, "g":96}),"a b c e=42 g=96 f=23")
    
    def test_formatException(self):
        self.assertEqual(formatException(Exception("toto")), LIGHTRED + "toto" + ENDC)
    
    def test_formatException2(self):
        self.assertEqual(formatException(DefaultPyshellException("toto")), LIGHTRED + "toto" + ENDC)
        
    def test_formatException3(self):
        self.assertEqual(formatException(DefaultPyshellException("toto", WARNING)), LIGHTORANGE + "toto" + ENDC)
        
    def test_formatException4(self):
        self.assertEqual(formatException(DefaultPyshellException("toto", NOTICE)), LIGHTGREEN + "toto" + ENDC)
    
    def test_formatException4b(self):
        self.assertEqual(formatException(DefaultPyshellException("toto", NOTICE),"plop: "), LIGHTGREEN + "plop: toto" + ENDC)
    
    def test_formatException5(self):
        l = ListOfException()
        l.addException(Exception("plop"))
        l.addException(DefaultPyshellException("plip", WARNING))
        l.addException(DefaultPyshellException("toto", NOTICE))
        
        self.assertEqual(formatException(l), LIGHTRED+"plop"+ENDC +"\n"+ LIGHTORANGE+"plip"+ENDC +"\n"+ LIGHTGREEN+"toto"+ENDC)
    
    def test_formatException6(self):
        l = ListOfException()
        l.addException(Exception("plop"))
        l.addException(DefaultPyshellException("plip", WARNING))
        l.addException(DefaultPyshellException("toto", NOTICE))
        
        self.assertEqual(formatException(l, "plap"), LIGHTRED+"plap"+ENDC+"\n" + "     "+LIGHTRED+"plop"+ENDC +"\n"+ "     "+LIGHTORANGE+"plip"+ENDC +"\n"+ "     "+LIGHTGREEN+"toto"+ENDC)

    def test_formatException7(self):
        self.debugContext.settings.setIndexValue(1)
        
        stackTrace = LIGHTORANGE + "toto" + ENDC + LIGHTORANGE + "\n\n" \
                   + "Traceback (most recent call last):\n" \
                   + "  File \""+os.getcwd() + os.sep + "printingTest.py\", line 343, in test_formatException7\n" \
                   + "    raise DefaultPyshellException(\"toto\", WARNING)\n" \
                   + "DefaultPyshellException: toto\n" \
                   + ""+ENDC
        
        try:
            raise DefaultPyshellException("toto", WARNING)
        except Exception as ex:
            self.assertEqual(formatException(ex), stackTrace)

    def test_formatException8(self):
        self.debugContext.settings.setIndexValue(1)
        
        l = ListOfException()
        l.addException(Exception("plop"))
        l.addException(DefaultPyshellException("plip", WARNING))
        l.addException(DefaultPyshellException("toto", NOTICE))
        
        stackTrace = LIGHTRED+"plop"+ENDC +"\n"+ LIGHTORANGE+"plip"+ENDC +"\n"+ LIGHTGREEN+"toto"+ENDC + LIGHTRED + "\n\n" \
                   + "Traceback (most recent call last):\n" \
                   + "  File \""+os.getcwd() + os.sep + "printingTest.py\", line 363, in test_formatException8\n" \
                   + "    raise l\n" \
                   + "ListOfException: 3 exception(s) in list\n" \
                   + ""+ENDC
        
        try:
            raise l
        except Exception as ex:
            self.assertEqual(formatException(ex), stackTrace)
            
    def test_formatException9(self):
        self.debugContext.settings.setIndexValue(1)
        
        l = ListOfException()
        l.addException(Exception("plop"))
        l.addException(DefaultPyshellException("plip", WARNING))
        l.addException(DefaultPyshellException("toto", NOTICE))
        
        stackTrace = LIGHTRED+"plap"+ENDC+"\n" + "     "+LIGHTRED+"plop"+ENDC +"\n"+ "     "+LIGHTORANGE+"plip"+ENDC +"\n"+ "     "+LIGHTGREEN+"toto"+ENDC + LIGHTRED + "\n\n" \
                   + "Traceback (most recent call last):\n" \
                   + "  File \""+os.getcwd() + os.sep + "printingTest.py\", line 383, in test_formatException9\n" \
                   + "    raise l\n" \
                   + "ListOfException: 3 exception(s) in list\n" \
                   + ""+ENDC
        
        try:
            raise l
        except Exception as ex:
            self.assertEqual(formatException(ex, "plap"), stackTrace)
    
    def test_formatException10(self): #exception with suffix
        self.assertEqual(formatException(Exception("toto"), prefix="plop: ", suffix=" (burg)"), LIGHTRED + "plop: toto (burg)" + ENDC)
        
    def test_formatException11(self): #DefaultPyshellException with suffix
        self.assertEqual(formatException(DefaultPyshellException("toto"), prefix="plop: ", suffix=" (burg)"), LIGHTRED + "plop: toto (burg)" + ENDC)
    
    def test_formatException12(self): #ListOfException with suffix
        l = ListOfException()
        l.addException(Exception("plop"))
        l.addException(DefaultPyshellException("plip", WARNING))
        l.addException(DefaultPyshellException("toto", NOTICE))
        
        self.assertEqual(formatException(l, prefix="plop:", suffix=" (burg)"), LIGHTRED+"plop: (burg)"+ENDC +"\n     "+ LIGHTRED+"plop"+ENDC +"\n     "+ LIGHTORANGE+"plip"+ENDC +"\n     "+ LIGHTGREEN+"toto"+ENDC)
    
    def test_indentString(self):
        p = Printer.getInstance()
        self.assertEqual(p.indentString("plop"),"     plop")
        self.assertEqual(p.indentString("plop\nplip\nplap\n"),"     plop\n     plip\n     plap\n     ")
        
    def test_indentTokenList(self):
        p = Printer.getInstance()
        self.assertEqual(p.indentListOfToken( ("plop","plop\nplip\nplap\n")),["     plop","     plop\n     plip\n     plap\n     "])
            
if __name__ == '__main__':
    unittest.main()
    
