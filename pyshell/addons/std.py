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

from tries.exception                   import triesException
from pyshell.loader.command            import registerStopHelpTraversalAt, registerCommand
from pyshell.arg.decorator             import shellMethod
from pyshell.command.command           import MultiOutput
from pyshell.simpleProcess.postProcess import printResultHandler, stringListResultHandler
from pyshell.arg.argchecker            import defaultInstanceArgChecker,listArgChecker, parameterChecker, IntegerArgChecker, booleanValueArgChecker
from pyshell.utils.constants           import ENVIRONMENT_NAME
from pyshell.utils.exception           import DefaultPyshellException, USER_WARNING, USER_ERROR, WARNING

## FUNCTION SECTION ##

def exitFun():
    "Exit the program"
    exit()

@shellMethod(args=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def echo(args):
    "echo all the args"
    
    s = ""
    for a in args:
        s += str(a)+" "
        
    return s

@shellMethod(args=listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def echo16(args):
    "echo all the args in hexa"
    
    s = ""
    for a in args:
        try:
            s += "0x%x "%int(a)
        except ValueError:
            s += str(a)+" "

    return s

@shellMethod(args=listArgChecker(defaultInstanceArgChecker.getIntegerArgCheckerInstance()))
def intToAscii(args):
    "echo all the args into chars"
    s = ""
    for a in args:
        try:
            s += chr(a)
        except ValueError:
            s += str(a)

    return s
    
@shellMethod(args    = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance(),1), 
             mltries = parameterChecker("levelTries", ENVIRONMENT_NAME))
def usageFun(args, mltries):
    "print the usage of a fonction"
    
    try:
        searchResult = mltries.getValue().advancedSearch(args, False)
    except triesException as te:
        raise DefaultPyshellException("failed to find the command '"+str(args)+"', reason: "+str(te))

    if searchResult.isAmbiguous():
        tokenIndex = len(searchResult.existingPath) - 1
        tries = searchResult.existingPath[tokenIndex][1].localTries
        keylist = tries.getKeyList(args[tokenIndex])

        raise DefaultPyshellException("ambiguity on command '"+" ".join(args)+"', token '"+str(args[tokenIndex])+"', possible value: "+ ", ".join(keylist), USER_WARNING)

    if not searchResult.isPathFound():
        tokenNotFound = searchResult.getNotFoundTokenList()
        raise DefaultPyshellException("command not found, unknown token '"+tokenNotFound[0]+"'", USER_ERROR)

    if not searchResult.isAvalueOnTheLastTokenFound():
        raise DefaultPyshellException("parent token, no usage on this path", USER_WARNING)

    cmd = searchResult.getLastTokenFoundValue()
    return cmd.usage()

@shellMethod(mltries = parameterChecker("levelTries", ENVIRONMENT_NAME), 
             args    = listArgChecker(defaultInstanceArgChecker.getArgCheckerInstance()))
def helpFun(mltries, args=None):
    "print the help"

    if args == None:
        args = ()

    #little hack to be able to get help about for a function who has another function as suffix
    if len(args) > 0:
        fullArgs = args[:]
        suffix = args[-1]
        args = args[:-1]
    else:
        suffix = None
        fullArgs = None

    #manage ambiguity cases
    if fullArgs != None:
        advancedResult = mltries.getValue().advancedSearch(fullArgs, False)
        ambiguityOnLastToken = False
        if advancedResult.isAmbiguous():
            tokenIndex = len(advancedResult.existingPath) - 1
            tries = advancedResult.existingPath[tokenIndex][1].localTries
            keylist = tries.getKeyList(fullArgs[tokenIndex])

            #don't care about ambiguity on last token
            ambiguityOnLastToken = tokenIndex == len(fullArgs) -1
            if not ambiguityOnLastToken:
                #if ambiguity occurs on an intermediate key, stop the search
                raise DefaultPyshellException("Ambiguous value on key index <"+str(tokenIndex)+">, possible value: "+", ".join(keylist), USER_WARNING)

        #manage not found case
        if not ambiguityOnLastToken and not advancedResult.isPathFound():
            notFoundToken = advancedResult.getNotFoundTokenList()
            raise DefaultPyshellException("unkwnon token "+str(advancedResult.getTokenFoundCount())+": '"+notFoundToken[0]+"'", USER_ERROR)
    
    found = []
    stringKeys = []
    #cmd with stop traversal, this will retrieve every tuple path/value
    dic = mltries.getValue().buildDictionnary(args, ignoreStopTraversal=False, addPrexix=True, onlyPerfectMatch=False)
    for k in dic.keys():
        #if (fullArgs == None and len(k) < len(args)) or (fullArgs != None and len(k) < len(fullArgs)):
        #    continue

        #the last corresponding token in k must start with the last token of args => suffix
        if suffix != None and len(k) >= (len(args)+1) and not k[len(args)].startswith(suffix):
            continue

        #is it a hidden cmd ?
        if mltries.getValue().isStopTraversal(k):
            continue

        line = " ".join(k)
        hmess = dic[k].helpMessage
        if hmess != None and len(hmess) > 0:
            line += ": "+hmess
        
        found.append(  (k,hmess,)  )
        stringKeys.append(line)

    #cmd without stop traversal (parent category only)
    dic2 = mltries.getValue().buildDictionnary(args, ignoreStopTraversal=True, addPrexix=True, onlyPerfectMatch=False)
    stop = {}
    for k in dic2.keys():
        #if k is in dic, already processed
        if k in dic:
            continue
        
        #if (fullArgs == None and len(k) < len(args)) or (fullArgs != None and len(k) < len(fullArgs)):
        #    continue

        #the last corresponding token in k must start with the last token of args => suffix
        if suffix != None and len(k) >= (len(args)+1) and not k[len(args)].startswith(suffix):
            continue

        #is it a hidden cmd ? only for final node, because they don't appear in dic2
        #useless, "k in dic" is enough
        #if mltries.getValue().isStopTraversal(k):
        #    continue

        #is there a disabled token ?
        for i in range(1,len(k)):
            #this level of k is disabled, not the first occurence
            if k[0:i] in stop:
                if i == len(k):
                    break

                if k[i] not in stop[ k[0:i] ]:
                    stop[ k[0:i] ].append(k[i])

                break

            #this level of k is disabled, first occurence
            if mltries.getValue().isStopTraversal(k[0:i]):

                #if the disabled string token is in the args to print, it is equivalent to enabled
                equiv = False
                if fullArgs != None and len(fullArgs) >= len(k[0:i]):
                    equiv = True
                    for j in range(0,min(  len(fullArgs), len(k) ) ):
                        if not k[j].startswith(fullArgs[j]):
                            equiv = False 
                
                #if the args are not a prefix for every corresponding key, is is disabled
                if not equiv:
                    if i == len(k):
                        stop[ k[0:i] ] = []
                    else:
                        stop[ k[0:i] ] = ([ k[i] ])
                    
                    break

            #this path is not disabled and it is the last path, occured with a not disabled because in the path
            if i == (len(k) -1):
                line = " ".join(k)
                hmess = dic2[k].helpMessage
                if hmess != None and len(hmess) > 0:
                    line += ": "+hmess
                
                found.append( (k,hmess,) )
                stringKeys.append(line)
    
    #build the "real" help
    if len(stop) == 0:
        if len(found) == 0:
            if len(fullArgs) > 0:
                raise DefaultPyshellException("unkwnon token 0: '"+fullArgs[0]+"'", USER_ERROR)
            else:
                raise DefaultPyshellException("no help available",WARNING)
        
            return ()
        elif len(found) == 1 :
            if found[0][1] == None:
                description = "No description"
            else:
                description = found[0][1]

            return ( "Command Name:","       "+" ".join(found[0][0]),"", "Description:","       "+description,"","Usage: ","       "+usageFun(found[0][0], mltries), "",)
        
    for stopPath, subChild in stop.items():
        if len(subChild) == 0:
            continue

        string = " ".join(stopPath) + ": {" + ",".join(subChild[0:3])
        if len(subChild) > 3:
            string += ",..."

        stringKeys.append(string+"}")

    return sorted(stringKeys)

@shellMethod(start       = IntegerArgChecker(),
             stop        = IntegerArgChecker(),
             step        = IntegerArgChecker(),
             multiOutput = booleanValueArgChecker())
def generator(start=0,stop=100,step=1, multiOutput = True):
    "generate a list of integer"
    if multiOutput:
        return MultiOutput(range(start,stop,step))
    else:
        return range(start,stop,step)
        
### REGISTER SECTION ###

registerCommand( ("exit",) ,                          pro=exitFun)
registerCommand( ("quit",) ,                          pro=exitFun)
registerStopHelpTraversalAt( ("quit",) )
registerCommand( ("echo",) ,                          pro=echo,         post=printResultHandler)
registerCommand( ("echo16",) ,                        pro=echo16,       post=printResultHandler)
registerCommand( ("toascii",) ,                       pro=intToAscii,   post=printResultHandler)
registerCommand( ("usage",) ,                         pro=usageFun,     post=printResultHandler)
registerCommand( ("help",) ,                          pro=helpFun,      post=stringListResultHandler)
registerCommand( ("?",) ,                             pro=helpFun,      post=stringListResultHandler)
registerStopHelpTraversalAt( ("?",) )
registerCommand( ("range",) ,                         pre=generator)


