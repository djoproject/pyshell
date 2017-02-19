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

from pyshell.system.parameter.environment import EnvironmentParameter
from pyshell.system.setting.variable import VariableLocalSettings
from pyshell.system.setting.variable import VariableSettings
from pyshell.utils.constants import EMPTY_STRING
from pyshell.utils.string65 import isString


def _parseValues(output_values, input_values):
    if isString(input_values):
        # with py3, str has starts to heve an attribute __iter__
        output_values.append(input_values)
    elif hasattr(input_values, "__iter__"):
        for v in input_values:
            _parseValues(output_values, v)
    else:
        output_values.append(str(input_values))


class VariableParameter(EnvironmentParameter):
    @staticmethod
    def getInitSettings():
        return VariableLocalSettings()

    @staticmethod
    def getAllowedParentSettingClass():
        return VariableSettings

    # value can be a list or not, it will be processed
    def __init__(self, value, settings=None):
        parsed_value = []
        _parseValues(parsed_value, value)

        EnvironmentParameter.__init__(self,
                                      value=parsed_value,
                                      settings=settings)

    def __str__(self):
        if len(self.value) == 0:
            return EMPTY_STRING

        to_ret = ""

        for v in self.value:
            to_ret += str(v)+" "

        to_ret = to_ret[:-1]

        return to_ret

    def __repr__(self):
        if len(self.value) == 0:
            return "Variable (empty)"

        return "Variable, value: '%s'" % str(self.value)
