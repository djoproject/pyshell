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

from pyshell.arg.argchecker import ArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.command.command import MultiCommand
from pyshell.command.engine import EMPTY_DATA_TOKEN
from pyshell.command.engine import EngineV3
from pyshell.command.exception import ExecutionException


@shellMethod(arg=ArgChecker())
def plop(arg):
    return arg


class TestsplitAndMerge(object):

    def test_mergeWithCustomeMap(self):
        mc = MultiCommand()
        mc.addProcess(plop, plop, plop)
        mc.addProcess(plop, plop, plop)
        mc.addProcess(plop, plop, plop)

        engine = EngineV3([mc, mc, mc],
                          [[], [], []],
                          [[{}, {}, {}], [{}, {}, {}], [{}, {}, {}]])

        # FAIL
        # empty stack
        del engine.stack[:]
        with pytest.raises(ExecutionException):
            engine.mergeDataAndSetEnablingMap(-1, None, 2)

        for i in range(0, 5):
            engine.stack.append(([None], [0], 0, None,))
        for i in range(0, len(engine.stack)):
            for j in range(1, 6):
                engine.stack[i][0].append(str(i + 1) + str(j))

        # set a map of invalid length
        with pytest.raises(ExecutionException):
            engine.mergeDataAndSetEnablingMap(-1, [True, True, True, True], 2)

        # set a map of valid length but with the current subcmd disabled
        with pytest.raises(ExecutionException):
            engine.mergeDataAndSetEnablingMap(-1, [False, True, True], 2)

        # SUCCESS
        # set a None map on a not None map merged
        del engine.stack[:]

        for i in range(0, 5):
            engine.stack.append(([None], [0], 0, [True, False, True],))
        for i in range(0, len(engine.stack)):
            for j in range(1, 6):
                engine.stack[i][0].append(str(i + 1) + str(j))

        engine.mergeDataAndSetEnablingMap(-1, None, 2)
        assert engine.stack[-1][3] is None

        # set a instanciated map
        del engine.stack[:]
        for i in range(0, 5):
            engine.stack.append(([None], [0], 0, None,))
        for i in range(0, len(engine.stack)):
            for j in range(1, 6):
                engine.stack[i][0].append(str(i + 1) + str(j))

        engine.mergeDataAndSetEnablingMap(-1, [True, False, True], 2)
        assert engine.stack[-1][3] == [True, False, True]

    def test_basicMerge(self):
        mc = MultiCommand()
        mc.addProcess(plop, plop, plop)
        mc.addProcess(plop, plop, plop)
        mc.addProcess(plop, plop, plop)

        engine = EngineV3([mc, mc, mc],
                          [[], [], []],
                          [[{}, {}, {}], [{}, {}, {}], [{}, {}, {}]])
        for i in range(0, 4):
            engine.stack.append(([None], [0], 0, None,))

        for i in range(0, len(engine.stack)):
            for j in range(1, 6):
                engine.stack[i][0].append(str(i + 1) + str(j))

        # FAIL
        # count < 2
        assert not engine.mergeData(-1, 1, None)
        assert not engine.mergeData(0, 0, None)

        # toppestItemToMerge invalid
        with pytest.raises(ExecutionException):
            engine.mergeData(-100, 4, None)

        # count with more to merge than available
        with pytest.raises(ExecutionException):
            engine.mergeData(-1, 400, None)

        # merge pro/post process
            # at the top or in the middle
        del engine.stack[:]
        for i in range(0, 5):
            engine.stack.append(([None], [0], i % 3, None,))
        with pytest.raises(ExecutionException):
            engine.mergeData(-1, 3, None)
        del engine.stack[:]
        for i in range(0, 5):
            engine.stack.append(([None], [0], 0, None,))

        # select a map outside of the scope
        with pytest.raises(ExecutionException):
            engine.mergeData(-1, 2, [True, False, True, False])

        # select a map without the current process included
        with pytest.raises(ExecutionException):
            engine.mergeData(-1, 2, [False, False, True])

        # try to merge some preprocess with different path
        del engine.stack[:]
        for i in range(0, 5):
            engine.stack.append(([None], [0] * (i + 1), i % 3, None,))
            # path of same length but different
        with pytest.raises(ExecutionException):
            engine.mergeData(-1, 2, None)

        del engine.stack[:]
        for i in range(0, 5):
            engine.stack.append(([None], [i % 2, i % 3, i * 2], i % 3, None,))
            # path with a different length
        with pytest.raises(ExecutionException):
            engine.mergeData(-1, 2, None)

        # empty stack
        del engine.stack[:]
        with pytest.raises(ExecutionException):
            engine.mergeData(-1, 2, None)

        # SUCCESS
        # try normal merge
            # with or without selected map
        for k in range(1, 5):
            # reinit
            del engine.stack[:]
            for i in range(0, 5):
                engine.stack.append(([None], [0], 0, None,))
            for i in range(0, len(engine.stack)):
                for j in range(1, 6):
                    engine.stack[i][0].append(str(i + 1) + str(j))

            engine.mergeData(k, 2, None)
            for i in range(0, k - 1):
                assert len(engine.stack[i][0]) == 6

            assert len(engine.stack[k - 1][0]) == 12

            for i in range(k, 4):
                assert len(engine.stack[i][0]) == 6

        for k in range(2, 5):
            # reinit
            del engine.stack[:]
            for i in range(0, 5):
                engine.stack.append(([None], [0], 0, None,))
            for i in range(0, len(engine.stack)):
                for j in range(1, 6):
                    engine.stack[i][0].append(str(i + 1) + str(j))

            engine.mergeData(k, 3, None)
            for i in range(0, k - 2):
                assert len(engine.stack[i][0]) == 6

            assert len(engine.stack[k - 2][0]) == 18

            for i in range(k - 1, 3):
                assert len(engine.stack[i][0]) == 6

    def test_splitWithSet(self):
        mc = MultiCommand()
        mc.addProcess(plop, plop, plop)
        mc.addProcess(plop, plop, plop)
        mc.addProcess(plop, plop, plop)

        engine = EngineV3([mc, mc, mc],
                          [[], [], []],
                          [[{}, {}, {}], [{}, {}, {}], [{}, {}, {}]])
        engine.appendData("11")
        engine.appendData("22")
        engine.appendData("33")
        engine.appendData("44")
        engine.appendData("55")

        # map1 is not None with wrong size
        with pytest.raises(ExecutionException):
            engine.splitDataAndSetEnablingMap(-1, 1, [True, False], None)

        # map1 is not None with current index disabled
        with pytest.raises(ExecutionException):
            engine.splitDataAndSetEnablingMap(-1, 1, [False, True, True], None)

        # map1 is not None with wrong size
        with pytest.raises(ExecutionException):
            engine.splitDataAndSetEnablingMap(-1, 1, None, [True, False])

        # map1 is not None and fully disabled
        with pytest.raises(ExecutionException):
            splitmap = [False, False, False]
            engine.splitDataAndSetEnablingMap(-1, 1, None, splitmap)

        # split at 0 index
        assert engine.stack.size() == 1
        engine.splitDataAndSetEnablingMap(0, 0, None, None)
        assert engine.stack.size() == 1
        assert engine.stack[0][3] is None
        assert engine.stack[0][1] == [0]

        # split at >0 index
        assert engine.stack.size() == 1
        engine.splitDataAndSetEnablingMap(0, 2, None, None)
        assert engine.stack.size() == 2

        assert engine.stack[0][3] is None
        assert engine.stack[1][3] is None

        assert engine.stack[1][1] == [0]
        assert engine.stack[0][1] == [0]

        engine = EngineV3([mc, mc, mc],
                          [[], [], []],
                          [[{}, {}, {}], [{}, {}, {}], [{}, {}, {}]])
        engine.appendData("11")
        engine.appendData("22")
        engine.appendData("33")
        engine.appendData("44")
        engine.appendData("55")

        # split at 0 index with new map
        assert engine.stack.size() == 1
        engine.splitDataAndSetEnablingMap(0,
                                          0,
                                          [True, False, False],
                                          [False, False, True])
        assert engine.stack.size() == 1
        assert engine.stack[0][3] == [True, False, False]
        assert engine.stack[0][1] == [0]

        # split at >0 index with new map
        assert engine.stack.size() == 1
        engine.splitDataAndSetEnablingMap(0,
                                          2,
                                          [True, False, True],
                                          [False, False, True])
        assert engine.stack.size() == 2
        assert engine.stack[1][3] == [True, False, True]
        assert engine.stack[0][3] == [False, False, True]
        assert engine.stack[1][1] == [0]
        assert engine.stack[0][1] == [0]

    def test_split(self):
        mc = MultiCommand()
        mc.addProcess(plop, plop, plop)
        mc.addProcess(plop, plop, plop)
        mc.addProcess(plop, plop, plop)

        engine = EngineV3([mc, mc, mc],
                          [[], [], []],
                          [[{}, {}, {}], [{}, {}, {}], [{}, {}, {}]])
        engine.appendData("11")
        engine.appendData("22")
        engine.appendData("33")
        engine.appendData("44")
        engine.appendData("55")

        # split at 0 index
        assert not engine.splitData(-1, 0, False)
        assert engine.stack.size() == 1

        # split on pro/post
        engine.stack[0] = (engine.stack[0][0],
                           engine.stack[0][1],
                           2,
                           engine.stack[0][3],)
        with pytest.raises(ExecutionException):
            engine.splitData(-1, 1, False)
        engine.stack[0] = (engine.stack[0][0],
                           engine.stack[0][1],
                           0,
                           engine.stack[0][3],)

        # invalid index
        with pytest.raises(ExecutionException):
            engine.splitData(4000, 1, False)
        with pytest.raises(ExecutionException):
            engine.splitData(-1, -4000, False)

        # normal split
        assert engine.splitData(-1, 1, False)
        assert engine.stack.size() == 2
        assert len(engine.stack[1][0]) == 1
        assert engine.stack[1][0][0] == EMPTY_DATA_TOKEN
        assert len(engine.stack[0][0]) == 5
        # print engine.printStack()
        for i in range(1, 6):
            assert engine.stack[0][0][i - 1] == str(i) + str(i)
        assert engine.stack[1][1] == [0]
        assert engine.stack[0][1] == [0]
        assert engine.stack[1][2] == 0
        assert engine.stack[0][2] == 0
        assert engine.stack[1][3] is None
        assert engine.stack[0][3] is None

        # empty stack
        del engine.stack[:]
        with pytest.raises(ExecutionException):
            engine.splitData(-1, 1, False)

    def test_multiLevel(self):
        mc = MultiCommand()
        mc.addProcess(plop, plop, plop)
        mc.addProcess(plop, plop, plop)
        mc.addProcess(plop, plop, plop)

        for k in range(0, 5):
            engine = EngineV3([mc, mc, mc],
                              [[], [], []],
                              [[{}, {}, {}], [{}, {}, {}], [{}, {}, {}]])
            engine.stack.append(([EMPTY_DATA_TOKEN], [0], 0, None,))
            engine.stack.append(([EMPTY_DATA_TOKEN], [0], 0, None,))
            engine.stack.append(([EMPTY_DATA_TOKEN], [0], 0, None,))
            engine.stack.append(([EMPTY_DATA_TOKEN], [0], 0, None,))

            if k == 0:
                tab = [True, True, True]
            elif k == 1:
                tab = [False, True, True]
            elif k == 2:
                tab = [True, False, True]
            elif k == 3:
                tab = [False, False, True]
            else:  # if k == 4:
                tab = [False, False, False]

            engine.stack.setEnableMapOnIndex(k, tab)

            for i in range(0, len(engine.stack)):
                for j in range(1, 6):
                    engine.stack[i][0].append(str(i + 1) + str(j))

            assert engine.stack.size() == 5
            assert engine.splitData(k, 2, False)
            assert engine.stack.size() == 6

            for i in range(0, len(engine.stack)):
                if i < k:
                    assert len(engine.stack[i][0]) == 6
                    assert engine.stack[i][3] is None
                    for j in range(0, 6):
                        if j == 0:
                            assert engine.stack[i][0][j] == EMPTY_DATA_TOKEN
                            continue

                            assert engine.stack[i][0][
                                j] == (str(i + 1) + str(j))

                elif k == i:
                    assert len(engine.stack[i][0]) == 4
                    for j in range(2, 6):
                        assert engine.stack[i][0][
                            j - 2] == (str(i + 1) + str(j))

                elif k + 1 == i:
                    assert len(engine.stack[i][0]) == 2
                    for j in range(0, 2):
                        if j == 0:
                            assert engine.stack[i][0][j] == EMPTY_DATA_TOKEN
                            continue

                        assert engine.stack[i][0][j] == (str(i) + str(j))

                else:
                    assert engine.stack[i][3] is None
                    assert len(engine.stack[i][0]) == 6
                    for j in range(0, 6):
                        if j == 0:
                            assert engine.stack[i][0][j] == EMPTY_DATA_TOKEN
                            continue

                        assert engine.stack[i][0][j] == (str(i) + str(j))

                if k == i:
                    if k == 0:
                        assert engine.stack[i][3] == [True, True, True]
                        assert engine.stack[i][1] == [0]
                        assert engine.stack[i + 1][3] == [True, True, True]
                        assert engine.stack[i + 1][1] == [0]
                    elif k == 1:
                        assert engine.stack[i][3] == [False, True, True]
                        assert engine.stack[i][1] == [0]
                        assert engine.stack[i + 1][3] == [False, True, True]
                        # initial value, not recomputed on split even if
                        # bitmap set to false
                        assert engine.stack[i + 1][1] == [0]
                    elif k == 2:
                        assert engine.stack[i][3] == [True, False, True]
                        assert engine.stack[i][1] == [0]
                        assert engine.stack[i + 1][3] == [True, False, True]
                        assert engine.stack[i + 1][1] == [0]
                    elif k == 3:
                        assert engine.stack[i][3] == [False, False, True]
                        assert engine.stack[i][1] == [0]
                        assert engine.stack[i + 1][3] == [False, False, True]
                        # initial value, not recomputed on split even if
                        # bitmap set to false
                        assert engine.stack[i + 1][1] == [0]
                    else:  # if k == 4:
                        assert engine.stack[i][3] == [False, False, False]
                        assert engine.stack[i][1] == [0]
                        assert engine.stack[i + 1][3] == [False, False, False]
                        assert engine.stack[i + 1][1] == [0]

                assert engine.stack[i][2] == 0
