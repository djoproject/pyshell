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

from pyshell.arg.argchecker   import environmentParameterChecker, filePathArgChecker
from pyshell.arg.decorator    import shellMethod
from pyshell.loader.command   import registerCommand, registerSetGlobalPrefix, registerStopHelpTraversalAt
from pyshell.loader.parameter import registerSetEnvironment
from pyshell.utils.constants  import DEFAULT_CONFIG_DIRECTORY, ENVIRONMENT_LEVEL_TRIES_KEY 
from pyshell.utils.executing  import preParseNotPipedCommand, preParseLine
from pyshell.utils.exception  import ParameterLoadingException, ListOfException
from pyshell.system.procedure import Procedure 
from pyshell.system.environment import EnvironmentParameter

import sys, os

try:
    pyrev = sys.version_info.major
except AttributeError:
    pyrev = sys.version_info[0]

if pyrev == 2:
    import ConfigParser 
else:
    import configparser as ConfigParser

#XXX TODO REFACTOR IF NEEDED
    #some update occured in parsing and system/procedure, maybe some refactoring is needed here 

#XXX PROCEDURE DEFINITION
    #a procedure has a string list as name
        #this string list is store in the command tries
        
    #a procedure hold a list of command string and their argument (if any argument)
        #a command could be several piped command a| b| c| ...
    
    #argument of command must be checked at the adding in the procedure
        #except for an alone command or the first command of a piped commands
            #if they are allowed to receive argument from procedure
                #they can have uncomplete arg list
            #otherwise check every args of every command
                
    #if argument are given to procedure which command will use them ? (SEE PRBLM 4)
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
            #Solution 3: use named procedure without value at the beginning
                #then only use add to associate a command to an procedure
                    #bof, need two step to create an procedure :/
            #Solution 4: procedure are a one token string
                #et on stocke ça dans un parameter avec un parent special "procedure"
                #permettrait d'avoir les procedure qui se sauvegarde tout seul
                
                #drawback
                    #procedure a un seul token string
                    #categorie parente figée (???)

#TODO PRBLM 2: procedure must be disabled if one of the included command has been unloaded
    #disappearing of one of the used command
        #we need to know if a command is linked to an procedure
        
            #Solution 1: keep a map of the procedure and check at the unload
                #the procedure list ?
            #Solution 2: add an attribute to the multiCommand object
                #mark the command used in an procedure ?
            #Solution 3: add an unload routine in corresponding unloader
                #need to identify it before to add the routine
                    #be carefull to limit the amount of process in unloader search 
                    #to only save a limited amount of computation for an occasional unload
                #if possible to identify unload with O(1), could be interesting 
            
#TODO PRBLM 3: how to store the procedure ?
    #need an efficient and simple way to store them
        
        #Solution 1: keep a list of procedure in the system
            #pair of (List<String>, ProcedureObject)
            #store a special object in the command tree, this object will retrieve its ProcedureObject from the list at execution
            
            #PRO:
                #easy to manage
                    #to unload a command, just check in every procedure object if the command is used
                
            #CON:
                #need another additional structure to store the procedure
            
        #Solution 2: no list in the system
            #no more structure
            #store a special cmd object
                #a kind of decorated function
                
            #PRO
                #no more structure
            
            #con
                #hard to list existing procedure, only a prlbm for list...
                #could be interesting to reuse the help function and filter on these object
                    #if instance of ProcedureObject, then print
            
#TODO PRBLM 4: what about piping |
    #What happen if we add piping in procedure list ?
        #just store them like that and check the args of the command if needed
            #if command not linked to the arg passing of the procedure, check the args provided for the command
            #if not the first command of a piped command, check the args provided
        
    #how to manage argument passing from procedure to subcmd ?
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

@shellMethod(mltries = environmentParameterChecker(ENVIRONMENT_LEVEL_TRIES_KEY),
             filePath = environmentParameterChecker("procedure_filepath")) #TODO should be in constant
def load(mltries, filePath):
    #TODO refactor

    #load file
    filePath = filePath.getValue()
    mltries = mltries.getValue()
    
    if not os.path.exists(filePath):
        return

    config = ConfigParser.RawConfigParser()
    try:
        config.read(filePath)
    except Exception as ex:
        raise ParameterLoadingException("fail to read procedure file : "+str(ex))
    
    #parse config
    errorList = ListOfException()
    for section in config.sections():
        parsedSection = preParseNotPipedCommand(section)

        if len(parsedSection) == 0:
            errorList.addException(ParameterLoadingException("an empty section or a section only composed with white space exists in procedure file, this is not allowed"))
            continue

        mltriesSearchResult = mltries.advancedSearch( parsedSection, True ) 
        if mltriesSearchResult.isValueFound():
            alreadyExist = True
            procedure = mltriesSearchResult.getValue()

            if not isinstance(procedure, Procedure):
                errorList.addException(ParameterLoadingException("a section holds an already existing path: '"+" ".join(parsedSection)+"'"))
                continue

            if procedure.isReadOnly():
                errorList.addException(ParameterLoadingException("an procedure already exist on path '"+" ".join(parsedSection)+"' but it is readonly"))
                continue
        else:
            alreadyExist = False
            procedure = Procedure(" ".join(parsedSection))
        
        onError  = False
        lockedTo = -1
        for option in config.options(section):
            value = config.get(section, option)
            methDeco = {"executeonpre":procedure.setExecuteOnPre,
                        "removable":procedure.setRemovable,
                        "readonly":procedure.setReadOnly}
                        
            if option in methDeco:
                validBool, boolValue = isBool(value)
                if not validBool:
                    errorList.addException(ParameterLoadingException("a boolean value was expected for parameter '"+str(option)+"' of procedure '"+str(section)+"', got '"+str(value)+"'"))
                    onError = True
                    continue
                
                methDeco[option](boolValue)
                #setattr(procedure,option,boolValue)
            elif option == "lockedto":
                validInt, intValue = isInt(value)

                if not validInt:
                    errorList.addException(ParameterLoadingException("an integer value was expected for parameter 'lockedTo' of procedure '"+str(section)+"', got '"+str(value)+"'"))
                    onError = True
                    continue
                lockedTo = intValue
            elif option == "errorgranularity":
                validInt, intValue = isInt(value)

                if not validInt:
                    procedure.setNeverStopProcedureIfErrorOccured()
                else:
                    try:
                        procedure.setStopProcedureIfAnErrorOccuredWithAGranularityLowerOrEqualTo(intValue)
                    except Exception as ex:
                        errorList.addException(ex)
                        onError = True
            else:
                #is it an index key ?
                validInt, intValue = isInt(option)
                if not validInt:
                    errorList.addException(ParameterLoadingException("a unknown key has been found for procedure '"+str(section)+"': "+str(option)))
                    onError = True
                    continue
                
                #parse cmd
                #TODO some of the error are just warning and shouldn't disable the insertion
                preParsedCmd = preParseLine(value)
                if len(preParsedCmd) == 0:
                    continue

                #add cmd
                try:
                    realid = procedure.setCommand(intValue, preParsedCmd[0])
                    for i in xrange(1, len(preParsedCmd)):
                        procedure.addPipeCommand(realid, preParsedCmd[i])
                except Exception as ex:
                    errorList.addException(ex) #TODO find a way to include section name
                    onError = True 
        
        try:
            procedure.setLockedTo(lockedTo)
        except Exception as ex:
            errorList.addException(ex) #TODO find a way to include section name
            onError = True 
        
        if not onError and not alreadyExist:
            mltries.insert(parsedSection, procedure)

    #raise if error
    if errorList.isThrowable():
        raise errorList

def _saveTraversal(path, node, config, level):
    if not node.isValueSet():
        return config

    if not isinstance(node.value, Procedure):
        return config

    procedureObject = node.value
    
    if procedureObject.isTransient():
        return config
        
    procedureName = " ".join(path)
    
    config.add_section(procedureName)
    config.set(procedureName, "errorGranularity",                str(procedureObject.errorGranularity))
    config.set(procedureName, "executeOnPre",                    str(procedureObject.executeOnPre))
    config.set(procedureName, "lockedTo",                        str(procedureObject.lockedTo))
    config.set(procedureName, "readonly",                        str(procedureObject.readonly))
    config.set(procedureName, "removable",                       str(procedureObject.removable))
    
    index = 0
    for cmd in procedureObject.stringCmdList:
        tmp = []
        for subcmd in cmd:
            tmp.append(" ".join(subcmd))
        
        config.set(procedureName, str(index), " | ".join(tmp))
        index += 1

    return config

@shellMethod(mltries = environmentParameterChecker(ENVIRONMENT_LEVEL_TRIES_KEY),
             filePath = environmentParameterChecker("procedure_filepath")) #TODO should be in constant
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

    if not isinstance(node.value, Procedure):
        return state

    state[tuple(path)] = node.value
    return state

@shellMethod(mltries = environmentParameterChecker(ENVIRONMENT_LEVEL_TRIES_KEY))
def listProcedure(mltries):
    mltries = mltries.getValue()
    result = mltries.genericBreadthFirstTraversal(_listTraversal, {}, True,True, (), True)
    
    for k,v in result.items():
        print " ".join(k)
        
        for cmd in v.stringCmdList:
            tmp = []
            for subcmd in cmd:
                tmp.append(" ".join(subcmd))
            
            print "    "+" | ".join(tmp)
        
def listProcedureContent(idProcedure, mltries):
    pass #TODO

def execute(name):
    pass #TODO

def fire(name):
    pass #TODO

def setProperty(idProcedure, name, value):
    pass #TODO

#TODO
    #XXXXX use a single wrapped string for the command string XXXXX


def createProcedure(name, command):
    pass #TODO

def removeProcedure(idProcedure):
    #TODO don't forget to check removable properties

    pass #TODO
    
def addMethodToProcedure(idProcedure, command):
    pass #TODO

def moveCommandInProcedure(idProcedure, indexCommand, newIndex):
    pass #TODO

def moveCommandUpInProcedure(idProcedure, indexCommand):
    pass #TODO

def moveCommandDownInProcedure(idProcedure, indexCommand):
    pass #TODO

### REGISTER SECTION ###
    
registerSetGlobalPrefix( ("procedure", ) )
registerStopHelpTraversalAt()
registerCommand( ("list", ), pro=listProcedure )
registerCommand( ("load", ), pro=load )
registerCommand( ("save", ), pro=save )

#TODO register filename
registerSetEnvironment(envKey="procedure_filepath", env=EnvironmentParameter(os.path.join(DEFAULT_CONFIG_DIRECTORY, ".pyshell_procedure"),  typ=filePathArgChecker(readable=True, isFile=True), transient = False, readonly = False, removable = True), noErrorIfKeyExist = True, override = False)

    
    

