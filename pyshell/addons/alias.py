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
from pyshell.utils.aliasManager import Alias  
from pyshell.utils.executing    import preParseNotPipedCommand, preParseLine
from pyshell.utils.exception    import ParameterLoadingException, ListOfException
from pyshell.loader.parameter   import registerSetEnvironment
from pyshell.utils.parameter    import EnvironmentParameter
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

def isInt(value):
    try:
        return True, int(value) 
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

@shellMethod(mltries = parameterChecker("levelTries", ENVIRONMENT_NAME),
             filePath = parameterChecker("alias_filepath", ENVIRONMENT_NAME))
def load(mltries, filePath):

    #load file
    filePath = filePath.getValue()
    mltries = mltries.getValue()
    
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

            if not isinstance(alias, Alias):
                errorList.addException(ParameterLoadingException("a section holds an already existing path: '"+" ".join(parsedSection)+"'"))
                continue

            if alias.isReadOnly():
                errorList.addException(ParameterLoadingException("an alias already exist on path '"+" ".join(parsedSection)+"' but it is readonly"))
                continue
        else:
            alreadyExist = False
            alias = Alias(" ".join(parsedSection))
        
        onError  = False
        lockedTo = -1
        for option in config.options(section):
            value = config.get(section, option)
            methDeco = {"executeonpre":alias.setExecuteOnPre,
                        "removable":alias.setRemovable,
                        "readonly":alias.setReadOnly}
                        
            if option in methDeco:
                validBool, boolValue = isBool(value)
                if not validBool:
                    errorList.addException(ParameterLoadingException("a boolean value was expected for parameter '"+str(option)+"' of alias '"+str(section)+"', got '"+str(value)+"'"))
                    onError = True
                    continue
                
                methDeco[option](boolValue)
                #setattr(alias,option,boolValue)
            elif option == "lockedto":
                validInt, intValue = isInt(value)

                if not validInt:
                    errorList.addException(ParameterLoadingException("an integer value was expected for parameter 'lockedTo' of alias '"+str(section)+"', got '"+str(value)+"'"))
                    onError = True
                    continue
                lockedTo = intValue
            elif option == "errorgranularity":
                validInt, intValue = isInt(value)

                if not validInt:
                    alias.setErrorGranularity(None)
                else:
                    try:
                        alias.setErrorGranularity(intValue)
                    except Exception as ex:
                        errorList.addException(ex)
                        onError = True
            else:
                #is it an index key ?
                validInt, intValue = isInt(option)
                if not validInt:
                    errorList.addException(ParameterLoadingException("a unknown key has been found for alias '"+str(section)+"': "+str(option)))
                    onError = True
                    continue
                
                #parse cmd
                #TODO some of the error are just warning and shouldn't disable the insertion
                preParsedCmd = preParseLine(value)
                if len(preParsedCmd) == 0:
                    continue

                #add cmd
                try:
                    realid = alias.setCommand(intValue, preParsedCmd[0])
                    for i in xrange(1, len(preParsedCmd)):
                        alias.addPipeCommand(realid, preParsedCmd[i])
                except Exception as ex:
                    errorList.addException(ex) #TODO find a way to include section name
                    onError = True 
        
        try:
            alias.setLockedTo(lockedTo)
        except Exception as ex:
            errorList.addException(ex) #TODO find a way to include section name
            onError = True 
        
        if not onError and not alreadyExist:
            mltries.insert(parsedSection, alias)

    #raise if error
    if errorList.isThrowable():
        raise errorList

def _saveTraversal(path, node, config, level):
    if not node.isValueSet():
        return config

    if not isinstance(node.value, Alias):
        return config

    aliasObject = node.value
    
    if aliasObject.isTransient():
        return config
        
    aliasName = " ".join(path)
    
    config.add_section(aliasName)
    config.set(aliasName, "errorGranularity",                str(aliasObject.errorGranularity))
    config.set(aliasName, "executeOnPre",                    str(aliasObject.executeOnPre))
    config.set(aliasName, "lockedTo",                        str(aliasObject.lockedTo))
    config.set(aliasName, "readonly",                        str(aliasObject.readonly))
    config.set(aliasName, "removable",                       str(aliasObject.removable))
    
    index = 0
    for cmd in aliasObject.stringCmdList:
        tmp = []
        for subcmd in cmd:
            tmp.append(" ".join(subcmd))
        
        config.set(aliasName, str(index), " | ".join(tmp))
        index += 1

    return config

@shellMethod(mltries = parameterChecker("levelTries", ENVIRONMENT_NAME),
             filePath = parameterChecker("alias_filepath", ENVIRONMENT_NAME))
def save(mltries, filePath):
    config = ConfigParser.RawConfigParser()
    
    mltries = mltries.getValue()
    mltries.genericBreadthFirstTraversal(_saveTraversal, config, True,True, (), True)
    filePath = filePath.getValue()
    with open(filePath, 'wb') as configfile:
        config.write(configfile)

def _listTraversal(path, node, state, level):
    if not node.isValueSet():
        return state

    if not isinstance(node.value, Alias):
        return state

    state[tuple(path)] = node.value
    return state

@shellMethod(mltries = parameterChecker("levelTries", ENVIRONMENT_NAME))
def listAlias(mltries):
    mltries = mltries.getValue()
    result = mltries.genericBreadthFirstTraversal(_listTraversal, {}, True,True, (), True)
    
    for k,v in result.items():
        print " ".join(k)
        
        for cmd in v.stringCmdList:
            tmp = []
            for subcmd in cmd:
                tmp.append(" ".join(subcmd))
            
            print "    "+" | ".join(tmp)
        
def listAliasContent(idAlias, mltries):
    pass #TODO

def execute(name):
    pass #TODO

def fire(name):
    pass #TODO

def setProperty(idAlias, name, value):
    pass #TODO

def createAlias(name, command):
    pass #TODO

def removeAlias(idAlias):
    #TODO don't forget to check removable properties

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

    
    

