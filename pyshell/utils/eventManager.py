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
from pyshell.utils.exception import DefaultPyshellException, USER_ERROR, ListOfException, ParameterException, ParameterLoadingException
from pyshell.utils.utils     import raiseIfInvalidKeyList

try:
    pyrev = sys.version_info.major
except AttributeError:
    pyrev = sys.version_info[0]

if pyrev == 2:
    import ConfigParser 
else:
    import configparser as ConfigParser

#TODO TODO TODO TODO TODO
    #convert brainstorming into TODO

    #keep track of running event and be able to kill one or all of them
    
    #XXX XXX XXX a stored event is absolutly on the same form than an alias should be XXX XXX XXX
        #except that an alias has any string token list size as name
        #an fire alias occurs in a new thread, an execute alias occurs immediately in the same thread
        
    #find a new name, not really an alias, and not really an event
    
    #rename all variable like stringCmdList, it is difficult to understand what is what
    
#XXX XXX XXX XXX brainstorming XXX XXX XXX XXX

    #event avec ou sans argument ? avec XXX OK
    
    #comment sont identifier les events ? string XXX OK

    #format de la commande ? or where to convert from string to object ? XXX OK
        #TYPE 1: pure texte XXX SELECTED THIS ONE
            #--- les erreurs de commandes inconnues se produisent lors de l'execution de l'event
                #+++ mais possibilité de les corriger pour la prochaine execution de l'event si on load le module manquant et aussi avec le param stopOnError
            #+++ possible de reconvertir en text immediatement
            
            
        #TYPE 2: convertie en objet
            #+++ les erreurs de commandes inconnues se produisent lors de l'ajout de la commande dans un event
                #--- si l'event n'est pas loadé ou que la ligne est retirée, cela peut modifier le comportement de l'event
            #--- pas moyen de reconvertir en texte ensuite, besoin de stocker la chaine d'origine
            
    #what about the storage/parsing of piped command ? XXX OK
        #axioms:
            #1. store parsed full text but not converted to object
    
        #storage TYPE 1 : forbide piping
            #--- lose of huge power, not possible to do that
        
        #storage TYPE 2 : manage piping XXX SELECTED THIS ONE
            #probleme to solve
                #how to add piped command in the shell ? 
                    #use two command:
                        #one to add a new command to an event
                        #one to pipe a new command to an existing event
                        
                        #don't forget command to manage them (update, move, remove, ...)
                
                #how to store them in memory full text ? 
                    #how to store them on memory
                        #2 dimension :
                            #first level list: piped command
                            #second level: string token

                        #eg: aa bb cc | dd ee ff
                            #in storage: (("aa", "bb", "cc",), ("dd", "ee", "ff",))

                    #how to store them in file
                        #with pipe included: "aa bb cc | dd ee ff"

            #move parsing function from executer to here

    #should be possible to fire a command from shell XXX OK
        #so in another thread
        #even if there is piping
    
        #how to say to the system to start in another thread ?
            #should be possible to do it explictly or not
            #not possible to create a process to do it because we are already too far in the process execution

            #use both solution
        
            #SOLUTION 1 : use a special keyword to start the command SELECTED
                #E.G. "fire", but this keyword must be locked and not possible to add/remove in the tries from addon
                    #fire plop a bc | toto 1 2 3 | tutu $rt
             
            #SOLUTION 2 : act like in standard shell, use "&" character SELECTED
                #so if a command finish with at least one space then &, run it like an event in a new thread

            #... 

    #what about execution of an alias in a piping processes:  a | alias | b | c XXX OK
        #can not be splitted in pre/pro/post
            #why ? because there are maybe already piping in the process inside the alias
            
        #can be pre or pro or post
            #not pro, because in case of piping, alias will not be executed 
        
        #so pro or pre ?
            #by default pre
            #but could be interesting to act as post in certain cases
            
        #yeah but how to do that ?
            #Event object should inherite from singlecommand (or multicommand ?)
                #and override pre and post from command
                #have an access to the tries
                    #to be able to execute stored command

    #how to store event object in the software ? TODO
        #the current way is not efficient, need to be accessible from tries

        #what we need
            #the alias/event must be accessible from the tries
            #it must be possible to list alias/event
        
        #SOLUTION 1:
            #store the alias only in the tries
            #traversal the whole tries to retrieve the list of alias/event, bof bof
            #just need a tag or an attribute to know if it is a command or an alias
            
        #SOLUTION 2: for the moment, this is the best solution
            #store in the tries and in an independant structure with the list of alias
            #need to manage two data structure and maintain a coherence between them, bof bof
            
        # ...
    
    #what about security access to the alias ? TODO
        #readonly ? removable ? transient ? OK
            #do it like this, with these three booleans
        
        #lock on certain command in the alias ? TODO
            # E.G. can't remove cmd 2 but it is possible to remove cmd 5
            #is it really useful ?

class Event(object):
    def __init__(self, readonly = False, removable = True, transient = False):
        self.stringCmdList = []  
        self.stopOnError                     = True
        self.argFromEventOnlyForFirstCommand = False
        self.useArgFromEvent                 = True
        self.executeOnPre                    = True

        #TODO
    
    def setStopOnError(self, value):
        if type(value) != bool:
            raise ParameterException("(Event) setStopOnError, expected a boolean value as parameter, got '"+str(type(value))+"'")
    
        self.stopOnError = value
        
    def setArgFromEventOnlyForFirstCommand(self, value):
        if type(value) != bool:
            raise ParameterException("(Event) setStopOnError, expected a boolean value as parameter, got '"+str(type(value))+"'")
    
        self.argFromEventOnlyForFirstCommand = value
        
    def setUseArgFromEvent(self, value):
        if type(value) != bool:
            raise ParameterException("(Event) setStopOnError, expected a boolean value as parameter, got '"+str(type(value))+"'")
    
        self.useArgFromEvent = value
        
    def setExecuteOnPre (self, value):
        if type(value) != bool:
            raise ParameterException("(Event) setExecuteOnPre, expected a boolean value as parameter, got '"+str(type(value))+"'")
    
        self.executeOnPre = value
        
    def isStopOnError(self):
        return self.stopOnError
        
    def isArgFromEventOnlyForFirstCommand(self):
        return self.argFromEventOnlyForFirstCommand
        
    def isUseArgFromEvent(self):
        return self.useArgFromEvent
        
    def isExecuteOnPre(self):
        return self.executeOnPre
    
    def addCommand(self, commandStringList):
        raiseIfInvalidKeyList(commandStringList, ParameterException,"Event", "addCommand")    
        self.stringCmdList.append( commandStringList )
        
    def removeCommand(self, index):
        try:
            del self.stringCmdList[index]
        except IndexError:
            pass #do nothing
        
    def moveCommand(self,fromIndex, toIndex):
        try:
            self.stringCmdList[fromIndex]
        except IndexError:
            if len(self.stringCmdList) == 0:
                message = "command list is empty"
            elif len(self.stringCmdList) == 1:
                message = "only index 0 is available"
            else:
                message = "a value between 0 and "+str(len(self.stringCmdList)-1) + " was expected"
        
            raise ParameterException("(Event) moveCommand, invalid index 'from',"+message+" , got '"+str(fromIndex)+"'")
        
        #transforme to positive index if needed
        if fromIndex < 0:
            fromIndex = len(self.stringCmdList) + fromIndex
        
        try:
            self.stringCmdList[toIndex]
        except IndexError:
            if len(self.stringCmdList) == 0:
                message = "command list is empty"
            elif len(self.stringCmdList) == 1:
                message = "only index 0 is available"
            else:
                message = "a value between 0 and "+str(len(self.stringCmdList)-1) + " was expected"
        
            raise ParameterException("(Event) moveCommand, invalid index 'to',"+message+" , got '"+str(fromIndex)+"'")
            
        #transforme to positive index if needed
        if toIndex < 0:
            toIndex = len(self.stringCmdList) + toIndex
            
        if fromIndex == toIndex:
            return
        
        #manage the case when we try to insert after the existing index
        if fromIndex < toIndex:
            toIndex -= 1
            
        self.stringCmdList.insert(toIndex, self.stringCmdList.pop(fromIndex))
        
    def upCommand(self,index):
        self.moveCommand(index,index-1)
        
    def downCommand(self,index):
        self.moveCommand(index,index+1)
        
    def clone(self):
        e = Event()
    
        e.stringCmdList                   = self.stringCmdList[:]
        e.stopOnError                     = self.stopOnError
        e.argFromEventOnlyForFirstCommand = self.argFromEventOnlyForFirstCommand
        e.useArgFromEvent                 = self.useArgFromEvent
        e.executeOnPre                    = self.executeOnPre
        
        return e

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
        self.events = {} #TODO remove and store event/alias somewhere else
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
                #in case of existing event, manage security (need to be defined)
            
            event = Event()
            onError = False
        
            for option in config.options(section):
                value = config.get(section, option)
                if option in ["stopOnError","argFromEventOnlyForFirstCommand","useArgFromEvent", "executeOnPre"] :
                    validBool, boolValue = isBool(value)
                    if not validBool:
                        errorList.addException(ParameterLoadingException("(EventManager) load, a boolean value was expected for parameter '"+str(option)+"' of event '"+str(section)+"', got '"+str(value)+"'"))
                        onError = True
                        continue
                    
                    setattr(event,option,boolValue)
                    
                else:
                    validInt, intValue = isInt(option)
                    if not validInt:
                        errorList.addException(ParameterLoadingException("(EventManager) load, a unknown key has been found for event '"+str(section)+"': "+str(option)))
                        continue
                    
                    #TODO a new command to process
                        #need to parse value to string token
                        #need to know the format
                        
                    #event.stringCmdList.insert(intValue, )
            
            if not onError:
                self.events[section] = event
        
    def save(self):
        if self.filePath is None:
            return
        
        config = ConfigParser.RawConfigParser()
        
        for eventName, eventObject in self.events.items():
            config.add_section(eventName)
            
            #set event properties
            config.set(eventName, "stopOnError",                     eventObject.stopOnError)
            config.set(eventName, "argFromEventOnlyForFirstCommand", eventObject.argFromEventOnlyForFirstCommand)
            config.set(eventName, "useArgFromEvent",                 eventObject.useArgFromEvent)
            config.set(eventName, "executeOnPre",                    eventObject.executeOnPre)
            
            #write each command in order
            index = 0
            for cmd in eventObject.stringCmdList:
                config.set(eventName, str(index), " ".join(cmd))
                index += 1
            
        with open(self.filePath, 'wb') as configfile:
            config.write(configfile)
    
    def addCommand(self, eventName, cmdList):
        if eventName not in self.events:
            self.events[eventName] = Event()
            
        self.events[eventName].addCommand(cmdList)

    def executeEvent(self, eventName, argList = None):
        self.fireEvent(eventName, argList, False)

    def fireEvent(self, eventName, argList = None, onThread = True):
        if eventName not in self.events:
            raise DefaultPyshellException("(EventManager) fireEvent, unknown event '"+str(eventName)+"'",USER_ERROR)

        event = self.events[eventName].clone()

        #start thread
        if onThread:
            t = threading.Thread(None, self._fireEvent, None, (event,))
            t.start()
        else:
            self._fireEvent(event)

    def _fireEvent(self, event): 
        #TODO use arg executeOnPre
       
        first = True
        for cmdsAndArgs in event.stringCmdList:
            if event.useArgFromEvent:
                if first or not event.argFromEventOnlyForFirstCommand:
                    first = False
                    
                    #TODO append event args to command args
                        #need to know the format
        
        
            if eventArgList is not None:
                argList = argList[:]
                argList.append(eventArgList)
        
            if not self.executeCommand(cmdStringList) and event.stopOnError:
                break

    def executeCommand(self, cmdsAndArgs):
        pass #TODO copy (or move) from executer



        




