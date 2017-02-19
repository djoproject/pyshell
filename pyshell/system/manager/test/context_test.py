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

from pyshell.system.manager.context import ContextParameterManager
from pyshell.system.manager.test.fakeparent import FakeParentManager
from pyshell.system.parameter.context import ContextParameter
from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.utils.constants import CONTEXT_ATTRIBUTE_NAME
from pyshell.utils.exception import ParameterException


class TestContextParameterManager(object):

    def test_manager1(self):
        assert ContextParameterManager(FakeParentManager()) is not None

    def test_getLoaderName(self):
        name = ContextParameterManager.getLoaderName()
        assert name is CONTEXT_ATTRIBUTE_NAME

    # try to set valid value
    def test_manager2(self):
        manager = ContextParameterManager(FakeParentManager())
        param = manager.setParameter("context.test", ("plop",))
        assert param.getSelectedValue() == "plop"
        assert param.getValue() == ["plop"]

    # try to set valid parameter
    def test_manager3(self):
        manager = ContextParameterManager(FakeParentManager())
        param = manager.setParameter("context.test",
                                     ContextParameter(("plop",)))
        assert param.getSelectedValue() == "plop"
        assert param.getValue() == ["plop"]

    # try to set invalid parameter
    def test_manager4(self):
        manager = ContextParameterManager(FakeParentManager())
        with pytest.raises(ParameterException):
            manager.setParameter("test.var", EnvironmentParameter("0x1122ff"))
