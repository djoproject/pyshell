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

from pyshell.arg.argchecker import listArgChecker, ArgChecker, IntegerArgChecker
import os

if sys.version_info.major == 2:
    import ConfigParser 
else:
    import configparser as ConfigParser
    
DEFAULT_PARAMETER_FILE = os.path.join(os.path.expanduser("~"), ".pyshellrc")
MAIN_CATEGORY          = "main"

#TODO
	#finish loader
	#executer command mapping
	#context/env manager ?
	    #to manage concurrency for example ?
	#test
	

#TODO prblm to solve
    #if the parent is a child key, and not a parent key
        #could be some conflict if two parent store the same child key
        
        #prblm in environment storage
        
        #prblm in loading
        
        #SOLUTION 1: not really a parent, some kind of family, keep the unicity of env key
            #bof bof
            
        #SOLUTION 2: prefix every variable with the name of the parent
            #store it in the file with the parent name
                #not obsious to manually update :/
            
            #easy to manage in dictionary
            
        #SOLUTION 3: store in several files, one per parent
            #solve the problem of file storage
            #but what about memory storage ?
                #one dico per parent
                    #so no need to store parent name in parameter object
            
            #PRBLM avec les parametres normaux...
                #voir plus bas

#SOLUTION
    #un seul fichier
    #context et EnvironmentParameter n'ont pas de parent
        #context.parent = "context"
        #EnvironmentParameter.parent = "environment"
    #GenericParameter a un parent
        #parent quelconque
            #excepté nom d'env ou nom de contexte
    #on garde un dictionnaire a deux niveaux
        #a[parent][key]
    #il n'y a plus de variable parent dans les class, ça se trouve dans les dictionnaires
    
    #!!! un parent ne peut pas avoir un nom de contexte/env et vice versa !!!
        #sinon impossible a gerer dans le fichier...
        #quoi que rien n'empeche de le gerer tant qu'on a pas une des cles de config de l'un de ces objets
            #oui mais le fichier va devenir crade...
    
    #TODO creer des methodes pour generer de nouveaux contexte, env, generic
        #faire une classe


def loadParametersFromFileV3(filepath, existingParams):
    #load params
    config = None
    if os.path.exists(filepath):
        config = ConfigParser.RawConfigParser()
        try:
            config.read(filepath)
        except Exception as ex:
            print("(ParameterManager) loadFile, fail to read parameter file : "+str(ex))
            return
    else:
        return saveParametersFromFileV3(filepath, existingParams)

    #read and parse
    for section in config.section():
        if config.has_option(section, "value"):
            contextDefined = False
            if config.has_option(section, "contextType"):
                try:
                    contextDefined = bool(config.get(section, "contextType"))
                except Exception:
                    contextDefined = False
                    
            if contextDefined:
                if "context" not in existingParams:
                    existingParams["context"] = {}
            
                #TODO manage existing
            
                pass #TODO ContextParameter
                
            else:
                if "environment" not in existingParams:
                    existingParams["environment"] = {}
            
                #TODO manage existing
            
                pass #TODO EnvironmentParameter
                
        else:
            if section in ("context", "environment", ):
                print("(ParameterManager) loadFile, parent section of name \"context\" or \"environment\" are not allowed")
                continue
        
            for option in config.options(section):
                if section not in existingParams:
                    existingParams[section] = {}
                
                if option in existingParams[section]:
                    if isinstance(existingParams[section][option], Parameter):
                        existingParams[section][option].setValue(config.get(section, option))
                        continue        
                        
                existingParams[section][option] = GenericParameter(value=config.get(section, option))
        
    return existingParams
    
def saveParametersFromFileV3(filepath, params):

    #manage standard parameter
    config = ConfigParser.RawConfigParser()
    for parent, childs in params.items():   
        if parent in ("context", "environment", ):
            continue
        
        if parent == None:
            parent = MAIN_CATEGORY
        
        for childName, childValue in childs:
            if isinstance(childValue, Parameter):
                if childValue.isTransient():
                    continue
            
                value = str(childValue.getValue())
            else:
                value = str(childValue)
        
            config.set(parent, childName, value)
    
    #manage context and environment
    for s in ("context", "environment", ):
        if s in params:
            for contextName, contextValue in params[s].items():
                if contextValue.isTransient():
                    continue
            
                for name, value in contextValue.getParameterSerializableField():
                    config.set(contextName, name, value)
    
    

"""def loadParametersFromDirectory(directoryPath, existingParams):
    for f in os.listdir(directoryPath):
        if not f.endswith(".conf"):
            continue
        
        parentName = f[0:-4]
        
        if len(parentName) <= 0:
            continue
        
        completeFilePath = directoryPath + f
        config = ConfigParser.RawConfigParser()
        try:
            config.read(filepath)
        except Exception as ex:
            print("(ParameterManager) loadFile, fail to read configuration file <"+parentName+"> : "+str(ex))
            continue
        
        if parentName in existingParams:
            dico = existingParams[parentName]
        else:
            dico = {}
        
        for section in config.section():
            if config.has_option(section, "value"):
            
                #type is difined ?
                typeDefined = False
                if config.has_option(section, "type"):
                    typeDefined = True
                
                #context is difined ?
                contextDefined = False
                if config.has_option(section, "contextType"):
                    try:
                        contextDefined = bool(config.get(section, "contextType"))
                    except Exception:
                        contextDefined = False
                        
                if typeDefined:
                    if contextDefined:
                        pass #TODO ContextParameter(value, typ, transient = False, transientIndex = False, defaultIndex = 0, parent = None)
                    else:
                        pass #TODO EnvironmentParameter(value, typ, transient = False, readonly = False, removable = False, parent = None)
                else:
                    pass #TODO GenericParameter(value, transient = False, readonly = False, removable = False, parent = None)
                
                
            else:
                continue #invalid parameter TODO what to do with this ?
                            #it will disapper on the next save...
                        #create a new level of parameter?, a dictionary of key/value
                        #not really usefull :/
        
        if len(dico) > 0:
            existingParams[parentName] = dico
        

def loadParametersFromFile(filepath, existingParams):
    #load params
    config = None
    if os.path.exists(filepath):
        config = ConfigParser.RawConfigParser()
        try:
            config.read(filepath)
        except Exception as ex:
            print("(ParameterManager) loadFile, fail to read parameter file : "+str(ex))
            return
    else:
        saveParametersFromFile(filepath, existingParams)
        self.saveFile()
        return

    #read and parse
    for section in config.section():
        if config.has_option(section, "value"):
            pass #TODO ContextParameter or EnvironmentParameter
        else:
            for option in config.options(section):
                pass #TODO GenericParameter
        
    return existingParams


def saveParametersFromFile(filepath, params):
    config = ConfigParser.RawConfigParser()

    #build config
	for k,v in params.items():
	    #not parameter type (user mistake)
	    if isinstance(v, Parameter):
	        config.set(MAIN_CATEGORY, k, str(v))
	        continue
	
	    #transient type, no need to store them
	    if v.isTransient():
	        continue
        
        
        subParams = v.getParameterSerializableField()
        
        #with type, advanced param structure
        if "type" in subParams:
            for subk,subv in subParams.items():
                config.set(k, subk, str(subv))
        
        #no type, its just a key/value string pair
        else:
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
        print("(ParameterManager) saveParametersFromFile, fail to save parameter file : "+str(ex))"""

def getInitParameters():
	params = {}

	params["prompt"]     = EnvironmentParameter(value="pyshell:>", typ=stringArgChecker())
	params["vars"]       = GenericParameter(value={},transient=True,readonly=True, removable=False)
	params["levelTries"] = GenericParameter(value=multiLevelTries(),transient=True,readonly=True, removable=False)
	params["debug"]      = ContextParameter(value=(1,2,3,4,5,), typ=IntegerArgChecker(), transient = False, transientIndex = False, defaultIndex = 0)

	return params


class Parameter(object): #abstract
	def __init__(self, transient = False):
		self.transient = transient

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
		
	def getParameterSerializableField(self):
	    return {}

class EnvironmentParameter(Parameter):
	def __init__(self, value, typ, transient = False, readonly = False, removable = False):
		Parameter.__init__(transient)
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

	def getParameterSerializableField(self):
	    toret = Parameter.getParameterSerializableField(self)
	    toret["value"]     = str(self.value)
	    toret["type"]      = str(self.typ)
	    toret["readonly"]  = str(self.readonly)
	    toret["removable"] = str(self.removable)
	    
	    if isinstance(self.typ, listArgChecker):
	        toret["listType"] = str(True)
        else:
            toret["listType"] = str(False)

	    return toret


class GenericParameter(EnvironmentParameter):
	def __init__(self, value, transient = False, readonly = False, removable = True):
		EnvironmentParameter.__init__(self, value, ArgChecker(), transient, readonly, removable)
		self.setValue(value)
		
	def getParameterSerializableField(self):
	    toret = EnvironmentParameter.getParameterSerializableField(self)
	    
	    if "type" in toret:
	        del toret["type"]

	    return toret

class ContextParameter(EnvironmentParameter):
	def __init__(self, value, typ, transient = False, transientIndex = False, defaultIndex = 0):

		if not isinstance(typ,listArgChecker):
			typ = listArgChecker(typ)

		EnvironmentParameter.__init__(self, value, typ, transient)
		self.index = defaultIndex
		self.defaultIndex = defaultIndex
		self.transientIndex = transientIndex

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
		
	def setTransientIndex(self,transientIndex):
	    self.transientIndex = transientIndex
	    
    def getTransientIndex(self):
        return self.transientIndex
        
    def setDefaultIndex(self,defaultIndex):
        try:
            self.value[defaultIndex]
        except IndexError:
            raise Exception("(ContextParameter) setDefaultIndex, invalid index value, a value between 0 and "+str(len(self.value))+"was expected, got "+str(defaultIndex))
        except TypeError:
            raise Exception("(ContextParameter) setDefaultIndex, invalid index value, a value between 0 and "+str(len(self.value))+"was expected, got "+str(defaultIndex))
            
        self.defaultIndex = defaultIndex
        
    def getDefaultIndex(self):
        return self.defaultIndex

	def getParameterSerializableField(self):
	    toret = EnvironmentParameter.getParameterSerializableField(self)
	    
	    if not self.transientIndex:
	        toret["index"] = str(self.index)
	        
        toret["defaultIndex"] = str(self.defaultIndex)
        toret["contextType"]  = str(True)
        toret["listType"]     = str(True)

	    return toret
	    
    def reset(self):
        self.index = self.defaultIndex


