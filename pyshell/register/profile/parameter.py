#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2016  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.register.profile.default import DefaultProfile
from pyshell.register.profile.exception import RegisterException
from pyshell.system.manager import isAValidStringPath
from pyshell.system.parameter import Parameter
from pyshell.utils.raises import raiseIfNotSubclass


class ParameterLoaderProfile(DefaultProfile):

    def __init__(self, parameter_definition):
        DefaultProfile.__init__(self)

        raiseIfNotSubclass(parameter_definition,
                           "parameter_definition",
                           Parameter,
                           RegisterException,
                           "__init__",
                           self.__class__.__name__)

        self.parameter_to_set = {}
        self.parameter_to_unset = []
        self.parameter_definition = parameter_definition

    def addParameter(self, parameter_name, parameter):
        # test parameter_name
        state, result = isAValidStringPath(parameter_name)
        if not state:
            excmsg = "(" + self.__class__.__name__ + \
                ") addParameter, " + result
            raise RegisterException(excmsg)

        if not isinstance(parameter, self.parameter_definition):
            if isinstance(parameter, Parameter):
                excmsg = ("(" + self.__class__.__name__ + ") addParameter, "
                          "parameter must be an instance of '" +
                          str(self.parameter_definition.__name__) +
                          "' got '" + str(type(parameter)) + "'")
                raise RegisterException(excmsg)

            try:
                parameter = self.parameter_definition(parameter)
            except Exception as ex:
                excmsg = ("(" + self.__class__.__name__ + ") addParameter, "
                          "fail to instanciate the parameter, reason: " +
                          str(ex))
                raise RegisterException(excmsg)

        parameter.enableGlobal()
        self.parameter_to_set[parameter_name] = parameter
        return parameter
