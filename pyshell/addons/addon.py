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
from pyshell.loader.command import registerSetTempPrefix, registerCommand, registerStopHelpTraversalAt
from pyshell.arg.decorator import shellMethod
import os
from pyshell.simpleProcess.postProcess import stringListResultHandler
from pyshell.arg.argchecker import defaultInstanceArgChecker, completeEnvironmentChecker

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

## FUNCTION SECTION ##

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
             parameters=completeEnvironmentChecker())
def loadAddonFun(name, parameters, subAddon = None):
    "load an external shell addon"
    toLoad = "pyshell.addons."+str(name)

    if subAddon == "":
        subAddon = None

    try:
        mod = __import__(toLoad,fromlist=["_loaders"])
        
        if not hasattr(mod, "_loaders"):
            print("invalid addon, no loader found.  don't forget to register at least one command in the addon")
        
        mod._loaders.load(parameters, subAddon)
        
        """if subAddon not in mod._loaders:
            print("sub addon does not exist in the addon <"+str(name)+">")
        
        mod._loaders[None]._load(levelTries.getValue())"""
        print "   "+toLoad+" loaded !"  
    except ImportError as ie:
        print "import error in <"+str(name)+"> loading : "+str(ie)
    except NameError as ne:
        print "name error in <"+str(name)+"> loading : "+str(ne)

def unloadAddon():
    "unload an addon"
    
    pass #TODO

def reloadAddon():
    "reload an addon"

    pass #TODO

### REGISTER SECTION ###

registerSetTempPrefix( ("addon", ) )
registerCommand( ("list",) ,                  pro=listAddonFun, post=stringListResultHandler)
registerCommand( ("load",) ,                  pro=loadAddonFun)
registerStopHelpTraversalAt( ("addon",) )
