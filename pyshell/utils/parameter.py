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

#TODO prblm
    #1) prblm with the new parameter created
        #for example, create a context parameter non transient, its type will not stored
            #so after a reboot of the application, it will be a GenericParameter in place of a ContextParameter

    #2) quid, store everything in the same directory, or keep a single dictionary for env, context and generic
       
### XXX brainstoming XXX ###
    #SOLUTION 1 to prblm 1
        #parent is the name of the field
            #sub element: type, value, acces boolean, ...
            
        #if a parent has at least the subelement "value", parse it
        
        #otherelse, how to manage it ?
            #load them like basic GenericParameter
            #imply to store them in the same way
            
        #so two store system in the same file

from pyshell.arg.argchecker import listArgChecker, ArgChecker

if sys.version_info.major == 2:
    import ConfigParser 
else:
    import configparser as ConfigParser
    
DEFAULT_PARAMETER_FILE = os.path.join(os.path.expanduser("~"), ".pyshellrc")
MAIN_CATEGORY          = "main"

#TODO
	#save/load method

def loadParametersFromFile(filepath, existingParams):
    #TODO load params

    #TODO returns params

	pass #TODO

def saveParametersFromFile(filepath, params):
    config = ConfigParser.RawConfigParser()

    #build config
	for k,v in params.items():
	    if v.isTransient():
	        continue
	        
        if v.getParent() == None:
            parent = MAIN_CATEGORY
        else:
            parent = v.getParent()
            
        config.set(parent, k, str(v.getValue()))
	
	#save the config
	try:
        with open(filepath, 'wb') as configfile:
            config.write(configfile)
    except Exception as ex:
        print("(ParameterManager) saveParametersFromFile, fail to save parameter file : "+str(ex))

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

class GenericParameter(EnvironmentParameter):
	def __init__(self, value, transient = False, parent = None):
		EnvironmentParameter.__init__(self, value, ArgChecker(), transient, False,True , parent)
		self.value = value

class EnvironmentParameter(Parameter):
	def __init__(self, value, typ, transient = False, readonly = False, removable = False, parent = None):
		Parameter.__init__(transient, parent)
		self.readonly  = readonly
		self.removable = removable

		#typ must be argChecker
		if not isinstance(typ,ArgChecker):
		    raise Exception("(EnvironmentParameter) __init__, invalid type instance, must be an ArgChecker instance")

		self.typ = typ
        self.setValue(value)

	def getValue(self):
		return self.value

	def setValue(self,value):
		self.value = self.typ.getValue(value)

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
		self.index = 0 #TODO transient index or not ?

	def setIndex(self, index):
		try:
            self.value[index]
        except IndexError:
            raise Exception("(ContextParameter) setIndex, invalid index value, a value between 0 and "+str(len(self.value))+"was expected, got "+str(index))
        except TypeError:
            raise Exception("(ContextParameter) setIndex, invalid index value, a value between 0 and "+str(len(self.value))+"was expected, got "+str(index))
            
        self.index = index

	def getIndex(self):
		return self.index

	def getSelectedValue(self):
		return self.value[self.index]




