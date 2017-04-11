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

from abc import ABCMeta, abstractmethod

from pyshell.arg.abstract import AbstractArg
from pyshell.arg.exception import ArgException


class AbstractAccessor(AbstractArg):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.engine = None

    # TODO move these two into arg.abstract
    # TODO these two shouldn't be used in accessor...
    def _raiseArgException(self,
                           message,
                           arg_number=None,
                           arg_name_to_bind=None):
        prefix = ""

        if arg_number is not None:
            prefix += "Token <"+str(arg_number)+">"

        if arg_name_to_bind is not None:
            if len(prefix) > 0:
                prefix += " "

            prefix += "at argument '"+str(arg_name_to_bind)+"'"

        if len(prefix) > 0:
            prefix += ": "

        raise ArgException("("+self.getTypeName()+") "+prefix+message)

    def _raiseArgInitializationException(self, excmsg):
        pass  # TODO copy from argchecker

    def _getValue(self, arg_number=None, arg_name_to_bind=None):
        if not self.hasAccessorValue():
            self._raiseArgException(message=self.buildErrorMessage(),
                                    arg_number=None,
                                    arg_name_to_bind=arg_name_to_bind)

        return self.getAccessorValue()

    def setEngine(self, engine):
        self.engine = engine

    def getMaximumSize(self):
        return 0

    def getMinimumSize(self):
        return 0

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        return self._getValue(arg_number, arg_name_to_bind)

    def isShowInUsage(self):
        return False

    def getUsage(self):
        return ""

    def hasDefaultValue(self, arg_name_to_bind=None):
        return self.hasAccessorValue()

    def getDefaultValue(self, arg_name_to_bind=None):
        return self._getValue(None, arg_name_to_bind)

    def setDefaultValue(self, value, arg_name_to_bind=None):
        pass

    @abstractmethod
    def hasAccessorValue(self):
        pass

    @abstractmethod
    def getAccessorValue(self):
        pass

    @abstractmethod
    def buildErrorMessage(self):
        pass
