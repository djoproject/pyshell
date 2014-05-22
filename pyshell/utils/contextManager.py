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
        #if new key, checker must be different of None
    #check value

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
                #if checker 
            
                values = []
                self.context[key] = values, 0, checker
            else:
                values, index, checker = self.context[key]

            values.append(value)
        
    def addValues(self,key, newValues, checker = None):
        with self.lock:
            if key not in self.context:
                values = []
                self.context[key] = values, 0, checker
            else:
                values, index, checker = self.context[key]

            values.extend(newValues)

    def setValues(self, key, new_value, new_checker = None):
        with self.lock:
            if key not in self.context:
                values = []
                self.context[key] = new_value, 0, new_checker
            else:
                values, index, checker = self.context[key]
                self.context[key] = new_value, 0, checker

    def selectValue(self,key, value):
        if value not in self.context[key][0]:
            pass #TODO
            
        values, index, checker = self.context[key]
        self.context[key] = values, values.index(value), checker

    def selectValueIndex(self,key, new_index):
        try:
            self.context[key][0][index]
        except IndexError:
            pass #TODO
        except TypeError:
            pass #TODO
        
        values, index, checker = self.context[key]
        self.context[key] = values, new_index, checker

    def getKeys(self):
        return self.context.keys()

    def getValues(self,key):
        return self.context[key][0]

    def getSelectedValue(self, key):
        return self.context[key][0][self.context[key][1]]

    def getSelectedIndex(self, key):
        return self.context[key][1]

    def hasKey(self, key):
        return key in self.context

