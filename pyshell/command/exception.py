#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2012  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.utils.exception import CORE_ERROR
from pyshell.utils.exception import CORE_WARNING
from pyshell.utils.exception import PyshellException


class ExecutionInitException(PyshellException):
    def __init__(self, value):
        PyshellException.__init__(self, CORE_ERROR)
        self.value = value

    def __str__(self):
        return str(self.value)


class ExecutionException(PyshellException):
    def __init__(self, value):
        PyshellException.__init__(self, CORE_ERROR)
        self.value = value

    def __str__(self):
        return str(self.value)


class CommandException(PyshellException):
    def __init__(self, value):
        PyshellException.__init__(self, CORE_ERROR)
        self.value = value

    def __str__(self):
        return str(self.value)


class EngineInterruptionException(PyshellException):
    def __init__(self, value, abnormal=False):
        if abnormal:
            PyshellException.__init__(self, CORE_ERROR)
        else:
            PyshellException.__init__(self, CORE_WARNING)

        self.abnormal = abnormal
        self.value = value

    def __str__(self):
        return str(self.value)
