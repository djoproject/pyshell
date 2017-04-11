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

from pyshell.register.profile.exception import RegisterException
from pyshell.utils.raises import raiseIfNotSubInstance


class DefaultProfile(object):
    def __init__(self,
                 root_profile,
                 load_priority=100.0,
                 unload_priority=100.0):
        raiseIfNotSubInstance(root_profile,
                              "root_profile",
                              DefaultProfile,
                              RegisterException,
                              "__init__",
                              self.__class__.__name__)

        self.load_priority = load_priority
        self.unload_priority = unload_priority
        self.last_exception = None
        self.root_profile = root_profile

    def getRootProfile(self):
        return self.root_profile

    def getLoadPriority(self):
        return self.load_priority

    def getUnloadPriority(self):
        return self.unload_priority

    def _checkInteger(self, value, method_name):
        try:
            return float(value)
        except TypeError:
            excmsg = ("("+self.__class__.__name__+") "+method_name+" an "
                      "integer value was expected for the argument value, "
                      "got '"+str(type(value))+"'")
            raise RegisterException(excmsg)

    def setLoadPriority(self, value):
        self.load_priority = self._checkInteger(value, "setLoadPriority")

    def setUnloadPriority(self, value):
        self.unload_priority = self._checkInteger(value, "setUnloadPriority")

    def setLastException(self, ex=None, stacktrace=None):
        """
            this method is used at loading/unloading to keep track of the
            last exception that occured in the loader execution.

            So it is not used to register anything, it is not relevant to
            check the type and to raise an exception if arguments are of the
            wrong type.
            An exception had already been raised and when we just want to
            keep track of it.
        """
        self.last_exception = ex
        if ex is not None:
            setattr(self.last_exception, 'stacktrace', stacktrace)

    def getLastException(self):
        return self.last_exception

    def getContentList(self):
        return ()
