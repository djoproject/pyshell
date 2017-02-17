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

from pyshell.utils.exception import DefaultPyshellException
from pyshell.utils.exception import PARSE_WARNING
from pyshell.utils.exception import SYSTEM_WARNING


class LoadException(DefaultPyshellException):
    """
    This exception is used for any error that can happen during
    the load process.  It must be used only in this case.
    """
    def __init__(self, value):
        DefaultPyshellException.__init__(self, value, PARSE_WARNING)


class UnloadException(DefaultPyshellException):
    """
    This exception is used for any error that can happen during
    the unload process.  It must be used only in this case.
    """
    def __init__(self, value):
        DefaultPyshellException.__init__(self, value, SYSTEM_WARNING)
