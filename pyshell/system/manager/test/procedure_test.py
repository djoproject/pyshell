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

import os

import pytest

from pyshell.system.manager.procedure import ProcedureParameterManager
from pyshell.system.manager.test.fakeparent import FakeParentManager
from pyshell.system.parameter.context import ContextParameter
from pyshell.system.parameter.procedure import ProcedureParameter
from pyshell.utils.constants import PROCEDURE_ATTRIBUTE_NAME
from pyshell.utils.exception import ParameterException


def getScriptPath(script_name):
    current_file_path = os.path.realpath(__file__)
    current_directory_path = os.path.dirname(current_file_path)
    return os.path.join(current_directory_path, 'resources', script_name)


class TestProcedureManager(object):
    def test_manager1(self):
        assert ProcedureParameterManager(FakeParentManager()) is not None

    def test_getLoaderName(self):
        name = ProcedureParameterManager.getLoaderName()
        assert name is PROCEDURE_ATTRIBUTE_NAME

    # try to set valid value
    def test_manager2(self):
        manager = ProcedureParameterManager(FakeParentManager())
        path = getScriptPath("script")
        param = manager.setParameter("env.test", path)
        assert param.getValue() == path

    # try to set valid parameter
    def test_manager3(self):
        manager = ProcedureParameterManager(FakeParentManager())
        path = getScriptPath("script")
        param = manager.setParameter("env.test", ProcedureParameter(path))
        assert param.getValue() == path

    # try to set invalid parameter
    def test_manager4(self):
        manager = ProcedureParameterManager(FakeParentManager())
        with pytest.raises(ParameterException):
            manager.setParameter("env.test", ContextParameter("0x1122ff"))
