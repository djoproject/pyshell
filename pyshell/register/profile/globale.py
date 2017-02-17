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

from pyshell.register.exception import LoaderException
from pyshell.register.loader.abstractloader import AbstractLoader
from pyshell.register.result.abstractresult import AbstractResult
from pyshell.utils.raises import raiseIfNotInstance
from pyshell.utils.raises import raiseIfNotSubclass


class GlobalProfile(object):

    def __init__(self, name, addon_information):
        self._name = name
        self._informations = addon_information
        self._result = {}

    def getName(self):
        return self._name

    def getAddonInformations(self):
        return self._informations

    def postResult(self, loader_class_def, result_instance):
        raiseIfNotSubclass(loader_class_def,
                           "loader_class_def",
                           AbstractLoader,
                           LoaderException,
                           "postResult",
                           self.__class__.__name__)

        raiseIfNotInstance(result_instance,
                           "result_instance",
                           AbstractResult,
                           LoaderException,
                           "postResult",
                           self.__class__.__name__)

        class_key = result_instance.__class__

        if (class_key in self._result and
                loader_class_def in self._result[class_key]):
            excmsg = ("(" + self.__class__.__name__ + ") postResult, a "
                      "result of type '" + str(type(result_instance)) + "'"
                      " already exists for the key '" +
                      str(type(loader_class_def)) + "'")
            raise LoaderException(excmsg)

        if class_key not in self._result:
            self._result[class_key] = {}

        self._result[class_key][loader_class_def] = result_instance

    def getResult(self, result_class_def):
        return self._result.get(result_class_def, {})

    def flushResult(self):
        self._result.clear()
