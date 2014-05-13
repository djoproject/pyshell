#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyshell.command.loader import *
from pyshell.arg.decorator import shellMethod
from pyshell.arg.argchecker import ArgChecker,listArgChecker, IntegerArgChecker, engineChecker, stringArgChecker, environmentChecker
from pyshell.simpleProcess.postProcess import printResultHandler, stringListResultHandler
from tries.exception import triesException
import os

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

@shellMethod(engine=engineChecker())
def listEnvFun(engine):
    "list all the environment variable"
    return [str(k)+" : "+str(v) for k,v in engine.getEnv().iteritems()]

@shellMethod(name=stringArgChecker(), levelTries=environmentChecker("levelTries"))
def loadAddonFun(name, levelTries):
    "load an external shell addon"
    
    toLoad = "pyshell.addons."+str(name)
    print "toLoad",toLoad
    try:
        mod = __import__(toLoad)
        print mod
        mod._loader._load(levelTries)
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
def helpFun(mltries, args=()):
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

