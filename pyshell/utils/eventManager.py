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

EVENT_ON_STARTUP      = "onstartup" #at application launch
EVENT_AT_EXIT         = "atexit" #at application exit
EVENT_AT_ADDON_LOAD   = "onaddonload" #at addon load (args=addon name)
EVENT_AT_ADDON_UNLOAD = "onaddonunload" #at addon unload (args=addon name)

import threading

#XXX brainstorming
    #event avec ou sans argument ? avec
    
    #comment sont identifier les events ? string

    #format de la commande ?

    

class EventManager(object):
	def __init__(self):
		self.events = {}

	def addCommand(self, eventName, cmd):
		#TODO check cmd

		if eventName not in self.events:
			self.events[eventName] = []

		#TODO add cmd

	def fireEvent(self, eventName, argList = None):
		if eventName not in self.events:
			pass #TODO raise

		cmdList = self.events[eventName]:

		#start thread
		t = threading.Thread(None, self._fireEvent, None, (cmdList[:], argList,))
		t.start()

	def _fireEvent(self,cmdList, argList=None):
		for cmd in cmdList:
			self.executeCommand(cmd)

	def executeCommand(self, cmd, eventArg=None):
		#TODO get lock list

		#TODO order lock

		#TODO lock

		#TODO execute

		#TODO unlock

		pass #TODO


