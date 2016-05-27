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


class AbstractLoader(object):
    def __init__(self, priority=100):
        self.last_exception = None
        self.priority = priority

    def load(self, parameter_manager, profile=None):
        pass  # TO OVERRIDE

    def unload(self, parameter_manager, profile=None):
        pass  # TO OVERRIDE

    def getPriority(self):
        return self.priority
        # CAN BE OVERRIDEN TOO
