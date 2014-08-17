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

#from pyshell.utils.loader import *
from pyshell.loader.command            import registerSetTempPrefix, registerCommand, registerStopHelpTraversalAt
from pyshell.loader.parameter          import registerSetEnvironment
from pyshell.arg.decorator             import shellMethod
import os
from pyshell.simpleProcess.postProcess import stringListResultHandler
from pyshell.arg.argchecker            import defaultInstanceArgChecker, completeEnvironmentChecker, stringArgChecker, listArgChecker, environmentParameterChecker
from pyshell.utils.parameter           import EnvironmentParameter
from pyshell.utils.constants           import ENVIRONMENT_NAME

ADDONLIST_KEY = "loader_addon"
ADDON_PREFIX  = "pyshell.addons."

### addon ###

#TODO
    #be able to only reload (and only reload, because different parts are linkend and can't be loaded single) a specific part of a module, only parameters for example
    #subaddon name must be part of the key in addon_dico
    #print subbadon loaded in list process
    #manage multi src addon, addon from the outside of "addon" directory

## FUNCTION SECTION ##

@shellMethod(addon_dico=environmentParameterChecker(ADDONLIST_KEY))
def listAddonFun(addon_dico):
    "list the available addons"
    
    addon_dico = addon_dico.getValue()

    l = []
    if os.path.exists("./pyshell/addons/"):
        for dirname, dirnames, filenames in os.walk('./pyshell/addons/'):
            for name in filenames:
                if name.endswith(".py") and name != "__init__.py":
                    name = ADDON_PREFIX + name[0:-3]

                    if name in addon_dico:
                        l.append(name+" LOADED")
                    else:
                        l.append(name+" NOT LOADED")

    #TODO manage external addon
        #just print them as loaded
        #they are in addon_dico but not in filenames

    return l

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             subAddon=stringArgChecker(), 
             parameters=completeEnvironmentChecker())
def loadAddonFun(name, parameters, subAddon = None):
    "load a internal shell addon, just use the name of the module, no need to use the absolute name"
    toLoad = ADDON_PREFIX+str(name)

    if not parameters.hasParameter(ADDONLIST_KEY, ENVIRONMENT_NAME):
        raise Exception("no addon list defined")

    addon_dico = parameters.getParameter(ADDONLIST_KEY, ENVIRONMENT_NAME).getValue()

    if toLoad in addon_dico:
        raise Exception("already loaded addon")

    try:
        mod = __import__(toLoad,fromlist=["_loaders"])
    except ImportError as ie:
        raise Exception("fail to load addon, reason: "+str(ie))

    if not hasattr(mod, "_loaders"):
        raise Exception("invalid addon, no loader found.  don't forget to register at least one command in the addon")

    addon_dico[toLoad] = mod
    mod._loaders.load(parameters, subAddon)

    print "   "+toLoad+" loaded !" 

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             subAddon=stringArgChecker(), 
             parameters=completeEnvironmentChecker())
def unloadAddon(name, parameters, subAddon = None):
    "unload an addon"

    if not parameters.hasParameter(ADDONLIST_KEY, ENVIRONMENT_NAME):
        raise Exception("no addon list defined")

    addon_dico = parameters.getParameter(ADDONLIST_KEY, ENVIRONMENT_NAME).getValue()
    
    if name not in addon_dico:
        raise Exception("unknown addon <"+str(name)+">")
    
    addon_dico[name].unload(parameters, subAddon)
    del addon_dico[name]

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             subAddon=stringArgChecker(), 
             parameters=completeEnvironmentChecker())
def reloadAddon(name, parameters, subAddon = None):
    "reload an addon"

    if not parameters.hasParameter(ADDONLIST_KEY, ENVIRONMENT_NAME):
        raise Exception("no addon list defined")

    addon_dico = parameters.getParameter(ADDONLIST_KEY, ENVIRONMENT_NAME).getValue()
    
    if name not in addon_dico:
        raise Exception("unknown addon <"+str(name)+">")
    
    addon_dico[name].reload(parameters, subAddon)

def importExternal():
    pass #TODO import module from outside

### REGISTER SECTION ###

registerSetEnvironment(ADDONLIST_KEY, EnvironmentParameter(value = {}, typ=defaultInstanceArgChecker.getArgCheckerInstance(), transient = True, readonly = True, removable = False), noErrorIfKeyExist = False, override = True)

registerSetTempPrefix( ("addon", ) )
registerCommand( ("list",) ,                  pro=listAddonFun, post=stringListResultHandler)
registerCommand( ("load",) ,                  pro=loadAddonFun)
registerCommand( ("unload",) ,                pro=unloadAddon)
registerCommand( ("reload",) ,                pro=reloadAddon)
registerStopHelpTraversalAt( ("addon",) )
