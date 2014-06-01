#!/usr/bin/python
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

from pyshell.arg.argchecker import listArgChecker, ArgChecker

#TODO
	#save/load method

def loadParametersFromFile():
	pass #TODO

def saveParametersFromFile():
	pass #TODO

def getInitParameters():
	params = {}

	params["prompt"]     = EnvironmentParameter(value="pyshell:>", typ=stringArgChecker())
	params["vars"]       = GenericParameter(value={},transient=True)
	params["levelTries"] = GenericParameter(value=multiLevelTries(),transient=True)



	return params


class Parameter(object):
	def __init__(self, transient = False, parent = None):
		self.transient = transient
		self.parent    = parent

	def getValue(self):
		pass #TO OVERRIDE

	def setValue(self,value):
		pass #TO OVERRIDE


	def setTransient(self,state):
		self.transient = state

	def isTransient(self):
		return self.transient


	def isReadOnly(self):
		return False

	def isRemovable(self):
		return self.transient


	def getParent(self):
		return self.parent

	def setParent(self, parent):
		self.parent = parent

class GenericParameter(Parameter):
	def __init__(self, value, transient = False, parent = None):
		Parameter.__init__(transient, parent)
		self.value = value

	def getValue(self):
		return self.value

	def setValue(self,value):
		self.value = value

class EnvironmentParameter(Parameter):
	def __init__(self, value, typ, transient = False, readonly = False, removable = False, parent = None):
		Parameter.__init__(transient, parent)
		self.readonly  = readonly
		self.removable = removable

		#TODO typ must be argChecker

		self.typ = typ

		#TODO value must be checked

		self.value = value
		

	def getValue(self):
		return self.value

	def setValue(self,value):
		#TODO value must be checked

		self.value = value

	def isReadOnly(self):
		return self.readonly

	def isRemovable(self):
		return self.removable

	def setReadOnly(self, state):
		self.readonly = state

	def setRemovable(self, state):
		self.removable = state

class ContextParameter(EnvironmentParameter):
	def __init__(self, value, typ, transient = False, parent = None):

		if not isinstance(typ,listArgChecker):
			typ = listArgChecker(typ)

		EnvironmentParameter.__init__(self, value, typ, transient, parent)
		self.index = 0

	def setIndex(self, index):
		pass #TODO

	def getIndex(self):
		return self.index

	def getSelectedValue(self):
		return self.value[self.index]




