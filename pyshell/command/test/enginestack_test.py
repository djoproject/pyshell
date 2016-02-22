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

from pyshell.command.exception import ExecutionException
from pyshell.command.stackEngine import EngineStack


class TestEngineStack(object):

    def setup_method(self, method):
        self.stack = EngineStack()

    def test_insert(self):
        assert self.stack.size() == 0
        assert self.stack.isEmpty()
        assert not self.stack.isLastStackItem()
        with pytest.raises(ExecutionException):
            self.stack.raiseIfEmpty()
        with pytest.raises(ExecutionException):
            self.stack.raiseIfEmpty("plop")
        self.stack.push(1, 2, 3, 4)
        assert self.stack[0][0] == 1
        assert self.stack[0][1] == 2
        assert self.stack[0][2] == 3
        assert self.stack[0][3] == 4
        self.stack.raiseIfEmpty()
        self.stack.raiseIfEmpty("plop")
        assert self.stack.size() == 1
        assert not self.stack.isEmpty()
        assert self.stack.isLastStackItem()

        self.stack.push(5, 6, 7)
        assert self.stack[-1][0] == 5
        assert self.stack[-1][1] == 6
        assert self.stack[-1][2] == 7
        assert self.stack[-1][3] is None
        self.stack.raiseIfEmpty()
        self.stack.raiseIfEmpty("plop")
        assert self.stack.size() == 2
        assert not self.stack.isEmpty()
        assert not self.stack.isLastStackItem()

    def test_basicMeth(self):
        self.stack.push(["a"], [1, 2], 2, [True, False])
        assert len(self.stack.data(0)) == 1
        assert self.stack.data(0)[0] == "a"
        assert len(self.stack.path(0)) == 2
        assert self.stack.path(0)[0] == 1
        assert self.stack.path(0)[1] == 2
        assert self.stack.type(0) == 2
        assert len(self.stack.enablingMap(0)) == 2
        assert self.stack.enablingMap(0)[0]
        assert not self.stack.enablingMap(0)[1]
        assert self.stack.cmdIndex(0) == 1
        assert self.stack.cmdLength(0) == 2
        assert self.stack.item(0) == self.stack[0]
        cmd_list = [[1, 2, 3, 4], [5, 6, 7], [8, 9]]
        assert self.stack.getCmd(0, cmd_list) == cmd_list[1]
        assert self.stack.subCmdLength(0, cmd_list) == 3
        assert self.stack.subCmdIndex(0) == 2

    def test_basicMethWithSuffix(self):
        self.stack.push(["a", "b"], [0, 1], 0, [True, False])
        self.stack.push(["b", "c", "d"], [1, 2], 1, [True, False, True])
        self.stack.push(["c", "d", "e", "f"],
                        [2, 3],
                        2,
                        [True, False, True, False])
        self.stack.push(["d", "e", "f", "g", "h"],
                        [3, 4, 5],
                        3,
                        [True, False, True, False, True])
        self.stack.push(["e", "f", "g", "h", "i", "j"],
                        [4, 5, 6],
                        4,
                        [True, False, True, False, True, False])

        cmd_list = [[1, 2, 3, 4, 5], [5, 6, 7], [8, 9]]
        letter = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]

        for i in range(0, 5):
            dept = len(self.stack) - 1 - i

            # DATA
            data_i = self.stack.dataOnIndex(i)
            data_d = self.stack.dataOnDepth(dept)
            data_t = self.stack.dataOnTop()
            assert len(data_i) == i + 2
            assert len(data_d) == i + 2
            assert len(data_t), 6
            for j in range(0, len(data_i)):
                assert data_i[j] == letter[j + i]
                assert data_d[j] == letter[j + i]
                assert data_t[j] == letter[j + 4]

            # PATH
            path_i = self.stack.pathOnIndex(i)
            path_d = self.stack.pathOnDepth(dept)
            path_t = self.stack.pathOnTop()

            if i < 3:
                assert len(path_i) == 2
                assert len(path_d) == 2
                assert self.stack.cmdIndexOnIndex(i) == 1
                assert self.stack.cmdIndexOnDepth(dept) == 1

                assert self.stack.subCmdLengthOnIndex(i, cmd_list) == 3
                assert self.stack.subCmdLengthOnDepth(dept, cmd_list) == 3

                assert self.stack.subCmdIndexOnIndex(i) == i + 1
                assert self.stack.subCmdIndexOnDepth(dept) == i + 1

                assert self.stack.cmdLengthOnIndex(i) == 2
                assert self.stack.cmdLengthOnDepth(dept) == 2

                assert self.stack.getCmdOnIndex(i, cmd_list) == cmd_list[1]
                assert self.stack.getCmdOnDepth(dept, cmd_list) == cmd_list[1]
            else:
                assert len(path_i) == 3
                assert len(path_d) == 3
                assert self.stack.cmdIndexOnIndex(i) == 2
                assert self.stack.cmdIndexOnDepth(dept) == 2

                assert self.stack.subCmdLengthOnIndex(i, cmd_list) == 2
                assert self.stack.subCmdLengthOnDepth(dept, cmd_list) == 2

                assert self.stack.subCmdIndexOnIndex(i) == i + 2
                assert self.stack.subCmdIndexOnDepth(dept) == i + 2

                assert self.stack.cmdLengthOnIndex(i) == 3
                assert self.stack.cmdLengthOnDepth(dept) == 3

                assert self.stack.getCmdOnIndex(i, cmd_list) == cmd_list[2]
                assert self.stack.getCmdOnDepth(dept, cmd_list) == cmd_list[2]

            assert self.stack.getCmdOnTop(cmd_list) == cmd_list[2]
            assert self.stack.cmdLengthOnTop() == 3
            assert self.stack.subCmdIndexOnTop() == 6
            assert self.stack.cmdIndexOnTop() == 2
            assert self.stack.subCmdLengthOnTop(cmd_list) == 2
            assert len(path_t) == 3
            for j in range(0, len(path_i)):
                assert j + i == path_i[j]
                assert j + i == path_d[j]

            for j in range(0, 3):
                assert j + 4 == path_t[j]

            # TYPE
            assert self.stack.typeOnIndex(i) == i
            assert self.stack.typeOnDepth(dept) == i
            assert self.stack.typeOnTop() == 4

            # ITEM
            assert self.stack.itemOnIndex(i) == self.stack[i]
            assert self.stack.itemOnDepth(dept) == self.stack[i]
            assert self.stack.itemOnTop() == self.stack[-1]

            # MAP
            map_i = self.stack.enablingMapOnIndex(i)
            map_d = self.stack.enablingMapOnDepth(dept)
            map_t = self.stack.enablingMapOnTop()

            assert len(map_i) == i + 2
            assert len(map_d) == i + 2
            assert len(map_t) == 6

            for i in range(0, i + 1):
                if i % 2 == 1:
                    assert not map_i[i]
                    assert not map_d[i]
                else:
                    assert map_i[i]
                    assert map_d[i]

            for i in range(0, 6):
                if i % 2 == 1:
                    assert not map_t[i]
                else:
                    assert map_t[i]

    def test_methMapper(self):
        with pytest.raises(ExecutionException):
            self.stack.__getattr__("totoOnIndex")
