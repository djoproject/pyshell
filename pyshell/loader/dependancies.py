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

from pyshell.loader.utils     import getAndInitCallerModule, AbstractLoader
from pyshell.loader.exception import RegisterException

#TODO
    #need to have the list of already loaded addons
        #and/or the subaddons part

def _local_getAndInitCallerModule(subLoaderName = None)
    return getAndInitCallerModule(DependanciesLoader.__module__+"."+DependanciesLoader.__name__,DependanciesLoader, 3, subLoaderName)
    
def registerDependOnAddon(name, subLoaderName = None):
    if type(name) != str and type(name) != unicode:
        raise RegisterException("(Loader) registerDependOnAddon, only string or unicode addon name are allowed")

    loader = _local_getAndInitCallerModule(subLoaderName)
    loader.dep.append(name)
    
class DependanciesLoader(AbstractLoader):
    def __init__(self):
        AbstractLoader.__init__(self)
        self.dep = []
        
    def load(self, parameterManager, subLoaderName = None):
        pass #TODO raise if a dependancies is not satisfied
