#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

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

import unittest

class UtilsTest(unittest.TestCase):
    def setUp(self):
        pass
        
    ## getAndInitCallerModule ##
    
    def test_getAndInitCallerModule1(self):#getAndInitCallerModule, parent module does not have _loader
        pass #TODO
        
    def test_getAndInitCallerModule2(self):#getAndInitCallerModule, parent module has _loader
        pass #TODO
        
    def test_getAndInitCallerModule3(self):#getAndInitCallerModule, parent module has _loader but with a wrong type
        pass #TODO
        
    ## AbstractLoader ##
    
    def test_AbstractLoader1(self):#AbstractLoader, init, exist without arg
        pass #TODO
        
    def test_AbstractLoader2(self):#AbstractLoader, load, exist, test args
        pass #TODO
        
    def test_AbstractLoader3(self):#AbstractLoader, unload, exist, test args
        pass #TODO
        
    def test_AbstractLoader4(self):#AbstractLoader, reload, exist, test args
        pass #TODO
    
    ## GlobalLoader ##
    
    #GlobalLoader, test init, subAddons must be empty
    #getLoader, classDefinition is not an AbstractLoader type
    #getLoader
        #subAddonName is None
        #subAddonName is equal to default
        #subAddonName is not None or equal to default
        
        #subAddonName does not exist
        #subAddonName exists
        
        #
        
if __name__ == '__main__':
    unittest.main()
