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

#from pyshell.utils.loader import *
from pyshell.loader.command    import registerSetGlobalPrefix, registerCommand, registerStopHelpTraversalAt, registerSetTempPrefix
from pyshell.loader.utils      import GlobalLoaderLoadingState, DEFAULT_SUBADDON_NAME
from pyshell.arg.decorator     import shellMethod
import os, sys
from pyshell.utils.postProcess import printColumn, listResultHandler
from pyshell.arg.argchecker    import defaultInstanceArgChecker, completeEnvironmentChecker, stringArgChecker, listArgChecker, environmentParameterChecker, contextParameterChecker
from pyshell.utils.constants   import ADDONLIST_KEY, ENVIRONMENT_ADDON_TO_LOAD_KEY
from pyshell.utils.exception   import ListOfException
from pyshell.utils.printing    import notice, formatException, formatGreen, formatOrange, formatRed, formatBolt
from pyshell.system.parameter  import EnvironmentParameter

ADDON_PREFIX  = "pyshell.addons."

## FUNCTION SECTION ##

def _tryToGetDicoFromParameters(parameters):
    param = parameters.environment.getParameter(ADDONLIST_KEY, perfectMatch = True)
    if param is None:
        raise Exception("no addon list defined")

    return param.getValue()

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
        raise Exception("fail to load addon '"+str(name)+"', reason: "+str(ie))

    if not hasattr(mod, "_loaders"):
        raise Exception("invalid addon '"+str(name)+"', no loader found.  don't forget to register something in the addon")

    return mod._loaders

def _formatState(state, printok, printwarning, printerror):
    if state in (GlobalLoaderLoadingState.STATE_LOADED, GlobalLoaderLoadingState.STATE_RELOADED,):
        return printok(state)
    elif state in (GlobalLoaderLoadingState.STATE_UNLOADED, GlobalLoaderLoadingState.STATE_REGISTERED,):
        return printwarning(state)
    else:
        return printerror(state)

@shellMethod(addon_dico=environmentParameterChecker(ADDONLIST_KEY))
def listAddonFun(addon_dico):
    "list the available addons"
    
    addon_dico = addon_dico.getValue()

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
        
        for subAddonName, (subloader,state, ) in loader.subAddons.items():
            l.append( (name, subAddonName, _formatState(state.state, formatGreen, formatOrange, formatRed ), ) )

    for name in local_addon:
        l.append( (name,"",formatOrange(GlobalLoaderLoadingState.STATE_UNLOADED), ) )

    l.sort()

    if len(l) == 0:
        return [("No addon available",)]
    
    l.insert(0, (formatBolt("Addon name"),formatBolt("Sub part"),formatBolt("State"), ) )
    return l

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             subAddon=stringArgChecker(), 
             parameters=completeEnvironmentChecker())
def unloadAddon(name, parameters, subAddon = None):
    "unload an addon"

    addon = _tryToGetAddonFromParameters(parameters, name)
    addon.unload(parameters, subAddon)
    notice(str(name)+" unloaded !")

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             subAddon=stringArgChecker(), 
             parameters=completeEnvironmentChecker())
def reloadAddon(name, parameters, subAddon = None):
    "reload an addon from memory"

    addon = _tryToGetAddonFromParameters(parameters, name)
    addon.reload(parameters, subAddon)
    notice(str(name)+" reloaded !")

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             subAddon=stringArgChecker(), 
             parameters=completeEnvironmentChecker())
def loadAddonFun(name, parameters, subAddon = None):
    "load an addon"

    #get addon list
    addon_dico = _tryToGetDicoFromParameters(parameters)

    #import from file
    loader = _tryToImportLoaderFromFile(name)

    #load and register
    addon_dico[name] = loader
    loader.load(parameters, subAddon)

    notice(name+" loaded !") 

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(), 
             subAddon=stringArgChecker(), 
             parameters=completeEnvironmentChecker())
def hardReload(name, parameters, subAddon = None):
    "reload an addon from file"
    
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

    notice(name+" hard reloaded !") 

@shellMethod(name=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             addon_dico=environmentParameterChecker(ADDONLIST_KEY),
             tabsize=environmentParameterChecker("tabsize"))
def getAddonInformation(name, addon_dico, tabsize, ):
    "print all available information about an addon"

    tab = " "*tabsize.getValue()

    #if not in the list, try to load it
    addon_dico = addon_dico.getValue()
    if name not in addon_dico:
        addon = _tryToImportLoaderFromFile(name)
    else:
        addon = addon_dico[name]
    
    lines = []
    #extract information from _loaders
        #current name
    lines.append(formatBolt("Addon")+" '"+str(name)+"'")

    #each sub addon
    for subAddonName, (subloaders, status, ) in addon.subAddons.items():
        #current status
        lines.append(tab+formatBolt("Sub addon")+" '"+str(subAddonName)+"': "+_formatState(status.state, formatGreen, formatOrange, formatRed ) )

        #loader in each subbadon
        for name, loader in subloaders.items():
            #print information error for each loader
            if loader.lastException is not None:
                if isinstance(loader.lastException, ListOfException):
                    lines.append(tab*2 + formatBolt("Loader")+" '"+str(name) + "' (error count = "+formatRed(str(len(loader.lastException.exceptions)))+")")

                    for exc in loader.lastException.exceptions:
                        lines.append(tab*5 + "*" + formatException(exc))

                else:
                    lines.append(tab*2 + formatBolt("Loader")+" '"+str(name) + "' (error count = "+formatRed("1")+")")
                    lines.append(tab*3 + formatRed(str(loader.lastException)))
                    
                    if hasattr(loader.lastException, "stackTrace") and loader.lastException is not None:
                        lastExceptionSplitted = loader.lastException.split("\n")
                        for string in lastExceptionSplitted:
                            lines.append(tab*3 + string)
            else:
                lines.append(tab*2 + formatBolt("Loader")+" '"+str(name) + "' (error count = 0)")

    return lines

@shellMethod(name =          defaultInstanceArgChecker.getStringArgCheckerInstance(),
             subLoaderName = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             subAddon =      stringArgChecker(), 
             parameters =    completeEnvironmentChecker())
def subLoaderReload(name, subLoaderName, parameters, subAddon = None):
    "reload a sub part of an addon from memory"    
    
    #addon name exist ?
    addon = _tryToGetAddonFromParameters(parameters, name)

    if subAddon is None:
        subAddon = DEFAULT_SUBADDON_NAME

    #subaddon exist ?
    if subAddon not in addon.subAddons:
        raise Exception("Unknown sub addon '"+str(subAddon)+"'")

    loaderDictionnary, status = addon.subAddons[subAddon]

    #subloader exist ?
    if subLoaderName not in loaderDictionnary:
        raise Exception("Unknown sub loader '"+str(subLoaderName)+"'")

    loader = loaderDictionnary[subLoaderName]

    #reload subloader
    try:
        loader.reload(parameters, subAddon)
    except Exception as ex:
        loader.lastException = ex
        loader.lastException.stackTrace = traceback.format_exc()
        raise ex

    notice("sub loader '"+str(subLoaderName)+"' reloaded !")

@shellMethod(addonName          = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             addonListOnStartUp = environmentParameterChecker(ENVIRONMENT_ADDON_TO_LOAD_KEY))
def addOnStartUp(addonName, addonListOnStartUp):
    "add an addon loading on startup"
    
    #package exist ?
    _tryToImportLoaderFromFile(addonName)

    addonList = addonListOnStartUp.getValue()

    if addonName not in addonList:
        addonList.append(addonName)
        addonListOnStartUp.setValue(addonList)

@shellMethod(addonName          = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             addonListOnStartUp = environmentParameterChecker(ENVIRONMENT_ADDON_TO_LOAD_KEY))
def removeOnStartUp(addonName, addonListOnStartUp):
    "remove an addon loading from startup"    
    
    addonList = addonListOnStartUp.getValue()

    if addonName in addonList:
        addonList.remove(addonName)
        addonListOnStartUp.setValue(addonList)
        
@shellMethod(addonListOnStartUp = environmentParameterChecker(ENVIRONMENT_ADDON_TO_LOAD_KEY))
def listOnStartUp(addonListOnStartUp):
    "list addon enabled on startup"

    addons = addonListOnStartUp.getValue()
    
    if len(addons) == 0:
        return ()
        
    r = []
    r.append( (formatBolt("Order"), formatBolt("Addon name"),) )
    for i in range(0,len(addons)):
        r.append( (str(i), str(addons[i]), ) )
    
    return r

@shellMethod(addonName          = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             addonListOnStartUp = environmentParameterChecker(ENVIRONMENT_ADDON_TO_LOAD_KEY))
def downAddonInList(addonName, addonListOnStartUp):
    "reduce the loading priority at startup for an addon"

    addonList = addonListOnStartUp.getValue()
    
    if addonName not in addonList:
        raise Exception("unknown addon name '"+str(addonName)+"'")
        
    position = addonList.index(addonName)
    addonList.remove(addonName)
    addonList.insert(position+1, addonName)
    
@shellMethod(addonName          = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             addonListOnStartUp = environmentParameterChecker(ENVIRONMENT_ADDON_TO_LOAD_KEY))
def upAddonInList(addonName, addonListOnStartUp):
    "increase the loading priority at startup for an addon"

    addonList = addonListOnStartUp.getValue()
    
    if addonName not in addonList:
        raise Exception("unknown addon name '"+str(addonName)+"'")
        
    position = addonList.index(addonName)
    addonList.remove(addonName)
    addonList.insert(max(position-1,0), addonName)
    
@shellMethod(addonName          = defaultInstanceArgChecker.getStringArgCheckerInstance(),
             position           = defaultInstanceArgChecker.getIntegerArgCheckerInstance(),
             addonListOnStartUp = environmentParameterChecker(ENVIRONMENT_ADDON_TO_LOAD_KEY))
def setAddonPositionInList(addonName, position, addonListOnStartUp):
    "set the loading position at startup for an addon"

    addonList = addonListOnStartUp.getValue()
    
    if addonName not in addonList:
        raise Exception("unknown addon name '"+str(addonName)+"'")
        
    addonList.remove(addonName)
    addonList.insert(max(position,0), addonName)

@shellMethod(addonListOnStartUp = environmentParameterChecker(ENVIRONMENT_ADDON_TO_LOAD_KEY),
             params = defaultInstanceArgChecker.getCompleteEnvironmentChecker())
def loadAddonOnStartUp(addonListOnStartUp, params):

    addonList = addonListOnStartUp.getValue()

    errorList = ListOfException()
    for addonName in addonList:
        try:
            loadAddonFun(addonName, params)
        except Exception as ex:
            errorList.addException(ex) #TODO the information about the failing addon is lost here...
            
    if errorList.isThrowable():
        raise errorList

#TODO load all

### REGISTER SECTION ###

registerSetGlobalPrefix( ("addon", ) )
registerCommand( ("list",) ,                  pro=listAddonFun, post=printColumn)
registerCommand( ("unload",) ,                pro=unloadAddon)
registerSetTempPrefix( ("reload",  ) )
registerCommand( ("addon",) ,                 pro=reloadAddon)
registerCommand( ("hard",) ,                  pro=hardReload)
registerCommand( ("subloader",) ,             pro=subLoaderReload)
registerSetTempPrefix( () )
registerStopHelpTraversalAt( ("reload",) )
registerCommand( ("load",) ,                  pro=loadAddonFun)
registerCommand( ("info",) ,                  pro=getAddonInformation,post=listResultHandler)
registerSetTempPrefix( ("onstartup",  ) )
registerCommand( ("add",) ,                   pro=addOnStartUp)
registerCommand( ("remove",) ,                pro=removeOnStartUp)
registerCommand( ("list",) ,                  pro=listOnStartUp, post=printColumn)
registerCommand( ("up",) ,                    pro=upAddonInList)
registerCommand( ("down",) ,                  pro=downAddonInList)
registerCommand( ("index",) ,                 pro=setAddonPositionInList)
registerCommand( ("load",) ,                  pro=loadAddonOnStartUp)
registerStopHelpTraversalAt( ("onstartup",) )
registerStopHelpTraversalAt( () )
