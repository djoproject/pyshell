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
            
## FUNCTION SECTION ##

def createAlias(name, command):
    pass #TODO

def removeAlias(name):
    pass #TODO
    
def addMethodToAlias(name, command):
    pass #TODO
    
def listAlias(name):
    pass #TODO
    
### REGISTER SECTION ###

    #TODO
    
    

