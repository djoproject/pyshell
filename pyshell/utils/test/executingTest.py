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
from pyshell.utils.executing    import execute, _generateSuffix, _execute
from pyshell.utils.exception    import ListOfException
from pyshell.system.variable    import VariableParameterManager
from pyshell.system.container   import ParameterContainer
from pyshell.system.environment import EnvironmentParameter, EnvironmentParameterManager
from pyshell.system.context     import ContextParameter, ContextParameterManager
from pyshell.utils.constants    import ENVIRONMENT_TAB_SIZE_KEY, CONTEXT_COLORATION_KEY, DEBUG_ENVIRONMENT_NAME, ENVIRONMENT_LEVEL_TRIES_KEY, CONTEXT_EXECUTION_SHELL, CONTEXT_EXECUTION_SCRIPT, CONTEXT_EXECUTION_DAEMON, CONTEXT_EXECUTION_KEY, CONTEXT_COLORATION_LIGHT,CONTEXT_COLORATION_DARK,CONTEXT_COLORATION_NONE
from pyshell.command.command    import UniCommand, Command, MultiCommand
from pyshell.arg.decorator      import shellMethod
from pyshell.arg.argchecker     import defaultInstanceArgChecker,listArgChecker, IntegerArgChecker
from pyshell.utils.parsing      import Parser
from pyshell.arg.exception      import *
from pyshell.command.exception  import *
from pyshell.command.engine     import engineV3
from pyshell.utils.test.printingTest import NewOutput
from time import sleep

RESULT     = None
RESULT_BIS = None

@shellMethod(param=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def plop_meth(param):
    global RESULT
    param.append(threading.current_thread().ident)
    RESULT = param
    return param

@shellMethod(param=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def tutu_meth(param):
    global RESULT_BIS
    param.append(threading.current_thread().ident)
    RESULT_BIS = param
    return param

@shellMethod(param=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def raiseExc1(param):
    raise executionInitException("test 1")

@shellMethod(param=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def raiseExc2(param):
    raise executionException("test 2")

@shellMethod(param=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def raiseExc3(param):
    raise commandException("test 3")

@shellMethod(param=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def raiseExc4(param):
    e = engineInterruptionException("test 4")
    e.abnormal = True
    raise e

@shellMethod(param=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def raiseExc5(param):
    e = engineInterruptionException("test 5")
    e.abnormal = False
    raise e

@shellMethod(param=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def raiseExc6(param):
    raise argException("test 6") 

@shellMethod(param=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def raiseExc7(param):
    l = ListOfException()
    l.addException(Exception("test 7"))
    raise l

@shellMethod(param=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def raiseExc8(param):
    raise Exception("test 8")  

class ExecutingTest(unittest.TestCase):
    def setUp(self):
        global RESULT, RESULT_BIS
        
        self.params = ParameterContainer()
        self.params.registerParameterManager("environment", EnvironmentParameterManager(self.params))
        self.params.registerParameterManager("context", ContextParameterManager(self.params))
        self.params.registerParameterManager("variable", VariableParameterManager(self.params))

        self.debugContext = ContextParameter(value=tuple(range(0,91)), typ=defaultInstanceArgChecker.getIntegerArgCheckerInstance())
        self.params.context.setParameter(DEBUG_ENVIRONMENT_NAME, self.debugContext, localParam = False)
        self.debugContext.settings.setTransient(False)
        self.debugContext.settings.setTransientIndex(False)
        self.debugContext.settings.setRemovable(False)
        self.debugContext.settings.setReadOnly(True)
        
        self.shellContext = ContextParameter(value=(CONTEXT_EXECUTION_SHELL, CONTEXT_EXECUTION_SCRIPT, CONTEXT_EXECUTION_DAEMON,), typ=defaultInstanceArgChecker.getStringArgCheckerInstance())
        self.params.context.setParameter(CONTEXT_EXECUTION_KEY, self.shellContext, localParam = False)
        self.shellContext.settings.setTransient(True)
        self.shellContext.settings.setTransientIndex(True)
        self.shellContext.settings.setRemovable(False)
        self.shellContext.settings.setReadOnly(True)
        
        self.backgroundContext = ContextParameter(value=(CONTEXT_COLORATION_LIGHT,CONTEXT_COLORATION_DARK,CONTEXT_COLORATION_NONE,), typ=defaultInstanceArgChecker.getStringArgCheckerInstance())
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
        
        self.mltries = multiLevelTries()
        
        m = UniCommand("plop", plop_meth)
        self.mltries.insert( ("plop",) ,m)
        
        param = self.params.environment.setParameter(ENVIRONMENT_LEVEL_TRIES_KEY,       EnvironmentParameter(value=self.mltries, typ=defaultInstanceArgChecker.getArgCheckerInstance()), localParam = False)
        param.settings.setTransient(True)
        param.settings.setRemovable(False)
        param.settings.setReadOnly(True)

        RESULT = None
        RESULT_BIS = None
        
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
        
        threadId = self.params.variable.getParameter("!").getValue()
        
        for t in threading.enumerate():
            if t.ident == threadId[0]:
                t.join(4)
                break
        sleep(0.1)
        
        self.assertNotEqual(RESULT,None)
        self.assertEqual(len(RESULT),4)
        self.assertNotEqual(RESULT[3],threading.current_thread().ident)
        
    def test_execute9(self):#test with an empty command
        self.assertEqual(RESULT, None)
        self.assertRaises(Exception, execute, "plap", self.params, processArg=object())
        self.assertEqual(RESULT,None)
        
    def test_execute10(self):#check if commands are correctly cloned        
        m = MultiCommand("tutu")
        m.addProcess(process=plop_meth)

        c = Command()
        c.process = tutu_meth
        m.addDynamicCommand(c)

        self.mltries.insert( ("tutu",) ,m)

        self.assertEqual(RESULT, None)
        self.assertEqual(RESULT_BIS, None)

        lastException, engine = execute("tutu aa bb cc", self.params)

        self.assertEqual(lastException, None)
        self.assertNotEqual(engine, None)
        self.assertEqual(RESULT, ["aa", "bb", "cc",threading.current_thread().ident ])
        self.assertEqual(RESULT_BIS, None)
        
    def test_execute11(self):#raise every exception
        #IDEA create a command that raise a defined exception, and call it
    
        n = NewOutput()

        m = MultiCommand("test_1")
        m.addProcess(process=raiseExc1)

        self.mltries.insert( ("test_1",) ,m)

        lastException, engine = execute("test_1 aa bb cc", self.params)
        self.assertIsInstance(lastException, executionInitException)
        self.assertNotEqual(engine, None)
        self.assertEqual(n.lastOutPut, "Fail to init an execution object: test 1\n")
        n.flush()

        ##

        m = MultiCommand("test_2")
        m.addProcess(process=raiseExc2)

        self.mltries.insert( ("test_2",) ,m)

        lastException, engine = execute("test_2 aa bb cc", self.params)
        self.assertIsInstance(lastException, executionException)
        self.assertNotEqual(engine, None)
        self.assertEqual(n.lastOutPut, "Fail to execute: test 2\n")
        n.flush()

        ##

        m = MultiCommand("test_3")
        m.addProcess(process=raiseExc3)

        self.mltries.insert( ("test_3",) ,m)

        lastException, engine = execute("test_3 aa bb cc", self.params)
        self.assertIsInstance(lastException, commandException)
        self.assertNotEqual(engine, None)
        self.assertEqual(n.lastOutPut, "Error in command method: test 3\n")
        n.flush()

        ##

        m = MultiCommand("test_4")
        m.addProcess(process=raiseExc4)

        self.mltries.insert( ("test_4",) ,m)

        lastException, engine = execute("test_4 aa bb cc", self.params)
        self.assertIsInstance(lastException, engineInterruptionException)
        self.assertNotEqual(engine, None)
        self.assertEqual(n.lastOutPut, "Abnormal execution abort, reason: test 4\n")
        n.flush()

        ##

        m = MultiCommand("test_5")
        m.addProcess(process=raiseExc5)

        self.mltries.insert( ("test_5",) ,m)

        lastException, engine = execute("test_5 aa bb cc", self.params)
        self.assertIsInstance(lastException, engineInterruptionException)
        self.assertNotEqual(engine, None)
        self.assertEqual(n.lastOutPut, "Normal execution abort, reason: test 5\n")
        n.flush()

        ##

        m = MultiCommand("test_6")
        m.addProcess(process=raiseExc6)

        self.mltries.insert( ("test_6",) ,m)

        lastException, engine = execute("test_6 aa bb cc", self.params)
        self.assertIsInstance(lastException, argException)
        self.assertNotEqual(engine, None)
        self.assertEqual(n.lastOutPut, "Error while parsing argument: test 6\n")
        n.flush()

        ##

        m = MultiCommand("test_7")
        m.addProcess(process=raiseExc7)

        self.mltries.insert( ("test_7",) ,m)

        lastException, engine = execute("test_7 aa bb cc", self.params)
        self.assertIsInstance(lastException, ListOfException)
        self.assertNotEqual(engine, None)
        self.assertEqual(n.lastOutPut, "List of exception(s): \ntest 7\n")
        n.flush()

        ##

        m = MultiCommand("test_8")
        m.addProcess(process=raiseExc8)

        self.mltries.insert( ("test_8",) ,m)

        lastException, engine = execute("test_8 aa bb cc", self.params)
        self.assertIsInstance(lastException, Exception)
        self.assertNotEqual(engine, None)
        self.assertEqual(n.lastOutPut, "test 8\n")
        n.flush()

        n.restore()

    ### _generateSuffix test ###
    def test_generateSuffix0(self):#no suffix production
        self.assertEqual(_generateSuffix(self.params,(("plop",),),None,"__process__"),None)

    def test_generateSuffix1(self):#test with debug
        self.debugContext.settings.setIndexValue(1)
        self.assertEqual(_generateSuffix(self.params,(("plop",),),None,"__process__")," (threadId="+str(threading.current_thread().ident)+", level=0, process='__process__')")
        self.debugContext.settings.setIndexValue(0)
        self.assertEqual(_generateSuffix(self.params,(("plop",),),None,"__process__"),None)
        
    def test_generateSuffix2(self):#test outside shell context
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SHELL)
        self.assertEqual(_generateSuffix(self.params,(("plop",),),None,"__process__"),None)
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        self.assertEqual(_generateSuffix(self.params,(("plop",),),None,"__process__")," (threadId="+str(threading.current_thread().ident)+", level=0, process='__process__')")
        
    def test_generateSuffix3(self):#test with processName provided or not
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        self.assertEqual(_generateSuffix(self.params,(("plop",),),None,"__process__")," (threadId="+str(threading.current_thread().ident)+", level=0, process='__process__')")
        self.assertEqual(_generateSuffix(self.params,(("plop",),),None,None)," (threadId="+str(threading.current_thread().ident)+", level=0)")
        
    def test_generateSuffix5(self):#test without commandNameList
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        e = engineV3([UniCommand("plop", plop_meth)], [["titi"]],["titi"] )
        self.assertEqual(_generateSuffix(self.params,None,e,"__process__")," (threadId="+str(threading.current_thread().ident)+", level=0, process='__process__')")
        
    def test_generateSuffix6(self):#test with None engine
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        self.assertEqual(_generateSuffix(self.params,(("plop",),),None,"__process__")," (threadId="+str(threading.current_thread().ident)+", level=0, process='__process__')")
        
    def test_generateSuffix7(self):#test with empty engine
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        e = engineV3([UniCommand("plop", plop_meth)], [["titi"]],["titi"])
        del e.stack[:]
        self.assertEqual(_generateSuffix(self.params,(("plop",),),e,"__process__")," (threadId="+str(threading.current_thread().ident)+", level=0, process='__process__')")
        
    def test_generateSuffix8(self):#test with valid engine and commandNameList
        self.shellContext.settings.setIndexValue(CONTEXT_EXECUTION_SCRIPT)
        e = engineV3([UniCommand("plop", plop_meth)], [["titi"]],["titi"])
        self.assertEqual(_generateSuffix(self.params,(("plop",),),e,"__process__")," (threadId="+str(threading.current_thread().ident)+", level=0, process='__process__', command='plop')")

        
if __name__ == '__main__':
    unittest.main()
