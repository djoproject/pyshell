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
from pyshell.arg.argchecker import ArgChecker,listArgChecker, IntegerArgChecker, engineChecker, stringArgChecker, environmentChecker, tokenValueArgChecker, completeEnvironmentChecker, booleanValueArgChecker
from pyshell.simpleProcess.postProcess import printResultHandler, stringListResultHandler,listResultHandler
from tries.exception import triesException
import os
from pyshell.command.exception import engineInterruptionException
from pyshell.utils.parameterManager import MAIN_CATEGORY

#TODO
    #implement ambiguity management in usage
    #emplement alias management

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
    
@shellMethod(args=listArgChecker(ArgChecker()), mltries=environmentChecker("levelTries"))
def usageFun(args, mltries):
    "print the usage of a fonction"
    try:
        searchResult = mltries.advancedSearch(args, False)
    except triesException as te:
        print "failed to find the command <"+str(args)+">, reason: "+str(te)
        return

    if searchResult.isAmbiguous():
        print "ambiguity"#TODO show the different possibility, see in executer
        return
    elif not searchResult.isAvalueOnTheLastTokenFound():
        print "no result"
        return

    cmd = searchResult.getLastTokenFoundValue()
    print cmd.usage()

@shellMethod(mltries=environmentChecker("levelTries"), args=listArgChecker(ArgChecker()))
def helpFun(mltries, args=None):
    "print the usage of a fonction"

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
    advancedResult = mltries.advancedSearch(args, False)
    if advancedResult.isAmbiguous():
        tokenIndex = len(advancedResult.existingPath) - 1
        tries = advancedResult.existingPath[tokenIndex][1].localTries
        print tries.childs[0].childs[1].childs
        keylist = tries.getKeyList(args[tokenIndex])

        #if ambiguity occurs on an intermediate key, stop the search
        print "Ambiguous value on key index <"+str(tokenIndex)+">, possible value: "+", ".join(keylist)
        return

    stringKeys = []
    #cmd without stop traversal
    dic = mltries.buildDictionnary(args, False, True, False)
    for k in dic.keys():
        if prefix != None and len(k) >= (len(args)+1) and not k[len(args)].startswith(prefix):
            continue

        line = " ".join(k)
        hmess = dic[k].helpMessage
        if hmess != None and len(hmess) > 0:
            line += ": "+hmess

        stringKeys.append(line)

    #cmd with stop traversal
    dic2 = mltries.buildDictionnary(args, True, True, False)
    stop = {}
    for k in dic2.keys():
        if k in dic:
            continue

        if prefix != None and len(k) >= (len(args)+1) and not k[len(args)].startswith(prefix):
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
            if mltries.isStopTraversal(k[0:i]):

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

### parameter ###

@shellMethod(key=stringArgChecker(),
             parameters=environmentChecker("params"),
             parent=stringArgChecker())
def removeParameterValues(key, parameters, parent=None):
    "remove a value from the Parameter"

    if not parameters.keyExist(key):
        return #no job to do

    if parent != None:
        parameters.remove(key, parent)
    else:
        parameters.remove(key)

@shellMethod(key=stringArgChecker(),
             env=completeEnvironmentChecker(),
             parent=stringArgChecker())
def getParameterValues(key, env, parent=None): 
    "get a value from the environment"

    parameters, typ,readonly,removable = env["params"]
    
    if not parameters.keyExist(key):
        raise engineInterruptionException("Unknow parameter key", True)

    if parent == None:
        return parameters.getValue(key)
    else:
        return parameters.getValue(key, parent)

@shellMethod(key=stringArgChecker(),
             values=listArgChecker(ArgChecker(),1),
             #FIXME parent=stringArgChecker(),
             parameter=environmentChecker("params"))
def setParameterValue(key, values, parent = MAIN_CATEGORY, parameter = None):
    parameter.setValue(key, ', '.join(str(x) for x in values), parent)
            
### env management ###

@shellMethod(key=stringArgChecker(),
             env=completeEnvironmentChecker())
def removeEnvironmentContextValues(key, env):
    if key not in env:
        return #no job to do

    val,typ,readonly, removable = env[key]
    
    if readonly or not removable:
        raise engineInterruptionException("this environment object is not removable", True)

    del env[key]

@shellMethod(key=stringArgChecker(),
             env=completeEnvironmentChecker())
def getEnvironmentValues(key, env): 
    if key not in env:
        raise engineInterruptionException("Unknow environment key", True)

    val, typ,readonly, removable = env[key]
    return val

@shellMethod(key=stringArgChecker(),
             values=listArgChecker(ArgChecker(),1),
             env=completeEnvironmentChecker())
def setEnvironmentValuesFun(key, values, env): 
    if key not in env:
        raise engineInterruptionException("Unknow environment key", True)
        
    val, typ,readonly, removable = env[key]

    if readonly:
        raise engineInterruptionException("this environment object is not removable", True)

    #TODO actualy, not possible to set a single value, work only for listchecker
        #manage the case with only one value

    env[key] = (checker.getValue(values), checker, readonly, removable,)

@shellMethod(key=stringArgChecker(),
             value=ArgChecker(),
             env=completeEnvironmentChecker())
def createEnvironmentValueFun(key, value, env): 
    #build checker
    checker = _getChecker(valueType)
    
    #check value
    value = checker.getValue(value)
    
    #assign
    if key not in env:
        raise engineInterruptionException("Unknow environment key", True)
        
    val, typ, readonly, removable = env[key]

    if readonly:
        raise engineInterruptionException("this environment object is not removable", True)

    env[key] = (checker.getValue(values), checker, readonly, removable,)

@shellMethod(valueType=tokenValueArgChecker({"string":"string", "integer":"integer", "boolean":"boolean", "float":"float"}), 
             key=stringArgChecker(),
             values=listArgChecker(ArgChecker()),
             #FIXME noErrorIfExists=booleanValueArgChecker(),
             env=completeEnvironmentChecker())
def createEnvironmentValuesFun(valueType, key, values, noErrorIfExists=False, env=None): 
    #build checker
    checker = listArgChecker(_getChecker(valueType),1)
    
    #check value
    value = checker.getValue(values)
    
    #assign
    if key in env:
        if noErrorIfExists:
            return

        raise engineInterruptionException("Unknow environment key", True)

    env[key] = (value, valueType, False, True,)

@shellMethod(key=stringArgChecker(),
             values=listArgChecker(ArgChecker()),
             env=completeEnvironmentChecker())
def addEnvironmentValuesFun(key, values, env):
    if key in env:
        value, checker,readonly, removable = env[key]

        if readonly:
            raise engineInterruptionException("this environment object is not removable", True)
            
        if not isinstance(checker,listArgChecker) or not hasattr(value, "__iter__"):
            raise engineInterruptionException("Variable <"+str(key)+"> is not a list, can not append new value", True)
    
        newValues = []
        for i in range(0, len(values)):
            newValues.append(checker.getValue(values[i],i))
        
        value = list(value)
        value.append(newValues)
        env[key] = (value, checker,readonly, removable,)

@shellMethod(env=completeEnvironmentChecker())
def listEnvFun(env):
    "list all the environment variable"
    return [str(k)+" : "+str(v) for k,v in env.iteritems()]

### context management ###

@shellMethod(key=stringArgChecker(),
             context=environmentChecker("context"))
def removeContextValues(key, context):
    if not context.hasKey(key):
        return #no job to do

    context.removeContextKey(key)

@shellMethod(key=stringArgChecker(),
             context=environmentChecker("context"))
def getContextValues(key, context):
    if not context.hasKey(key):
        raise engineInterruptionException("Unknow context key", True)

    return context.getValues(key)

@shellMethod(key=stringArgChecker(),
             values=listArgChecker(ArgChecker(),1),
             context=environmentChecker("context"))
def setContextValuesFun(key, values, context):
    if not context.hasKey(key):
        raise engineInterruptionException("Unknow context key", True)

    context.setValues(key, values)

@shellMethod(valueType=tokenValueArgChecker({"string":"string", "integer":"integer", "boolean":"boolean", "float":"float"}), 
             key=stringArgChecker(),
             values=listArgChecker(ArgChecker()),
             #FIXME noErrorIfExists=booleanValueArgChecker(),
             context=environmentChecker("context"))
def createContextValuesFun(valueType, key, values, noErrorIfExists=False, context=None):
    #build checker
    checker = listArgChecker(_getChecker(valueType),1)
    
    #check value
    value = checker.getValue(values)

    if context.hasKey(key):
        if noErrorIfExists:
            return

        raise engineInterruptionException("Unknow context key", True)
    
    #assign
    context.addValues(key, value, checker)

@shellMethod(key=stringArgChecker(),
             values=listArgChecker(ArgChecker()),
             context=environmentChecker("context"))
def addContextValuesFun(key, values, context):
    if not context.hasKey(key):
        raise engineInterruptionException("Unknow context key", True)

    context.addValues(key, values)

@shellMethod(key=stringArgChecker(),
             value=ArgChecker(),
             context=environmentChecker("context"))
def selectValue(key, value, context):
    if not context.hasKey(key):
        raise engineInterruptionException("Unknow context key", True)

    context.selectValue(key, value)
    
@shellMethod(key=stringArgChecker(),
             index=IntegerArgChecker(),
             context=environmentChecker("context"))
def selectValueIndex(key, index, context):
    if not context.hasKey(key):
        raise engineInterruptionException("Unknow context key", True)

    context.selectValueIndex(key, index)

@shellMethod(key=stringArgChecker(),
             context=environmentChecker("context"))
def getSelectedContextValue(key, context):
    if not context.hasKey(key):
        raise engineInterruptionException("Unknow context key", True)

    return context.getSelectedValue(key)

@shellMethod(key=stringArgChecker(),
             context=environmentChecker("context"))
def getSelectedContextIndex(key, context):
    if not context.hasKey(key):
        raise engineInterruptionException("Unknow context key", True)

    return context.getSelectedIndex(key)

@shellMethod(context=environmentChecker("context"))
def listContext(context):
    strlist = []
    for k in context.getKeys():
        strlist.append(k + " : " + ', '.join("<"+str(+x)+">" for x in context.getValues(k)) + "  (selected index: "+str(context.getSelectedIndex(k))+", value: <"+str(context.getSelectedValue(k))+">)")

    return strlist

### var management ###

@shellMethod(key=stringArgChecker(),
             values=listArgChecker(ArgChecker(),1),
             _vars=environmentChecker("vars"))
def setVar(key, values, _vars):
    _vars[key] = values

@shellMethod(key=stringArgChecker(),
             _vars=environmentChecker("vars"))
def getVar(key, _vars):
    if key not in _vars:
        raise engineInterruptionException("(getVar) Unknow var key <"+str(key)+">",True)

    return _vars[key]

@shellMethod(key=stringArgChecker(),
             _vars=environmentChecker("vars"))
def unsetVar(key, _vars):
    if key in _vars:
        del _vars[key]

@shellMethod(_vars=environmentChecker("vars"))
def listVar(_vars):
    ret = []
    
    for k,v in _vars.items():
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

@shellMethod(name=stringArgChecker(), subAddon=stringArgChecker(), levelTries=environmentChecker("levelTries"))
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
        
        mod._loader[None]._load(levelTries)
        print "   "+toLoad+" loaded !"  
    except ImportError as ie:
        print "import error in <"+name+"> loading : "+str(ie)
    except NameError as ne:
        print "name error in <"+name+"> loading : "+str(ne)

def unloadAddon():
    pass #TODO

def reloadAddon():
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

    #parameter/context/environment/var
        #create a false create method
            #just check or not (boolean) if the value already exist, then make a set

        #list

        #saisir une variable de manière interractive

    #alias


#TODO         
"""def addAlias(self,CommandStrings,AliasCommandStrings):
        #pas aussi simple
            #on doit pouvoir gerer des alias avec des arguments fixe
        
        #commande speciale
            #contient le path vers la commande
            #les arguments ou une partie des arguments
        
        #TODO CommandStrings can't contain special token : >, >>, |, ...
        
        #TODO find the command in the tree
        
        #TODO build alias command
        
        #TODO insert in tree
        
        pass #TODO"""

#<misc>
registerCommand( ("exit",) ,                          pro=exitFun)
registerCommand( ("quit",) ,                          pro=exitFun)
registerCommand( ("echo",) ,                          pro=echo,         post=printResultHandler)
registerCommand( ("echo16",) ,                        pro=echo16,       post=printResultHandler)
registerCommand( ("toascii",) ,                       pro=intToAscii,   post=printResultHandler)
registerCommand( ("usage",) ,                         pro=usageFun)
registerCommand( ("help",) ,                          pro=helpFun,      post=stringListResultHandler)

#var
registerCommand( ("var", "set",) ,                    post=setVar)
registerCommand( ("var", "get",) ,                    pre=getVar, pro=stringListResultHandler)
registerCommand( ("var", "unset",) ,                  pro=unsetVar)
registerCommand( ("var", "list",) ,                   pre=listVar, pro=stringListResultHandler)
registerStopHelpTraversalAt( ("var",) )

#context
registerCommand( ("context", "unset",) ,              pro=removeContextValues)
registerCommand( ("context", "get",) ,                pre=getContextValues, pro=listResultHandler)
registerCommand( ("context", "set",) ,                post=setContextValuesFun)
registerCommand( ("context", "create",) ,             post=createContextValuesFun)
registerCommand( ("context", "add",) ,                post=addContextValuesFun)
registerCommand( ("context", "value",) ,              pre=getSelectedContextValue, pro=printResultHandler)
registerCommand( ("context", "index",) ,              pre=getSelectedContextIndex, pro=printResultHandler)
registerCommand( ("context", "select", "index",) ,    post=selectValueIndex)
registerCommand( ("context", "select", "value",) ,    post=selectValue)
registerCommand( ("context", "list",) ,               pre=listContext, pro=stringListResultHandler)
registerStopHelpTraversalAt( ("context",) )

#parameter   
registerCommand( ("parameter", "unset",) ,            pro=removeParameterValues)
registerCommand( ("parameter", "get",) ,              pre=getParameterValues, pro=printResultHandler)
registerCommand( ("parameter", "set",) ,              post=setParameterValue)
registerStopHelpTraversalAt( ("parameter",) )

#env
registerCommand( ("environment", "list",) ,           pro=listEnvFun,   post=stringListResultHandler)
registerCommand( ("environment", "create","single",), post=createEnvironmentValueFun)
registerCommand( ("environment", "create","list",),   post=createEnvironmentValuesFun)
registerCommand( ("environment", "get",) ,            pre=getEnvironmentValues, pro=listResultHandler)
registerCommand( ("environment", "unset",) ,          pro=removeEnvironmentContextValues)
registerCommand( ("environment", "set",) ,            post=setEnvironmentValuesFun)
registerCommand( ("environment", "add",) ,            post=addEnvironmentValuesFun)
registerStopHelpTraversalAt( ("environment",) )

#addon
registerCommand( ("addon","list",) ,                  pro=listAddonFun, post=stringListResultHandler)
registerCommand( ("addon","load",) ,                  pro=loadAddonFun)
registerStopHelpTraversalAt( ("addon",) )

#alias



