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

from pyshell.system.manager.parent import ParentManager
from pyshell.system.manager.variable import VariableParameterManager
from pyshell.system.parameter.variable import VariableParameter
from pyshell.utils.exception import ParameterException
from pyshell.utils.raises import raiseIfNotInstance


def setArgs(container, args=None):
    raiseIfNotInstance(container,
                       "container",
                       ParentManager,
                       ParameterException,
                       "setArgs")

    variables = container.getVariableManager()

    raiseIfNotInstance(variables,
                       "variables",
                       VariableParameterManager,
                       ParameterException,
                       "setArgs")

    if args is None:
        args = ()

    if not hasattr(args, "__iter__"):
        raise ParameterException("(setArgs) args argument is not iterable")

    # all in one string
    var = VariableParameter(' '.join(str(x) for x in args))
    variables.setParameter("*", var, local_param=True)

    # arg count
    var = VariableParameter(len(args))
    variables.setParameter("#", var, local_param=True)

    # all args
    var = VariableParameter(args)
    variables.setParameter("@", var, local_param=True)

    # value from last command
    var = VariableParameter(())
    variables.setParameter("?", var, local_param=True)

    # last pid started in background
    var = VariableParameter("")
    variables.setParameter("!", var, local_param=True)

    # current process id
    var = VariableParameter(container.getCurrentId())
    variables.setParameter("$", var, local_param=True)
