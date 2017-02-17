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

from pyshell.utils.constants import CONTEXT_ATTRIBUTE_NAME
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME
from pyshell.utils.constants import KEY_ATTRIBUTE_NAME
from pyshell.utils.constants import VARIABLE_ATTRIBUTE_NAME


def getManager(manager_name):
    # imports occur in the method to avoid cyclic redundancy
    if manager_name == ENVIRONMENT_ATTRIBUTE_NAME:
        from pyshell.system.environment import EnvironmentParameterManager
        return EnvironmentParameterManager
    elif manager_name == CONTEXT_ATTRIBUTE_NAME:
        from pyshell.system.context import ContextParameterManager
        return ContextParameterManager
    elif manager_name == VARIABLE_ATTRIBUTE_NAME:
        from pyshell.system.variable import VariableParameterManager
        return VariableParameterManager
    elif manager_name == KEY_ATTRIBUTE_NAME:
        from pyshell.system.key import CryptographicKeyParameterManager
        return CryptographicKeyParameterManager
    else:
        return None
