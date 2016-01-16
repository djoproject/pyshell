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

class Valuable(object):
    def getValue(self):
        pass #TO OVERRIDE
        
class SelectableValuable(Valuable):
    def getSelectedValue(self):
        pass #TO OVERRIDE
        
class DefaultValuable(SelectableValuable):
    def __init__(self, value):
        self.value = value

    def getValue(self):
        return self.value

    def getSelectedValue(self):
        return self.value
        
class SimpleValuable(SelectableValuable):
    def __init__(self, value = None):
        self.value = value

    def getValue(self):
        return self.value
        
    def setValue(self, value):
        self.value = value
        return value

    def getSelectedValue(self):
        return self.value
