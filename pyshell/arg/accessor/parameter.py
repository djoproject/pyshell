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

from pyshell.arg.accessor.container import ContainerAccessor
from pyshell.arg.checker.argchecker import ArgChecker
from pyshell.utils.string65 import isString


# TODO make it abstract
class AbstractParameterAccessor(ContainerAccessor):
    def __init__(self, keyname, container_attribute):
        ContainerAccessor.__init__(self)

        if (keyname is None or
           not isString(keyname) or
           not isinstance(keyname, collections.Hashable)):
            excmsg = "keyname must be hashable string, got '%s'"
            excmsg %= str(keyname)
            self._raiseArgInitializationException(excmsg)

        self.keyname = keyname

        if container_attribute is None or not isString(container_attribute):
            excmsg = "container_attribute must be a valid string, got '%s'"
            excmsg %= str(type(container_attribute))
            self._raiseArgInitializationException(excmsg)

        self.container_attribute = container_attribute

    def getManager(self, container):
        pass  # TODO make it abstract

    def hasAccessorValue(self):
        if not ContainerAccessor.hasAccessorValue(self):
            return False

        container = ContainerAccessor.getAccessorValue(self)
        """if not hasattr(container, self.container_attribute):
            return False

        manager = getattr(container, self.container_attribute)"""
        manager = self.getManager(container)

        return manager.hasParameter(self.keyname)

    def getAccessorValue(self):
        container = ContainerAccessor.getAccessorValue(self)
        # manager = getattr(container, self.container_attribute)
        manager = self.getManager(container)
        return manager.getParameter(self.keyname)

    def buildErrorMessage(self):
        if not ContainerAccessor.hasAccessorValue(self):
            return ContainerAccessor.buildErrorMessage(self)

        container = ContainerAccessor.getAccessorValue(self)
        if not hasattr(container, self.container_attribute):
            excmsg = "environment container does not have the attribute '%s'"
            excmsg %= str(self.container_attribute)
            return excmsg

        return "the key '%s' is not available but needed" % self.keyname


class AbstractParameterDynamicAccessor(ArgChecker):
    def __init__(self, container_attribute):
        ArgChecker.__init__(self, 1, 1, False)

        if container_attribute is None or not isString(container_attribute):
            excmsg = "container_attribute must be a valid string, got '%s'"
            excmsg %= str(type(container_attribute))
            self._raiseArgInitializationException(excmsg)

        self.container_attribute = container_attribute

    def getManager(self, container):
        pass  # TODO make it abstract

    def _getManager(self, arg_number=None, arg_name_to_bind=None):
        if not hasattr(self, "engine") or self.engine is None:
            excmsg = ("can not get container, no engine linked to this "
                      "argument instance")
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        if not hasattr(self.engine, "getEnv"):
            excmsg = ("can not get container, linked engine does not have a "
                      "method to get the environment")
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        container = self.engine.getEnv()
        if container is None:
            excmsg = ("can not get container, no container linked to the "
                      "engine")
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        return self.getManager(container)

        """if not hasattr(container, self.container_attribute):
            excmsg = "environment container does not have the attribute '%s'"
            excmsg %= str(self.container_attribute)
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        return getattr(container, self.container_attribute)"""

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        if not isinstance(value, collections.Hashable):
            excmsg = "keyname must be hashable, got '%s'"
            excmsg %= str(value)
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        manager = self._getManager(arg_number, arg_name_to_bind)

        if not manager.hasParameter(value):
            excmsg = "the key '%s' is not available but needed" % str(value)
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        return manager.getParameter(value)

    def hasDefaultValue(self, arg_name_to_bind=None):
        return False

    def setDefaultValue(self, value, arg_name_to_bind=None):
        pass

    def erraseDefaultValue(self):
        pass
