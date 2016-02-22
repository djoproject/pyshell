#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from threading import current_thread

import pytest

from pyshell.system.container import AbstractParameterContainer
from pyshell.system.container import DummyParameterContainer
from pyshell.system.container import ParameterContainer
from pyshell.system.container import _ThreadInfo
from pyshell.system.parameter import ParameterManager
from pyshell.utils.constants import DEFAULT_PROFILE_NAME
from pyshell.utils.constants import SYSTEM_VIRTUAL_LOADER
from pyshell.utils.exception import DefaultPyshellException


class TestException(object):
    # # misc # #

    # def test_misc(self):
    #    self.assertEqual(len(AVAILABLE_ORIGIN), 3)
    #    self.assertTrue(ORIGIN_FILE in AVAILABLE_ORIGIN)
    #    self.assertTrue(ORIGIN_PROCESS in AVAILABLE_ORIGIN)
    #    self.assertTrue(ORIGIN_LOADER in AVAILABLE_ORIGIN)

    # # thread info # #

    def test_threadInfo2(self):
        ti = _ThreadInfo()
        assert hasattr(ti, "procedureStack")
        assert ti.procedureStack == []
        assert len(ti.procedureStack) == 0

    def test_threadInfo3(self):
        ti = _ThreadInfo()
        assert hasattr(ti, "origin")
        assert ti.origin == SYSTEM_VIRTUAL_LOADER

    def test_threadInfo4(self):
        ti = _ThreadInfo()
        assert hasattr(ti, "origin_profile")
        assert ti.origin_profile == DEFAULT_PROFILE_NAME

    def test_threadInfo5(self):
        ti = _ThreadInfo()
        assert ti.canBeDeleted()

    def test_threadInfo6(self):
        ti = _ThreadInfo()
        ti.procedureStack.append("plop")
        assert not ti.canBeDeleted()

    def test_threadInfo7(self):
        ti = _ThreadInfo()
        ti.origin = "plop"
        assert not ti.canBeDeleted()

    # # AbstractParameterContainer # #

    def test_abstractParameterContainer1(self):
        apc = AbstractParameterContainer()

        assert hasattr(apc, "getCurrentId")
        assert hasattr(apc.getCurrentId, "__call__")
        assert apc.getCurrentId() is None

    def test_abstractParameterContainer2(self):
        apc = AbstractParameterContainer()

        assert hasattr(apc, "getOrigin")
        assert hasattr(apc.getOrigin, "__call__")
        assert apc.getOrigin() is None

    def test_abstractParameterContainer3(self):
        apc = AbstractParameterContainer()

        assert hasattr(apc, "setOrigin")
        assert hasattr(apc.setOrigin, "__call__")
        assert apc.setOrigin("plop", "plip") is None
        assert apc.setOrigin("plop") is None

    # # DummyParameterContainer # #

    def test_dummyParameterContainer1(self):
        dpc = DummyParameterContainer()
        assert dpc.getOrigin() == (SYSTEM_VIRTUAL_LOADER,
                                   DEFAULT_PROFILE_NAME,)
        assert dpc.getCurrentId() == (current_thread().ident, None)

    # def test_DummyParameterContainer2(self):
    #    dpc = DummyParameterContainer()
    #    self.assertRaises(DefaultPyshellException, dpc.setOrigin, "plop")

    def test_dummyParameterContainer3(self):
        dpc = DummyParameterContainer()
        dpc.setOrigin("plop", "plip")
        assert dpc.getOrigin() == ("plop", "plip",)
        assert dpc.getCurrentId() == (current_thread().ident, None)

    # def test_DummyParameterContainer4(self):
    #    dpc = DummyParameterContainer()
    #    dpc.setOrigin(ORIGIN_LOADER, "plip")
    #    self.assertEqual(dpc.getOrigin(), (ORIGIN_LOADER, None,) )
    #    self.assertEqual(dpc.getCurrentId(), (current_thread().ident, None) )

    # def test_DummyParameterContainer5(self):
    #    dpc = DummyParameterContainer()
    #    dpc.setOrigin(SYSTEM_VIRTUAL_LOADER, "plip")
    #    self.assertEqual(dpc.getOrigin(), (SYSTEM_VIRTUAL_LOADER, None,) )
    #    self.assertEqual(dpc.getCurrentId(), (current_thread().ident, None) )

    # # ParameterContainer # #

    def test_parameterContainer1(self):
        pc = ParameterContainer()
        assert pc.isMainThread()
        assert pc.getCurrentProcedure() is None
        assert pc.getOrigin() == (SYSTEM_VIRTUAL_LOADER, DEFAULT_PROFILE_NAME,)
        assert pc.getCurrentId() == (current_thread().ident, -1,)
        assert len(pc.threadInfo) == 0

    # registerParameterManager, try to register a not flushable
    # parameterManager
    def test_parameterContainer2(self):
        pc = ParameterContainer()
        with pytest.raises(DefaultPyshellException):
            pc.registerParameterManager("plop", object())

    # registerParameterManager, try to register two parameterManager with
    # the same name
    def test_parameterContainer3(self):
        pc = ParameterContainer()
        pc.registerParameterManager("plop", ParameterManager())
        with pytest.raises(DefaultPyshellException):
            pc.registerParameterManager("plop", ParameterManager())

    # registerParameterManager, flush test
    def test_parameterContainer4(self):
        pc = ParameterContainer()
        assert len(pc.parameterManagerList) == 0
        pc.registerParameterManager("plop", ParameterManager())
        assert len(pc.parameterManagerList) == 1

        # entering level 0
        pc.pushVariableLevelForThisThread("process")
        ti = pc.getThreadInfo()
        pc.plop.setParameter("toto", "plop", local_param=True)
        assert pc.plop.hasParameter("toto",
                                    local_param=True,
                                    explore_other_level=True)
        assert ti.procedureStack == ["process"]
        assert ti.origin == SYSTEM_VIRTUAL_LOADER
        assert ti.origin_profile == DEFAULT_PROFILE_NAME
        assert len(ti.procedureStack) == 1

        # exiting level 0, so go to -1
        pc.popVariableLevelForThisThread()
        ti = pc.getThreadInfo()
        # not the same level, the parameter does not exist
        assert not pc.plop.hasParameter("toto",
                                        local_param=True,
                                        explore_other_level=True)
        assert ti.procedureStack == []
        assert ti.origin == SYSTEM_VIRTUAL_LOADER
        assert ti.origin_profile == DEFAULT_PROFILE_NAME
        assert len(ti.procedureStack) == 0

        # entering level 0 again
        pc.pushVariableLevelForThisThread("process2")
        ti = pc.getThreadInfo()
        # same level, but the parameter has been flushed on pop, so doesn't
        # exist anymore
        assert not pc.plop.hasParameter("toto",
                                        local_param=True,
                                        explore_other_level=True)
        assert ti.procedureStack == ["process2"]
        assert ti.origin == SYSTEM_VIRTUAL_LOADER
        assert ti.origin_profile == DEFAULT_PROFILE_NAME
        assert len(ti.procedureStack) == 1

    # getThreadInfo, it does not exist
    def test_parameterContainer5(self):
        pc = ParameterContainer()
        ti = pc.getThreadInfo()
        assert ti.procedureStack == []
        assert ti.origin == SYSTEM_VIRTUAL_LOADER
        assert ti.origin_profile == DEFAULT_PROFILE_NAME
        assert len(ti.procedureStack) == 0

    # getThreadInfo, it exists
    def test_parameterContainer6(self):
        pc = ParameterContainer()
        ti = pc.getThreadInfo()

        ti.procedureStack.append("plop")

        ti = pc.getThreadInfo()
        assert ti.procedureStack == ["plop"]
        assert ti.origin == SYSTEM_VIRTUAL_LOADER
        assert ti.origin_profile == DEFAULT_PROFILE_NAME
        assert len(ti.procedureStack) == 1

    # push
    def test_parameterContainer7(self):
        pc = ParameterContainer()
        assert len(pc.parameterManagerList) == 0

        pc.pushVariableLevelForThisThread("lpopProcess")
        assert len(pc.threadInfo) == 1

        ti = pc.getThreadInfo()
        assert ti.procedureStack == ["lpopProcess"]
        assert ti.origin == SYSTEM_VIRTUAL_LOADER
        assert ti.origin_profile == DEFAULT_PROFILE_NAME
        assert len(ti.procedureStack) == 1

    # push
    def test_parameterContainer8(self):
        pc = ParameterContainer()
        assert len(pc.threadInfo) == 0

        pc.pushVariableLevelForThisThread("lpopProcess")
        pc.pushVariableLevelForThisThread("lpopProcess1")
        pc.pushVariableLevelForThisThread("lpopProcess2")
        pc.pushVariableLevelForThisThread("lpopProcess3")
        pc.pushVariableLevelForThisThread("lpopProcess4")
        pc.pushVariableLevelForThisThread("lpopProcess5")
        assert len(pc.threadInfo) == 1

        ti = pc.getThreadInfo()
        assert ti.procedureStack == ["lpopProcess",
                                     "lpopProcess1",
                                     "lpopProcess2",
                                     "lpopProcess3",
                                     "lpopProcess4",
                                     "lpopProcess5"]
        assert ti.origin == SYSTEM_VIRTUAL_LOADER
        assert ti.origin_profile == DEFAULT_PROFILE_NAME
        assert len(ti.procedureStack) == 6

    # pop, empty threadInfo
    def test_parameterContainer9(self):
        pc = ParameterContainer()
        pc.popVariableLevelForThisThread()

    # pop, deletable thread info
    def test_parameterContainer10(self):
        pc = ParameterContainer()
        pc.getThreadInfo()
        assert len(pc.threadInfo) == 1
        pc.popVariableLevelForThisThread()
        assert len(pc.threadInfo) == 0

    # 1 push + 1 pop
    def test_parameterContainer11(self):
        pc = ParameterContainer()
        assert len(pc.threadInfo) == 0
        pc.pushVariableLevelForThisThread("lpopProcess")
        assert len(pc.threadInfo) == 1
        ti = pc.getThreadInfo()
        assert len(ti.procedureStack) == 1
        pc.popVariableLevelForThisThread()
        assert len(pc.threadInfo) == 0

    # 2 push + 1 pop
    def test_parameterContainer12(self):
        pc = ParameterContainer()
        assert len(pc.threadInfo) == 0
        pc.pushVariableLevelForThisThread("lpopProcess")
        ti = pc.getThreadInfo()
        assert len(ti.procedureStack) == 1
        pc.pushVariableLevelForThisThread("lpopProcess2")
        ti = pc.getThreadInfo()
        assert len(ti.procedureStack) == 2
        assert len(pc.threadInfo) == 1
        pc.popVariableLevelForThisThread()
        assert len(pc.threadInfo) == 1
        ti = pc.getThreadInfo()
        assert len(ti.procedureStack) == 1

    # 2 push + 3 pop
    def test_parameterContainer13(self):
        pc = ParameterContainer()
        assert len(pc.threadInfo) == 0

        pc.pushVariableLevelForThisThread("lpopProcess")
        ti = pc.getThreadInfo()
        assert len(ti.procedureStack) == 1

        pc.pushVariableLevelForThisThread("lpopProcess2")
        ti = pc.getThreadInfo()
        assert len(ti.procedureStack) == 2

        pc.popVariableLevelForThisThread()
        pc.popVariableLevelForThisThread()
        pc.popVariableLevelForThisThread()

        assert len(pc.threadInfo) == 0

    # getCurrentId, thread info exists
    def test_parameterContainer14(self):
        pc = ParameterContainer()
        assert len(pc.threadInfo) == 0
        assert pc.getCurrentId() == (current_thread().ident, -1)

    # getCurrentId, thread info does not exist
    def test_parameterContainer15(self):
        pc = ParameterContainer()
        pc.pushVariableLevelForThisThread("lpopProcess")
        assert len(pc.threadInfo) == 1
        assert pc.getCurrentId() == (current_thread().ident, 0)

    # isMainThread, true
    def test_parameterContainer16(self):
        pc = ParameterContainer()
        assert pc.isMainThread()

    # isMainThread, false
    def test_parameterContainer17(self):
        pc = ParameterContainer()
        pc.mainThread += 1
        assert not pc.isMainThread()

    # getCurrentProcedure, no thread info for this thread
    def test_parameterContainer18(self):
        pc = ParameterContainer()
        assert pc.getCurrentProcedure() is None

    # getCurrentProcedure, no level for this thread
    def test_parameterContainer19(self):
        pc = ParameterContainer()
        pc.setOrigin("plip", "tutu")
        assert pc.getCurrentProcedure() is None

    # getCurrentProcedure, valid procedure stack for this thread
    def test_parameterContainer20(self):
        pc = ParameterContainer()
        pc.pushVariableLevelForThisThread("lpopProcess")
        assert pc.getCurrentProcedure() == "lpopProcess"

    # getOrigin, no thread info for this thread
    def test_parameterContainer21(self):
        pc = ParameterContainer()
        assert pc.getOrigin() == (SYSTEM_VIRTUAL_LOADER, DEFAULT_PROFILE_NAME,)

    # getOrigin, valid procedure stack for this thread
    def test_parameterContainer22(self):
        pc = ParameterContainer()
        pc.pushVariableLevelForThisThread("lpopProcess")
        assert pc.getOrigin() == (SYSTEM_VIRTUAL_LOADER, DEFAULT_PROFILE_NAME,)

    # setOrigin, not a valid origin
    # def test_parameterContainer23(self):
    #    pc = ParameterContainer()
    #    self.assertRaises(DefaultPyshellException,pc.setOrigin,"plop")

    # setOrigin, origin == SYSTEM_VIRTUAL_LOADER AND no thread info for
    # this thread
    def test_parameterContainer24(self):
        pc = ParameterContainer()
        assert len(pc.threadInfo) == 0
        pc.setOrigin(SYSTEM_VIRTUAL_LOADER, DEFAULT_PROFILE_NAME)
        assert len(pc.threadInfo) == 0
        assert pc.getOrigin() == (SYSTEM_VIRTUAL_LOADER, DEFAULT_PROFILE_NAME,)

    # setOrigin, origin == SYSTEM_VIRTUAL_LOADER AND thread info for this
    # thread
    def test_parameterContainer25(self):
        pc = ParameterContainer()
        pc.pushVariableLevelForThisThread("lpopProcess")
        assert len(pc.threadInfo) == 1
        pc.setOrigin(SYSTEM_VIRTUAL_LOADER, "plop")
        assert pc.getOrigin() == (SYSTEM_VIRTUAL_LOADER, "plop",)

    # setOrigin, origin == SYSTEM_VIRTUAL_LOADER AND thread info for this
    # thread AND cause the thread info removal
    def test_parameterContainer26(self):
        pc = ParameterContainer()
        pc.setOrigin("plup", "plop")
        assert len(pc.threadInfo) == 1
        pc.setOrigin(SYSTEM_VIRTUAL_LOADER, DEFAULT_PROFILE_NAME)
        assert len(pc.threadInfo) == 0
        assert pc.getOrigin() == (SYSTEM_VIRTUAL_LOADER, DEFAULT_PROFILE_NAME,)

    # setOrigin, origin != SYSTEM_VIRTUAL_LOADER AND no thread info for
    # this thread
    def test_parameterContainer27(self):
        pc = ParameterContainer()
        pc.setOrigin("plap", "plop")
        assert len(pc.threadInfo) == 1
        assert pc.getOrigin() == ("plap", "plop",)

    # setOrigin, origin != SYSTEM_VIRTUAL_LOADER AND thread info for this
    # thread
    def test_parameterContainer28(self):
        pc = ParameterContainer()
        pc.pushVariableLevelForThisThread("lpopProcess")
        pc.setOrigin("plup", "plop")
        assert len(pc.threadInfo) == 1
        assert pc.getOrigin() == ("plup", "plop",)
