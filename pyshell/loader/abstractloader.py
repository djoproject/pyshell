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

from abc import ABCMeta, abstractmethod


class AbstractLoader(object):
    __metaclass__ = ABCMeta

    def __init__(self, parent=None, load_priority=100.0, unload_priority=100.0):
        self.parent = parent
        self.load_priority = load_priority
        self.unload_priority = unload_priority
        self.last_exception = None

    @abstractmethod
    def load(self, parameter_container=None, profile=None):
        pass

    @abstractmethod
    def unload(self, parameter_container=None, profile=None):
        pass

    def getLoadPriority(self):
        return self.load_priority

    def getUnloadPriority(self):
        return self.unload_priority

    def saveCommands(self, section_name, command_list, addons_set=None):
        if self.parent is not None:
            self.parent.saveCommands(section_name, command_list, addons_set)
