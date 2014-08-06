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

class ParameterException(Exception):
    def __init__(self,value):
        self.value = value

    def __str__(self):
        return str(self.value)
        
class AbstractListableException(Exception):
    def __init__(self,value):
        self.value = value

    def __str__(self):
        return str(self.value)

class ListOfException(AbstractListableException):
    def __init__(self):
        self.exceptions = []

    def addException(self,exception):
        if isinstance(exception, ListOfException):
            self.exceptions.extend(exception)
        elif isinstance(exception, AbstractListableException):
            self.exceptions.append(exception)
        else:
            raise Exception("(ListOfException) addException, can only store exception of type AbstractListableException or ListOfException, got <"+str(type(exception))+">")
        
    def isThrowable(self):
        return len(self.exceptions) > 0

    def __str__(self):
        if len(self.exceptions) == 0:
            return "no error, this exception shouldn't be throwed"

        to_ret = ""
        for e in self.exceptions:
            to_ret += str(e)+"\n"
            
        return to_ret
        
class ParameterLoadingException(AbstractListableException):
    def __init__(self,value):
        self.value = value

    def __str__(self):
        return str(self.value)
        
        
