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

from pyshell.system.manager.test.fakeparent import FakeParentManager
from pyshell.system.manager.variable import VariableParameterManager
from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.system.parameter.variable import VariableParameter
from pyshell.utils.constants import VARIABLE_ATTRIBUTE_NAME
from pyshell.utils.exception import ParameterException


class TestVariableManager(object):
    def test_manager(self):
        assert VariableParameterManager(FakeParentManager()) is not None

    def test_getLoaderName(self):
        name = VariableParameterManager.getLoaderName()
        assert name is VARIABLE_ATTRIBUTE_NAME

    def test_addAValidVariable(self):
        manager = VariableParameterManager(FakeParentManager())
        manager.setParameter("test.var", VariableParameter("0x1122ff"))
        assert manager.hasParameter("t.v")
        param = manager.getParameter("te.va")
        assert isinstance(param,  VariableParameter)
        assert hasattr(param.getValue(), "__iter__")
        assert param.getValue() == ["0x1122ff"]

    def test_addNotAllowedParameter(self):
        manager = VariableParameterManager(FakeParentManager())
        with pytest.raises(ParameterException):
            manager.setParameter("test.var", EnvironmentParameter("0x1122ff"))
