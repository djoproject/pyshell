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

from threading import Lock

#TODO
    #store an argchecker with the value

class contextManager(object):
    def __init__(self):
        self.lock = Lock()
        self.context = {}
                
    def removeContextKey(self,key):
        if key in self.context:
            with self.lock:
                if key in self.context:
                    del self.context[key]
        
    def addValue(self,key, value, checker = None):
        with self.lock:
            if key not in self.context:
                values = []
                self.context[key] = values
            else:
                values = self.context[key]

            values.append(value)
        
    def addValues(self,key, values, checker = None):
        with self.lock:
            if key not in self.context:
                values = []
                self.context[key] = values
            else:
                values = self.context[key]

            values.extend(value)

    def selectValue(self,key, value):
        pass #TODO

    def getKeys(self):
        pass #TODO

    def getValues(self,key):
        pass #TODO

    def getSelectedValue(self, key):
        pass #TODO

    def hasKey(self, key):
        return key in self.context
