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

from threading import Thread
from threading import current_thread

import pytest

from pyshell.system.container import AbstractParameterContainer
from pyshell.system.container import DummyParameterContainer
from pyshell.system.container import MAIN_LEVEL
from pyshell.system.container import PROCEDURE_LEVEL
from pyshell.system.container import ParameterContainer
from pyshell.system.manager import ParameterManager
from pyshell.utils.abstract.flushable import Flushable
from pyshell.utils.exception import DefaultPyshellException


class TestAbstractParameterContainer(object):
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


class TestDummyParameterContainer(object):
    def test_dummyParameterContainer1(self):
        dpc = DummyParameterContainer()
        assert dpc.getCurrentId() == current_thread().ident


class FakeFlushable(Flushable):
    def __init__(self):
        self.flushed = False

    def flush(self):
        self.flushed = True


class TestParameterContainer(object):
    def test_parameterContainer1(self):
        pc = ParameterContainer()
        assert pc.isMainThread()
        assert pc.getCurrentId() == (current_thread().ident, "main",)

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

    # isMainThread, true
    def test_parameterContainer16(self):
        pc = ParameterContainer()
        assert pc.isMainThread()

    # isMainThread, false
    def test_parameterContainer17(self):
        pc = ParameterContainer()

        def testNotInMainThread(pc):
            assert not pc.isMainThread()

        t = Thread(target=testNotInMainThread, args=(pc,))
        t.start()
        t.join()

    def test_increment(self):
        pc = ParameterContainer()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

        pc.incrementLevel()

        tid, level = pc.getCurrentId()
        assert level is PROCEDURE_LEVEL

    def test_decrement(self):
        pc = ParameterContainer()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

        pc.decrementLevel()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

    def test_incrementThenDecrement(self):
        pc = ParameterContainer()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

        pc.incrementLevel()

        tid, level = pc.getCurrentId()
        assert level is PROCEDURE_LEVEL

        pc.decrementLevel()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

    def test_twoConsecutiveIncrement(self):
        pc = ParameterContainer()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

        pc.incrementLevel()

        tid, level = pc.getCurrentId()
        assert level is PROCEDURE_LEVEL

        with pytest.raises(DefaultPyshellException):
            pc.incrementLevel()

        tid, level = pc.getCurrentId()
        assert level is PROCEDURE_LEVEL

    def test_twoConsecutiveDecrement(self):
        pc = ParameterContainer()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

        pc.decrementLevel()
        pc.decrementLevel()

        tid, level = pc.getCurrentId()
        assert level is MAIN_LEVEL

    def test_flush(self):
        f = FakeFlushable()
        pc = ParameterContainer()
        pc.registerParameterManager('toto', f)
        assert not f.flushed
        pc.flush()
        assert f.flushed
