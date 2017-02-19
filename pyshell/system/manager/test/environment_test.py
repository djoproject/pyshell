#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2017  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.system.manager.environment import EnvironmentParameterManager
from pyshell.system.manager.test.fakeparent import FakeParentManager
from pyshell.system.parameter.context import ContextParameter
from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME
from pyshell.utils.exception import ParameterException


class TestEnvironmentManager(object):
    def test_manager1(self):
        assert EnvironmentParameterManager(FakeParentManager()) is not None

    def test_getLoaderName(self):
        name = EnvironmentParameterManager.getLoaderName()
        assert name is ENVIRONMENT_ATTRIBUTE_NAME

    # try to set valid value
    def test_manager2(self):
        manager = EnvironmentParameterManager(FakeParentManager())
        param = manager.setParameter("env.test", ("plop",))
        assert param.getValue() == ["plop"]

    # try to set valid parameter
    def test_manager3(self):
        manager = EnvironmentParameterManager(FakeParentManager())
        param = manager.setParameter("env.test",
                                     EnvironmentParameter(("plop",)))
        assert param.getValue() == ["plop"]

    # try to set invalid parameter
    def test_manager4(self):
        manager = EnvironmentParameterManager(FakeParentManager())
        with pytest.raises(ParameterException):
            manager.setParameter("env.test", ContextParameter("0x1122ff"))
