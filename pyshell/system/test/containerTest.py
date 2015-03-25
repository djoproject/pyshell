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

import unittest
from pyshell.system.container import _ThreadInfo, AbstractParameterContainer, DummyParameterContainer, ParameterContainer
from pyshell.system.parameter import ParameterManager
from pyshell.utils.constants import AVAILABLE_ORIGIN, ORIGIN_FILE, ORIGIN_PROCESS, ORIGIN_LOADER
from pyshell.utils.exception import DefaultPyshellException
from threading import current_thread

class ExceptionTest(unittest.TestCase):
    def setUp(self):
        pass
        
    ## misc ##
    
    def test_misc(self):
        self.assertEqual(len(AVAILABLE_ORIGIN), 3)
        self.assertTrue(ORIGIN_FILE in AVAILABLE_ORIGIN)
        self.assertTrue(ORIGIN_PROCESS in AVAILABLE_ORIGIN)
        self.assertTrue(ORIGIN_LOADER in AVAILABLE_ORIGIN)
        
    ## thread info ##
    
    def test_threadInfo2(self):
        ti = _ThreadInfo()
        self.assertTrue(hasattr(ti, "procedureStack"))
        self.assertEqual(ti.procedureStack, [])
        self.assertEqual(len(ti.procedureStack), 0)
        
    def test_threadInfo3(self):
        ti = _ThreadInfo()
        self.assertTrue(hasattr(ti, "origin"))
        self.assertEqual(ti.origin, ORIGIN_PROCESS)
        
    def test_threadInfo4(self):
        ti = _ThreadInfo()
        self.assertTrue(hasattr(ti, "originArg"))
        self.assertEqual(ti.originArg, None)
        
    def test_threadInfo5(self):
        ti = _ThreadInfo()
        self.assertTrue(ti.canBeDeleted())
        
    def test_threadInfo6(self):
        ti = _ThreadInfo()
        ti.procedureStack.append("plop")
        self.assertFalse(ti.canBeDeleted())

    def test_threadInfo7(self):
        ti = _ThreadInfo()
        ti.origin = "plop"
        self.assertFalse(ti.canBeDeleted())
    
    ## AbstractParameterContainer ##
    
    def test_AbstractParameterContainer1(self):
        apc = AbstractParameterContainer()
        
        self.assertTrue(hasattr(apc, "getCurrentId"))
        self.assertTrue(hasattr(apc.getCurrentId, "__call__"))
        self.assertIs(apc.getCurrentId(), None)
    
    def test_AbstractParameterContainer2(self):
        apc = AbstractParameterContainer()
        
        self.assertTrue(hasattr(apc, "getOrigin"))
        self.assertTrue(hasattr(apc.getOrigin, "__call__"))
        self.assertIs(apc.getOrigin(), None)
        
    def test_AbstractParameterContainer3(self):
        apc = AbstractParameterContainer()
        
        self.assertTrue(hasattr(apc, "setOrigin"))
        self.assertTrue(hasattr(apc.setOrigin, "__call__"))
        self.assertIs(apc.setOrigin("plop", "plip"), None)
        self.assertIs(apc.setOrigin("plop"), None)
    
    ## DummyParameterContainer ##
    
    def test_DummyParameterContainer1(self):
        dpc = DummyParameterContainer()
        self.assertEqual(dpc.getOrigin(), (ORIGIN_PROCESS, None,) )
        self.assertEqual(dpc.getCurrentId(), (current_thread().ident, None) )

    def test_DummyParameterContainer2(self):
        dpc = DummyParameterContainer()
        self.assertRaises(DefaultPyshellException, dpc.setOrigin, "plop")
        
    def test_DummyParameterContainer3(self):
        dpc = DummyParameterContainer()
        dpc.setOrigin(ORIGIN_FILE, "plip")
        self.assertEqual(dpc.getOrigin(), (ORIGIN_FILE, None,) )
        self.assertEqual(dpc.getCurrentId(), (current_thread().ident, None) )
        
    def test_DummyParameterContainer4(self):
        dpc = DummyParameterContainer()
        dpc.setOrigin(ORIGIN_LOADER, "plip")
        self.assertEqual(dpc.getOrigin(), (ORIGIN_LOADER, None,) )
        self.assertEqual(dpc.getCurrentId(), (current_thread().ident, None) )
        
    def test_DummyParameterContainer5(self):
        dpc = DummyParameterContainer()
        dpc.setOrigin(ORIGIN_PROCESS, "plip")
        self.assertEqual(dpc.getOrigin(), (ORIGIN_PROCESS, None,) )
        self.assertEqual(dpc.getCurrentId(), (current_thread().ident, None) )

    ## ParameterContainer ##
    
    def test_ParameterContainer1(self):
        pc = ParameterContainer()
        self.assertTrue(pc.isMainThread())
        self.assertIs(pc.getCurrentProcedure(), None)       
        self.assertEqual(pc.getOrigin(), (ORIGIN_PROCESS, None,) ) 
        self.assertEqual(pc.getCurrentId(), (current_thread().ident, -1,) ) 
        self.assertEqual(len(pc.threadInfo),0)
    
    def test_ParameterContainer2(self):#registerParameterManager, try to register a not flushable parameterManager
        pc = ParameterContainer()
        self.assertRaises(DefaultPyshellException, pc.registerParameterManager, "plop", object())
        
    def test_ParameterContainer3(self):#registerParameterManager, try to register two parameterManager with the same name
        pc = ParameterContainer()
        pc.registerParameterManager("plop", ParameterManager())
        self.assertRaises(DefaultPyshellException, pc.registerParameterManager, "plop", ParameterManager())
        
    def test_ParameterContainer4(self):#registerParameterManager, flush test
        pc = ParameterContainer()
        self.assertEqual(len(pc.parameterManagerList),0)
        pc.registerParameterManager("plop", ParameterManager())
        self.assertEqual(len(pc.parameterManagerList),1)
        
        #entering level 0
        pc.pushVariableLevelForThisThread("process")
        ti = pc.getThreadInfo()
        pc.plop.setParameter("toto", "plop", localParam = True)
        self.assertTrue(pc.plop.hasParameter("toto", localParam = True, exploreOtherLevel=True))
        self.assertEqual(ti.procedureStack, ["process"])
        self.assertEqual(ti.origin, ORIGIN_PROCESS)
        self.assertEqual(ti.originArg, None)
        self.assertEqual(len(ti.procedureStack), 1)
        
        #exiting level 0, so go to -1
        pc.popVariableLevelForThisThread()
        ti = pc.getThreadInfo()
        self.assertFalse(pc.plop.hasParameter("toto", localParam = True, exploreOtherLevel=True)) #not the same level, the parameter does not exist
        self.assertEqual(ti.procedureStack, [])
        self.assertEqual(ti.origin, ORIGIN_PROCESS)
        self.assertEqual(ti.originArg, None)
        self.assertEqual(len(ti.procedureStack), 0)
        
        #entering level 0 again
        pc.pushVariableLevelForThisThread("process2")
        ti = pc.getThreadInfo()
        self.assertFalse(pc.plop.hasParameter("toto", localParam = True, exploreOtherLevel=True)) #same level, but the parameter has been flushed on pop, so doesn't exist anymore
        self.assertEqual(ti.procedureStack, ["process2"])
        self.assertEqual(ti.origin, ORIGIN_PROCESS)
        self.assertEqual(ti.originArg, None)
        self.assertEqual(len(ti.procedureStack), 1)
        
    def test_ParameterContainer5(self): #getThreadInfo, it does not exist
        pc = ParameterContainer()
        ti = pc.getThreadInfo()
        self.assertEqual(ti.procedureStack, [])
        self.assertEqual(ti.origin, ORIGIN_PROCESS)
        self.assertEqual(ti.originArg, None)
        self.assertEqual(len(ti.procedureStack), 0)
        
    def test_ParameterContainer6(self): #getThreadInfo, it exists
        pc = ParameterContainer()
        ti = pc.getThreadInfo()
        
        ti.procedureStack.append("plop")

        ti = pc.getThreadInfo()
        self.assertEqual(ti.procedureStack, ["plop"])
        self.assertEqual(ti.origin, ORIGIN_PROCESS)
        self.assertEqual(ti.originArg, None)
        self.assertEqual(len(ti.procedureStack), 1)
        
    def test_ParameterContainer7(self): #push
        pc = ParameterContainer()
        self.assertEqual(len(pc.parameterManagerList),0)
        
        pc.pushVariableLevelForThisThread("lpopProcess")
        self.assertEqual(len(pc.threadInfo),1)
        
        ti = pc.getThreadInfo()
        self.assertEqual(ti.procedureStack, ["lpopProcess"])
        self.assertEqual(ti.origin, ORIGIN_PROCESS)
        self.assertEqual(ti.originArg, None)
        self.assertEqual(len(ti.procedureStack), 1)
        
    def test_ParameterContainer8(self): #push
        pc = ParameterContainer()
        self.assertEqual(len(pc.threadInfo),0)
        
        pc.pushVariableLevelForThisThread("lpopProcess")
        pc.pushVariableLevelForThisThread("lpopProcess1")
        pc.pushVariableLevelForThisThread("lpopProcess2")
        pc.pushVariableLevelForThisThread("lpopProcess3")
        pc.pushVariableLevelForThisThread("lpopProcess4")
        pc.pushVariableLevelForThisThread("lpopProcess5")
        self.assertEqual(len(pc.threadInfo),1)
        
        ti = pc.getThreadInfo()
        self.assertEqual(ti.procedureStack, ["lpopProcess","lpopProcess1","lpopProcess2","lpopProcess3","lpopProcess4","lpopProcess5"])
        self.assertEqual(ti.origin, ORIGIN_PROCESS)
        self.assertEqual(ti.originArg, None)
        self.assertEqual(len(ti.procedureStack), 6)
        
    def test_ParameterContainer9(self): #pop, empty threadInfo
        pc = ParameterContainer()
        pc.popVariableLevelForThisThread()
        
    def test_ParameterContainer10(self): #pop, deletable thread info
        pc = ParameterContainer()
        pc.getThreadInfo()
        self.assertEqual(len(pc.threadInfo),1)
        pc.popVariableLevelForThisThread()
        self.assertEqual(len(pc.threadInfo),0)
        
    def test_ParameterContainer11(self): #1 push + 1 pop
        pc = ParameterContainer()
        self.assertEqual(len(pc.threadInfo),0)
        pc.pushVariableLevelForThisThread("lpopProcess")
        self.assertEqual(len(pc.threadInfo),1)
        ti = pc.getThreadInfo()
        self.assertEqual(len(ti.procedureStack), 1)
        pc.popVariableLevelForThisThread()
        self.assertEqual(len(pc.threadInfo),0)
        
    def test_ParameterContainer12(self): #2 push + 1 pop
        pc = ParameterContainer()
        self.assertEqual(len(pc.threadInfo),0)
        pc.pushVariableLevelForThisThread("lpopProcess")
        ti = pc.getThreadInfo()
        self.assertEqual(len(ti.procedureStack), 1)
        pc.pushVariableLevelForThisThread("lpopProcess2")
        ti = pc.getThreadInfo()
        self.assertEqual(len(ti.procedureStack), 2)
        self.assertEqual(len(pc.threadInfo),1)
        pc.popVariableLevelForThisThread()
        self.assertEqual(len(pc.threadInfo),1)
        ti = pc.getThreadInfo()
        self.assertEqual(len(ti.procedureStack), 1)
        
    def test_ParameterContainer13(self): #2 push + 3 pop
        pc = ParameterContainer()
        self.assertEqual(len(pc.threadInfo),0)
        
        pc.pushVariableLevelForThisThread("lpopProcess")
        ti = pc.getThreadInfo()
        self.assertEqual(len(ti.procedureStack), 1)
        
        pc.pushVariableLevelForThisThread("lpopProcess2")
        ti = pc.getThreadInfo()
        self.assertEqual(len(ti.procedureStack), 2)
        
        pc.popVariableLevelForThisThread()
        pc.popVariableLevelForThisThread()
        pc.popVariableLevelForThisThread()
        
        self.assertEqual(len(pc.threadInfo),0)
        
    def test_ParameterContainer14(self): #getCurrentId, thread info exists
        pc = ParameterContainer()
        self.assertEqual(len(pc.threadInfo),0)
        self.assertEqual(pc.getCurrentId(), (current_thread().ident, -1) )
        
    def test_ParameterContainer15(self): #getCurrentId, thread info does not exist
        pc = ParameterContainer()
        pc.pushVariableLevelForThisThread("lpopProcess")
        self.assertEqual(len(pc.threadInfo),1)
        self.assertEqual(pc.getCurrentId(), (current_thread().ident, 0) )
        
    def test_ParameterContainer16(self): #isMainThread, true
        pc = ParameterContainer()
        self.assertTrue(pc.isMainThread())
        
    def test_ParameterContainer17(self): #isMainThread, false
        pc = ParameterContainer()
        pc.mainThread += 1 
        self.assertFalse(pc.isMainThread())
        
    def test_ParameterContainer18(self):#getCurrentProcedure, no thread info for this thread
        pc = ParameterContainer()
        self.assertIs(pc.getCurrentProcedure(), None)
    
    def test_ParameterContainer19(self):#getCurrentProcedure, no level for this thread
        pc = ParameterContainer()
        pc.setOrigin(ORIGIN_FILE, "tutu")
        self.assertEqual(pc.getCurrentProcedure(), None)
    
    def test_ParameterContainer20(self):#getCurrentProcedure, valid procedure stack for this thread
        pc = ParameterContainer()
        pc.pushVariableLevelForThisThread("lpopProcess")
        self.assertEqual(pc.getCurrentProcedure(), "lpopProcess")
        
    def test_ParameterContainer21(self):#getOrigin, no thread info for this thread
        pc = ParameterContainer()
        self.assertEqual(pc.getOrigin(), (ORIGIN_PROCESS, None,) )
        
    def test_ParameterContainer22(self):#getOrigin, valid procedure stack for this thread
        pc = ParameterContainer()
        pc.pushVariableLevelForThisThread("lpopProcess")
        self.assertEqual(pc.getOrigin(), (ORIGIN_PROCESS, None,) )
        
    def test_ParameterContainer23(self):#setOrigin, not a valid origin
        pc = ParameterContainer()
        self.assertRaises(DefaultPyshellException,pc.setOrigin,"plop")
        
    def test_ParameterContainer24(self):#setOrigin, origin == ORIGIN_PROCESS AND no thread info for this thread
        pc = ParameterContainer()
        self.assertEqual(len(pc.threadInfo),0)
        pc.setOrigin(ORIGIN_PROCESS, "plop")
        self.assertEqual(len(pc.threadInfo),0)
        self.assertEqual(pc.getOrigin(), (ORIGIN_PROCESS, None,) )
        
    def test_ParameterContainer25(self):#setOrigin, origin == ORIGIN_PROCESS AND thread info for this thread
        pc = ParameterContainer()
        pc.pushVariableLevelForThisThread("lpopProcess")
        self.assertEqual(len(pc.threadInfo),1)
        pc.setOrigin(ORIGIN_PROCESS, "plop")
        self.assertEqual(pc.getOrigin(), (ORIGIN_PROCESS, "plop",) )
        
    def test_ParameterContainer26(self):#setOrigin, origin == ORIGIN_PROCESS AND thread info for this thread AND cause the thread info removal
        pc = ParameterContainer()
        pc.setOrigin(ORIGIN_FILE, "plop")
        self.assertEqual(len(pc.threadInfo),1)
        pc.setOrigin(ORIGIN_PROCESS, "plop")
        self.assertEqual(len(pc.threadInfo),0)
        self.assertEqual(pc.getOrigin(), (ORIGIN_PROCESS, None,) )
        
    def test_ParameterContainer27(self):#setOrigin, origin != ORIGIN_PROCESS AND no thread info for this thread
        pc = ParameterContainer()
        pc.setOrigin(ORIGIN_FILE, "plop")
        self.assertEqual(len(pc.threadInfo),1)
        self.assertEqual(pc.getOrigin(), (ORIGIN_FILE, "plop",) )
        
    def test_ParameterContainer28(self):#setOrigin, origin != ORIGIN_PROCESS AND thread info for this thread
        pc = ParameterContainer()
        pc.pushVariableLevelForThisThread("lpopProcess")
        pc.setOrigin(ORIGIN_FILE, "plop")
        self.assertEqual(len(pc.threadInfo),1)
        self.assertEqual(pc.getOrigin(), (ORIGIN_FILE, "plop",) )
        
        
if __name__ == '__main__':
    unittest.main()
