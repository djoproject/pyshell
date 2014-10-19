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

from pyshell.arg.decorator      import shellMethod
from pyshell.loader.command     import registerCommand, registerSetGlobalPrefix, registerStopHelpTraversalAt
from pyshell.arg.argchecker     import parameterChecker, filePathArgChecker
from pyshell.utils.constants    import ENVIRONMENT_NAME, DEFAULT_CONFIG_DIRECTORY
from pyshell.utils.eventManager import Event  
from pyshell.utils.executing    import preParseNotPipedCommand
from pyshell.utils.exception    import ParameterLoadingException
from pyshell.loader.parameter   import registerSetEnvironment
from pyshell.utils.parameter           import EnvironmentParameter
import sys, os

try:
    pyrev = sys.version_info.major
except AttributeError:
    pyrev = sys.version_info[0]

if pyrev == 2:
    import ConfigParser 
else:
    import configparser as ConfigParser

#XXX ALIAS DEFINITION
    #an alias has a string list as name
        #this string list is store in the command tries
        
    #an alias hold a list of command string and their argument (if any argument)
        #a command could be several piped command a| b| c| ...
    
    #argument of command must be checked at the adding in the alias
        #except for an alone command or the first command of a piped commands
            #if they are allowed to receive argument from alias
                #they can have uncomplete arg list
            #otherwise check every args of every command
                
    #if argument are given to alias which command will use them ? (SEE PRBLM 4)
        #three possibilities:
            #all
            #first (n first ?, list of id)
            #none of them

#TODO PRBLM 1: name and command are both unknows length string list
        #so it is difficult to known where finish the first one
        
            #Solution 1: wait for parameter implementation
                #not intuitive
            #Solution 2: use variable
                #not intuitive
            #Solution 3: use named alias without value at the beginning
                #then only use add to associate a command to an alias
                    #bof, need two step to create an alias :/
            #Solution 4: alias are a one token string
                #et on stocke ça dans un parameter avec un parent special "alias"
                #permettrait d'avoir les alias qui se sauvegarde tout seul
                
                #drawback
                    #alias a un seul token string
                    #categorie parente figée (???)

#TODO PRBLM 2: alias must be disabled if one of the included command has been unloaded
    #disappearing of one of the used command
        #we need to know if a command is linked to an alias
        
            #Solution 1: keep a map of the alias and check at the unload
                #the alias list ?
            #Solution 2: add an attribute to the multiCommand object
                #mark the command used in an alias ?
            #Solution 3: add an unload routine in corresponding unloader
                #need to identify it before to add the routine
                    #be carefull to limit the amount of process in unloader search 
                    #to only save a limited amount of computation for an occasional unload
                #if possible to identify unload with O(1), could be interesting 
            
#TODO PRBLM 3: how to store the alias ?
    #need an efficient and simple way to store them
        
        #Solution 1: keep a list of alias in the system
            #pair of (List<String>, AliasObject)
            #store a special object in the command tree, this object will retrieve its aliasObject from the list at execution
            
            #PRO:
                #easy to manage
                    #to unload a command, just check in every alias object if the command is used
                
            #CON:
                #need another additional structure to store the alias
            
        #Solution 2: no list in the system
            #no more structure
            #store a special cmd object
                #a kind of decorated function
                
            #PRO
                #no more structure
            
            #con
                #hard to list existing alias, only a prlbm for list...
                #could be interesting to reuse the help function and filter on these object
                    #if instance of AliasObject, then print
            
#TODO PRBLM 4: what about piping |
    #What happen if we add piping in alias list ?
        #just store them like that and check the args of the command if needed
            #if command not linked to the arg passing of the alias, check the args provided for the command
            #if not the first command of a piped command, check the args provided
        
    #how to manage argument passing from alias to subcmd ?
        #several politics possible
        #give them to
            #all
            #first
            #none of them
            #a list of index
            #...
            
        #how to efficiently manage these politics in the shell ?
            
## FUNCTION SECTION ##

@shellMethod(mltries = parameterChecker("levelTries", ENVIRONMENT_NAME),
             filePath = parameterChecker("alias_filepath", ENVIRONMENT_NAME))
def load(mltries, filePath):

    #load file
    filePath = filePath.getValue()
    
    if not os.path.exists(filePath):
        return

    config = ConfigParser.RawConfigParser()
    try:
        config.read(filePath)
    except Exception as ex:
        raise ParameterLoadingException("fail to read alias file : "+str(ex))
    
    #parse config
    errorList = ListOfException()
    for section in config.sections():
        parsedSection = preParseNotPipedCommand(section)

        if len(parsedSection) == 0:
            errorList.addException(ParameterLoadingException("an empty section or a section only composed with white space exists in alias file, this is not allowed"))
            continue

        mltriesSearchResult = mltries.advancedSearch( parsedSection, True ) 
        if mltriesSearchResult.isValueFound():
            alreadyExist = True
            alias = mltriesSearchResult.getValue()

            if not isinstance(alias, Event):
                errorList.addException(ParameterLoadingException("a section holds an already existing path: '"+" ".join(parsedSection)+"'"))
                continue

            if alias.isReadOnly():
                errorList.addException(ParameterLoadingException("an alias already exist on path '"+" ".join(parsedSection)+"' but it is readonly"))
                continue
        else:
            alreadyExist = False
            alias = Event()
        
        onError = False
        for option in config.options(section):
            value = config.get(section, option)
            if option in ["stopOnError","argFromEventOnlyForFirstCommand","useArgFromEvent", "executeOnPre"] :
                validBool, boolValue = isBool(value)
                if not validBool:
                    errorList.addException(ParameterLoadingException("a boolean value was expected for parameter '"+str(option)+"' of alias '"+str(section)+"', got '"+str(value)+"'"))
                    onError = True
                    continue
                
                setattr(alias,option,boolValue)
            
            #TODO there is other thing to parse

            else:
                #is it an index key ?
                validInt, intValue = isInt(option)
                if not validInt:
                    errorList.addException(ParameterLoadingException("a unknown key has been found for alias '"+str(section)+"': "+str(option)))
                    onError = True
                    continue
                
                #parse cmd
                preParsedCmd = preParseLine(value)
                if len(preParsedCmd) == 0:
                    continue

                #add cmd
                try:
                    event.setCommand(intValue, preParsedCmd[0])

                    for i in xrange(1, len(preParsedCmd)):
                        event.addPipeCommand(intValue, preParsedCmd[0])

                except Exception as ex:
                    errorList.addException(ex) #TODO find a way to include section name
                    onError = True 
        
        if not onError and not alreadyExist:
            mltries.insert(parsedSection, alias)

    #raise if error
    if errorList.isThrowable():
        raise errorList

@shellMethod(mltries = parameterChecker("levelTries", ENVIRONMENT_NAME),
             filePath = parameterChecker("alias_filepath", ENVIRONMENT_NAME))
def save(mltries, filePath): #TODO adapt
    config = ConfigParser.RawConfigParser()
    
    for eventName, eventObject in self.events.items(): #TODO
        config.add_section(eventName)
        
        #set event properties
        config.set(eventName, "stopOnError",                     eventObject.stopOnError)
        config.set(eventName, "argFromEventOnlyForFirstCommand", eventObject.argFromEventOnlyForFirstCommand)
        config.set(eventName, "useArgFromEvent",                 eventObject.useArgFromEvent)
        config.set(eventName, "executeOnPre",                    eventObject.executeOnPre)
        
        #TODO store new fields in event

        #write each command in order
        #TODO will be a map soon, need to adapt that
        index = 0
        for cmd in eventObject.stringCmdList:
            config.set(eventName, str(index), " ".join(cmd))
            index += 1
        
    with open(filePath, 'wb') as configfile:
        config.write(configfile)

def _listTraversal(path, node, state, level):
    if not node.isValueSet():
        return state

    if not isinstance(node.value, Event):
        return state

    state[tuple(path)] = node.value
    return state

@shellMethod(mltries = parameterChecker("levelTries", ENVIRONMENT_NAME))
def listAlias(mltries):
    mltries = mltries.getValue()
    result = mltries.genericBreadthFirstTraversal(_listTraversal, {}, True,True, (), True)

    for k,v in result:
        print k,v

def execute(name):
    pass #TODO

def fire(name):
    pass #TODO

def setProperty(idAlias, name, value):
    pass #TODO

def createAlias(name, command):
    pass #TODO

def removeAlias(idAlias):
    pass #TODO
    
def addMethodToAlias(idAlias, command):
    pass #TODO

def addPipedMethodToAlias(idAlias, command):
    pass #TODO

def moveCommandInAlias(idAlias, indexCommand, newIndex):
    pass #TODO

def moveCommandUpInAlias(idAlias, indexCommand):
    pass #TODO

def moveCommandDownInAlias(idAlias, indexCommand):
    pass #TODO

### REGISTER SECTION ###
    
registerSetGlobalPrefix( ("alias", ) )
registerStopHelpTraversalAt( () )
registerCommand( ("list", ), pro=listAlias )
registerCommand( ("load", ), pro=load )
registerCommand( ("save", ), pro=save )

#TODO register filename
registerSetEnvironment(envKey="alias_filepath", env=EnvironmentParameter(os.path.join(DEFAULT_CONFIG_DIRECTORY, ".pyshell_alias"),  typ=filePathArgChecker(readable=True, isFile=True), transient = False, readonly = False, removable = True), noErrorIfKeyExist = True, override = False)

    
    

