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
from pyshell.utils.utils     import raiseIfInvalidKeyList

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
    
#XXX brainstorming XXX
    #event avec ou sans argument ? avec OK
    
    #comment sont identifier les events ? string OK

    #format de la commande ? or where to convert from string to object ? OK
        #TYPE 1: pure texte
            #--- les erreurs de commandes inconnues se produisent lors de l'execution de l'event
                #+++ mais possibilité de les corriger pour la prochaine execution de l'event si on load le module manquant
            #+++ possible de reconvertir en text immediatement
            
            
        #TYPE 2: convertie en objet
            #+++ les erreurs de commandes inconnues se produisent lors de l'ajout de la commande dans un event
                #--- si l'event n'est pas loadé ou que la ligne est retirée, cela peut modifier le comportement de l'event
            #--- pas moyen de reconvertir en texte ensuite, besoin de stocker la chaine d'origine
    
    #what about security access to the alias ? TODO
        #readonly ? removable ? transient ?
        
    #what about execution of an alias in a piping processes:  a | alias | b | c TODO
        #can not be splitted in pre/pro/post
            #why ? because there are maybe already piping in the process inside the alias
            
        #can be pre or pro or post
            #not pro, because in case of piping, alias will not be executed 
        
        #so pro or pre ?
            #by default pre
            #but could be interesting to act as post in certain cases


class Event(object):
    def __init__(self):
        self.stringCmdList = []  
        self.stopOnError                     = True
        self.argFromEventOnlyForFirstCommand = False
        self.useArgFromEvent                 = True
        self.executeOnPre                    = True
    
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
                        errorList.addException(ParameterLoadingException("(EventManager) load, ")) #TODO
                        continue
                    
                    #TODO a new command to process
                        #need to parse value to string token
                        
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
            pass #TODO raise

        event = self.events[eventName].clone()

        #start thread
        if onThread:
            t = threading.Thread(None, self._fireEvent, None, (event,))
            t.start()
        else:
            self._fireEvent(event)

    def _fireEvent(self, event):
        #TODO use stopOnError, argFromEventOnlyForFirstCommand, useArgFromEvent, ...
    
        for cmdsAndArgs in cmdsAndArgsList:
            cmdObjects, argList = cmdsAndArgs
        
            if eventArgList is not None:
                argList = argList[:]
                argList.append(eventArgList)
        
            self.executeCommand(cmdStringList)

    def executeCommand(self, cmdList, argList):
        pass #TODO copy (or move) from executer



        




