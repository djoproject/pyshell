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

import unittest, threading
from tries import multiLevelTries
from pyshell.utils.executing  import execute, _generateSuffix, _execute
from pyshell.system.parameter import ParameterContainer,EnvironmentParameter
from pyshell.utils.constants  import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.command.command  import UniCommand, Command, MultiCommand
from pyshell.arg.decorator    import shellMethod
from pyshell.arg.argchecker   import defaultInstanceArgChecker,listArgChecker
from pyshell.utils.parsing    import Parser
from time import sleep

RESULT = None

@shellMethod(param=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def plop_meth(param):
    global RESULT
    param.append(threading.current_thread().ident)
    RESULT = param
    return param

class ExecutingTest(unittest.TestCase):
    def setUp(self):
        global RESULT
        
        self.params = ParameterContainer()
        
        self.mltries = multiLevelTries()
        
        m = UniCommand("plop", plop_meth)
        self.mltries.insert( ("plop",) ,m)
        
        self.params.environment.setParameter(ENVIRONMENT_LEVEL_TRIES_KEY,       EnvironmentParameter(value=self.mltries,transient=True,readonly=True, removable=False), localParam = False)
        RESULT = None
        
        self.m = MultiCommand("plap")
        self.mltries.insert( ("plap",) ,self.m)
                
    ### execute test ###
    def test_execute1(self):#with processArg iterable
        self.assertEqual(RESULT, None)
        lastException, engine = execute("plop", self.params, processArg=(1,2,3,))
        self.assertEqual(lastException, None)
        self.assertNotEqual(engine, None)
        self.assertEqual(RESULT,["1","2","3",threading.current_thread().ident])
        self.assertEqual(engine.getLastResult(),[["1","2","3",threading.current_thread().ident]])
    
    def test_execute2(self):#with processArg as string
        self.assertEqual(RESULT, None)
        lastException, engine = execute("plop", self.params, processArg="1 2 3")
        self.assertEqual(lastException, None)
        self.assertNotEqual(engine, None)
        self.assertEqual(RESULT,["1","2","3",threading.current_thread().ident])
        self.assertEqual(engine.getLastResult(),[["1","2","3",threading.current_thread().ident]])
        
    def test_execute3(self):#with processArg as something else
        self.assertEqual(RESULT, None)
        self.assertRaises(Exception, execute, "plop", self.params, processArg=object())
        self.assertEqual(RESULT,None)
        
    def test_execute4(self):#with parser parsed
        p = Parser("plop 1 2 3")
        self.assertEqual(RESULT, None)
        lastException, engine = execute(p, self.params)
        self.assertEqual(lastException, None)
        self.assertNotEqual(engine, None)
        self.assertEqual(RESULT,["1","2","3",threading.current_thread().ident])
        self.assertEqual(engine.getLastResult(),[["1","2","3",threading.current_thread().ident]])
        
    def test_execute5(self):#with parser not parsed
        p = Parser("plop 1 2 3")
        p.parse()
        self.assertEqual(RESULT, None)
        lastException, engine = execute(p, self.params)
        self.assertEqual(lastException, None)
        self.assertNotEqual(engine, None)
        self.assertEqual(RESULT,["1","2","3",threading.current_thread().ident])
        self.assertEqual(engine.getLastResult(),[["1","2","3",threading.current_thread().ident]])
        
    def test_execute6(self):#with string as parser
        self.assertEqual(RESULT, None)
        lastException, engine = execute("plop 1 2 3", self.params)
        self.assertEqual(lastException, None)
        self.assertNotEqual(engine, None)
        self.assertEqual(RESULT,["1","2","3",threading.current_thread().ident])
        self.assertEqual(engine.getLastResult(),[["1","2","3",threading.current_thread().ident]])
        
    def test_execute7(self):#with empty parser
        p = Parser("")
        p.parse()
        self.assertEqual(RESULT, None)
        lastException, engine = execute(p, self.params)
        self.assertEqual(lastException, None)
        self.assertEqual(engine, None)
        self.assertEqual(RESULT,None)
        
        
    def test_execute8(self):#try in thread
        self.assertEqual(RESULT, None)
        lastException, engine = execute("plop 1 2 3 &", self.params)
        self.assertEqual(lastException, None)
        self.assertEqual(engine, None)
        
        threadId = self.params.variable.getParameter("$!").getValue()
        
        for t in threading.enumerate():
            if t.ident == threadId[0]:
                t.join(4)
                break
        
        self.assertNotEqual(RESULT,None)
        self.assertEqual(len(RESULT),4)
        self.assertNotEqual(RESULT[3],threading.current_thread().ident)
        
    def test_execute9(self):#test with an empty command
        self.assertEqual(RESULT, None)
        self.assertRaises(Exception, execute, "plap", self.params, processArg=object())
        self.assertEqual(RESULT,None)
        
    def test_execute10(self):#check if commands are correctly cloned
        #IDEA #self.m.addDynamicCommand(Command())
            #create a multiCommand with a static and a dynamic command
            #only the static will be executed
        
        pass #TODO
        
    def test_execute11(self):#raise every exception
        #IDEA create a command that raise a defined exception, and call it
    
        pass #TODO
        
    ### _generateSuffix test ###
    def test_generateSuffix1(self):#test with debug
        pass #TODO
        
    def test_generateSuffix2(self):#test outside shell context
        pass #TODO
        
    def test_generateSuffix3(self):#test with processName provided
        pass #TODO
        
    def test_generateSuffix4(self):#test without processName provided
        pass #TODO
        
    def test_generateSuffix5(self):#test without commandNameList
        pass #TODO
        
    def test_generateSuffix6(self):#test with None engine
        pass #TODO
        
    def test_generateSuffix7(self):#test with empty engine
        pass #TODO
        
    def test_generateSuffix8(self):#test with valid engine and commandNameList
        pass #TODO
        
if __name__ == '__main__':
    unittest.main()
