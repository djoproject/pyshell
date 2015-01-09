#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject,net>

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

#ordered from worst (0) to insignifiant (inf)
ERROR         = 0
CORE_ERROR    = 1
SYSTEM_ERROR  = 2
LIBRARY_ERROR = 3
PARSE_ERROR   = 4
USER_ERROR    = 5

WARNING         = 10
CORE_WARNING    = 11
SYSTEM_WARNING  = 12
LIBRARY_WARNING = 13
PARSE_WARNING   = 14
USER_WARNING    = 15

NOTICE         = 20
CORE_NOTICE    = 21
SYSTEM_NOTICE  = 22
LIBRARY_NOTICE = 23
PARSE_NOTICE   = 24
USER_NOTICE    = 25

class PyshellException(Exception):
    def __init__(self,severity = ERROR):
        self.severity = severity
        
class DefaultPyshellException(PyshellException):
    def __init__(self, value = None,severity = ERROR):
        PyshellException.__init__(self,severity)
        self.value = value

    def __str__(self):
        return str(self.value)

class ParameterException(PyshellException):
    "Exception used when a error is triggered by the utilisation of parameter"
    def __init__(self,value):
        PyshellException.__init__(self, USER_ERROR)
        self.value = value

    def __str__(self):
        return str(self.value)
        
class ListOfException(DefaultPyshellException):
    def __init__(self, severity=ERROR):
        DefaultPyshellException.__init__(self,None, severity)
        self.exceptions = []

    def addException(self,exception):
        if isinstance(exception, ListOfException):
            self.exceptions.extend(exception.exceptions)
        elif isinstance(exception, Exception):
            self.exceptions.append(exception)
        else:
            raise Exception("(ListOfException) addException, can only store exception of type Exception or ListOfException, got '"+str(type(exception))+"'")
        
    def isThrowable(self):
        return len(self.exceptions) > 0

    def __str__(self):
        if len(self.exceptions) == 0:
            return "no error, this exception shouldn't be throwed"

        to_ret = ""
        for e in self.exceptions:
            to_ret += str(e)+"\n"
            
        return to_ret
        
class ParameterLoadingException(DefaultPyshellException):
    def __init__(self,value):
        DefaultPyshellException.__init__(self,None, PARSE_WARNING)
        self.value = value

    def __str__(self):
        return str(self.value)

class KeyStoreException(PyshellException):
    def __init__(self,value=None, severity=ERROR):
        PyshellException.__init__(self, severity)
        self.value = value

    def __str__(self):
        return str(self.value)

class KeyStoreLoadingException(DefaultPyshellException):
    def __init__(self,value):
        DefaultPyshellException.__init__(self,None, PARSE_WARNING)
        self.value = value

    def __str__(self):
        return str(self.value)
        
