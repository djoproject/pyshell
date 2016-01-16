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

import unittest
from pyshell.utils.constants import ENVIRONMENT_TAB_SIZE_KEY, CONTEXT_COLORATION_KEY, CONTEXT_EXECUTION_KEY, DEBUG_ENVIRONMENT_NAME, CONTEXT_EXECUTION_SHELL,CONTEXT_EXECUTION_SCRIPT, CONTEXT_EXECUTION_DAEMON, CONTEXT_COLORATION_LIGHT, CONTEXT_COLORATION_DARK, CONTEXT_COLORATION_NONE
from pyshell.utils.test.printingTest import NewOutput
from pyshell.utils.postProcess import listResultHandler, listFlatResultHandler, printStringCharResult, printBytesAsString, printColumnWithouHeader, printColumn
from pyshell.utils.printing  import Printer
from pyshell.utils.valuable  import SimpleValuable
from pyshell.system.container   import ParameterContainer
from pyshell.system.environment import EnvironmentParameter, EnvironmentParameterManager
from pyshell.system.context     import ContextParameter, ContextParameterManager
from pyshell.arg.argchecker   import defaultInstanceArgChecker, IntegerArgChecker

class PostProcessTest(unittest.TestCase):
    def setUp(self):
        p = Printer.getInstance()
        self.params = ParameterContainer()
        self.params.registerParameterManager("environment", EnvironmentParameterManager(self.params))
        self.params.registerParameterManager("context", ContextParameterManager(self.params))
        
        self.debugContext = ContextParameter(value=tuple(range(0,91)), typ=defaultInstanceArgChecker.getIntegerArgCheckerInstance(), defaultIndex = 0,index=0)
        self.params.context.setParameter(DEBUG_ENVIRONMENT_NAME, self.debugContext, localParam = False)
        self.debugContext.settings.setTransient(False)
        self.debugContext.settings.setTransientIndex(False)
        self.debugContext.settings.setRemovable(False)
        self.debugContext.settings.setReadOnly(True)
        
        self.shellContext = ContextParameter(value=(CONTEXT_EXECUTION_SHELL, CONTEXT_EXECUTION_SCRIPT, CONTEXT_EXECUTION_DAEMON,), typ=defaultInstanceArgChecker.getStringArgCheckerInstance(), defaultIndex = 0)
        self.params.context.setParameter(CONTEXT_EXECUTION_KEY, self.shellContext, localParam = False)
        self.shellContext.settings.setTransient(True)
        self.shellContext.settings.setTransientIndex(True)
        self.shellContext.settings.setRemovable(False)
        self.shellContext.settings.setReadOnly(True)
        
        self.backgroundContext = ContextParameter(value=(CONTEXT_COLORATION_LIGHT,CONTEXT_COLORATION_DARK,CONTEXT_COLORATION_NONE,), typ=defaultInstanceArgChecker.getStringArgCheckerInstance(), defaultIndex = 0)
        self.params.context.setParameter(CONTEXT_COLORATION_KEY, self.backgroundContext, localParam = False)
        self.backgroundContext.settings.setTransient(False)
        self.backgroundContext.settings.setTransientIndex(False)
        self.backgroundContext.settings.setRemovable(False)
        self.backgroundContext.settings.setReadOnly(True)
        
        self.spacingContext = EnvironmentParameter(value=5, typ=IntegerArgChecker(0))
        self.params.environment.setParameter(ENVIRONMENT_TAB_SIZE_KEY, self.spacingContext, localParam = False)
        self.spacingContext.settings.setTransient(False)
        self.spacingContext.settings.setRemovable(False)
        self.spacingContext.settings.setReadOnly(False)
        
        p.setParameters(self.params)
        
        """self.shellContext = SimpleValuable(CONTEXT_EXECUTION_SHELL) #CONTEXT_EXECUTION_SHELL, CONTEXT_EXECUTION_SCRIPT, CONTEXT_EXECUTION_DAEMON
        p.setShellContext(self.shellContext)
        
        self.promptShowedContext = SimpleValuable(True) #True or False
        p.setPromptShowedContext(self.promptShowedContext)
        
        self.spacingContext = SimpleValuable(5) #an integer bigger than 0
        p.setSpacingContext(self.spacingContext)
        
        self.backgroundContext = SimpleValuable(CONTEXT_COLORATION_LIGHT) #CONTEXT_COLORATION_LIGHT, CONTEXT_COLORATION_DARK, CONTEXT_COLORATION_NONE
        p.setBakcgroundContext(self.backgroundContext)
        
        self.debugContext = SimpleValuable(0) #an integer between [0,5]
        p.setDebugContext(self.debugContext)"""
    
    def test_listResultHandler1(self):
        no = NewOutput()
        
        listResultHandler( () )
        self.assertEqual(no.lastOutPut, "")
        
        no.restore()
        
    def test_listResultHandler2(self):
        no = NewOutput()
        
        listResultHandler( ("aa",) )
        self.assertEqual(no.lastOutPut, "     aa\n")
        
        no.restore()
        
    def test_listResultHandler3(self):
        no = NewOutput()
        
        listResultHandler( ("aa",42,) )
        self.assertEqual(no.lastOutPut, "     aa\n     42\n")
        
        no.restore()
        
    ###
        
    def test_listFlatResultHandler1(self):
        no = NewOutput()
        
        listFlatResultHandler( () )
        self.assertEqual(no.lastOutPut, "     \n")
        
        no.restore()
        
    def test_listFlatResultHandler2(self):
        no = NewOutput()
        
        listFlatResultHandler( ("aa",) )
        self.assertEqual(no.lastOutPut, "     aa\n")
        
        no.restore()
        
    def test_listFlatResultHandler3(self):
        no = NewOutput()
        
        listFlatResultHandler( ("aa",42,) )
        self.assertEqual(no.lastOutPut, "     aa 42\n")
        
        no.restore()
        
    ###
    
    def test_printStringCharResult1(self):
        no = NewOutput()
        
        printStringCharResult( () )
        self.assertEqual(no.lastOutPut, "     \n")
        
        no.restore()
        
    def test_printStringCharResult2(self):
        no = NewOutput()
        
        printStringCharResult( (60,) )
        self.assertEqual(no.lastOutPut, "     <\n")
        
        no.restore()
        
    def test_printStringCharResult3(self):
        no = NewOutput()
        
        printStringCharResult( (60,42,) )
        self.assertEqual(no.lastOutPut, "     <*\n")
        
        no.restore()
        
    ###
    
    def test_printBytesAsString1(self):
        no = NewOutput()
        
        printBytesAsString( () )
        self.assertEqual(no.lastOutPut, "     \n")
        
        no.restore()
        
    def test_printBytesAsString2(self):
        no = NewOutput()
        
        printBytesAsString( (0x25,) )
        self.assertEqual(no.lastOutPut, "     25\n")
        
        no.restore()
        
    def test_printBytesAsString3(self):
        no = NewOutput()
        
        printBytesAsString( (0x25,0x42,) )
        self.assertEqual(no.lastOutPut, "     2542\n")
        
        no.restore()
        
    ###
    
    def test_printColumnWithouHeader1(self):
        no = NewOutput()
        
        printColumnWithouHeader( () )
        self.assertEqual(no.lastOutPut, "")
        
        no.restore()
        
    def test_printColumnWithouHeader2(self):
        no = NewOutput()
        
        printColumnWithouHeader( ("TOTO",) )
        self.assertEqual(no.lastOutPut, "     TOTO\n")
        
        no.restore()
        
    def test_printColumnWithouHeader3(self):
        no = NewOutput()
        
        printColumnWithouHeader( ("TOTO","TUTUTU",) )
        self.assertEqual(no.lastOutPut, "     TOTO\n     TUTUTU\n")
        
        no.restore()
        
    def test_printColumnWithouHeader4(self):
        no = NewOutput()
        
        printColumnWithouHeader( ("TOTO","TUTUTU", "tata",) )
        self.assertEqual(no.lastOutPut, "     TOTO\n     TUTUTU\n     tata\n")
        
        no.restore()
        
    def test_printColumnWithouHeader5(self):
        no = NewOutput()
        
        printColumnWithouHeader( ( ("TOTO","tata"),"TUTUTU",) )
        self.assertEqual(no.lastOutPut, "     TOTO    tata\n     TUTUTU\n")
        
        no.restore()

    def test_printColumnWithouHeader6(self):
        no = NewOutput()
        
        printColumnWithouHeader( ( ("TOTO","tata"),"TUTUTU",("aaaaaaaaaa","bbbbbbbb","cccccc",),) )
        self.assertEqual(no.lastOutPut, "     TOTO        tata\n     TUTUTU\n     aaaaaaaaaa  bbbbbbbb  cccccc\n")
        
        no.restore()
        
    ###
    
    def test_printColumn1(self):
        no = NewOutput()
        
        printColumn( () )
        self.assertEqual(no.lastOutPut, "")
        
        no.restore()
        
    def test_printColumn2(self):
        no = NewOutput()
        
        printColumn( ("TOTO",) )
        self.assertEqual(no.lastOutPut, "     TOTO\n")
        
        no.restore()
        
    def test_printColumn3(self):
        no = NewOutput()
        
        printColumn( ("TOTO","TUTUTU",) )
        self.assertEqual(no.lastOutPut, "     TOTO\n      TUTUTU\n")
        
        no.restore()
        
    def test_printColumn4(self):
        no = NewOutput()
        
        printColumn( ("TOTO","TUTUTU", "tata",) )
        self.assertEqual(no.lastOutPut, "     TOTO\n      TUTUTU\n      tata\n")
        
        no.restore()
        
    def test_printColumn5(self):
        no = NewOutput()
        
        printColumn( ( ("TOTO","tata"),"TUTUTU",) )
        self.assertEqual(no.lastOutPut, "     TOTO     tata\n      TUTUTU\n")
        
        no.restore()

    def test_printColumn6(self):
        no = NewOutput()
        
        printColumn( ( ("TOTO","tata"),"TUTUTU",("aaaaaaaaaa","bbbbbbbb","cccccc",),) )
        self.assertEqual(no.lastOutPut, "     TOTO         tata\n      TUTUTU\n      aaaaaaaaaa   bbbbbbbb   cccccc\n")
        
        no.restore()
        
    def test_printColumn7(self):
        no = NewOutput()
        
        printColumn( ( ("TOTO","tata","plapplap"),"TUTUTU",("aaaaaaaaaa","bbbbbbbb","cccccc",),("lalala","lulu"),) )
        self.assertEqual(no.lastOutPut, "     TOTO         tata       plapplap\n      TUTUTU\n      aaaaaaaaaa   bbbbbbbb   cccccc\n      lalala       lulu\n")
        
        no.restore()
        
        
if __name__ == '__main__':
    unittest.main()
