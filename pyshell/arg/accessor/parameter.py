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

import collections

from abc import ABCMeta, abstractmethod

from pyshell.arg.accessor.container import ContainerAccessor
from pyshell.utils.string65 import isString


class AbstractParameter(ContainerAccessor):
    __metaclass__ = ABCMeta

    def __init__(self, container_attribute):
        ContainerAccessor.__init__(self)

        if container_attribute is None or not isString(container_attribute):
            excmsg = "container_attribute must be a valid string, got '%s'"
            excmsg %= str(type(container_attribute))
            self._raiseArgInitializationException(excmsg)

        self.container_attribute = container_attribute

    @abstractmethod
    def getManager(self, container):
        pass

    @abstractmethod
    def getKeyName(self):
        pass

    def hasAccessorValue(self):
        if not ContainerAccessor.hasAccessorValue(self):
            return False

        container = ContainerAccessor.getAccessorValue(self)
        manager = self.getManager(container)
        return manager.hasParameter(self.getKeyName())

    def getAccessorValue(self):
        container = ContainerAccessor.getAccessorValue(self)
        manager = self.getManager(container)
        return manager.getParameter(self.getKeyName())

    def buildErrorMessage(self):
        if not ContainerAccessor.hasAccessorValue(self):
            return ContainerAccessor.buildErrorMessage(self)

        return "the key '%s' is not available but needed" % self.getKeyName()


class AbstractParameterAccessor(AbstractParameter):
    __metaclass__ = ABCMeta

    def __init__(self, keyname, container_attribute):
        AbstractParameter.__init__(self, keyname)

        if (keyname is None or
           not isString(keyname) or
           not isinstance(keyname, collections.Hashable)):
            excmsg = "keyname must be hashable string, got '%s'"
            excmsg %= str(keyname)
            self._raiseArgInitializationException(excmsg)

        self.keyname = keyname

    def getKeyName(self):
        return self.keyname


# TODO (issue #127) should not inherit from ArgChecker
# TODO (issue #127) BUG seems to not appear in the help message, check why
# TODO (issue #127) this class (and its children) is between accessor and
#   checker...
# TODO (issue #127) what about the arguments of getParameter? (perfect_match,
#   local_param, explore_other_scope.
class AbstractParameterDynamicAccessor(AbstractParameter):
    def __init__(self, container_attribute):
        AbstractParameter.__init__(self, container_attribute)
        self.default_keyname = None
        self.getvalue_keyname = None

    def _checkKeyName(self, keyname):
        if (keyname is None or
           not isString(keyname) or
           not isinstance(keyname, collections.Hashable)):
            excmsg = "keyname must be hashable string, got '%s'"
            excmsg %= str(keyname)
            self._raiseArgException(excmsg)

    def getKeyName(self):
        if self.getvalue_keyname is None:
            return self.default_keyname
        return self.getvalue_keyname

    def getMaximumSize(self):
        return 1

    def getMinimumSize(self):
        return 1

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        # TODO not thread safe or thread sharing...
        # a first thread could set the keyname, then another thread, then
        # the first thread will call AbstractParameter.getValue
        self.getvalue_keyname = value
        try:
            return AbstractParameter.getValue(
                self, value, arg_number, arg_name_to_bind)
        finally:
            self.getvalue_keyname = None

    def isShowInUsage(self):
        return True

    def getUsage(self):
        return ""  # TODO (issue #127)

    def setDefaultValue(self, value, arg_name_to_bind=None):
        pass
