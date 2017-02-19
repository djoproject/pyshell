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

from pyshell.arg.accessor.engine import EngineAccessor

TYPENAME = "container"


class ContainerAccessor(EngineAccessor):
    def hasAccessorValue(self):
        return (EngineAccessor.hasAccessorValue(self) and
                self.engine.getEnv() is not None)

    def getAccessorValue(self):
        return EngineAccessor.getAccessorValue(self).getEnv()

    def buildErrorMessage(self):
        if not EngineAccessor.hasAccessorValue(self):
            return EngineAccessor.buildErrorMessage(self)
        return "provided engine has no associated container"

    @classmethod
    def getTypeName(cls):
        return TYPENAME
