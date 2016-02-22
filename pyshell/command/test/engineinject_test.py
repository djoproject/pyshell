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

from pyshell.command.command import MultiCommand
from pyshell.command.engine import EngineV3
from pyshell.command.engine import POSTPROCESS_INSTRUCTION
from pyshell.command.engine import PREPROCESS_INSTRUCTION
from pyshell.command.engine import PROCESS_INSTRUCTION
from pyshell.command.exception import ExecutionException


def noneFun():
    pass


class TestInject(object):

    def setup_method(self, method):
        self.mc = MultiCommand()
        self.mc.addProcess(noneFun, noneFun, noneFun)
        self.mc.addProcess(noneFun, noneFun, noneFun)
        self.mc.addProcess(noneFun, noneFun, noneFun)
        self.mc.addProcess(noneFun, noneFun, noneFun)

        self.mc2 = MultiCommand()
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)
        self.mc2.addProcess(noneFun, noneFun, noneFun)

        self.e = EngineV3([self.mc, self.mc2, self.mc2, self.mc2],
                          [[], [], [], []],
                          [[{}, {}, {}],
                           [{}, {}, {}],
                           [{}, {}, {}],
                           [{}, {}, {}]])

    def resetStack(self):
        del self.e.stack[:]
        self.e.stack.append((["a"], [0, 2], PREPROCESS_INSTRUCTION, None, ))

        self.e.stack.append((["b"],
                             [0, 2, 0],
                             PREPROCESS_INSTRUCTION,
                             [True, True, True, True], ))
        self.e.stack.append((["b"],
                             [0, 2, 0],
                             PREPROCESS_INSTRUCTION,
                             [True, False, True, True], ))
        self.e.stack.append((["b"],
                             [0, 2, 0],
                             PREPROCESS_INSTRUCTION,
                             [True, True, False, True], ))

        self.e.stack.append((["c"], [0, 3, 0, 0], PROCESS_INSTRUCTION, None, ))
        self.e.stack.append((["d"], [0, 2, 0, 0], PROCESS_INSTRUCTION, None, ))

        self.e.stack.append((["e"], [0, 3], POSTPROCESS_INSTRUCTION, None, ))
        self.e.stack.append(
            (["f"], [0, 2, 0], POSTPROCESS_INSTRUCTION, None, ))

    def test_getTheIndexWhereToStartTheSearch(self):
        # FAIL
        with pytest.raises(ExecutionException):
            self.e._getTheIndexWhereToStartTheSearch(42)
            # try a value different of pre/pro/post process

        # SUCCESS
        # if stack empty return zero
        del self.e.stack[:]
        r = self.e._getTheIndexWhereToStartTheSearch(POSTPROCESS_INSTRUCTION)
        assert r is 0

        r = self.e._getTheIndexWhereToStartTheSearch(PROCESS_INSTRUCTION)
        assert r is 0

        r = self.e._getTheIndexWhereToStartTheSearch(PREPROCESS_INSTRUCTION)
        assert r is 0

        # three different type on stack, search each of them
        self.e.stack.append((["a"], [0], PREPROCESS_INSTRUCTION, None, ))
        self.e.stack.append((["b"], [0], PREPROCESS_INSTRUCTION, None, ))
        self.e.stack.append((["c"], [0], PROCESS_INSTRUCTION, None, ))
        self.e.stack.append((["d"], [0], PROCESS_INSTRUCTION, None, ))
        self.e.stack.append((["e"], [0], POSTPROCESS_INSTRUCTION, None, ))
        self.e.stack.append((["f"], [0], POSTPROCESS_INSTRUCTION, None, ))

        r = self.e._getTheIndexWhereToStartTheSearch(POSTPROCESS_INSTRUCTION)
        assert r is 5

        r = self.e._getTheIndexWhereToStartTheSearch(PROCESS_INSTRUCTION)
        assert r is 3

        r = self.e._getTheIndexWhereToStartTheSearch(PREPROCESS_INSTRUCTION)
        assert r is 1

        # search for each type when they are missing on stack
        del self.e.stack[:]
        self.e.stack.append((["a"], [0], PREPROCESS_INSTRUCTION, None, ))
        self.e.stack.append((["b"], [0], PREPROCESS_INSTRUCTION, None, ))
        self.e.stack.append((["c"], [0], PROCESS_INSTRUCTION, None, ))
        self.e.stack.append((["d"], [0], PROCESS_INSTRUCTION, None, ))

        r = self.e._getTheIndexWhereToStartTheSearch(POSTPROCESS_INSTRUCTION)
        assert r is 3

        del self.e.stack[:]
        self.e.stack.append((["a"], [0], PREPROCESS_INSTRUCTION, None, ))
        self.e.stack.append((["b"], [0], PREPROCESS_INSTRUCTION, None, ))
        self.e.stack.append((["e"], [0], POSTPROCESS_INSTRUCTION, None, ))
        self.e.stack.append((["f"], [0], POSTPROCESS_INSTRUCTION, None, ))

        r = self.e._getTheIndexWhereToStartTheSearch(PROCESS_INSTRUCTION)
        assert r is 1

        del self.e.stack[:]
        self.e.stack.append((["c"], [0], PROCESS_INSTRUCTION, None, ))
        self.e.stack.append((["d"], [0], PROCESS_INSTRUCTION, None, ))
        self.e.stack.append((["e"], [0], POSTPROCESS_INSTRUCTION, None, ))
        self.e.stack.append((["f"], [0], POSTPROCESS_INSTRUCTION, None, ))

        r = self.e._getTheIndexWhereToStartTheSearch(PREPROCESS_INSTRUCTION)
        assert r is -1

    def test_findIndexToInject(self):
        # FAIL
        # try to find too big cmd_path, to generate invalid index
        with pytest.raises(ExecutionException):
            self.e._findIndexToInject([1, 2, 3, 4], PREPROCESS_INSTRUCTION)
        # try to find path with invalid sub index
        with pytest.raises(ExecutionException):
            self.e._findIndexToInject([0, 25], PREPROCESS_INSTRUCTION)

        # try to inject pro process with non root path
        with pytest.raises(ExecutionException):
            self.e._findIndexToInject([0, 0], PROCESS_INSTRUCTION)

        # SUCCESS

        # perfect match
        self.resetStack()
        r = self.e._findIndexToInject([0, 2, 0], POSTPROCESS_INSTRUCTION)
        assert r[1] is 7
        assert r[0] == self.e.stack[7]

        r = self.e._findIndexToInject([0, 3], POSTPROCESS_INSTRUCTION)
        assert r[1] is 6
        assert r[0] == self.e.stack[6]

        r = self.e._findIndexToInject([0, 2, 0, 0], PROCESS_INSTRUCTION)
        assert r[1] is 5
        assert r[0] == self.e.stack[5]

        r = self.e._findIndexToInject([0, 3, 0, 0], PROCESS_INSTRUCTION)
        assert r[1] is 4
        assert r[0] == self.e.stack[4]

        r = self.e._findIndexToInject([0, 2, 0], PREPROCESS_INSTRUCTION)
        assert len(r) is 3
        for i in range(0, 3):
            assert r[i][1] is 3 - i
            assert r[i][0] == self.e.stack[3 - i]

        r = self.e._findIndexToInject([0, 3], PREPROCESS_INSTRUCTION)
        assert len(r) is 1
        assert r[0][1] is 0
        assert r[0][0] is self.e.stack[0]

        # partial match
        r = self.e._findIndexToInject([0, 2, 1], PREPROCESS_INSTRUCTION)
        assert len(r) is 3
        for i in range(0, 3):
            assert r[i][1] is 3 - i
            assert r[i][0] == self.e.stack[3 - i]

        r = self.e._findIndexToInject([0, 3], PREPROCESS_INSTRUCTION)
        assert len(r) is 1
        assert r[0][1] is 0
        assert r[0][0] is self.e.stack[0]

        # no match
        # too long path stop
        r = self.e._findIndexToInject([0, 2, 0, 0], POSTPROCESS_INSTRUCTION)
        assert r[1] is 8
        assert r[0] is None

        # too hight path on stack stop
        r = self.e._findIndexToInject([0, 1, 0], POSTPROCESS_INSTRUCTION)
        assert r[1] is 8
        assert r[0] is None

        # too long path stop
        r = self.e._findIndexToInject([0, 1, 0, 0], PROCESS_INSTRUCTION)
        assert r[1] is 6
        assert r[0] is None

        # too long path stop
        r = self.e._findIndexToInject([0, 2, 0, 0], PREPROCESS_INSTRUCTION)
        assert len(r) is 1
        assert r[0][1] is 4
        assert r[0][0] is None

        # too hight path on stack stop
        r = self.e._findIndexToInject([0, 1, 0], PREPROCESS_INSTRUCTION)
        assert len(r) is 1
        assert r[0][1] is 4
        assert r[0][0] is None

    def test_injectDataProOrPos(self):
        # FAIL
        self.resetStack()
        # try to insert unexistant path with onlyAppend=True
        with pytest.raises(ExecutionException):
            self.e._injectDataProOrPos("toto",
                                       [0, 3, 42],
                                       POSTPROCESS_INSTRUCTION,
                                       True)

        # SUCCESS
        # existant
        self.e._injectDataProOrPos("titi",
                                   [0, 3, 0, 0],
                                   PROCESS_INSTRUCTION,
                                   True)
        assert "titi" in self.e.stack[4][0]
        self.e._injectDataProOrPos("toto",
                                   [0, 3],
                                   POSTPROCESS_INSTRUCTION,
                                   True)
        assert "toto" in self.e.stack[6][0]

        # not existant
        self.e._injectDataProOrPos(
            "plop", [0, 1, 0, 0], PROCESS_INSTRUCTION)
        assert "plop" in self.e.stack[6][0]

        self.e._injectDataProOrPos("plap", [1], POSTPROCESS_INSTRUCTION)
        assert "plap" in self.e.stack[7][0]

    def test_injectDataPre(self):
        # FAIL
            # map of invalid length
        with pytest.raises(ExecutionException):
            self.e.injectDataPre("plop", [0, 1, 2], "toto")
        with pytest.raises(ExecutionException):
            self.e.injectDataPre("plop", [0, 1, 2], [1, 2, 3, 4])
        with pytest.raises(ExecutionException):
            self.e.injectDataPre("plop", [0, 1, 2], [True, False])

            # no match and onlyAppend = True
        with pytest.raises(ExecutionException):
            self.e.injectDataPre("plop",
                                 [0, 1, 2],
                                 [True, False, True, False],
                                 True)

            # onlyAppend=True and existant path and different map
        self.resetStack()
        with pytest.raises(ExecutionException):
            self.e.injectDataPre("plop",
                                 [0, 2, 0],
                                 [True, False, True, False],
                                 True)

        # SUCCESS
        # insert unexisting
        self.e.injectDataPre("plop", [0, 1, 2], [True, False, True, False])
        assert self.e.stack[4][0] == ["plop"]
        assert self.e.stack[4][1] == [0, 1, 0]
        assert self.e.stack[4][2] == PREPROCESS_INSTRUCTION
        assert self.e.stack[4][3] == [True, False, True, False]

        # insert existing with path matching
        self.e.injectDataPre("plip", [0, 2, 0], [True, False, True, True])
        assert self.e.stack[2][0] == ["b", "plip"]

        # insert existing whitout path matching with
        # ifNoMatchExecuteSoonerAsPossible = True
        self.e.injectDataPre("plap",
                             [0, 2, 0],
                             [True, False, True, False],
                             False,
                             True)
        assert self.e.stack[4][0] == ["plap"]
        assert self.e.stack[4][1] == [0, 2, 0]
        assert self.e.stack[4][2] == PREPROCESS_INSTRUCTION
        assert self.e.stack[4][3] == [True, False, True, False]

        # insert existing whitout path matching with
        # ifNoMatchExecuteSoonerAsPossible = False
        self.e.injectDataPre("plyp",
                             [0, 2, 0],
                             [True, False, False, False],
                             False,
                             False)
        assert self.e.stack[1][0] == ["plyp"]
        assert self.e.stack[1][1] == [0, 2, 0]
        assert self.e.stack[1][2] == PREPROCESS_INSTRUCTION
        assert self.e.stack[1][3] == [True, False, False, False]

    def test_insertDataToPreProcess(self):
        # FAIL
        # empty stack
        del self.e.stack[:]
        with pytest.raises(ExecutionException):
            self.e.insertDataToPreProcess("plop")

        # SUCCESS
        # insert with preprocess at top
        self.e.stack.append((["a"], [0, 2], PREPROCESS_INSTRUCTION, None, ))
        self.e.insertDataToPreProcess("plip")
        assert self.e.stack[0][0] == ["a", "plip"]
        assert self.e.stack[0][1] == [0, 2]
        assert self.e.stack[0][2] == PREPROCESS_INSTRUCTION
        assert self.e.stack[0][3] is None

        # insert with anything else at top except preprocess
        # onlyForTheLinkedSubCmd = True
        self.e.stack.append((["a"], [0, 2], POSTPROCESS_INSTRUCTION, None, ))
        self.e.insertDataToPreProcess("plop", True)

        assert self.e.stack[1][0] == ["plop"]
        assert self.e.stack[1][1] == [0, 0]
        assert self.e.stack[1][2] == PREPROCESS_INSTRUCTION
        assert self.e.stack[1][3] == [False, False, True, False]

        # onlyForTheLinkedSubCmd = False
        self.e.insertDataToPreProcess("plap", False)
        assert self.e.stack[0][0] == ["a", "plip", "plap"]
        assert self.e.stack[0][1] == [0, 2]
        assert self.e.stack[0][2] == PREPROCESS_INSTRUCTION
        assert self.e.stack[0][3] is None

    def test_insertDataToProcess(self):
        # FAIL
        # empty stack
        del self.e.stack[:]
        with pytest.raises(ExecutionException):
            self.e.insertDataToProcess("toto")

        # not postprocess on top
        self.e.stack.append((["a"], [0, 2, 0, 0], PROCESS_INSTRUCTION, None, ))
        with pytest.raises(ExecutionException):
            self.e.insertDataToProcess("toto")

        # not root path on top
        self.e.stack.append((["a"], [0, 1], PREPROCESS_INSTRUCTION, None, ))
        with pytest.raises(ExecutionException):
            self.e.insertDataToProcess("toto")

        # SUCCESS
        # success insert
        self.e.stack.append(
            (["a"], [0, 0, 0, 0], POSTPROCESS_INSTRUCTION, None, ))
        self.e.insertDataToProcess("toto")

        assert self.e.stack[2][0] == ["toto"]
        assert self.e.stack[2][1] == [0, 0, 0, 0]
        assert self.e.stack[2][2] == PROCESS_INSTRUCTION
        assert self.e.stack[2][3] is None

    def test_insertDataToNextSubCommandPreProcess(self):
        # FAIL
        # empty stack
        del self.e.stack[:]
        with pytest.raises(ExecutionException):
            self.e.insertDataToNextSubCommandPreProcess("toto")

        # last sub cmd of a cmd on top
        self.e.stack.append(
            (["a"], [0, 0, 0, 3], POSTPROCESS_INSTRUCTION, None, ))
        with pytest.raises(ExecutionException):
            self.e.insertDataToNextSubCommandPreProcess("toto")

        # SUCCESS
        # success insert
        self.e.stack.append(
            (["a"], [0, 0, 0, 2], POSTPROCESS_INSTRUCTION, None, ))
        self.e.insertDataToNextSubCommandPreProcess("toto")

        assert self.e.stack[0][0] == ["toto"]
        assert self.e.stack[0][1] == [0, 0, 0, 0]
        assert self.e.stack[0][2] == PREPROCESS_INSTRUCTION
        assert self.e.stack[0][3] == [False, False, False, True]
