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

import pytest

from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.decorator import shellMethod
from pyshell.command.command import Command
from pyshell.command.command import MultiCommand
from pyshell.command.engine import EngineV3
from pyshell.command.engine import POSTPROCESS_INSTRUCTION
from pyshell.command.engine import PREPROCESS_INSTRUCTION
from pyshell.command.engine import PROCESS_INSTRUCTION
from pyshell.command.exception import ExecutionException


@shellMethod(arg=DefaultChecker.getArg())
def plop(arg):
    return arg


def noneFun():
    pass


class TestsplitAndMerge(object):

    def setup_method(self, method):
        self.mc = MultiCommand()
        self.mc.addProcess(noneFun, noneFun, noneFun)

        self.mc2 = MultiCommand()
        self.mc2.addProcess(noneFun, noneFun, noneFun)

        self.e = EngineV3([self.mc, self.mc2, self.mc2],
                          [[], [], []],
                          [[{}, {}, {}], [{}, {}, {}], [{}, {}, {}]])

    # _willThisCmdBeCompletlyDisabled(self,
    #    cmdID, startSkipRange, rangeLength=1)
    def test_willThisCmdBeCompletlyDisabled(self):
        mc = MultiCommand()
        for i in range(0, 6):
            mc.addProcess(noneFun, noneFun, noneFun)

        self.e = EngineV3([mc], [[]], [[{}, {}, {}]])

        # must return False
        # empty before range, at least on item true in the after range

        assert not self.e._willThisCmdBeCompletlyDisabled(0, 0, 1)
        assert not self.e._willThisCmdBeCompletlyDisabled(0, 0, 2)
        assert not self.e._willThisCmdBeCompletlyDisabled(0, 0, 5)

        # not empty before range but no value set to true, at least on
        # item true in the after range

        mc.disableCmd(0)
        assert not self.e._willThisCmdBeCompletlyDisabled(0, 1, 1)
        assert not self.e._willThisCmdBeCompletlyDisabled(0, 1, 2)
        assert not self.e._willThisCmdBeCompletlyDisabled(0, 1, 4)

        mc.disableCmd(1)
        assert not self.e._willThisCmdBeCompletlyDisabled(0, 2, 1)
        assert not self.e._willThisCmdBeCompletlyDisabled(0, 2, 2)
        assert not self.e._willThisCmdBeCompletlyDisabled(0, 2, 3)

        # empty after range, at least on item true in the before range

        mc.enableCmd(0)
        assert not self.e._willThisCmdBeCompletlyDisabled(0, 4, 1)
        assert not self.e._willThisCmdBeCompletlyDisabled(0, 3, 2)
        assert not self.e._willThisCmdBeCompletlyDisabled(0, 2, 3)

        # range must have a size of 1 or more than 1
        # skip range must have a size of 0, 1 or more than 1

        # this test will explore every node
        mc.enableCmd(1)
        mc.disableCmd(5)
        assert not self.e._willThisCmdBeCompletlyDisabled(0, 0, 0)
        assert not self.e._willThisCmdBeCompletlyDisabled(0, 6, 0)

        mc.enableCmd(5)
        # mist return True
        # empty before and empty after range
        assert self.e._willThisCmdBeCompletlyDisabled(0, 0, 6)

        # empty before range and after range only set to False
        mc.disableCmd(5)
        mc.disableCmd(4)
        assert self.e._willThisCmdBeCompletlyDisabled(0, 0, 5)
        assert self.e._willThisCmdBeCompletlyDisabled(0, 0, 4)
        mc.enableCmd(5)
        mc.enableCmd(4)

        # before range not empty but only with false value, after range empty
        mc.disableCmd(0)
        mc.disableCmd(1)
        assert self.e._willThisCmdBeCompletlyDisabled(0, 1, 5)
        assert self.e._willThisCmdBeCompletlyDisabled(0, 2, 4)

        # before range not empty but only with false value, after range not
        # empty but only with false value
        mc.disableCmd(5)
        mc.disableCmd(4)
        assert self.e._willThisCmdBeCompletlyDisabled(0, 1, 4)
        assert self.e._willThisCmdBeCompletlyDisabled(0, 1, 3)
        assert self.e._willThisCmdBeCompletlyDisabled(0, 2, 3)
        assert self.e._willThisCmdBeCompletlyDisabled(0, 2, 2)

        # range must have a size of 1 or more than 1
        # skip range must have a size of 0, 1 or more than 1

    # _willThisDataBunchBeCompletlyDisabled(self, dataIndex, startSkipRange,
    #     rangeLength=1)
    def test_willThisDataBunchBeCompletlyDisabledNoneDatabunch(self):
        mc = MultiCommand()
        for i in range(0, 6):
            mc.addProcess(noneFun, noneFun, noneFun)

        self.e = EngineV3([mc], [[]], [[{}, {}, {}]])

        # must return False
        # empty before range, at least on item true in the after range

        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 0, 1)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 0, 2)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 0, 5)

        # not empty before range but no value set to true, at least on item
        # true in the after range

        mc.disableCmd(0)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 1, 1)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 1, 2)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 1, 4)

        mc.disableCmd(1)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 2, 1)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 2, 2)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 2, 3)

        # empty after range, at least on item true in the before range

        mc.enableCmd(0)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 4, 1)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 3, 2)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 2, 3)

        # range must have a size of 1 or more than 1
        # skip range must have a size of 0, 1 or more than 1

        # this test will explore every node
        mc.enableCmd(1)
        mc.disableCmd(5)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 0, 0)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 6, 0)

        mc.enableCmd(5)
        # mist return True
        # empty before and empty after range
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 0, 6)

        # empty before range and after range only set to False
        mc.disableCmd(5)
        mc.disableCmd(4)
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 0, 5)
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 0, 4)
        mc.enableCmd(5)
        mc.enableCmd(4)

        # before range not empty but only with false value, after range empty
        mc.disableCmd(0)
        mc.disableCmd(1)
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 1, 5)
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 2, 4)

        # before range not empty but only with false value, after range not
        # empty but only with false value
        mc.disableCmd(5)
        mc.disableCmd(4)
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 1, 4)
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 1, 3)
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 2, 3)
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 2, 2)

        # range must have a size of 1 or more than 1
        # skip range must have a size of 0, 1 or more than 1

    def test_willThisDataBunchBeCompletlyDisabledNotNoneDatabunch(self):
        mc = MultiCommand()
        for i in range(0, 6):
            mc.addProcess(noneFun, noneFun, noneFun)

        self.e = EngineV3([mc], [[]], [[{}, {}, {}]])
        self.e.stack.setEnableMapOnIndex(0, [True] * 6)
        emap = self.e.stack.enablingMap(0)

        # must return False
        # empty before range, at least on item true in the after range

        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 0, 1)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 0, 2)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 0, 5)

        # not empty before range but no value set to true, at least on
        # item true in the after range

        emap[0] = False
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 1, 1)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 1, 2)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 1, 4)

        emap[1] = False
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 2, 1)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 2, 2)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 2, 3)

        # empty after range, at least on item true in the before range

        emap[0] = True
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 4, 1)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 3, 2)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 2, 3)

        # range must have a size of 1 or more than 1
        # skip range must have a size of 0, 1 or more than 1

        # this test will explore every node
        emap[1] = True
        emap[5] = False
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 0, 0)
        assert not self.e._willThisDataBunchBeCompletlyDisabled(0, 6, 0)

        emap[5] = True
        # mist return True
        # empty before and empty after range
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 0, 6)

        # empty before range and after range only set to False
        emap[5] = False
        emap[4] = False
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 0, 5)
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 0, 4)
        emap[5] = True
        emap[4] = True

        # before range not empty but only with false value, after range empty
        emap[0] = False
        emap[1] = False
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 1, 5)
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 2, 4)

        # before range not empty but only with false value, after range not
        # empty but only with false value
        emap[5] = False
        emap[4] = False
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 1, 4)
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 1, 3)
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 2, 3)
        assert self.e._willThisDataBunchBeCompletlyDisabled(0, 2, 2)

        # range must have a size of 1 or more than 1
        # skip range must have a size of 0, 1 or more than 1
        # same test as previous, but every cmd are enabled and enableMap keep
        # the values, msut give the same results

    # _willThisDataBunchBeCompletlyEnabled(self, dataIndex, startSkipRange,
    #    rangeLength=1)
    def test_willThisDataBunchBeCompletlyEnabled(self):
        mc = MultiCommand()
        for i in range(0, 6):
            mc.addProcess(noneFun, noneFun, noneFun)

        self.e = EngineV3([mc], [[]], [[{}, {}, {}]])

        # map none
        assert self.e._willThisDataBunchBeCompletlyEnabled(0, 1, 3)

        self.e.stack.setEnableMapOnIndex(0, [False] * 6)
        emap = self.e.stack.enablingMap(0)

        # must return False
        # empty before range, at least on item true in the after range

        assert not self.e._willThisDataBunchBeCompletlyEnabled(0, 0, 1)
        assert not self.e._willThisDataBunchBeCompletlyEnabled(0, 0, 2)
        assert not self.e._willThisDataBunchBeCompletlyEnabled(0, 0, 5)

        # not empty before range but no value set to true, at least on item
        # true in the after range

        emap[0] = True
        assert not self.e._willThisDataBunchBeCompletlyEnabled(0, 1, 1)
        assert not self.e._willThisDataBunchBeCompletlyEnabled(0, 1, 2)
        assert not self.e._willThisDataBunchBeCompletlyEnabled(0, 1, 4)

        emap[1] = True
        assert not self.e._willThisDataBunchBeCompletlyEnabled(0, 2, 1)
        assert not self.e._willThisDataBunchBeCompletlyEnabled(0, 2, 2)
        assert not self.e._willThisDataBunchBeCompletlyEnabled(0, 2, 3)

        # empty after range, at least on item true in the before range

        emap[0] = False
        assert not self.e._willThisDataBunchBeCompletlyEnabled(0, 4, 1)
        assert not self.e._willThisDataBunchBeCompletlyEnabled(0, 3, 2)
        assert not self.e._willThisDataBunchBeCompletlyEnabled(0, 2, 3)

        # range must have a size of 1 or more than 1
        # skip range must have a size of 0, 1 or more than 1

        # this test will explore every node
        emap[1] = False
        emap[5] = True
        assert not self.e._willThisDataBunchBeCompletlyEnabled(0, 0, 0)
        assert not self.e._willThisDataBunchBeCompletlyEnabled(0, 6, 0)

        emap[5] = False
        # mist return True
        # empty before and empty after range
        assert self.e._willThisDataBunchBeCompletlyEnabled(0, 0, 6)

        # empty before range and after range only set to False
        emap[5] = True
        emap[4] = True
        assert self.e._willThisDataBunchBeCompletlyEnabled(0, 0, 5)
        assert self.e._willThisDataBunchBeCompletlyEnabled(0, 0, 4)
        emap[5] = False
        emap[4] = False

        # before range not empty but only with false value, after range empty
        emap[0] = True
        emap[1] = True
        assert self.e._willThisDataBunchBeCompletlyEnabled(0, 1, 5)
        assert self.e._willThisDataBunchBeCompletlyEnabled(0, 2, 4)

        # before range not empty but only with false value, after range not
        # empty but only with false value
        emap[5] = True
        emap[4] = True
        assert self.e._willThisDataBunchBeCompletlyEnabled(0, 1, 4)
        assert self.e._willThisDataBunchBeCompletlyEnabled(0, 1, 3)
        assert self.e._willThisDataBunchBeCompletlyEnabled(0, 2, 3)
        assert self.e._willThisDataBunchBeCompletlyEnabled(0, 2, 2)

    # _skipOnCmd(self,cmdID, subCmdID, skipCount = 1)
    def test_skipOnCmd(self):
        # FAILED
        # skip count < 1
        with pytest.raises(ExecutionException):
            self.e._skipOnCmd(0, 0, -10)

        # invalic cmd index
        with pytest.raises(ExecutionException):
            self.e._skipOnCmd(25, 0, 1)

        # invalid sub cmd index
        with pytest.raises(ExecutionException):
            self.e._skipOnCmd(0, 25, 1)

        # this will completly disable a entire cmd
        with pytest.raises(ExecutionException):
            self.e._skipOnCmd(0, 0, 1)

        # this will disable compeltly a databunch at the current cmdID
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        del self.e.stack[:]
        self.e.stack.append((["a"],
                             [0, 0],
                             PREPROCESS_INSTRUCTION,
                             [True, False, False], ))
        with pytest.raises(ExecutionException):
            self.e._skipOnCmd(1, 0, 1)

        # this will disable compeltly a databunch at a different cmdID but
        # with the same command
        del self.e.stack[:]
        self.e.stack.append((["a"],
                             [0, 0, 0],
                             PREPROCESS_INSTRUCTION,
                             [True, False, False], ))
        with pytest.raises(ExecutionException):
            self.e._skipOnCmd(1, 0, 1)

        # SUCCESS
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)

        del self.e.stack[:]
        self.e._skipOnCmd(1, 0, 1)
        assert self.e.cmd_list[1].isdisabledCmd(0)
        for i in range(1, 6):
            assert not self.e.cmd_list[1].isdisabledCmd(i)

        self.e._skipOnCmd(1, 0, 2)
        assert self.e.cmd_list[1].isdisabledCmd(0)
        assert self.e.cmd_list[1].isdisabledCmd(1)
        for i in range(2, 6):
            assert not self.e.cmd_list[1].isdisabledCmd(i)

        self.e._skipOnCmd(1, 4, 1)
        assert self.e.cmd_list[1].isdisabledCmd(0)
        assert self.e.cmd_list[1].isdisabledCmd(1)
        for i in range(2, 4):
            assert not self.e.cmd_list[1].isdisabledCmd(i)
        assert self.e.cmd_list[1].isdisabledCmd(4)
        assert not self.e.cmd_list[1].isdisabledCmd(5)

        self.e._skipOnCmd(1, 4, 2)
        assert self.e.cmd_list[1].isdisabledCmd(0)
        assert self.e.cmd_list[1].isdisabledCmd(1)
        for i in range(2, 4):
            assert not self.e.cmd_list[1].isdisabledCmd(i)
        assert self.e.cmd_list[1].isdisabledCmd(4)
        assert self.e.cmd_list[1].isdisabledCmd(5)

        self.e._skipOnCmd(1, 2, 1)
        for i in range(2, 4):
            if i == 3:
                assert not self.e.cmd_list[1].isdisabledCmd(i)
                continue
            assert self.e.cmd_list[1].isdisabledCmd(i)

        with pytest.raises(ExecutionException):
            self.e._skipOnCmd(1, 2, 2)

        for i in range(0, 6):
            self.e.cmd_list[1].enableCmd(i)

        del self.e.stack[:]
        self.e.stack.append((["a"],
                             [0, 0],
                             PREPROCESS_INSTRUCTION,
                             [True, True, True, False, False, False], ))

        self.e._skipOnCmd(1, 0, 1)
        assert self.e.cmd_list[1].isdisabledCmd(0)
        for i in range(1, 6):
            assert not self.e.cmd_list[1].isdisabledCmd(i)

        self.e._skipOnCmd(1, 0, 2)
        assert self.e.cmd_list[1].isdisabledCmd(0)
        assert self.e.cmd_list[1].isdisabledCmd(1)
        for i in range(2, 6):
            assert not self.e.cmd_list[1].isdisabledCmd(i)

        with pytest.raises(ExecutionException):
            self.e._skipOnCmd(1, 2, 1)

        del self.e.stack[:]
        self.e.stack.append((["a"],
                             [0, 0],
                             PREPROCESS_INSTRUCTION,
                             [False, False, True, True, True, True], ))

        self.e._skipOnCmd(1, 4, 1)
        assert self.e.cmd_list[1].isdisabledCmd(0)
        assert self.e.cmd_list[1].isdisabledCmd(1)
        for i in range(2, 4):
            assert not self.e.cmd_list[1].isdisabledCmd(i)
        assert self.e.cmd_list[1].isdisabledCmd(4)
        assert not self.e.cmd_list[1].isdisabledCmd(5)

        self.e._skipOnCmd(1, 4, 2)
        assert self.e.cmd_list[1].isdisabledCmd(0)
        assert self.e.cmd_list[1].isdisabledCmd(1)
        for i in range(2, 4):
            assert not self.e.cmd_list[1].isdisabledCmd(i)
        assert self.e.cmd_list[1].isdisabledCmd(4)
        assert self.e.cmd_list[1].isdisabledCmd(5)

        self.e._skipOnCmd(1, 2, 1)
        for i in range(0, 6):
            if i == 3:
                assert not self.e.cmd_list[1].isdisabledCmd(i)
                continue
            assert self.e.cmd_list[1].isdisabledCmd(i)

        with pytest.raises(ExecutionException):
            self.e._skipOnCmd(1, 2, 2)

        # disable range
        #   at the biggining
        #   at the end
        #   in the middle
        # range of length 1 or more than 1
        # with empty stack or not
        # with pre/post/pro process on the stack
        # switch to False some already false, or not

    # _enableOnCmd(self, cmdID, subCmdID, enableCount = 1)
    def test_enableOnCmd(self):
        # FAILED
        # skip count < 1
        with pytest.raises(ExecutionException):
            self.e._enableOnCmd(0, 0, -10)

        # invalic cmd index
        with pytest.raises(ExecutionException):
            self.e._enableOnCmd(25, 0, 1)

        # invalid sub cmd index
        with pytest.raises(ExecutionException):
            self.e._enableOnCmd(0, 25, 1)

        # SUCCESS
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)

        for i in range(0, 6):
            self.e.cmd_list[1].disableCmd(i)

        self.e._enableOnCmd(1, 0, 1)
        assert not self.e.cmd_list[1].isdisabledCmd(0)
        for i in range(1, 6):
            assert self.e.cmd_list[1].isdisabledCmd(i)

        self.e._enableOnCmd(1, 0, 2)
        assert not self.e.cmd_list[1].isdisabledCmd(0)
        assert not self.e.cmd_list[1].isdisabledCmd(1)
        for i in range(2, 6):
            assert self.e.cmd_list[1].isdisabledCmd(i)

        self.e._enableOnCmd(1, 4, 1)
        assert not self.e.cmd_list[1].isdisabledCmd(0)
        assert not self.e.cmd_list[1].isdisabledCmd(1)
        for i in range(2, 4):
            assert self.e.cmd_list[1].isdisabledCmd(i)
        assert not self.e.cmd_list[1].isdisabledCmd(4)
        assert self.e.cmd_list[1].isdisabledCmd(5)

        self.e._enableOnCmd(1, 4, 2)
        assert not self.e.cmd_list[1].isdisabledCmd(0)
        assert not self.e.cmd_list[1].isdisabledCmd(1)
        for i in range(2, 4):
            assert self.e.cmd_list[1].isdisabledCmd(i)
        assert not self.e.cmd_list[1].isdisabledCmd(4)
        assert not self.e.cmd_list[1].isdisabledCmd(5)

        self.e._enableOnCmd(1, 2, 1)
        for i in range(2, 4):
            if i == 3:
                assert self.e.cmd_list[1].isdisabledCmd(i)
                continue
            assert not self.e.cmd_list[1].isdisabledCmd(i)

        self.e._enableOnCmd(1, 2, 2)
        for i in range(0, 6):
            assert not self.e.cmd_list[1].isdisabledCmd(i)

        # enable range
        #   at the biggining
        #   at the end
        #   in the middle
        # range of length 1 or more than 1
        # switch to true some already true, or not

    # _skipOnDataBunch(self, dataBunchIndex, subCmdID, skipCount = 1)
    def test_skipOnDataBunch(self):
        # FAILED
        # skip count < 1
        with pytest.raises(ExecutionException):
            self.e._skipOnDataBunch(0, 0, -8000)

        # empty stack
        del self.e.stack[:]
        with pytest.raises(ExecutionException):
            self.e._skipOnDataBunch(0, 0, 1)

        # invalic dataBunchIndex index
        self.e.stack.append((["a"], [0], PREPROCESS_INSTRUCTION, None, ))
        with pytest.raises(ExecutionException):
            self.e._skipOnDataBunch(43, 0, 1)

        # invalid sub cmd index
        with pytest.raises(ExecutionException):
            self.e._skipOnDataBunch(0, 123, 1)

        # not a preprocess
        del self.e.stack[:]
        self.e.stack.append((["a"], [0], PROCESS_INSTRUCTION, None, ))
        with pytest.raises(ExecutionException):
            self.e._skipOnDataBunch(0, 0, 1)

        # will be completly disabled
        del self.e.stack[:]
        self.e.stack.append((["a"], [0, 0], PREPROCESS_INSTRUCTION, None, ))
        with pytest.raises(ExecutionException):
            self.e._skipOnDataBunch(0, 0, 1000)

        # SUCCESS
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)

        self.e._skipOnDataBunch(0, 0, 1)
        emap = self.e.stack.enablingMapOnIndex(0)
        assert not emap[0]
        for i in range(1, 6):
            assert emap[i]

        self.e._skipOnDataBunch(0, 0, 2)
        emap = self.e.stack.enablingMapOnIndex(0)
        assert not emap[0]
        assert not emap[1]
        for i in range(2, 6):
            assert emap[i]

        self.e._skipOnDataBunch(0, 4, 1)
        emap = self.e.stack.enablingMapOnIndex(0)
        assert not emap[0]
        assert not emap[1]
        for i in range(2, 4):
            assert emap[i]
        assert not emap[4]
        assert emap[5]

        self.e._skipOnDataBunch(0, 4, 2)
        assert not emap[0]
        assert not emap[1]
        for i in range(2, 4):
            assert emap[i]
        assert not emap[4]
        assert not emap[5]

        self.e._skipOnDataBunch(0, 2, 1)
        for i in range(2, 4):
            if i == 3:
                assert emap[i]
                continue
            assert not emap[i]

        with pytest.raises(ExecutionException):
            self.e._skipOnDataBunch(0, 2, 2)

    # _enableOnDataBunch(self, dataBunchIndex, subCmdID, enableCount = 1)
    def test_enableOnDataBunch(self):
        # FAILED
        # skip count < 1
        with pytest.raises(ExecutionException):
            self.e._enableOnDataBunch(0, 0, -8000)

        # empty stack
        del self.e.stack[:]
        with pytest.raises(ExecutionException):
            self.e._enableOnDataBunch(0, 0, 1)

        # invalic dataBunchIndex index
        self.e.stack.append((["a"], [0], PREPROCESS_INSTRUCTION, None, ))
        with pytest.raises(ExecutionException):
            self.e._enableOnDataBunch(43, 0, 1)

        # invalid sub cmd index
        with pytest.raises(ExecutionException):
            self.e._enableOnDataBunch(0, 123, 1)

        # not a preprocess
        del self.e.stack[:]
        self.e.stack.append((["a"], [0], PROCESS_INSTRUCTION, None, ))
        with pytest.raises(ExecutionException):
            self.e._enableOnDataBunch(0, 0, 1)

        # SUCCESS
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)

        # totaly reenabled a databunch
        # original map was None, or not
        del self.e.stack[:]
        self.e.stack.append((["a"],
                             [0, 0],
                             PREPROCESS_INSTRUCTION,
                             [False, False, False, False, False, False], ))

        self.e._enableOnDataBunch(0, 0, 1)
        emap = self.e.stack.enablingMapOnIndex(0)
        assert emap[0]
        for i in range(1, 6):
            assert not emap[i]

        self.e._enableOnDataBunch(0, 0, 2)
        assert emap[0]
        assert emap[1]
        for i in range(2, 6):
            assert not emap[i]

        self.e._enableOnDataBunch(0, 4, 1)
        assert emap[0]
        assert emap[1]
        for i in range(2, 4):
            assert not emap[i]
        assert emap[4]
        assert not emap[5]

        self.e._enableOnDataBunch(0, 4, 2)
        assert emap[0]
        assert emap[1]
        for i in range(2, 4):
            assert not emap[i]
        assert emap[4]
        assert emap[5]

        self.e._enableOnDataBunch(0, 2, 1)
        for i in range(2, 4):
            if i == 3:
                assert not emap[i]
                continue

            assert emap[i]

        self.e._enableOnDataBunch(0, 2, 2)
        assert self.e.stack.enablingMapOnIndex(0) is None

        # enable range
        #   at the biggining
        #   at the end
        #   in the middle
        # range of length 1 or more than 1
        # enablingMap is none, or not
        # switch to True some already True, or not

    # skipNextSubCommandOnTheCurrentData(self, skipCount=1):
    def test_skipNextSubCommandOnTheCurrentData(self):
        # FAILED
        # invalid skip count
        with pytest.raises(ExecutionException):
            self.e.skipNextSubCommandOnTheCurrentData(-234)

        # empty stack
        del self.e.stack[:]
        with pytest.raises(ExecutionException):
            self.e.skipNextSubCommandOnTheCurrentData(1)

        # not pre at top
        self.e.stack.append((["a"], [0], PROCESS_INSTRUCTION, None, ))
        with pytest.raises(ExecutionException):
            self.e.skipNextSubCommandOnTheCurrentData(1)

        # SUCCESS
        # add random skip count and check
        del self.e.stack[:]
        self.e.stack.append((["a"], [0], PREPROCESS_INSTRUCTION, None, ))
        self.e.skipNextSubCommandOnTheCurrentData(100)
        assert self.e.stack.subCmdIndexOnIndex(0) is 100

    # skipNextSubCommandForTheEntireDataBunch(self, skipCount=1):
    def test_skipNextSubCommandForTheEntireDataBunch(self):
        # FAILED
        # empty stack
        del self.e.stack[:]
        with pytest.raises(ExecutionException):
            self.e.skipNextSubCommandForTheEntireDataBunch(1)

        # SUCCESS
        # no test to do

    # skipNextSubCommandForTheEntireExecution(self, skipCount=1):
    def test_skipNextSubCommandForTheEntireExecution(self):
        # FAILED
        # empty stack
        del self.e.stack[:]
        with pytest.raises(ExecutionException):
            self.e.skipNextSubCommandForTheEntireExecution(1)

        # no preprocess at top
        self.e.stack.append((["a"], [0], PROCESS_INSTRUCTION, None, ))
        with pytest.raises(ExecutionException):
            self.e.skipNextSubCommandForTheEntireExecution(1)

        # SUCCESS
        # no test to do

    # disableEnablingMapOnDataBunch(self,index=0):
    def test_disableEnablingMapOnDataBunch(self):
        # FAILED
        # invalid index stack
        with pytest.raises(ExecutionException):
            self.e.disableEnablingMapOnDataBunch(8000)

        # not pre at index
        self.e.stack.append((["a"], [0], PROCESS_INSTRUCTION, None, ))
        with pytest.raises(ExecutionException):
            self.e.disableEnablingMapOnDataBunch(-1)

        # SUCCESS
        self.e.stack.append((["a"], [0], PREPROCESS_INSTRUCTION, [True], ))
        self.e.disableEnablingMapOnDataBunch(-1)
        assert self.e.stack.enablingMapOnIndex(-1) is None
        # valid disabling
        # where already none
        # where not
        self.e.stack.append((["a"], [0], PREPROCESS_INSTRUCTION, None, ))
        self.e.disableEnablingMapOnDataBunch(-1)
        assert self.e.stack.enablingMapOnIndex(-1) is None

    # flushArgs(self, index=None)
    def test_flushArgs(self):
        # FAILED
        # None index and empty stack
        del self.e.stack[:]
        with pytest.raises(ExecutionException):
            self.e.flushArgs()

        # invalid index
        with pytest.raises(ExecutionException):
            self.e.flushArgs(-8000)
        with pytest.raises(ExecutionException):
            self.e.flushArgs(123)

        # SUCCESS
        # valid index
        self.e.args_list[0].append("toto")
        self.e.args_list[1].append("tata")

        self.e.flushArgs(1)
        assert self.e.args_list[0] == ["toto"]
        assert self.e.args_list[1] is None

    # addSubCommand(self, cmd, cmdID = None, onlyAddOnce = True,
    #    useArgs = True)
    def test_addSubCommand(self):
        # FAILED
        # invalid sub cmd instance
        with pytest.raises(ExecutionException):
            self.e.addSubCommand(None)
        with pytest.raises(ExecutionException):
            self.e.addSubCommand("toto")
        with pytest.raises(ExecutionException):
            self.e.addSubCommand(52)

        # cmdID is None, and empty stack
        del self.e.stack[:]
        with pytest.raises(ExecutionException):
            self.e.addSubCommand(Command())

        # invalid cmd index
        with pytest.raises(ExecutionException):
            self.e.addSubCommand(Command(), -8000)
        with pytest.raises(ExecutionException):
            self.e.addSubCommand(Command(), 123)

        # SUCCESS
        # with empty stack
        self.e.addSubCommand(Command(), 1)
        assert len(self.e.cmd_list[1]) == 2

        # with not empty stack
        self.e.stack.append((["a", "b", "c"],
                             [0],
                             PREPROCESS_INSTRUCTION,
                             None,))
        self.e.stack.append((["d", "e", "f"],
                             [0, 1],
                             PREPROCESS_INSTRUCTION,
                             None,))

        # none cmd id must return the cmd index at the top
        self.e.addSubCommand(Command(), None)
        assert len(self.e.cmd_list[0]) == 1
        assert len(self.e.cmd_list[1]) == 3

        self.e.stack.append((["d", "e", "f"],
                             [0, 1],
                             PREPROCESS_INSTRUCTION,
                             [True, False, True],))
        self.e.stack.append((["d", "e", "f"],
                             [0, 1, 0],
                             PREPROCESS_INSTRUCTION,
                             [True, False, True],))

        # with stack (with random data on stack, not only matching result,
        #    != path, != preprocess)
        self.e.addSubCommand(Command(), 1)
        # with path not using this cmd
        # with path using this cmd
        #   with None map
        #   with map enabled
        # with cmd used several times in the cmd_list
        assert self.e.stack[1][3] is None
        assert len(self.e.stack[2][3]) == 4
        assert len(self.e.stack[3][3]) == 4

    # addCommand(self, cmd, convertProcessToPreProcess = False)
    def test_addCommand(self):
        # FAILED
        # try to insert a not MultiCommand instance
        with pytest.raises(ExecutionException):
            self.e.addCommand(None)
        with pytest.raises(ExecutionException):
            self.e.addCommand("toto")
        with pytest.raises(ExecutionException):
            self.e.addCommand(52)

        # try to insert with process at top
        # with more than one data
        del self.e.stack[:]
        self.e.stack.append((["a", "b", "c"], [0], PROCESS_INSTRUCTION, None,))
        with pytest.raises(ExecutionException):
            self.e.addCommand(self.mc)

        # try to insert with postprocess at top with process in the middle
        del self.e.stack[:]
        self.e.stack.append((["a", "b", "c"], [0], PROCESS_INSTRUCTION, None,))
        self.e.stack.append((["a"], [0], POSTPROCESS_INSTRUCTION, None,))
        with pytest.raises(ExecutionException):
            self.e.addCommand(self.mc)

        # SUCCESS
        # try to insert with process at top
        # with only one data
        del self.e.stack[:]
        self.e.stack.append((["a"], [0], PROCESS_INSTRUCTION, None,))
        self.e.addCommand(self.mc)

        # try to insert with postprocess at top without process in the middle
        del self.e.stack[:]
        self.e.stack.append((["a"], [0], POSTPROCESS_INSTRUCTION, None,))
        self.e.addCommand(self.mc)

        # insert a valid one with process in the stack, and see if they are
        # correctly converted
        del self.e.stack[:]
        self.e.stack.append((["a", "b", "c"], [0], PROCESS_INSTRUCTION, None,))
        self.e.stack.append((["a"], [0], POSTPROCESS_INSTRUCTION, None,))
        self.e.addCommand(self.mc, True)
        assert self.e.stack[0][2] == PREPROCESS_INSTRUCTION

    def test_isCurrentRootCommand(self):
        mc = MultiCommand()
        mc.addProcess(plop, plop, plop)
        mc.addProcess(plop, plop, plop)
        mc.addProcess(plop, plop, plop)

        engine = EngineV3([mc, mc, mc],
                          [[], [], []],
                          [[{}, {}, {}], [{}, {}, {}], [{}, {}, {}]])

        assert engine.isCurrentRootCommand()

        engine.stack[-1][1].append(2)
        assert not engine.isCurrentRootCommand()

        del engine.stack[:]
        with pytest.raises(ExecutionException):
            engine.isCurrentRootCommand()
