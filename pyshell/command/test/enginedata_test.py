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
from pyshell.command.engine import EMPTY_DATA_TOKEN
from pyshell.command.engine import EngineV3
from pyshell.command.exception import ExecutionException


def noneFun():
    pass


class TestData(object):

    def setup_method(self, method):
        self.mc = MultiCommand()
        self.mc.addProcess(noneFun, noneFun, noneFun)

    def test_flushData(self):
        e = EngineV3([self.mc], [[]], [[{}, {}, {}]])
        e.flushData()
        assert len(e.stack[0][0]) is 0

        e.addData(11)
        e.addData(12)
        e.addData(13)
        assert len(e.stack[0][0]) is 3
        e.flushData()
        assert len(e.stack[0][0]) is 0

        del e.stack[:]
        with pytest.raises(ExecutionException):
            e.flushData()

    def test_append(self):
        e = EngineV3([self.mc], [[]], [[{}, {}, {}]])

        e.appendData(11)
        e.appendData(12)
        e.appendData(13)

        assert len(e.stack[0][0]) is 4
        assert e.stack[0][0][0] is EMPTY_DATA_TOKEN
        assert e.stack[0][0][1] is 11
        assert e.stack[0][0][2] is 12
        assert e.stack[0][0][3] is 13

        del e.stack[:]
        with pytest.raises(ExecutionException):
            e.appendData(42)

    def test_addData(self):
        e = EngineV3([self.mc], [[]], [[{}, {}, {}]])
        with pytest.raises(ExecutionException):
            e.addData(33, 0)

        # regular addData
        e.addData(33, 0, False)
        assert len(e.stack[0][0]) is 2
        assert e.stack[0][0][0] is 33
        assert e.stack[0][0][1] is EMPTY_DATA_TOKEN

        e.addData(44)
        assert len(e.stack[0][0]) is 3
        assert e.stack[0][0][0] is 33
        assert e.stack[0][0][1] is 44
        assert e.stack[0][0][2] is EMPTY_DATA_TOKEN

        del e.stack[:]
        with pytest.raises(ExecutionException):
            e.addData(33)

    def test_removeData(self):
        e = EngineV3([self.mc], [[]], [[{}, {}, {}]])
        with pytest.raises(ExecutionException):
            e.removeData(-2)
        with pytest.raises(ExecutionException):
            e.removeData(1)

        e.removeData()
        assert len(e.stack[0][0]) is 0
        assert e.stack[0][1][-1] is 0

        e.addData(None)
        e.addData(44)
        e.addData(55)

        e.removeData(1)
        assert len(e.stack[0][0]) is 2
        assert e.stack[0][1][-1] is 0
        assert e.stack[0][0][1] is None
        assert e.stack[0][0][0] is 44

        e.flushData()
        e.addData(None)
        e.addData(44)
        e.addData(55)

        e.removeData(-2)
        assert len(e.stack[0][0]) is 2
        assert e.stack[0][1][-1] is 0
        assert e.stack[0][0][1] is None
        assert e.stack[0][0][0] is 44

        del e.stack[:]
        with pytest.raises(ExecutionException):
            e.removeData()

    def test_getData(self):
        e = EngineV3([self.mc], [[]], [[{}, {}, {}]])

        assert e.getData() == EMPTY_DATA_TOKEN
        e.setData(32)
        assert e.getData() == 32
        e.setData(None)
        assert e.getData() is None

        del e.stack[:]
        with pytest.raises(ExecutionException):
            e.getData()
        with pytest.raises(ExecutionException):
            e.setData(33)

    def test_hasNextData(self):
        e = EngineV3([self.mc], [[]], [[{}, {}, {}]])

        assert not e.hasNextData()
        e.addData(11)
        assert e.hasNextData()

        del e.stack[:]
        with pytest.raises(ExecutionException):
            e.hasNextData()

    def test_getRemainingDataCount(self):
        e = EngineV3([self.mc], [[]], [[{}, {}, {}]])

        assert e.getRemainingDataCount() == 0
        e.addData(11)
        assert e.getRemainingDataCount() == 1
        e.addData(12)
        e.addData(13)
        e.addData(14)
        e.addData(15)
        assert e.getRemainingDataCount() == 5

        del e.stack[:]
        with pytest.raises(ExecutionException):
            e.getRemainingDataCount()

    def test_getDataCount(self):
        e = EngineV3([self.mc], [[]], [[{}, {}, {}]])

        assert e.getDataCount() == 1
        e.addData(11)
        assert e.getDataCount() == 2
        e.addData(12)
        e.addData(13)
        e.addData(14)
        e.addData(15)
        assert e.getDataCount() == 6

        del e.stack[:]
        with pytest.raises(ExecutionException):
            e.getDataCount()
