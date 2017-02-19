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

from pyshell.arg.checker.argchecker import ArgChecker


class AbstractAccessor(ArgChecker):
    __metaclass__ = ABCMeta

    def __init__(self):
        ArgChecker.__init__(self,
                            minimum_size=0,
                            maximum_size=0,
                            show_in_usage=False)

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        return self._getValue(arg_number, arg_name_to_bind)

    def usage(self):
        return ""

    def getDefaultValue(self, arg_name_to_bind=None):
        return self._getValue(None, arg_name_to_bind)

    def _getValue(self, arg_number=None, arg_name_to_bind=None):
        if not self.hasAccessorValue():
            self._raiseArgException(message=self.buildErrorMessage(),
                                    arg_number=None,
                                    arg_name_to_bind=arg_name_to_bind)

        return self.getAccessorValue()

    def hasDefaultValue(self, arg_name_to_bind=None):
        return self.hasAccessorValue()

    def setDefaultValue(self, value, arg_name_to_bind=None):
        pass

    def erraseDefaultValue(self):
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
