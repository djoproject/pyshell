#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

#Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pyshell.utils.exception import DefaultPyshellException, USER_ERROR, PARSE_WARNING

class RegisterException(DefaultPyshellException):
    def __init__(self,value):
        DefaultPyshellException.__init__(self, value, USER_ERROR)

class LoadException(DefaultPyshellException):
    def __init__(self,value):
        DefaultPyshellException.__init__(self,value, PARSE_WARNING)
