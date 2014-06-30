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
from pyshell.arg.argchecker import ArgChecker,listArgChecker, IntegerArgChecker, engineChecker, stringArgChecker, parameterChecker, tokenValueArgChecker, completeEnvironmentChecker, booleanValueArgChecker
from pyshell.simpleProcess.postProcess import printResultHandler, stringListResultHandler,listResultHandler
from tries.exception import triesException
import os
from pyshell.command.exception import engineInterruptionException
from pyshell.utils.parameter import GenericParameter, CONTEXT_NAME, ENVIRONMENT_NAME, EnvironmentParameter, ContextParameter

#TODO
    #if help return only one command without ambiguity, return usage result instead
        #prblm help return a list of string, not a single string
            #solution return a list of one string

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

@shellMethod(args=listArgChecker(IntegerArgChecker()))
def intToAscii(args):
    "echo all the args into chars"
    s = ""
    for a in args:
        try:
            s += chr(a)
        except ValueError:
            s += str(a)

    return s
    
@shellMethod(args=listArgChecker(ArgChecker()), mltries=parameterChecker("levelTries"))
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
    print cmd.usage()

@shellMethod(mltries=parameterChecker("levelTries"), args=listArgChecker(ArgChecker()))
def helpFun(mltries, args=None):
    "print the help"

    #TODO what is the behaviour if we try to get the help on a node that is parent and hold a command ?
        #...

    if args == None:
        args = ()

    #little hack to be able to get help about for a function who has another function as prefix
    if len(args) > 0:
        fullArgs = args[:]
        prefix = args[-1]
        args = args[:-1]
    else:
        prefix = None
        fullArgs = None

    #manage ambiguity cases
    advancedResult = mltries.getValue().advancedSearch(args, False)
    if advancedResult.isAmbiguous():
        tokenIndex = len(advancedResult.existingPath) - 1
        tries = advancedResult.existingPath[tokenIndex][1].localTries
        keylist = tries.getKeyList(args[tokenIndex])

        #if ambiguity occurs on an intermediate key, stop the search
        print "Ambiguous value on key index <"+str(tokenIndex)+">, possible value: "+", ".join(keylist)
        return

    stringKeys = []
    #cmd without stop traversal
    dic = mltries.getValue().buildDictionnary(args, ignoreStopTraversal=False, addPrexix=True, onlyPerfectMatch=False)
    for k in dic.keys():
        if prefix != None and len(k) >= (len(args)+1) and not k[len(args)].startswith(prefix):
            continue

        #is it a hidden cmd ?
        if mltries.getValue().isStopTraversal(k):
            continue

        line = " ".join(k)
        hmess = dic[k].helpMessage
        if hmess != None and len(hmess) > 0:
            line += ": "+hmess

        stringKeys.append(line)

    #cmd with stop traversal
    dic2 = mltries.getValue().buildDictionnary(args, ignoreStopTraversal=True, addPrexix=True, onlyPerfectMatch=False)
    stop = {}
    for k in dic2.keys():
        if k in dic:
            continue

        if prefix != None and len(k) >= (len(args)+1) and not k[len(args)].startswith(prefix):
            continue

        #is it a hidden cmd ?
        if mltries.getValue().isStopTraversal(k):
            continue

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

                #is enable with the args ?
                equiv = False
                if fullArgs != None and len(fullArgs) >= len(k[0:i]):
                    equiv = True
                    for j in range(0,min(  len(fullArgs), len(k) ) ):
                        if not k[j].startswith(fullArgs[j]):
                            equiv = False 

                if not equiv:
                    if i == len(k):
                        stop[ k[0:i] ] = []
                    else:
                        stop[ k[0:i] ] = ([ k[i] ])
                    
                    break

            #this path is not disabled
            if i == (len(k) -1):
                line = " ".join(k)
                hmess = dic2[k].helpMessage
                if hmess != None and len(hmess) > 0:
                    line += ": "+hmess

                stringKeys.append(line)

    for stopPath, subChild in stop.items():
        if len(subChild) == 0:
            continue

        string = " ".join(stopPath) + ": {" + ",".join(subChild[0:3])
        if len(subChild) > 3:
            string += ",..."

        stringKeys.append(string+"}")

    return sorted(stringKeys)

### various method to manage var ###

def _getChecker(valueType):
    if valueType == "string":
        return stringArgChecker()
    elif valueType == "integer":
        return IntegerArgChecker()
    elif valueType == "boolean":
        return booleanValueArgChecker()
    elif valueType == "float":
        return floatTokenArgChecker()
    
    raise engineInterruptionException("Unknow value type", True)

#TODO
    #-create generic method

### parameter ###

@shellMethod(key=stringArgChecker(),
             parameters=completeEnvironmentChecker(),
             parent=stringArgChecker())
def removeParameterValues(key, parameters, parent=None):
    "remove a value from the Parameter"

    if not parameters.hasParameter(key, parent):
        return #no job to do

    parameters.unsetParameter(key, parent)

@shellMethod(key=stringArgChecker(),
             env=completeEnvironmentChecker(),
             parent=stringArgChecker())
def getParameterValues(key, env, parent=None): 
    "get a value from the environment"
    
    if not env.hasParameter(key, parent):
        raise engineInterruptionException("Unknow parameter key", True)

    return env.getParameter(key, parent).getValue()

@shellMethod(key=stringArgChecker(),
             values=listArgChecker(ArgChecker(),1),
             #FIXME parent=stringArgChecker(),
             parameter=completeEnvironmentChecker())
def setParameterValue(key, values, parent = None, parameter = None):
    parameter.setParameter(key,GenericParameter(', '.join(str(x) for x in values)), parent)

@shellMethod(parameter=completeEnvironmentChecker(),
             parent=stringArgChecker(),
             key=stringArgChecker())
def listParameter(parameter, parent=None, key=None, printParent = True):
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
    parameter.load()

@shellMethod(parameter=completeEnvironmentChecker())
def saveParameter(parameter):
    parameter.save()

### env management ###

@shellMethod(key=stringArgChecker(),
             parameters=completeEnvironmentChecker())
def removeEnvironmentContextValues(key, parameters):
    removeParameterValues(key, parameters, ENVIRONMENT_NAME)

@shellMethod(key=stringArgChecker(),
             env=completeEnvironmentChecker())
def getEnvironmentValues(key, env): 
    return getParameterValues(key, env, ENVIRONMENT_NAME)

@shellMethod(key=stringArgChecker(),
             values=listArgChecker(ArgChecker(),1),
             env=completeEnvironmentChecker())
def setEnvironmentValuesFun(key, values, env):
    if not env.hasParameter(key, ENVIRONMENT_NAME):
        raise engineInterruptionException("Unknow environment key <"+str(key)+">", True)

    envParam = env.getParameter(key, ENVIRONMENT_NAME)

    if isinstance(envParam.typ, listArgChecker):
        envParam.setValue(values)
    else:
        envParam.setValue(values[0])

@shellMethod(valueType=tokenValueArgChecker({"string":"string", "integer":"integer", "boolean":"boolean", "float":"float"}),
             key=stringArgChecker(),
             value=ArgChecker(),
             noErrorIfExists=booleanValueArgChecker(),
             env=completeEnvironmentChecker())
def createEnvironmentValueFun(valueType, key, value, noErrorIfExists=False, env=None): 
    if env.hasParameter(key,ENVIRONMENT_NAME):
        if noErrorIfExists:
            #TODO value assign

            return 

    #build checker
    checker = _getChecker(valueType)
    
    #check value
    value = checker.getValue(value)
    env.setEnvironement(key, EnvironmentParameter(value, checker))

@shellMethod(valueType=tokenValueArgChecker({"string":"string", "integer":"integer", "boolean":"boolean", "float":"float"}), 
             key=stringArgChecker(),
             values=listArgChecker(ArgChecker()),
             #FIXME noErrorIfExists=booleanValueArgChecker(),
             env=completeEnvironmentChecker())
def createEnvironmentValuesFun(valueType, key, values, noErrorIfExists=False, env=None): 
    if env.hasParameter(key,ENVIRONMENT_NAME):
        if noErrorIfExists:
            #TODO value assign

            return 

    #build checker
    checker = listArgChecker(_getChecker(valueType),1)
    
    #check value
    value = checker.getValue(values)
    env.setEnvironement(key, EnvironmentParameter(value, checker))

@shellMethod(key=stringArgChecker(),
             values=listArgChecker(ArgChecker()),
             env=completeEnvironmentChecker())
def addEnvironmentValuesFun(key, values, env):
    if not env.hasParameter(key, ENVIRONMENT_NAME):
        raise engineInterruptionException("Unknow environment key <"+str(key)+">", True)

    envParam = env.getParameter(key, ENVIRONMENT_NAME)

    if not isinstance(envParam.typ, listArgChecker):
        raise engineInterruptionException("This environment has not a list checker, can not add value", True)

    values = envParam.getValue()[:]
    values.extend(values)
    envParam.setValue(values)

@shellMethod(parameter=completeEnvironmentChecker(),
             key=stringArgChecker())
def listEnvFun(parameter, key=None):
    "list all the environment variable"
    return listParameter(parameter, ENVIRONMENT_NAME, key, False)

### context management ###

@shellMethod(key=stringArgChecker(),
             parameters=completeEnvironmentChecker())
def removeContextValues(key, parameters):
    removeParameterValues(key, parameters, CONTEXT_NAME)

@shellMethod(key=stringArgChecker(),
             env=completeEnvironmentChecker())
def getContextValues(key, env): 
    return getParameterValues(key, env, CONTEXT_NAME)

@shellMethod(key=stringArgChecker(),
             values=listArgChecker(ArgChecker(),1),
             env=completeEnvironmentChecker())
def setContextValuesFun(key, values, env):
    if not env.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = env.getParameter(key, CONTEXT_NAME)
    envParam.setValue(values)

@shellMethod(valueType=tokenValueArgChecker({"string":"string", "integer":"integer", "boolean":"boolean", "float":"float"}), 
             key=stringArgChecker(),
             values=listArgChecker(ArgChecker()),
             #FIXME noErrorIfExists=booleanValueArgChecker(),
             env=completeEnvironmentChecker())
def createContextValuesFun(valueType, key, values, noErrorIfExists=False, env=None): 
    if env.hasParameter(key,CONTEXT_NAME):
        if noErrorIfExists:
            #TODO value assign

            return 

    #build checker
    checker = listArgChecker(_getChecker(valueType),1)
    
    #check value
    value = checker.getValue(values)
    env.setEnvironement(key, ContextParameter(value, checker))

@shellMethod(key=stringArgChecker(),
             values=listArgChecker(ArgChecker()),
             env=completeEnvironmentChecker())
def addContextValuesFun(key, values, env):
    if not env.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = env.getParameter(key, CONTEXT_NAME)
    values = envParam.getValue()[:]
    values.extend(values)
    envParam.setValue(values)


@shellMethod(key=stringArgChecker(),
             value=ArgChecker(),
             context=completeEnvironmentChecker())
def selectValue(key, value, context):
    if not context.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = context.getParameter(key, CONTEXT_NAME)
    envParam.setIndexValue(value)
    
@shellMethod(key=stringArgChecker(),
             index=IntegerArgChecker(),
             context=completeEnvironmentChecker())
def selectValueIndex(key, index, context):
    if not context.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = context.getParameter(key, CONTEXT_NAME)
    envParam.setIndex(index)

@shellMethod(key=stringArgChecker(),
             context=completeEnvironmentChecker())
def getSelectedContextValue(key, context):
    if not context.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = context.getParameter(key, CONTEXT_NAME)

    return envParam.getSelectedValue()

@shellMethod(key=stringArgChecker(),
             context=completeEnvironmentChecker())
def getSelectedContextIndex(key, context):
    if not context.hasParameter(key, CONTEXT_NAME):
        raise engineInterruptionException("Unknow context key <"+str(key)+">", True)

    envParam = context.getParameter(key, CONTEXT_NAME)

    return envParam.getIndex()

@shellMethod(parameter=completeEnvironmentChecker(),
             key=stringArgChecker())
def listContext(parameter, key=None):
    "list all the context variable"
    return listParameter(parameter, CONTEXT_NAME, key, False)

### var management ###

@shellMethod(key=stringArgChecker(),
             values=listArgChecker(ArgChecker(),1),
             _vars=parameterChecker("vars"))
def setVar(key, values, _vars):
    _vars.getValue()[key] = values

@shellMethod(key=stringArgChecker(),
             _vars=parameterChecker("vars"))
def getVar(key, _vars):
    if key not in _vars.getValue():
        raise engineInterruptionException("(getVar) Unknow var key <"+str(key)+">",True)

    return _vars.getValue()[key]

@shellMethod(key=stringArgChecker(),
             _vars=parameterChecker("vars"))
def unsetVar(key, _vars):
    if key in _vars.getValue():
        del _vars.getValue()[key]

@shellMethod(_vars=parameterChecker("vars"))
def listVar(_vars):
    ret = []
    
    for k,v in _vars.getValue().items():
        ret.append(str(k)+" : "+str(v))
    
    return ret

### addon ###

def listAddonFun():
    "list the available addons"
    
    l = []
    if os.path.exists("./pyshell/addons/"):
        for dirname, dirnames, filenames in os.walk('./pyshell/addons/'):
            for name in filenames:
                if name.endswith(".py") and name != "__init__.py":
                    l.append(name[0:-3])

    return l

@shellMethod(name=stringArgChecker(), subAddon=stringArgChecker(), levelTries=parameterChecker("levelTries"))
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
    pass #TODO

def reloadAddon():
    pass #TODO

### aliad
def createAlias(name, command):
    pass #TODO

def removeAlias(name):
    pass #TODO
    
def addMethodToAlias(name, command):
    pass #TODO
    
def listAlias(name):
    pass #TODO

###

#TODO needed command
    #addon
        #unload addon
        #reload addon
        #list addon
            #print loaded or not loaded addon
        #manage multi src addon
        #in load addon
            #if addon have . in its path, just try to load it like that
            #withou adding a prefix
        
        #load/unload param from addons

    #parameter/context/environment/var
        #saisir une variable de manière interractive
            #demande a l'utilisateur d'encoder une valeur
        #usage pour les scripts
        
        #on peut envisager une boucle infinie jusqu'à ce que l'utilisateur encode une valeur correcte
        #et possibilité d'encoder dans une variable/cont/env/... deja existant ou d'en créer un

#<misc>
registerCommand( ("exit",) ,                          pro=exitFun)
registerCommand( ("quit",) ,                          pro=exitFun)
registerStopHelpTraversalAt( ("quit",) )
registerCommand( ("echo",) ,                          pro=echo,         post=printResultHandler)
registerCommand( ("echo16",) ,                        pro=echo16,       post=printResultHandler)
registerCommand( ("toascii",) ,                       pro=intToAscii,   post=printResultHandler)
registerCommand( ("usage",) ,                         pro=usageFun)
registerCommand( ("help",) ,                          pro=helpFun,      post=stringListResultHandler)
registerCommand( ("?",) ,                             pro=helpFun,      post=stringListResultHandler)
registerStopHelpTraversalAt( ("?",) )

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



