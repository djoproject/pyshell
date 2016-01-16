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
from pyshell.system.settings import Settings, LocalSettings, GlobalSettings
from pyshell.utils.exception import ParameterException

class SettingsTest(unittest.TestCase):
    def setUp(self):
        self.setHash = hash(Settings())

    ## Settings ##
    
    def test_settings1(self):
        s = Settings()
        
        self.assertFalse(s.isReadOnly())
        self.assertTrue(s.isRemovable())
        self.assertTrue(s.isTransient())
        self.assertEqual(s.getProperties(), (("removable", True, ), ("readOnly", False, ), ("transient", True, )) )
        self.assertEqual(hash(s), self.setHash)
    
    def test_settings2(self):
        s = Settings(readOnly = False, removable = False)
        
        self.assertFalse(s.isReadOnly())
        self.assertTrue(s.isRemovable())
        self.assertTrue(s.isTransient())
        self.assertEqual(s.getProperties(), (("removable", True, ), ("readOnly", False, ), ("transient", True, )) )
        self.assertEqual(hash(s), self.setHash)
    
    def test_settings3(self):
        s = Settings(readOnly = True, removable = True)
        
        self.assertFalse(s.isReadOnly())
        self.assertTrue(s.isRemovable())
        self.assertTrue(s.isTransient())
        self.assertEqual(s.getProperties(), (("removable", True, ), ("readOnly", False, ), ("transient", True, )) )
        self.assertEqual(hash(s), self.setHash)
        
    def test_settings4(self):
        s = Settings()
        s.setReadOnly(True)
        self.assertFalse(s.isReadOnly())
        self.assertEqual(hash(s), self.setHash)
        
    def test_settings5(self):
        s = Settings()
        s.setReadOnly(False)
        self.assertFalse(s.isReadOnly())
        self.assertEqual(hash(s), self.setHash)
        
    def test_settings6(self):
        s = Settings()
        s.setTransient(True)
        self.assertTrue(s.isTransient())
        self.assertEqual(hash(s), self.setHash)
        
    def test_settings7(self):
        s = Settings()
        s.setTransient(False)
        self.assertTrue(s.isTransient())
        self.assertEqual(hash(s), self.setHash)
        
    def test_settings8(self):
        s = Settings()
        s.setRemovable(True)
        self.assertTrue(s.isRemovable())
        self.assertEqual(hash(s), self.setHash)
        
    def test_settings9(self):
        s = Settings()
        s.setRemovable(False)
        self.assertTrue(s.isRemovable())
        self.assertEqual(hash(s), self.setHash)
        
    def test_settings10(self):
        s = Settings()
        self.assertIs(s.getLoaderSet(), None)
        s.addLoader("plop")
        self.assertIs(s.getLoaderSet(), None)
        self.assertEqual(hash(s), self.setHash)
    
    def test_settings11(self):
        s = Settings()
        s.mergeFromPreviousSettings(Settings())
        self.assertIs(s.getLoaderSet(), None)
        self.assertEqual(hash(s), self.setHash)
    
    ## LocalSettings ##
    
    def test_localSettings1(self):
        ls = LocalSettings()
        self.assertTrue(ls.isRemovable())
        self.assertFalse(ls.isReadOnly())
        
    def test_localSettings2(self):
        ls = LocalSettings(readOnly = True, removable = True)
        self.assertTrue(ls.isRemovable())
        self.assertTrue(ls.isReadOnly())
        
    def test_localSettings3(self):
        ls = LocalSettings(readOnly = False, removable = False)
        self.assertFalse(ls.isRemovable())
        self.assertFalse(ls.isReadOnly())
        
    def test_localSettings4(self):
        ls = LocalSettings()
        ls.setRemovable(True)
        self.assertTrue(ls.isRemovable())
        
    def test_localSettings5(self):
        ls = LocalSettings()
        ls.setRemovable(False)
        self.assertFalse(ls.isRemovable())
    
    def test_localSettings6(self):
        ls = LocalSettings()
        self.assertRaises(ParameterException, ls.setRemovable,"plop")
        
    def test_localSettings7(self):
        ls = LocalSettings(readOnly = True)
        self.assertRaises(ParameterException, ls.setRemovable,True)
        
    def test_localSettings8(self):
        ls = LocalSettings()
        ls.setReadOnly(True)
        self.assertTrue(ls.isReadOnly())
        
    def test_localSettings9(self):
        ls = LocalSettings()
        ls.setReadOnly(False)
        self.assertFalse(ls.isReadOnly())
    
    def test_localSettings10(self):
        ls = LocalSettings()
        self.assertRaises(ParameterException, ls.setReadOnly,"plop")
        
    def test_localSettings11(self):
        ls = LocalSettings(readOnly = True)
        self.assertRaises(ParameterException, ls._raiseIfReadOnly)
    
    def test_localSettings12(self):
        ls = LocalSettings(readOnly = True)
        self.assertRaises(ParameterException, ls._raiseIfReadOnly, "plop")
    
    def test_localSettings13(self):
        ls = LocalSettings(readOnly = True)
        self.assertRaises(ParameterException, ls._raiseIfReadOnly, "plop", "plip")
    
    ## GlobalSettings ##
    
    def test_globalSettings1(self):
        gs = GlobalSettings()
        self.assertFalse(gs.isReadOnly())
        self.assertTrue(gs.isRemovable())
        self.assertFalse(gs.isTransient())
        
    def test_globalSettings2(self):
        gs = GlobalSettings(readOnly = False, removable = False, transient = False)
        self.assertFalse(gs.isReadOnly())
        self.assertFalse(gs.isRemovable())
        self.assertFalse(gs.isTransient())
        
    def test_globalSettings3(self):
        gs = GlobalSettings(readOnly = True, removable = True, transient = True)
        self.assertTrue(gs.isReadOnly())
        self.assertTrue(gs.isRemovable())
        self.assertTrue(gs.isTransient())
        
    def test_globalSettings4(self):
        gs = GlobalSettings()
        gs.setTransient(True)
        self.assertTrue(gs.isTransient())
        
    def test_globalSettings5(self):
        gs = GlobalSettings()
        gs.setTransient(False)
        self.assertFalse(gs.isTransient())
    
    def test_globalSettings6(self):
        gs = GlobalSettings()
        self.assertRaises(ParameterException, gs.setTransient,"plop")
        
    def test_globalSettings7(self):
        gs = GlobalSettings(readOnly = True)
        self.assertRaises(ParameterException, gs.setTransient,True)
    
    def test_globalSettings8(self):
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")
        self.assertTrue(gs.isEqualToStartingHash("toto"))
        self.assertEqual(gs.getStartingPoint(), ("tutu", "tata",))
    
    def test_globalSettings9(self):
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")
        self.assertRaises(ParameterException, gs.setStartingPoint,"toto", "tutu", "tata")
    
    def test_globalSettings10(self):
        gs = GlobalSettings()
        self.assertIs(gs.getLoaderSet(), None)
        gs.addLoader("plop")
        gs.addLoader("plop")
        gs.addLoader("plop")
        gs.addLoader("plup")
        self.assertEqual(gs.getLoaderSet(), set( ("plop", "plup") ))
        
    def test_globalSettings11(self):#mergeFromPreviousSettings, settings is None
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")
        gs.addLoader("plop")
        gs.addLoader("plup")
        
        gs.mergeFromPreviousSettings(None)
        
        self.assertEqual(gs.getLoaderSet(), set( ("plop", "plup") ))
        self.assertTrue(gs.isEqualToStartingHash("toto"))
        self.assertEqual(gs.getStartingPoint(), ("tutu", "tata",))
        
    def test_globalSettings12(self):#mergeFromPreviousSettings, settings is not an instance of GlobalSettings
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")
        gs.addLoader("plop")
        gs.addLoader("plup")
        
        self.assertRaises(ParameterException, gs.mergeFromPreviousSettings, object())
        
    def test_globalSettings13(self):#mergeFromPreviousSettings, no loader in self, no loader in settings
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")
        
        gs2 = GlobalSettings()
        gs2.setStartingPoint("plop", "plup", "plap")
        
        gs.mergeFromPreviousSettings(gs2)
        
        self.assertIs(gs.getLoaderSet(), None )
        self.assertTrue(gs.isEqualToStartingHash("plop"))
        self.assertEqual(gs.getStartingPoint(), ("plup", "plap",))
        
    def test_globalSettings14(self):#mergeFromPreviousSettings, loader in self, no loader in settings
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")
        gs.addLoader("plop")
        gs.addLoader("plup")
        
        gs2 = GlobalSettings()
        gs2.setStartingPoint("plop", "plup", "plap")
        
        gs.mergeFromPreviousSettings(gs2)
        
        self.assertEqual(gs.getLoaderSet(), set( ("plop", "plup") ))
        self.assertTrue(gs.isEqualToStartingHash("plop"))
        self.assertEqual(gs.getStartingPoint(), ("plup", "plap",))
        
    def test_globalSettings15(self):#mergeFromPreviousSettings, no loader in self, loader in settings
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")
        
        gs2 = GlobalSettings()
        gs2.setStartingPoint("plop", "plup", "plap")
        gs2.addLoader("lolo")
        gs2.addLoader("lulu")
        
        gs.mergeFromPreviousSettings(gs2)
        
        self.assertEqual(gs.getLoaderSet(), set( ("lolo", "lulu") ))
        self.assertTrue(gs.isEqualToStartingHash("plop"))
        self.assertEqual(gs.getStartingPoint(), ("plup", "plap",))
        
    def test_globalSettings16(self):#mergeFromPreviousSettings, loader in self, loader in settings
        gs = GlobalSettings()
        gs.setStartingPoint("toto", "tutu", "tata")
        gs.addLoader("plop")
        gs.addLoader("plup")
        
        gs2 = GlobalSettings()
        gs2.setStartingPoint("plop", "plup", "plap")
        gs2.addLoader("plop")
        gs2.addLoader("lolo")
        gs2.addLoader("lulu")
        
        gs.mergeFromPreviousSettings(gs2)
        
        self.assertEqual(gs.getLoaderSet(), set( ("plop", "plup", "lolo", "lulu") ))
        self.assertTrue(gs.isEqualToStartingHash("plop"))
        self.assertEqual(gs.getStartingPoint(), ("plup", "plap",))

if __name__ == '__main__':
    unittest.main()
