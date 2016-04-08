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
from pyshell.system.parameter import ParameterManager
from pyshell.utils.exception import DefaultPyshellException


class TestException(object):
    # # misc # #

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
        assert dpc.getCurrentId() == current_thread().ident

    # # ParameterContainer # #

    def test_parameterContainer1(self):
        pc = ParameterContainer()
        assert pc.isMainThread()
        assert pc.getCurrentId() == current_thread().ident

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
        pc.mainThread += 1
        assert not pc.isMainThread()
