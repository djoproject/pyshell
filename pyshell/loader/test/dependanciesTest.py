#!/usr/bin/env python -t
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
from pyshell.loader.exception import RegisterException,LoadException
from pyshell.utils.constants  import DEFAULT_PROFILE_NAME, ADDONLIST_KEY, DEFAULT_PROFILE_NAME, STATE_LOADED, STATE_UNLOADED
from pyshell.system.container import ParameterContainer
from pyshell.system.environment import EnvironmentParameter, EnvironmentParameterManager
from pyshell.arg.argchecker import defaultInstanceArgChecker

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
        self.assertRaises(RegisterException,registerDependOnAddon,dependancyName=object(), dependancyProfile = None, profile = None)
        
    def testRegisterDependOnAddon2(self):#registerDependOnAddon with str dependancyName, profile None
        global _loaders
        self.assertFalse("_loaders" in globals())
        registerDependOnAddon(dependancyName="plop", dependancyProfile = None, profile = None)
        self.assertTrue("_loaders" in globals())
        l = _loaders.profileList[DEFAULT_PROFILE_NAME][0][DependanciesLoader.__module__+"."+DependanciesLoader.__name__]
        self.assertIsInstance(l, DependanciesLoader)
        self.assertEqual(l.dep[0], ("plop", None,))
        
    def testRegisterDependOnAddon3(self):#registerDependOnAddon with unicode dependancyName, profile None
        global _loaders
        self.assertFalse("_loaders" in globals())
        registerDependOnAddon(dependancyName=u"plop", dependancyProfile = None, profile = None)
        self.assertTrue("_loaders" in globals())
        l = _loaders.profileList[DEFAULT_PROFILE_NAME][0][DependanciesLoader.__module__+"."+DependanciesLoader.__name__]
        self.assertIsInstance(l, DependanciesLoader)
        self.assertEqual(l.dep[0], (u"plop", None,))
        
    def testRegisterDependOnAddon4(self):#registerDependOnAddon with invalid dependancyProfile, profile None
        self.assertRaises(RegisterException,registerDependOnAddon,dependancyName="plop", dependancyProfile = object(), profile = None)
        
    def testRegisterDependOnAddon5(self):#registerDependOnAddon with str dependancyProfile, profile None
        global _loaders
        self.assertFalse("_loaders" in globals())
        registerDependOnAddon(dependancyName="plop", dependancyProfile = "tutu", profile = None)
        self.assertTrue("_loaders" in globals())
        l = _loaders.profileList[DEFAULT_PROFILE_NAME][0][DependanciesLoader.__module__+"."+DependanciesLoader.__name__]
        self.assertIsInstance(l, DependanciesLoader)
        self.assertEqual(l.dep[0], ("plop", "tutu",))
        
    def testRegisterDependOnAddon6(self):#registerDependOnAddon with unicode dependancyProfile, profile None
        global _loaders
        self.assertFalse("_loaders" in globals())
        registerDependOnAddon(dependancyName=u"plop", dependancyProfile = u"tutu", profile = None)
        self.assertTrue("_loaders" in globals())
        l = _loaders.profileList[DEFAULT_PROFILE_NAME][0][DependanciesLoader.__module__+"."+DependanciesLoader.__name__]
        self.assertIsInstance(l, DependanciesLoader)
        self.assertEqual(l.dep[0], (u"plop", u"tutu",))
        
    
    def testRegisterDependOnAddon7(self):#registerDependOnAddon with invalid dependancyName, profile not None
        self.assertRaises(RegisterException,registerDependOnAddon,dependancyName=object(), dependancyProfile = None, profile = "ahah")
        
    def testRegisterDependOnAddon8(self):#registerDependOnAddon with str dependancyName, profile not None
        global _loaders
        self.assertFalse("_loaders" in globals())
        registerDependOnAddon(dependancyName="plop", dependancyProfile = None, profile = "ahah")
        self.assertTrue("_loaders" in globals())
        l = _loaders.profileList["ahah"][0][DependanciesLoader.__module__+"."+DependanciesLoader.__name__]
        self.assertIsInstance(l, DependanciesLoader)
        self.assertEqual(l.dep[0], ("plop", None,))
        
    def testRegisterDependOnAddon9(self):#registerDependOnAddon with unicode dependancyName, profile not None
        global _loaders
        self.assertFalse("_loaders" in globals())
        registerDependOnAddon(dependancyName=u"plop", dependancyProfile = None, profile = "ahah")
        self.assertTrue("_loaders" in globals())
        l = _loaders.profileList["ahah"][0][DependanciesLoader.__module__+"."+DependanciesLoader.__name__]
        self.assertIsInstance(l, DependanciesLoader)
        self.assertEqual(l.dep[0], (u"plop", None,))
        
    def testRegisterDependOnAddon10(self):#registerDependOnAddon with invalid dependancyProfile, profile not None
        self.assertRaises(RegisterException,registerDependOnAddon,dependancyName="plop", dependancyProfile = object(), profile = "uhuh")
        
    def testRegisterDependOnAddon11(self):#registerDependOnAddon with str dependancyProfile, profile not None
        global _loaders
        self.assertFalse("_loaders" in globals())
        registerDependOnAddon(dependancyName="plop", dependancyProfile = "tutu", profile = "uhuh")
        self.assertTrue("_loaders" in globals())
        l = _loaders.profileList["uhuh"][0][DependanciesLoader.__module__+"."+DependanciesLoader.__name__]
        self.assertIsInstance(l, DependanciesLoader)
        self.assertEqual(l.dep[0], ("plop", "tutu",))
        
    def testRegisterDependOnAddon12(self):#registerDependOnAddon with unicode dependancyProfile, profile not None
        global _loaders
        self.assertFalse("_loaders" in globals())
        registerDependOnAddon(dependancyName=u"plop", dependancyProfile = u"tutu", profile = "uhuh")
        self.assertTrue("_loaders" in globals())
        l = _loaders.profileList["uhuh"][0][DependanciesLoader.__module__+"."+DependanciesLoader.__name__]
        self.assertIsInstance(l, DependanciesLoader)
        self.assertEqual(l.dep[0], (u"plop", u"tutu",))
        
    
    ## DependanciesLoader ##
    
    def testDependanciesLoader_init(self):#__init__
        self.assertTrue(hasattr(DependanciesLoader, "__init__"))
        self.assertTrue(hasattr(DependanciesLoader.__init__, "__call__"))
        self.assertIsInstance(DependanciesLoader(), DependanciesLoader)
        self.assertRaises(TypeError, DependanciesLoader, None)
        
    def testDependanciesLoaderLoad1(self):#load with zero dep
        dl = DependanciesLoader()
        dl.load(None)
        
    def testDependanciesLoaderLoad2(self):#load with dep and ADDONLIST_KEY not in env
        dl = DependanciesLoader()
        dl.dep.append( ("addons.plop", None,) )
        pc = ParameterContainer()
        pc.registerParameterManager("environment", EnvironmentParameterManager())
        self.assertRaises(LoadException, dl.load, pc)
        
    def testDependanciesLoaderLoad3(self):#load with dep, ADDONLIST_KEY defined in env, with dependancyName not satisfied
        dl = DependanciesLoader()
        dl.dep.append( ("addons.plop", None,) )
        pc = ParameterContainer()
        pc.registerParameterManager("environment", EnvironmentParameterManager())
        pc.environment.setParameter(ADDONLIST_KEY,EnvironmentParameter(value = {}, typ=defaultInstanceArgChecker.getArgCheckerInstance()), local_param = False)
        self.assertRaises(LoadException, dl.load, pc)
        
    def testDependanciesLoaderLoad4(self):#load with dep, ADDONLIST_KEY defined in env, with dependancyName satisfied, dependancyProfile not satisfied
        dl = DependanciesLoader()
        dl.dep.append( ("addons.plop", "profile.plap",) )
        pc = ParameterContainer()
        pc.registerParameterManager("environment", EnvironmentParameterManager())
        param = pc.environment.setParameter(ADDONLIST_KEY,EnvironmentParameter(value = {}, typ=defaultInstanceArgChecker.getArgCheckerInstance()), local_param = False)
        param.getValue()["addons.plop"] = GlobalLoader()
        param.getValue()["addons.plop"].profileList[DEFAULT_PROFILE_NAME] = (None, STATE_LOADED,)
        self.assertRaises(LoadException, dl.load, pc)
        
    def testDependanciesLoaderLoad5(self):#load with dep, ADDONLIST_KEY defined in env, with dependancyName satisfied, dependancyProfile satisfied, loaded
        dl = DependanciesLoader()
        dl.dep.append( ("addons.plop", "profile.plap",) )
        pc = ParameterContainer()
        pc.registerParameterManager("environment", EnvironmentParameterManager())
        param = pc.environment.setParameter(ADDONLIST_KEY,EnvironmentParameter(value = {}, typ=defaultInstanceArgChecker.getArgCheckerInstance()), local_param = False)
        param.getValue()["addons.plop"] = GlobalLoader()
        param.getValue()["addons.plop"].profileList["profile.plap"] = (None, STATE_LOADED,)
        dl.load( pc)
        
    def testDependanciesLoaderLoad6(self):#load with dep, ADDONLIST_KEY defined in env, with dependancyName satisfied, dependancyProfile satisfied, not loaded
        dl = DependanciesLoader()
        dl.dep.append( ("addons.plop", "profile.plap",) )
        pc = ParameterContainer()
        pc.registerParameterManager("environment", EnvironmentParameterManager())
        param = pc.environment.setParameter(ADDONLIST_KEY,EnvironmentParameter(value = {}, typ=defaultInstanceArgChecker.getArgCheckerInstance()), local_param = False)
        param.getValue()["addons.plop"] = GlobalLoader()
        param.getValue()["addons.plop"].profileList["profile.plap"] = (None, STATE_UNLOADED,)
        self.assertRaises(LoadException, dl.load, pc)
        
if __name__ == '__main__':
    unittest.main()
