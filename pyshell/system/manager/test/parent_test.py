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

import threading

import pytest

from pyshell.system.manager.context import ContextParameterManager
from pyshell.system.manager.environment import EnvironmentParameterManager
from pyshell.system.manager.key import CryptographicKeyParameterManager
from pyshell.system.manager.parent import ParentManager
from pyshell.system.manager.procedure import ProcedureParameterManager
from pyshell.system.manager.variable import VariableParameterManager
from pyshell.utils.constants import DEFAULT_GROUP_NAME
from pyshell.utils.exception import DefaultPyshellException


class TestParentManager(object):
    def test_getEnvironmentManager(self):
        p = ParentManager()
        e1 = p.getEnvironmentManager()
        assert isinstance(e1, EnvironmentParameterManager)
        e2 = p.getEnvironmentManager()
        assert e1 is e2

    def test_getContextManager(self):
        p = ParentManager()
        c1 = p.getContextManager()
        assert isinstance(c1, ContextParameterManager)
        c2 = p.getContextManager()
        assert c1 is c2

    def test_getKeyManager(self):
        p = ParentManager()
        k1 = p.getKeyManager()
        assert isinstance(k1, CryptographicKeyParameterManager)
        k2 = p.getKeyManager()
        assert k1 is k2

    def test_getProcedureManager(self):
        p = ParentManager()
        p1 = p.getProcedureManager()
        assert isinstance(p1, ProcedureParameterManager)
        p2 = p.getProcedureManager()
        assert p1 is p2

    def test_getVariableManager(self):
        p = ParentManager()
        v1 = p.getVariableManager()
        assert isinstance(v1, VariableParameterManager)
        v2 = p.getVariableManager()
        assert v1 is v2

    def test_flush(self):
        p = ParentManager()
        e = p.getEnvironmentManager()
        e.setParameter("string_path", "value", local_param=True)
        assert e.hasParameter("string_path", local_param=True)
        p.flush()
        assert not e.hasParameter("string_path", local_param=True)

    def test_getCurrentId(self):
        p = ParentManager()
        assert p.getCurrentId() == threading.current_thread().ident

    def test_setDefaultGroupNameWithError(self):
        p = ParentManager()
        with pytest.raises(DefaultPyshellException):
            p.setDefaultGroupName(object)

    def test_setDefaultGroupNameValid(self):
        p = ParentManager()
        p.setDefaultGroupName("toto")
        p.getDefaultGroupName() == "toto"

    def test_getDefaultGroupName(self):
        p = ParentManager()
        p.getDefaultGroupName() == DEFAULT_GROUP_NAME

    def test_checkForSetGlobalParameter(self):
        p = ParentManager()
        p.checkForSetGlobalParameter("group_name", "loader_name")

    def test_checkForUnsetGlobalParameter(self):
        p = ParentManager()
        p.checkForUnsetGlobalParameter("group_name", "loader_name")
