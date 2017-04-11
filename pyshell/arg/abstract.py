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


class AbstractArg(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def setEngine(self, engine):
        pass

    @abstractmethod
    def getMaximumSize(self):
        pass

    @abstractmethod
    def getMinimumSize(self):
        pass

    @abstractmethod
    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        pass

    @abstractmethod
    def isShowInUsage(self):
        pass

    @abstractmethod
    def getUsage(self):
        pass

    @abstractmethod
    def hasDefaultValue(self, arg_name_to_bind=None):
        pass

    @abstractmethod
    def getDefaultValue(self, arg_name_to_bind=None):
        pass

    @abstractmethod
    def setDefaultValue(self, value, arg_name_to_bind=None):
        pass
