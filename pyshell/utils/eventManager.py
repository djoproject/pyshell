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

import threading, sys
from pyshell.utils.exception import ListOfException
from pyshell.utils.exception import ParameterException, ParameterLoadingException

try:
    pyrev = sys.version_info.major
except AttributeError:
    pyrev = sys.version_info[0]

if pyrev == 2:
    import ConfigParser 
else:
    import configparser as ConfigParser

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
                #+++ mais possibilité de les corriger pour la prochaine execution de l'event si on load le module manquant
            #+++ possible de reconvertir en text immediatement
            
            
        #TYPE 2: convertie en objet
            #+++ les erreurs de commandes inconnues se produisent lors de l'ajout de la commande dans un event
                #--- si l'event n'est pas loadé ou que la ligne est retirée, cela peut modifier le comportement de l'event
            #--- pas moyen de reconvertir en texte ensuite, besoin de stocker la chaine d'origine
    
    #what about security access to the alias ?
        #readonly ? removable ?
    
class Event(object):
    def __init__(self):
        self.stringCmdList = [] 
        self.stopOnError = True #TODO do accessor
        self.argFromEventOnlyForFirstCommand = False #TODO accessor + use it 
        self.useArgFromEvent = True #TODO accessor + use it
    
    def addCommand(self, commandList, argList):
        self.stringCmdList.append( (commandList, argList, ) )
        
    def removeCommand(self, index):
        try:
            del self.stringCmdList[index]
        except IndexError:
            pass #do nothing
        
    def moveCommand(self,fromIndex, toIndex):
        try:
            self.stringCmdList[fromIndex]
        except IndexError:
            pass #TODO raise
        
        #transforme to positive index if needed
        if fromIndex < 0:
            fromIndex = len(self.stringCmdList) + fromIndex
        
        try:
            self.stringCmdList[toIndex]
        except IndexError:
            pass #TODO raise
            
        #transforme to positive index if needed
        if toIndex < 0:
            toIndex = len(self.stringCmdList) + toIndex
            
        if fromIndex == toIndex:
            return
            
        if fromIndex < toIndex:
            toIndex -= 1
            
        self.stringCmdList.insert(toIndex, self.stringCmdList.pop(fromIndex))
        
    def upCommand(self,index):
        self.moveCommand(index,index-1)
        
    def downCommand(self,index):
        self.moveCommand(index,index+1)
        
    def clone(self):
        pass #TODO

def isInt(value):
    try:
        i = int(value) 
        return True, i 
    except ValueError:
        pass
    
    return False, None
    
def isBool(value):
    if type(value) != str and type(value) != unicode:
        return False, None
        
    if value.lower() == "true":
        return True,True
        
    if value.lower() == "false":
        return True,False
        
    return False,None

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
        
        errorList = ListOfException()
        for section in config.sections():
            #TODO get or create the event
            event = Event()
        
            for option in config.options(section):
                value = config.get(section, option)
                if option in ["stopOnError","argFromEventOnlyForFirstCommand","useArgFromEvent"] :
                    validBool, boolValue = isBool(value)
                    if not validBool:
                        errorList.addException(ParameterLoadingException("") #TODO set the error message
                        continue
                    
                    setattr(event,option,boolValue)
                    
                else:
                    validInt, intValue = isInt(option)
                    if not validInt:
                        #TODO notify the error
                    
                        continue
                    
                    #TODO a new command to process
                        #need to parse value to string token
                        
                    #event.stringCmdList.insert(intValue, )
                    
        
    def save(self):
        if self.filePath is None:
            return
        
        config = ConfigParser.RawConfigParser()
        
        for eventName, eventObject in self.events.items():
            config.add_section(eventName)
            
            #TODO set event properties
            #config.set(eventName, childName, value)
            
            #TODO write each command in order
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

        event = self.events[eventName]

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

if __name__ == "__main__":
    print "plop"
    config = ConfigParser.RawConfigParser()
    config.read("/home/djo/development/inputTest.conf")
    
    for section in config.sections():
        print section
        for option in config.options(section):
            print option
            print config.get(section, option)


        




