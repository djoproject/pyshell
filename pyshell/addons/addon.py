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
from pyshell.loader.utils              import GlobalLoaderLoadingState
from pyshell.arg.decorator             import shellMethod
import os, sys
from pyshell.simpleProcess.postProcess import printColumn, stringListResultHandler
from pyshell.arg.argchecker            import defaultInstanceArgChecker, completeEnvironmentChecker, stringArgChecker, listArgChecker, environmentParameterChecker, contextParameterChecker
from pyshell.utils.parameter           import EnvironmentParameter
from pyshell.utils.constants           import ENVIRONMENT_NAME
from pyshell.utils.coloration          import green, orange, bolt, nocolor, red

ADDONLIST_KEY = "loader_addon"
ADDON_PREFIX  = "pyshell.addons."

### addon ###

#TODO
    #be able to only reload (and only reload, because different parts are linkend and can't be loaded single) a specific part of a module
        #only parameters for example
        #from files or not
                
    #prblm with local addon name and external addon name
        #it is easy to use short name, but it is complicated to merge the use of both short and long name
        #best way is to only use complete name, but it is boring...
    
    #create a method to add/remove on startup

## FUNCTION SECTION ##

def _tryToGetDicoFromParameters(parameters):
    if not parameters.hasParameter(ADDONLIST_KEY, ENVIRONMENT_NAME):
        raise Exception("no addon list defined")

    return parameters.getParameter(ADDONLIST_KEY, ENVIRONMENT_NAME).getValue()

def _tryToGetAddonFromDico(addon_dico, name):
    if name not in addon_dico:
        raise Exception("unknown addon '"+str(name)+"'")

    return addon_dico[name]

def _tryToGetAddonFromParameters(parameters, name):
    return _tryToGetAddonFromDico(_tryToGetDicoFromParameters(parameters), name)

def _tryToImportLoaderFromFile(name):
    try:
        mod = __import__(name,fromlist=["_loaders"])
    except ImportError as ie:
        raise Exception("fail to load addon, reason: "+str(ie))

    if not hasattr(mod, "_loaders"):
        raise Exception("invalid addon, no loader found.  don't forget to register something in the addon")

    return mod._loaders

@shellMethod(addon_dico=environmentParameterChecker(ADDONLIST_KEY),
             execution_context = contextParameterChecker("execution"))
def listAddonFun(addon_dico, execution_context):
    "list the available addons"
    
    addon_dico = addon_dico.getValue()
    
    #define print style
    if execution_context.getSelectedValue() == "shell":
        printok      = green
        printwarning = orange
        printerror   = red
        title        = bolt
    else:
        printok      = nocolor
        printwarning = nocolor
        printerror   = nocolor
        title        = nocolor

    #create addon list from default addon directory
    local_addon = []
    if os.path.exists("./pyshell/addons/"):
        for dirname, dirnames, filenames in os.walk('./pyshell/addons/'):
            for name in filenames:
                if name.endswith(".py") and name != "__init__.py":
                    local_addon.append(ADDON_PREFIX + name[0:-3])
    
    l = []
    for name,loader in addon_dico.items():
        if name in local_addon:
            local_addon.remove(name)
        
        for subLoaderName, (subloader,state, ) in loader.subloader.items():
            if subLoaderName is None:
                subLoaderName = "(default)"

            if state.state in (GlobalLoaderLoadingState.STATE_LOADED, GlobalLoaderLoadingState.STATE_RELOADED,):
                l.append( (name, subLoaderName, printok(state.state), ) )
            elif state.state in (GlobalLoaderLoadingState.STATE_UNLOADED, GlobalLoaderLoadingState.STATE_REGISTERED,):
                l.append( (name, subLoaderName, printwarning(state.state), ) )
            else:
                l.append( (name, subLoaderName, printerror(state.state), ) )

    for name in local_addon:
        l.append( (name,"",printwarning(GlobalLoaderLoadingState.STATE_UNLOADED), ) )

    l.sort()

    if len(l) == 0:
        return [("No addon available",)]
    
    l.insert(0, (title("Addon name"),title("Sub part"),title("State"), ) )
    return l

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             subAddon=stringArgChecker(), 
             parameters=completeEnvironmentChecker())
def unloadAddon(name, parameters, subAddon = None):
    "unload an addon"

    addon = _tryToGetAddonFromParameters(parameters, name)
    addon.unload(parameters, subAddon)
    print(str(name)+" unloaded !")

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             subAddon=stringArgChecker(), 
             parameters=completeEnvironmentChecker())
def reloadAddon(name, parameters, subAddon = None):
    "reload an addon"

    addon = _tryToGetAddonFromParameters(parameters, name)
    addon.reload(parameters, subAddon)
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

    #get addon list
    addon_dico = _tryToGetDicoFromParameters(parameters)

    #import from file
    loader = _tryToImportLoaderFromFile(name)

    #load and register
    addon_dico[name] = loader
    loader.load(parameters, subAddon)

    print(name+" loaded !") 

#TODO register it, need to find an explicit command
@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             subAddon=stringArgChecker(), 
             parameters=completeEnvironmentChecker())
def hardReload(name, parameters, subAddon = None):
    
    #get addon list and addon
    addon_dico = _tryToGetDicoFromParameters(parameters)
    addon      = _tryToGetAddonFromDico(addon_dico, name)

    #unload addon
    addon.unload(parameters, subAddon)

    #load addon from file
    loader = _tryToImportLoaderFromFile(name)

    #load and register
    addon_dico[name] = loader
    loader.load(parameters, subAddon)

    print(name+" hard reloaded !") 

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             addon_dico=environmentParameterChecker(ADDONLIST_KEY))
def getAddonInformation(name, addon_dico, ):
    #TODO improve view

    #if not in the list, try to load it
    addon_dico = addon_dico.getValue()
    if name not in addon_dico:
        addon = _tryToImportLoaderFromFile(name)
    else:
        addon = addon_dico[name]
    
    lines = []
    #extract information from _loaders
        #current name
    lines.append("Addon Name: "+str(name))

    #each sub addon
    lines.append("sub addon list:")
    for subLoaderName, (subloaders, status, ) in addon.subloader.items():
        if subLoaderName is None:
            subLoaderName = "Default"

        #current status
        lines.append("    *"+str(subLoaderName)+": "+status.state)

        #loader in each subbadon
        lines.append("        sub addon part:")
        for name, loader in subloaders.items():
            lines.append("            *"+str(name))

        #TODO error from last load/unload/reload (if error is not none)
    
    return lines

### REGISTER SECTION ###

registerSetTempPrefix( ("addon", ) )
registerCommand( ("list",) ,                  pro=listAddonFun, post=printColumn)
registerCommand( ("load",) ,                  pro=loadAddonFun)
registerCommand( ("unload",) ,                pro=unloadAddon)
registerCommand( ("reload",) ,                pro=reloadAddon)
registerCommand( ("import",) ,                pro=importExternal)
registerCommand( ("info",) ,                  pro=getAddonInformation,post=stringListResultHandler)
registerStopHelpTraversalAt( ("addon",) )

registerSetEnvironment(ADDONLIST_KEY, EnvironmentParameter(value = {"pyshell.addons.addon":sys.modules[__name__]._loaders}, typ=defaultInstanceArgChecker.getArgCheckerInstance(), transient = True, readonly = True, removable = False), noErrorIfKeyExist = False, override = True)
