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

from pyshell.arg.accessor.container import ContainerAccessor
from pyshell.arg.accessor.parameter import AbstractParameterAccessor
from pyshell.arg.accessor.parameter import AbstractParameterDynamicAccessor
from pyshell.utils.constants import PROCEDURE_ATTRIBUTE_NAME

ACCESSOR_TYPENAME = "procedure"
DYNAMIC_ACCESSOR_TYPENAME = "procedure dynamic"
MANAGER_TYPENAME = "procedure manager"


class ProcedureAccessor(AbstractParameterAccessor):
    def __init__(self, procedure_string_path):
        AbstractParameterAccessor.__init__(self,
                                           procedure_string_path,
                                           PROCEDURE_ATTRIBUTE_NAME)

    def getManager(self, container):
        return container.getProcedureManager()

    @classmethod
    def getTypeName(cls):
        return ACCESSOR_TYPENAME


class ProcedureDynamicAccessor(AbstractParameterDynamicAccessor):
    def __init__(self):
        AbstractParameterDynamicAccessor.__init__(self,
                                                  PROCEDURE_ATTRIBUTE_NAME)

    def getManager(self, container):
        return container.getProcedureManager()

    @classmethod
    def getTypeName(cls):
        return DYNAMIC_ACCESSOR_TYPENAME


class ProcedureManagerAccessor(ContainerAccessor):
    def hasAccessorValue(self):
        if not ContainerAccessor.hasAccessorValue(self):
            return False

        container = ContainerAccessor.getAccessorValue(self)

        return container.getProcedureManager() is not None

    def getAccessorValue(self):
        return ContainerAccessor.getAccessorValue(self).getProcedureManager()

    def buildErrorMessage(self):
        if not ContainerAccessor.hasAccessorValue(self):
            return ContainerAccessor.buildErrorMessage(self)
        return "container provided has no procedure manager defined"

    @classmethod
    def getTypeName(cls):
        return MANAGER_TYPENAME
