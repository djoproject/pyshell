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

# TODO
#   use wraps https://docs.python.org/2/library/functools.html#functools.wraps

# use to mark a command that is allowed to return None


def allowToReturnNone(enable=True):
    def decorator(fun):
        fun.allowToReturnNone = enable
        return fun
    return decorator
