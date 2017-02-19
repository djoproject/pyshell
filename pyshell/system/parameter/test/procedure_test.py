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

import os

import pytest

from pyshell.arg.exception import ArgException
from pyshell.system.parameter.procedure import ProcedureParameter
from pyshell.system.setting.procedure import ProcedureGlobalSettings
from pyshell.utils.exception import ParameterException


def getScriptPath(script_name):
    current_file_path = os.path.realpath(__file__)
    current_directory_path = os.path.dirname(current_file_path)
    return os.path.join(current_directory_path, 'resources', script_name)


class TestProcedureParameter(object):

    def test_innitInvalidFilePath(self):
        with pytest.raises(ArgException) as excinfo:
            ProcedureParameter(file_path=object())
        assert 'does not exist and must exist' in str(excinfo.value)

    def test_innitValidFilePath(self):
        path = getScriptPath('script')
        fp = ProcedureParameter(file_path=path)
        assert fp.getValue() is path

    def test_innitInvalidCustomSettings(self):
        with pytest.raises(ParameterException):
            ProcedureParameter(file_path=getScriptPath('script'),
                               settings=object())

    def test_innitCustomSettings(self):
        path = getScriptPath('script')
        settings = ProcedureGlobalSettings()
        fp = ProcedureParameter(file_path=path, settings=settings)
        assert fp.getValue() is path
        assert fp.settings is settings

    def test_cloneWithParent(self):
        fp = ProcedureParameter(
            file_path=getScriptPath('several_actions_script'))
        fpc = ProcedureParameter(file_path=getScriptPath('script'))
        fpc.settings.setRemovable(False)

        fpc.clone(fp)

        assert fp is not fpc
        assert fp.settings is not fpc.settings
        assert fp.getValue() is fpc.getValue()
        assert fp.getValue() == fpc.getValue()
        assert hash(fp.settings) == hash(fpc.settings)
        assert hash(fp) == hash(fpc)

    def test_cloneWithoutParent(self):
        fp = ProcedureParameter(
            file_path=getScriptPath('several_actions_script'))
        fpc = fp.clone()

        assert fp is not fpc
        assert fp.settings is not fpc.settings
        assert fp.getValue() is fpc.getValue()
        assert fp.getValue() == fpc.getValue()
        assert hash(fp.settings) == hash(fpc.settings)
        assert hash(fp) == hash(fpc)
