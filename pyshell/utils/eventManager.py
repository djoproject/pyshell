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

#TODO
    #keep track of running event and be able to kill one or all of them
    
    #XXX XXX XXX a stored event is absolutly on the same form than an alias should be XXX XXX XXX
        #except that an alias has any string token list size as name
        #an fire alias occurs in a new thread, an execute alias occurs immediately in the same thread
        
    #find a new name, not really an alias, and not really an event
    
    #need to store setting with the command list

#XXX brainstorming
    #event avec ou sans argument ? avec
    
    #comment sont identifier les events ? string

    #format de la commande ? or where to convert from string to object ?
        #TYPE 1: pure texte
            #--- les erreurs de commandes inconnues se produisent lors de l'execution de l'event
            #+++ possible de reconvertir en text immediatement
            
        #TYPE 2: convertie en objet
            #+++ les erreurs de commandes inconnues se produisent lors de l'ajout de la commande dans un event
            #--- pas moyen de reconvertir en texte ensuite, besoin de stocker la chaine d'origine
            
class Event(object):
    def __init__(self):
        self.cmdsAndArgsList = [] 
        self.stopOnError = True #TODO do accessor
        self.argFromEventOnlyForFirstCommand = False #TODO accessor + use it 
        self.useArgFromEvent = True #TODO accessor + use it
        
    def addCommand(self, commandList, argList):
        self.cmdList.append( (commandList, argList, ) )
        
    def removeCommand(self, index):
        try:
            del self.cmdList[index]
        except IndexError:
            pass #do nothing
        
    def moveCommand(self,fromIndex, toIndex):
        try:
            self.cmdList[fromIndex]
        except IndexError:
            pass #TODO raise
        
        #transforme to positive index if needed
        if fromIndex < 0:
            fromIndex = len(self.cmdList) + fromIndex
        
        try:
            self.cmdList[toIndex]
        except IndexError:
            pass #TODO raise
            
        #transforme to positive index if needed
        if toIndex < 0:
            toIndex = len(self.cmdList) + toIndex
            
        if fromIndex == toIndex:
            return
            
        if fromIndex < toIndex:
            toIndex -= 1
            
        self.cmdList.insert(toIndex, self.cmdList.pop(fromIndex))
        
    def upCommand(self,index):
        self.moveCommand(index,index-1)
        
    def downCommand(self,index):
        self.moveCommand(index,index+1)
        
    def clone(self):
        pass #TODO

class EventManager(object):
	def __init__(self, filePath = None):
		self.events = {}
		self.filePath = filePath

    def load(self):
        if self.filePath is None:
            return
        
        config = None
        if os.path.exists(self.filePath):
            config = ConfigParser.RawConfigParser()
            try:
                config.read(self.filePath)
            except Exception as ex:
                raise ParameterLoadingException("(EventManager) load, fail to read event file : "+str(ex))
        
        for section in config.sections():
            for option in config.options(section):
                #config.get(section, option)
                pass#TODO
        
    def save(self):
        if self.filePath is None:
            return
        
        config = ConfigParser.RawConfigParser()
        
        for eventName, eventObject in self.events.items():
            config.add_section(eventName)
            
            #for ...
                #TODO generate event on text format
            
        with open(self.filePath, 'wb') as configfile:
            config.write(configfile)
    
	def addCommand(self, eventName, cmdList, argList):
		#TODO check cmd

		if eventName not in self.events:
			self.events[eventName] = Event(cmdList, argList)

	def fireEvent(self, eventName, argList = None):
		if eventName not in self.events:
			pass #TODO raise

		event = self.events[eventName]:

        #TODO clone the event and give it to the thread
            #to avoid unexpected behaviour if the event is updated after its fire

		#start thread
		t = threading.Thread(None, self._fireEvent, None, (event.cmdsAndArgsList[:], argList,))
		t.start()

	def _fireEvent(self, cmdsAndArgsList, eventArgList=None):
		for cmdsAndArgs in cmdsAndArgsList:
		    cmdObjects, argList = cmdsAndArgs
		
		    if eventArgList is not None:
		        argList = argList[:]
		        argList.append(eventArgList)
		
			self.executeCommand(cmdObjects, eventArgList)

	def executeCommand(self, cmdList, argList):
		pass #TODO copy (or move) from executer


