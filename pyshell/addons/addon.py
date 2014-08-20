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
import os, sys
from pyshell.simpleProcess.postProcess import printColumn
from pyshell.arg.argchecker            import defaultInstanceArgChecker, completeEnvironmentChecker, stringArgChecker, listArgChecker, environmentParameterChecker, contextParameterChecker
from pyshell.utils.parameter           import EnvironmentParameter
from pyshell.utils.constants           import ENVIRONMENT_NAME
from pyshell.utils.coloration          import green, orange, bolt, nocolor

ADDONLIST_KEY = "loader_addon"
ADDON_PREFIX  = "pyshell.addons."

### addon ###

#TODO
    #be able to get more information about a addon
        #which sub part are reloadable for example (needed for the next TODO)

    #be able to only reload (and only reload, because different parts are linkend and can't be loaded single) a specific part of a module
        #only parameters for example
                
    #prblm with local addon name and external addon name
        #it is easy to use short name, but it is complicated to merge the use of both short and long name

## FUNCTION SECTION ##

@shellMethod(addon_dico=environmentParameterChecker(ADDONLIST_KEY),
             execution_context = contextParameterChecker("execution"))
def listAddonFun(addon_dico, execution_context):
    "list the available addons"
    
    addon_dico = addon_dico.getValue()
    
    if execution_context.getSelectedValue() == "shell":
        colorfunLoaded = green
        colorfunNotLoaded = orange
        title = bolt
    else:
        colorfunLoaded = nocolor
        colorfunNotLoaded = nocolor
        title = nocolor

    #create addon list from default addon directory
    local_addon = []
    if os.path.exists("./pyshell/addons/"):
        for dirname, dirnames, filenames in os.walk('./pyshell/addons/'):
            for name in filenames:
                if name.endswith(".py") and name != "__init__.py":
                    local_addon.append(ADDON_PREFIX + name[0:-3])
    
    l = []
    for (name, subAddon) in addon_dico.keys():
        if name in local_addon:
            local_addon.remove(name)
        
        if subAddon is None:
            l.append( (name, "(default)", colorfunLoaded("LOADED"), ) )
        else:
            l.append( (name, "("+str(subAddon)+")", colorfunLoaded("LOADED"), ) )

    for name in local_addon:
        l.append( (name,"",colorfunNotLoaded("NOT LOADED"), ) )

    l.sort()

    if len(l) == 0:
        return [("No addon available",)]
    
    #FIXME does not work correctly
        #prblm, the bolt decoration are size computed in the colomn size :/
    
    #l.insert(0, (title("Name"),title("Sub part"),title("State"), ) )
    l.insert(0, ("Name","Sub part","State", ) )

    return l

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             subAddon=stringArgChecker(), 
             parameters=completeEnvironmentChecker())
def unloadAddon(name, parameters, subAddon = None):
    "unload an addon"

    if not parameters.hasParameter(ADDONLIST_KEY, ENVIRONMENT_NAME):
        raise Exception("no addon list defined")

    addon_dico = parameters.getParameter(ADDONLIST_KEY, ENVIRONMENT_NAME).getValue()
    key = (name,subAddon,)
    
    if key not in addon_dico:
        raise Exception("unknown addon '"+str(name)+"'")
    
    addon_dico[key].unload(parameters, subAddon)
    del addon_dico[key]
    print(str(name)+" unloaded !")

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             subAddon=stringArgChecker(), 
             parameters=completeEnvironmentChecker())
def reloadAddon(name, parameters, subAddon = None):
    "reload an addon"

    if not parameters.hasParameter(ADDONLIST_KEY, ENVIRONMENT_NAME):
        raise Exception("no addon list defined")

    addon_dico = parameters.getParameter(ADDONLIST_KEY, ENVIRONMENT_NAME).getValue()
    key = (name,subAddon,)
    
    if key not in addon_dico:
        raise Exception("unknown addon '"+str(name)+"'")
    
    addon_dico[key].reload(parameters, subAddon)
    print(str(name)+" reloaded !")

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             subAddon=stringArgChecker(), 
             parameters=completeEnvironmentChecker())
def loadAddonFun(name, parameters, subAddon = None):
    "load a internal shell addon, just use the name of the module, no need to use the absolute name"
    toLoad = ADDON_PREFIX+str(name)
    importExternal(toLoad, parameters, subAddon = None)

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             subAddon=stringArgChecker(), 
             parameters=completeEnvironmentChecker())
def importExternal(name, parameters, subAddon = None):
    "load an external addon, use the absolute name of the package to load"

    if not parameters.hasParameter(ADDONLIST_KEY, ENVIRONMENT_NAME):
        raise Exception("no addon list defined")

    addon_dico = parameters.getParameter(ADDONLIST_KEY, ENVIRONMENT_NAME).getValue()
    key = (name,subAddon,)
    
    if key in addon_dico:
        raise Exception("already loaded addon")

    try:
        mod = __import__(name,fromlist=["_loaders"])
    except ImportError as ie:
        raise Exception("fail to load addon, reason: "+str(ie))

    if not hasattr(mod, "_loaders"):
        raise Exception("invalid addon, no loader found.  don't forget to register something in the addon")

    addon_dico[key] = mod._loaders
    mod._loaders.load(parameters, subAddon)

    print "   "+name+" loaded !" 

#TODO decore it and register it
    #need to find an explicit command
    
def hardReload(name, parameters, subAddon = None):
    
    if not parameters.hasParameter(ADDONLIST_KEY, ENVIRONMENT_NAME):
        raise Exception("no addon list defined")

    addon_dico = parameters.getParameter(ADDONLIST_KEY, ENVIRONMENT_NAME).getValue()
    
    key = (name,subAddon,)
    #unload
    if key in addon_dico:
        addon_dico[key].unload(parameters, subAddon)
        print(str(name)+" unloaded !")
        
    #load from file
    try:
        mod = __import__(name,fromlist=["_loaders"])
    except ImportError as ie:
        raise Exception("fail to load addon, reason: "+str(ie))

    if not hasattr(mod, "_loaders"):
        raise Exception("invalid addon, no loader found.  don't forget to register something in the addon")

    addon_dico[key] = mod._loaders
    mod._loaders.load(parameters, subAddon)

    print "   "+name+" loaded !" 

### REGISTER SECTION ###

registerSetTempPrefix( ("addon", ) )
registerCommand( ("list",) ,                  pro=listAddonFun, post=printColumn)
registerCommand( ("load",) ,                  pro=loadAddonFun)
registerCommand( ("unload",) ,                pro=unloadAddon)
registerCommand( ("reload",) ,                pro=reloadAddon)
registerCommand( ("import",) ,                pro=importExternal)
registerStopHelpTraversalAt( ("addon",) )

registerSetEnvironment(ADDONLIST_KEY, EnvironmentParameter(value = { ("pyshell.addons.addon",None,):sys.modules[__name__]._loaders}, typ=defaultInstanceArgChecker.getArgCheckerInstance(), transient = True, readonly = True, removable = False), noErrorIfKeyExist = False, override = True)
