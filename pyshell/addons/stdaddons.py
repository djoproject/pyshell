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
from pyshell.arg.argchecker import ArgChecker,listArgChecker, IntegerArgChecker, engineChecker, stringArgChecker, environmentChecker, tokenValueArgChecker, completeEnvironmentChecker
from pyshell.simpleProcess.postProcess import printResultHandler, stringListResultHandler
from tries.exception import triesException
import os
from pyshell.command.exception import engineInterruptionException

#TODO
    #implement ambiguity management in usage
    #fix bug in help (see bug file)
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

def listAddonFun():
    "list the available addons"
    
    l = []
    if os.path.exists("./pyshell/addons/"):
        for dirname, dirnames, filenames in os.walk('./pyshell/addons/'):
            for name in filenames:
                if name.endswith(".py") and name != "__init__.py":
                    l.append(name[0:-3])

    return l

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

@shellMethod(env=completeEnvironmentChecker())
def listEnvFun(env):
    "list all the environment variable"
    return [str(k)+" : "+str(v) for k,v in env.iteritems()]

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

    dic = mltries.buildDictionnary(args, False, True, False)
    stringKeys = []

    for k in dic.keys():
        line = " ".join(k)
        hmess = dic[k].helpMessage
        if hmess != None and len(hmess) > 0:
            line += ": "+hmess

        stringKeys.append(line)

    return sorted(stringKeys)

@shellMethod(newStorageType=tokenValueArgChecker({"variable":"variable", "context":"context", "environment":"environment"}), 
             key=stringArgChecker(),
             engine=engineChecker())
def changeVariableType(newStorageType, key, engine):
    pass #TODO
        #only for variable, context and environment

@shellMethod(storageType=tokenValueArgChecker({"variable":"variable", "context":"context", "environment":"environment"}), 
             key=stringArgChecker(),
             values=listArgChecker(ArgChecker()),
             engine=engineChecker())
def addValuesFun(storageType, key, values, engine):
    
    if storageType == "variable":
        var, typ,readonly,removable = env["vars"]

        #TODO
        
    elif storageType  == "context":
        context, typ,readonly, removable = env["context"]

        #TODO
        
    elif storageType == "environment":
        if key in env:
            val, typ,readonly, removable = env[key]

            #TODO
        
    else:
        raise engineInterruptionException("Unknow storage type",True)

@shellMethod(storageType=tokenValueArgChecker({"parameter":"parameter", "variable":"variable", "context":"context", "environment":"environment"}), 
             valueType=tokenValueArgChecker({"string":"string", "integer":"integer", "boolean":"boolean", "float":"float"}), 
             key=stringArgChecker(),
             values=listArgChecker(ArgChecker()),
             engine=engineChecker(),
             parent=stringArgChecker())
def setValuesFun(storageType, valueType, key, values, engine, parent=None):
    pass #TODO
        #quid pour le parameter, chiant de stocker des listes...

@shellMethod(storageType=tokenValueArgChecker({"parameter":"parameter", "variable":"variable", "context":"context", "environment":"environment"}), 
             valueType=tokenValueArgChecker({"string":"string", "integer":"integer", "boolean":"boolean", "float":"float"}), 
             key=stringArgChecker(),
             value=ArgChecker(),
             env=completeEnvironmentChecker(),
             parent=stringArgChecker())
def setValueFun(storageType, valueType, key, value, env, parent=None):
    #TODO 
        #on devrait pouvoir assigner une variable juste avec sa clé, sa valeur et son type
            #on devrait pouvoir se passer de valueType quand la var existe déjà
    
    #build checker
    checker = None
    if valueType == "string":
        checker = stringArgChecker()
    elif valueType == "integer":
        checker = IntegerArgChecker()
    elif valueType == "boolean":
        checker = booleanValueArgChecker()
    elif valueType == "float":
        checker = floatTokenArgChecker()
    else:
        raise engineInterruptionException("Unknow value type", True)

    #check value
    value = checker.getValue(value)

    #store in the correct place
    if storageType == "parameter":
        val,typ,readonly, removable = env["params"]
        val.setValue(key, str(checker.getValue(value))) #do not store the type

    elif storageType == "variable":
        val,typ,readonly,removable = env["vars"]
        val[key] = (checker,value,)

        #TODO 
            #use which checker ? the new or the old ?
                #see below

    elif storageType  == "context":
        val,typ,readonly,removable = env["context"]

        #TODO if checker is not a list
            #convert the value to list
            #convert the checker to listchecker

        val.addValue(key, checker.getValue(value), checker)
    elif storageType == "environment":
        if key in env:
            typ,readonly,val = env[key]

            if readonly:
                raise engineInterruptionException("tis environment object is not removable", True)

        #TODO 
            #use which checker ? the new or the old ?
                #use the old, send a warning message if new checker is different
                #and print a message to explain how to change type
                #don't care abour new one if variable exists

        env[key] = (typ.getValue(value), checker, False, True,)

    else:
        raise engineInterruptionException("Unknow storage type",True)

@shellMethod(storageType=tokenValueArgChecker({"parameter":"parameter", "variable":"variable", "context":"context", "environment":"environment"}),  
             key=stringArgChecker(),
             env=completeEnvironmentChecker(),
             parent=stringArgChecker())
def getValues(storageType, key, env, parent=None):
    "get a value from the environment"

    if storageType == "parameter":
        parameters, typ,readonly,removable = env["params"]
        
        if not parameters.keyExist(key):
            raise engineInterruptionException("Unknow parameter key", True)

        if parent == None:
            return parameters.getValue(key)
        else:
            return parameters.getValue(key, parent)

    elif storageType == "variable":
        val, typ,readonly,removable = env["vars"]

        if key not in val:
            raise engineInterruptionException("Unknow variable key", True)

        return val[key]
    elif storageType  == "context":
        context, typ,readonly,removable = env["context"]
        
        if not context.hasKey(key):
            raise engineInterruptionException("Unknow context key", True)

        return context.getValues(key)

    elif storageType == "environment":
        if key not in env:
            raise engineInterruptionException("Unknow environment key", True)

        val, typ,readonly, removable = env[key]
        return val
    else:
        raise engineInterruptionException("Unknow storage type",True)

@shellMethod(storageType=tokenValueArgChecker({"parameter":"parameter", "variable":"variable", "context":"context", "environment":"environment"}),  
             key=stringArgChecker(),
             env=completeEnvironmentChecker(),
             parent=stringArgChecker())
def removeValues(storageType, key, env, parent=None):
    "remove a value from the environment"

    #TODO manage removable boolean

    if storageType == "parameter":
        parameters, typ,readonly, removable = env["params"]
        
        if not parameters.keyExist(key):
            raise engineInterruptionException("Unknow parameter key", True)

        if parent != None:
            parameters.remove(key, parent)
        else:
            parameters.remove(key)

    elif storageType == "variable":
        val,typ,readonly, removable = env["vars"]

        if key not in val:
            raise engineInterruptionException("Unknow variable key", True)

        del val[key]

    elif storageType  == "context":
        context,typ,readonly, removable = env["context"]
        
        if not context.hasKey(key):
            raise engineInterruptionException("Unknow context key", True)

        context.removeContextKey(key)

    elif storageType == "environment":
        if key not in env:
            raise engineInterruptionException("Unknow environment key", True)

        val,typ,readonly, removable = env[key]
        
        if readonly:
            raise engineInterruptionException("tis environment object is not removable", True)

        del env[key]

    else:
        raise engineInterruptionException("Unknow storage type",True)

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

    #parameter
        #list parameter parent

    #context
        #get selected context
        #select context value
        #list context
    
    #var
        #list var
        #saisir une variable de manière interractive
        #assigner par pipe
            #pas besoin d'une commande, juste besoin de la commande setValue
                #quid de la liste retournée

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

registerCommand( ("exit",) ,              pro=exitFun)
registerCommand( ("quit",) ,              pro=exitFun)
registerCommand( ("echo",) ,              pro=echo,         post=printResultHandler)
registerCommand( ("echo16",) ,            pro=echo16,       post=printResultHandler)
registerCommand( ("list","addon",) ,      pro=listAddonFun, post=stringListResultHandler)
registerCommand( ("toascii",) ,           pro=intToAscii,   post=printResultHandler)
registerCommand( ("list","environment") , pro=listEnvFun,   post=stringListResultHandler)
registerCommand( ("load","addon",) ,      pro=loadAddonFun)
registerCommand( ("usage",) ,             pro=usageFun)
registerCommand( ("help",) ,              pro=helpFun,      post=stringListResultHandler)

registerCommand( ("get","values") ,       pro=getValues,    post=printResultHandler)
registerCommand( ("remove","values") ,    pro=removeValues)

