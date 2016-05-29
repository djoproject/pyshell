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

from threading import current_thread

from pyshell.utils.abstract.flushable import Flushable
from pyshell.utils.exception import DefaultPyshellException


class AbstractParameterContainer(object):
    def getCurrentId(self):
        pass  # TO OVERRIDE

    def getOrigin(self):
        pass  # TO OVERRIDE

    def setOrigin(self, origin, origin_profile=None):
        pass  # TO OVERRIDE


class DummyParameterContainer(AbstractParameterContainer):
    def getCurrentId(self):
        return current_thread().ident

DEFAULT_DUMMY_PARAMETER_CONTAINER = DummyParameterContainer()


class ParameterContainer(AbstractParameterContainer):
    def __init__(self):
        self.mainThread = current_thread().ident
        self.parameterManagerList = []

    def registerParameterManager(self, name, obj):
        if not isinstance(obj, Flushable):
            raise DefaultPyshellException("(ParameterContainer) "
                                          "registerParameterManager, an "
                                          "instance of Flushable object was "
                                          "expected, got '"+str(type(obj))+"'")

        if hasattr(self, name):
            raise DefaultPyshellException("(ParameterContainer) "
                                          "registerParameterManager, an "
                                          "attribute is already registered "
                                          "with this name: '"+str(name)+"'")

        setattr(self, name, obj)
        self.parameterManagerList.append(name)

    def getCurrentId(self):
        return current_thread().ident

    def isMainThread(self):
        return self.mainThread == current_thread().ident
