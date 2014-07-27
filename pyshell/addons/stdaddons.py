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

from pyshell.utils.loader import *
from pyshell.arg.decorator import shellMethod
from pyshell.arg.argchecker import defaultInstanceArgChecker, ArgChecker,listArgChecker, engineChecker, parameterChecker, tokenValueArgChecker, completeEnvironmentChecker
from pyshell.simpleProcess.postProcess import printResultHandler, stringListResultHandler,listResultHandler
from tries.exception import triesException, pathNotExistsTriesException
import os
from pyshell.command.exception import engineInterruptionException
from pyshell.command.command import MultiOutput
from pyshell.utils.parameter import CONTEXT_NAME, ENVIRONMENT_NAME, EnvironmentParameter, ContextParameter   

#TODO
    #split into several sub addon

## MISC SECTION ##

def exitFun():
    "Exit the program"
    exit()

@shellMethod(args=listArgChecker(ArgChecker()))
def echo(args):
    "echo all the args"
    
    s = ""
    for a in args:
        s += str(a)+" "
        
    return s

@shellMethod(args=listArgChecker(ArgChecker()))
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
    
@shellMethod(args=listArgChecker(ArgChecker(),1), mltries=parameterChecker("levelTries"))
def usageFun(args, mltries):
    "print the usage of a fonction"
    
    try:
        searchResult = mltries.getValue().advancedSearch(args, False)
    except triesException as te:
        print "failed to find the command <"+str(args)+">, reason: "+str(te)
        return

    if searchResult.isAmbiguous():
        tokenIndex = len(searchResult.existingPath) - 1
        tries = searchResult.existingPath[tokenIndex][1].localTries
        keylist = tries.getKeyList(args[tokenIndex])

        print("ambiguity on command <"+" ".join(args)+">, token <"+str(args[tokenIndex])+">, possible value: "+ ", ".join(keylist))
        return

    if not searchResult.isPathFound():
        tokenNotFound = searchResult.getNotFoundTokenList()
        print "command not found, unknown token <"+tokenNotFound[0]+">"
        return 

    if not searchResult.isAvalueOnTheLastTokenFound():
        print "parent token, no usage on this path" 
        return

    cmd = searchResult.getLastTokenFoundValue()
    return cmd.usage()

@shellMethod(mltries=parameterChecker("levelTries"), args=listArgChecker(ArgChecker()))
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
                print "Ambiguous value on key index <"+str(tokenIndex)+">, possible value: "+", ".join(keylist)
                return

        #manage not found case
        if not ambiguityOnLastToken and not advancedResult.isPathFound():
            notFoundToken = advancedResult.getNotFoundTokenList()
            print "unkwnon token "+str(advancedResult.getTokenFoundCount())+": <"+notFoundToken[0]+">"
            return
    
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
                print "unkwnon token 0: <"+fullArgs[0]+">"
            else:
                print "no help available"
        
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

@shellMethod(start = defaultInstanceArgChecker.getIntegerArgCheckerInstance(),
             stop  = defaultInstanceArgChecker.getIntegerArgCheckerInstance(),
             step  = defaultInstanceArgChecker.getIntegerArgCheckerInstance(),
             multiOutput = defaultInstanceArgChecker.getbooleanValueArgCheckerInstance())
def generator(start=0,stop=100,step=1, multiOutput = True):
    "generate a list of integer"
    if multiOutput:
        return MultiOutput(range(start,stop,step))
    else:
        return range(start,stop,step)
        
### various method to manage parameter ###

def _getChecker(valueType):
    if valueType == "string":
        return defaultInstanceArgChecker.getStringArgCheckerInstance()
    elif valueType == "integer":
        return defaultInstanceArgChecker.getIntegerArgCheckerInstance()
    elif valueType == "boolean":
        return defaultInstanceArgChecker.getbooleanValueArgCheckerInstance()
    elif valueType == "float":
        return defaultInstanceArgChecker.getFloatTokenArgCheckerInstance()
    
    raise engineInterruptionException("Unknow value type", True)

#TODO
    #-create generic method
        #for which one ?
            #createContextValuesFun/createEnvironmentValueFun
            #addContextValuesFun/addEnvironmentValuesFun
    
    #-create setter/getter for parameter settings (transient/readonly/...)
    
    #reset params
        #load from default
    
    #unset/reset params from addons
        
    #print in log

    #!!!! MERGE environment and parameter !!!
        #the difference between both is difficult to understand

### parameter ###

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameters=completeEnvironmentChecker(),
             parent=defaultInstanceArgChecker.getStringArgCheckerInstance())
def removeParameterValues(key, parameters, parent=None):
    "remove a value from the Parameter"

    if not parameters.hasParameter(key, parent):
        return #no job to do

    parameters.unsetParameter(key, parent)

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             env=completeEnvironmentChecker(),
             parent=defaultInstanceArgChecker.getStringArgCheckerInstance())
def getParameterValues(key, env, parent=None): 
    "get a value from the environment"
    
    if not env.hasParameter(key, parent):
        raise engineInterruptionException("Unknow parameter key", True)

    return env.getParameter(key, parent).getValue()

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values=listArgChecker(ArgChecker(),1),
             #FIXME parent=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameter=completeEnvironmentChecker())
def setParameterValue(key, values, parent = None, parameter = None):
    "assign a value to a parameter"
    parameter.setParameter(key,EnvironmentParameter(', '.join(str(x) for x in values)), parent)

@shellMethod(parameter=completeEnvironmentChecker(),
             parent=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             key=defaultInstanceArgChecker.getStringArgCheckerInstance())
def listParameter(parameter, parent=None, key=None, printParent = True):
    "list every parameter sorted by the parent name"
    if parent != None:
        if parent not in parameter.params:
            raise engineInterruptionException("unknown parameter parent <"+str(parent)+">", True) 
        
        if key != None:
            if key not in parameter.params[parent]:
                raise engineInterruptionException("unknown key <"+str(key)+"> in parent <"+str(parent)+">", True) 
    
            return (str(parent)+"."+str(key)+" : \""+str(parameter.params[parent][key])+"\"",)
    
        keys = (parent,)
    else:
        keys = parameter.params.keys()
    
    to_ret = []
    for k in keys:
        if printParent:
            to_ret.append(k)

        for subk,subv in parameter.params[k].items():
            if printParent:
                to_ret.append("    "+subk+" : \""+str(subv)+"\"")
            else:
                to_ret.append(subk+" : \""+str(subv)+"\"")
            
    return to_ret

@shellMethod(parameter=completeEnvironmentChecker())
def loadParameter(parameter):
    "load parameters from the settings file"
    
    try:
        parameter.load()
    except Exception as ex:
        print("fail to load parameter fail: "+str(ex))

@shellMethod(parameter=completeEnvironmentChecker())
def saveParameter(parameter):
    "save not transient parameters to the settings file"
    
    try:
        parameter.save()
    except Exception as ex:
        print("fail to save parameter fail: "+str(ex))
    
### env management ###

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameters=completeEnvironmentChecker())
def removeEnvironmentContextValues(key, parameters):
    "remove an environment parameter"
    removeParameterValues(key, parameters, ENVIRONMENT_NAME)

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             env=completeEnvironmentChecker())
def getEnvironmentValues(key, env):
    "get an environment parameter value" 
    return getParameterValues(key, env, ENVIRONMENT_NAME)

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values=listArgChecker(ArgChecker(),1),
             env=completeEnvironmentChecker())
def setEnvironmentValuesFun(key, values, env):
    "set an environment parameter value"
     
    if not env.hasParameter(key, ENVIRONMENT_NAME):
        raise engineInterruptionException("Unknow environment key <"+str(key)+">", True)

    envParam = env.getParameter(key, ENVIRONMENT_NAME)

    if isinstance(envParam.typ, listArgChecker):
        envParam.setValue(values)
    else:
        envParam.setValue(values[0])

@shellMethod(valueType=tokenValueArgChecker({"string":"string", "integer":"integer", "boolean":"boolean", "float":"float"}),
             key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             value=ArgChecker(),
             noErrorIfExists=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),
             env=completeEnvironmentChecker())
def createEnvironmentValueFun(valueType, key, value, noErrorIfExists=False, env=None): 
    "create an environment parameter value" 
    if env.hasParameter(key,ENVIRONMENT_NAME):
        if noErrorIfExists:
            #TODO value assign

            return 

    #build checker
    checker = _getChecker(valueType)
    
    #check value
    value = checker.getValue(value, None, "Environment "+key)
    env.setParameter(key, EnvironmentParameter(value, checker),ENVIRONMENT_NAME)

@shellMethod(valueType=tokenValueArgChecker({"string":"string", "integer":"integer", "boolean":"boolean", "float":"float"}), 
             key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values=listArgChecker(ArgChecker()),
             #FIXME noErrorIfExists=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),
             env=completeEnvironmentChecker())
def createEnvironmentValuesFun(valueType, key, values, noErrorIfExists=False, env=None): 
    "create an environment parameter value list" 
    if env.hasParameter(key,ENVIRONMENT_NAME):
        if noErrorIfExists:
            #TODO value assign

            return 

    #build checker
    checker = listArgChecker(_getChecker(valueType),1)
    
    #check value
    value = checker.getValue(values, None, "Environment "+key)
    env.setParameter(key, EnvironmentParameter(value, checker),ENVIRONMENT_NAME)

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values=listArgChecker(ArgChecker()),
             env=completeEnvironmentChecker())
def addEnvironmentValuesFun(key, values, env):
    "add values to an environment parameter list"
     
    if not env.hasParameter(key, ENVIRONMENT_NAME):
        raise engineInterruptionException("Unknow environment key <"+str(key)+">", True)

    envParam = env.getParameter(key, ENVIRONMENT_NAME)

    if not isinstance(envParam.typ, listArgChecker):
        raise engineInterruptionException("This environment has not a list checker, can not add value", True)

    values = envParam.getValue()[:]
    values.extend(values)
    envParam.setValue(values)

@shellMethod(parameter=completeEnvironmentChecker(),
             key=defaultInstanceArgChecker.getStringArgCheckerInstance())
def listEnvFun(parameter, key=None):
    "list all the environment variable"
    return listParameter(parameter, ENVIRONMENT_NAME, key, False)

### context management ###

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             parameters=completeEnvironmentChecker())
def removeContextValues(key, parameters):
    "remove a context parameter"
    removeParameterValues(key, parameters, CONTEXT_NAME)

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             env=completeEnvironmentChecker())
def getContextValues(key, env): 
    "get a context parameter value" 
    return getParameterValues(key, env, CONTEXT_NAME)

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values=listArgChecker(ArgChecker(),1),
             env=completeEnvironmentChecker())
def setContextValuesFun(key, values, env):
    "set a context parameter value"

    if not env.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = env.getParameter(key, CONTEXT_NAME)
    envParam.setValue(values)

@shellMethod(valueType=tokenValueArgChecker({"string":"string", "integer":"integer", "boolean":"boolean", "float":"float"}), 
             key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values=listArgChecker(ArgChecker()),
             #FIXME noErrorIfExists=defaultInstanceArgChecker.getbooleanValueArgCheckerInstance(),
             env=completeEnvironmentChecker())
def createContextValuesFun(valueType, key, values, noErrorIfExists=False, env=None): 
    "create a context parameter value list"
    if env.hasParameter(key,CONTEXT_NAME):
        if noErrorIfExists:
            #TODO value assign

            return 

    #build checker
    checker = listArgChecker(_getChecker(valueType),1)
    
    #check value
    value = checker.getValue(values, None, "Context "+key)
    env.setParameter(key, ContextParameter(value, checker),CONTEXT_NAME)

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values=listArgChecker(ArgChecker()),
             env=completeEnvironmentChecker())
def addContextValuesFun(key, values, env):
    "add values to a context parameter list"
    if not env.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = env.getParameter(key, CONTEXT_NAME)
    values = envParam.getValue()[:]
    values.extend(values)
    envParam.setValue(values)


@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             value=ArgChecker(),
             context=completeEnvironmentChecker())
def selectValue(key, value, context):
    "select the value for the current context"
    if not context.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = context.getParameter(key, CONTEXT_NAME)
    envParam.setIndexValue(value)
    
@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             index=defaultInstanceArgChecker.getIntegerArgCheckerInstance(),
             context=completeEnvironmentChecker())
def selectValueIndex(key, index, context):
    "select the value index for the current context"
    if not context.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = context.getParameter(key, CONTEXT_NAME)
    envParam.setIndex(index)

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             context=completeEnvironmentChecker())
def getSelectedContextValue(key, context):
    "get the selected value for the current context"
    if not context.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = context.getParameter(key, CONTEXT_NAME)

    return envParam.getSelectedValue()

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             context=completeEnvironmentChecker())
def getSelectedContextIndex(key, context):
    "get the selected value index for the current context"
    if not context.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = context.getParameter(key, CONTEXT_NAME)

    return envParam.getIndex()

@shellMethod(parameter=completeEnvironmentChecker(),
             key=defaultInstanceArgChecker.getStringArgCheckerInstance())
def listContext(parameter, key=None):
    "list all the context variable"
    return listParameter(parameter, CONTEXT_NAME, key, False)

### var management ###

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             values=listArgChecker(ArgChecker(),1),
             _vars=parameterChecker("vars"))
def setVar(key, values, _vars):
    "assign a value to a var"
    _vars.getValue()[key] = values

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             _vars=parameterChecker("vars"))
def getVar(key, _vars):
    "get the value of a var"
    if key not in _vars.getValue():
        raise engineInterruptionException("(getVar) Unknow var key <"+str(key)+">",True)

    return _vars.getValue()[key]

@shellMethod(key=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             _vars=parameterChecker("vars"))
def unsetVar(key, _vars):
    "unset a var"
    if key in _vars.getValue():
        del _vars.getValue()[key]

@shellMethod(_vars=parameterChecker("vars"))
def listVar(_vars):
    "list every existing var"
    ret = []
    
    for k,v in _vars.getValue().items():
        ret.append(str(k)+" : "+str(v))
    
    return ret

### addon ###

#TODO
    #unload addon
    #reload addon
    #list addon
        #print loaded or not loaded addon
    #manage multi src addon
    #in load addon
        #if addon have . in its path, just try to load it like that
        #withou adding a prefix
    
    #load/unload param from addons


def listAddonFun():
    "list the available addons"
    
    l = []
    if os.path.exists("./pyshell/addons/"):
        for dirname, dirnames, filenames in os.walk('./pyshell/addons/'):
            for name in filenames:
                if name.endswith(".py") and name != "__init__.py":
                    l.append(name[0:-3])
                    
                    #TODO add an information about the state of the addon (not loaded/loaded)

    return l

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             subAddon=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             levelTries=parameterChecker("levelTries"))
def loadAddonFun(name, levelTries, subAddon = None):
    "load an external shell addon"
    toLoad = "pyshell.addons."+str(name)

    if subAddon == "":
        subAddon = None

    try:
        mod = __import__(toLoad,fromlist=["_loader"])
        
        if not hasattr(mod, "_loader"):
            print("invalid addon, no loader found.  don't forget to register at least one command in the addon")
        
        if subAddon not in mod._loader:
            print("sub addon does not exist in the addon <"+str(name)+">")
        
        mod._loader[None]._load(levelTries.getValue())
        print "   "+toLoad+" loaded !"  
    except ImportError as ie:
        print "import error in <"+name+"> loading : "+str(ie)
    except NameError as ne:
        print "name error in <"+name+"> loading : "+str(ne)

def unloadAddon():
    "unload an addon"
    
    pass #TODO

def reloadAddon():
    "reload an addon"

    pass #TODO

### alias

#TODO
    #problm to solve
        #name and command are both unknows length string list
        #so it is difficult to known where finish the first one
        
            #Solution 1: wait for parameter implementation
            #Solution 2: use variable
            #Solution 3: use named alias without value at the beginning
                #then only use add to associate a command to an alias
                    #bof, need two step to create an alias :/
            #Solution 4: alias are a one token string
                #et on stocke ça dans un parameter avec un parent special "alias"
                #permettrait d'avoir les alias qui se sauvegarde tout seul
                
                #drawback
                    #alias a un seul token string
                    #categorie parente figée
        
        #alias must be disabled if one of the included command has been unloaded
        #we need to know if a command is linked to an alias
        
            #Solution 1: keep a map of the alias and check at the unload
                #the alias list ?
            #Solution 2: add an attribute to the multiCommand object
            #Solution 3:
            
            

def createAlias(name, command):
    pass #TODO

def removeAlias(name):
    pass #TODO
    
def addMethodToAlias(name, command):
    pass #TODO
    
def listAlias(name):
    pass #TODO

###

#TODO
#parameter/context/environment/var
    #saisir une variable de manière interractive
        #demande a l'utilisateur d'encoder une valeur
    #usage pour les scripts
    
    #on peut envisager une boucle infinie jusqu'à ce que l'utilisateur encode une valeur correcte
    #et possibilité d'encoder dans une variable/cont/env/... deja existant ou d'en créer un
    
    #stocker juste dans les vars et ensuite assigner a para/cont/env si on le souhaite
    
    #peut poser des prblm avec le REPL
        #si on doit saisir quelque chose à l'écran
        #on va devoir faire une saisie
        #et si le REPL s'enclenche a ce moment là...

def askForValue():
    pass #TODO
    
def askForValueList():
    pass #TODO

### REGISTER SECTION ###

#<misc>
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

#var
registerSetTempPrefix( ("var", ) )
registerCommand( ("set",) ,                    post=setVar)
registerCommand( ("get",) ,                    pre=getVar, pro=stringListResultHandler)
registerCommand( ("unset",) ,                  pro=unsetVar)
registerCommand( ("list",) ,                   pre=listVar, pro=stringListResultHandler)
registerStopHelpTraversalAt( ("var",) )

#context
registerSetTempPrefix( ("context", ) )
registerCommand( ("unset",) ,              pro=removeContextValues)
registerCommand( ("get",) ,                pre=getContextValues, pro=listResultHandler)
registerCommand( ("set",) ,                post=setContextValuesFun)
registerCommand( ("create",) ,             post=createContextValuesFun)
registerCommand( ("add",) ,                post=addContextValuesFun)
registerCommand( ("value",) ,              pre=getSelectedContextValue, pro=printResultHandler)
registerCommand( ("index",) ,              pre=getSelectedContextIndex, pro=printResultHandler)
registerCommand( ("select", "index",) ,    post=selectValueIndex)
registerCommand( ("select", "value",) ,    post=selectValue)
registerCommand( ("list",) ,               pre=listContext, pro=stringListResultHandler)
registerStopHelpTraversalAt( ("context",) )

#parameter   
registerSetTempPrefix( ("parameter", ) )
registerCommand( ("unset",) ,            pro=removeParameterValues)
registerCommand( ("get",) ,              pre=getParameterValues, pro=listResultHandler)
registerCommand( ("set",) ,              post=setParameterValue)
registerCommand( ("list",) ,             pre=listParameter, pro=stringListResultHandler)
registerCommand( ("load",) ,             pro=loadParameter)
registerCommand( ("save",) ,             pro=saveParameter)
registerStopHelpTraversalAt( ("parameter",) )

#env
registerSetTempPrefix( ("environment", ) )
registerCommand( ("list",) ,           pro=listEnvFun,   post=stringListResultHandler)
registerCommand( ("create","single",), post=createEnvironmentValueFun)
registerCommand( ("create","list",),   post=createEnvironmentValuesFun)
registerCommand( ("get",) ,            pre=getEnvironmentValues, pro=listResultHandler)
registerCommand( ("unset",) ,          pro=removeEnvironmentContextValues)
registerCommand( ("set",) ,            post=setEnvironmentValuesFun)
registerCommand( ("add",) ,            post=addEnvironmentValuesFun)
registerStopHelpTraversalAt( ("environment",) )

#addon
registerSetTempPrefix( ("addon", ) )
registerCommand( ("list",) ,                  pro=listAddonFun, post=stringListResultHandler)
registerCommand( ("load",) ,                  pro=loadAddonFun)
registerStopHelpTraversalAt( ("addon",) )

#alias



