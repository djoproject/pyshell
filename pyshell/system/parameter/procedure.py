#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.system.setting.procedure import ProcedureLocalSettings
from pyshell.system.setting.procedure import ProcedureSettings


class ProcedureParameter(EnvironmentParameter):
    @staticmethod
    def getInitSettings():
        return ProcedureLocalSettings()

    @staticmethod
    def getAllowedParentSettingClass():
        return ProcedureSettings

    def __init__(self, file_path, settings=None):
        EnvironmentParameter.__init__(self, file_path, settings=settings)

    def clone(self, parent=None):
        if parent is None:
            parent = ProcedureParameter(self.getValue(),
                                        self.settings.clone())

        return EnvironmentParameter.clone(self, parent)
