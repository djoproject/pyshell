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
from pyshell.loader.utils import GlobalLoader
from pyshell.loader.dependancies import _local_getAndInitCallerModule, registerDependOnAddon, DependanciesLoader

def loader(profile=None):
    return _local_getAndInitCallerModule(profile)

class DependanciesTest(unittest.TestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        global _loaders
        if "_loaders" in globals():
            del _loaders
            
    ## _local_getAndInitCallerModule ##
    
    def test_local_getAndInitCallerModule1(self):#_local_getAndInitCallerModule with None profile
        global _loaders
        self.assertFalse("_loaders" in globals())
        a = loader()
        self.assertTrue("_loaders" in globals())
        self.assertIsInstance(_loaders, GlobalLoader)
        b = loader()
        self.assertIs(a,b)
        self.assertIsInstance(a,DependanciesLoader)
        
    def test_local_getAndInitCallerModule2(self):#_local_getAndInitCallerModule withouth None profile
        global _loaders
        self.assertFalse("_loaders" in globals())
        a = loader("plop")
        self.assertTrue("_loaders" in globals())
        self.assertIsInstance(_loaders, GlobalLoader)
        b = loader("plop")
        c = loader()
        self.assertIs(a,b)
        self.assertIsNot(a,c)
        self.assertIsInstance(a,DependanciesLoader)
        self.assertIsInstance(c,DependanciesLoader)
    
    ## registerDependOnAddon ##

    def testRegisterDependOnAddon1(self):#registerDependOnAddon with invalid dependancyName, profile None
        pass #TODO
        
    def testRegisterDependOnAddon2(self):#registerDependOnAddon with str dependancyName, profile None
        pass #TODO
        
    def testRegisterDependOnAddon3(self):#registerDependOnAddon with unicode dependancyName, profile None
        pass #TODO
        
    def testRegisterDependOnAddon4(self):#registerDependOnAddon with invalid dependancyProfile, profile None
        pass #TODO
        
    def testRegisterDependOnAddon5(self):#registerDependOnAddon with str dependancyProfile, profile None
        pass #TODO
        
    def testRegisterDependOnAddon6(self):#registerDependOnAddon with unicode dependancyProfile, profile None
        pass #TODO
        
    
    def testRegisterDependOnAddon7(self):#registerDependOnAddon with invalid dependancyName, profile not None
        pass #TODO
        
    def testRegisterDependOnAddon8(self):#registerDependOnAddon with str dependancyName, profile not None
        pass #TODO
        
    def testRegisterDependOnAddon9(self):#registerDependOnAddon with unicode dependancyName, profile not None
        pass #TODO
        
    def testRegisterDependOnAddon10(self):#registerDependOnAddon with invalid dependancyProfile, profile not None
        pass #TODO
        
    def testRegisterDependOnAddon11(self):#registerDependOnAddon with str dependancyProfile, profile not None
        pass #TODO
        
    def testRegisterDependOnAddon12(self):#registerDependOnAddon with unicode dependancyProfile, profile not None
        pass #TODO
        
    
    ## DependanciesLoader ##
    
    def testDependanciesLoader_init(self):#__init__
        pass #TODO
        
    def testDependanciesLoaderLoad1(self):#load with zero dep
        pass #TODO
        
    def testDependanciesLoaderLoad2(self):#load with dep and ADDONLIST_KEY not in env
        pass #TODO
        
    def testDependanciesLoaderLoad3(self):#load with dep, ADDONLIST_KEY defined in env, with dependancyName not satisfied
        pass #TODO
        
    def testDependanciesLoaderLoad4(self):#load with dep, ADDONLIST_KEY defined in env, with dependancyName satisfied, dependancyProfile not satisfied
        pass #TODO
        
    def testDependanciesLoaderLoad5(self):#load with dep, ADDONLIST_KEY defined in env, with dependancyName satisfied, dependancyProfile satisfied
        pass #TODO
        
if __name__ == '__main__':
    unittest.main()
