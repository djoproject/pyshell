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

DEFAULT_EVENT_TYPE = ("ON_STARTUP", "AT_EXIT","ON_CONTEXT_CHANGE",)

class eventManager(object):
    def __init__(self):
        pass #TODO
        
    def createNewEventType(self, eventType):
        pass #TODO
        
    def getEventTypeList(self, eventType):
        pass #TODO
        
    def getActionListForEventType(self, eventType):
        pass #TODO
        
    def addActionForEventType(self, eventType, action):
        pass #TODO
        
    def removeActionOnEventType(self, eventType, actionIndex = 0):
        pass #TODO
        
    def fireActionOnEventType(self, eventType):
        pass #TODO
        
    
