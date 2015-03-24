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
from pyshell.system.variable import VarParameter,VariableParameterManager, VariableLocalSettings, VariableGlobalSettings
from pyshell.system.environment import EnvironmentParameter
from pyshell.utils.exception import ParameterException

class Anything(object):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text

class VariableTest(unittest.TestCase):
    def setUp(self):
        pass
    
    ## settings ##
    
    def test_localSettings1(self):
        vls = VariableLocalSettings()
        
        self.assertTrue(vls.isTransient())
        vls.setTransient(True)
        self.assertTrue(vls.isTransient())
        
    def test_localSettings2(self):
        vls = VariableLocalSettings()
        
        self.assertFalse(vls.isReadOnly())
        vls.setReadOnly(True)
        self.assertFalse(vls.isReadOnly())
        
    def test_localSettings3(self):
        vls = VariableLocalSettings()
        
        self.assertTrue(vls.isRemovable())
        vls.setRemovable(False)
        self.assertTrue(vls.isRemovable())
        
    def test_localSettings4(self):
        vls = VariableLocalSettings()
        self.assertEqual(len(vls.getProperties()), 0)

    ##

    def test_globalSettings1(self):
        vls = VariableGlobalSettings()
        
        self.assertFalse(vls.isTransient())
        vls.setTransient(True)
        self.assertTrue(vls.isTransient())
        
    def test_globalSettings2(self):
        vls = VariableGlobalSettings(transient = True)
        
        self.assertTrue(vls.isTransient())
        vls.setTransient(False)
        self.assertFalse(vls.isTransient())
        
    def test_globalSettings3(self):
        vls = VariableGlobalSettings(transient = False)
        
        self.assertFalse(vls.isTransient())
        vls.setTransient(True)
        self.assertTrue(vls.isTransient())
        
    def test_globalSettings4(self):
        vls = VariableGlobalSettings()
        
        self.assertFalse(vls.isReadOnly())
        vls.setReadOnly(True)
        self.assertFalse(vls.isReadOnly())

    def test_globalSettings5(self):
        vls = VariableGlobalSettings()
        
        self.assertTrue(vls.isRemovable())
        vls.setRemovable(False)
        self.assertTrue(vls.isRemovable())
        
    def test_globalSettings6(self):
        vls = VariableGlobalSettings()
        vls.addLoader("plop")
        self.assertEqual(vls.getLoaderSet(), None)
        
    def test_globalSettings7(self):
        vls = VariableGlobalSettings()
        self.assertEqual(len(vls.getProperties()), 0)
    
    def test_globalSettings8(self):
        vls = VariableGlobalSettings()
        self.assertEqual(vls.getOrigin(), (None, None,) )
        vls.setStartingPoint(hash(vls),"titi","toto")
        self.assertEqual(vls.getOrigin(), ("titi","toto",) )
    
    def test_globalSettings9(self): 
        vls = VariableGlobalSettings()
        self.assertEqual(vls.getLoaderSet(), None)
        vls.addLoader("plop")
        self.assertEqual(vls.getLoaderSet(), None)
        
    def test_globalSettings10(self):
        vls = VariableGlobalSettings()
        vls.addLoader("ahah")
        vls.setStartingPoint(hash(vls),"titi","toto")
        
        vls2 = VariableGlobalSettings()
        vls2.mergeFromPreviousSettings(vls)
        
        self.assertEqual(vls2.getLoaderSet(), None)
        self.assertEqual(vls2.getOrigin(), ("titi","toto",) )
   
    def test_globalSettings11(self):
        vls = VariableGlobalSettings()
        vls.setStartingPoint(hash(self),"titi","toto")
        self.assertTrue(vls.isEqualToStartingHash(hash(self)))
        
    def test_globalSettings12(self):
        vls = VariableGlobalSettings()
        vls.setStartingPoint(hash(self),"titi","toto")
        self.assertRaises(ParameterException, vls.setStartingPoint, hash(self),"titi","toto")
    
    ## manager ##
    
    def test_manager(self):
        self.assertNotEqual(VariableParameterManager(), None)

    def test_addAValidVariable(self):
        manager = VariableParameterManager()
        manager.setParameter("test.var", VarParameter("0x1122ff"))
        self.assertTrue(manager.hasParameter("t.v"))
        param = manager.getParameter("te.va")
        self.assertTrue(isinstance(param, VarParameter))
        self.assertTrue(hasattr(param.getValue(), "__iter__"))
        self.assertEqual(param.getValue(), ["0x1122ff"])

    def test_addNotAllowedParameter(self):
        manager = VariableParameterManager()
        self.assertRaises(ParameterException,manager.setParameter, "test.var", EnvironmentParameter("0x1122ff"))

    ## properties ##

    def test_noProperties(self):
        v = VarParameter("plop")
        self.assertEqual(len(v.settings.getProperties()),0)

    ## parsing ##

    def test_varParsing1(self):#string sans espace
        v = VarParameter("plop")
        self.assertEqual(v.getValue(),["plop"])

    def test_varParsing2(self):#string avec espace
        v = VarParameter("plop plip plap")
        self.assertEqual(v.getValue(),["plop", "plip","plap"])

    def test_varParsing3(self):#anything
        v = VarParameter(Anything("toto"))
        self.assertEqual(v.getValue(),["toto"])

    def test_varParsing4(self):#list de string sans espace
        v = VarParameter( ["plop","plip","plap"])
        self.assertEqual(v.getValue(),["plop", "plip","plap"])

    def test_varParsing5(self):#list de string avec espace
        v = VarParameter( ["pl op","p li pi","pla pa"])
        self.assertEqual(v.getValue(),["pl","op", "p", "li", "pi","pla","pa"])

    def test_varParsing6(self):#list de anything
        v = VarParameter( [Anything("plop"),Anything("plip"),Anything("plap")])
        self.assertEqual(v.getValue(),["plop", "plip","plap"])

    def test_varParsing7(self):#list de list de string sans espace
        v = VarParameter( [ ["plop","plipi"],["plapa"]])
        self.assertEqual(v.getValue(),["plop", "plipi","plapa"])

    def test_varParsing8(self):#list de list de string avec espace
        v = VarParameter( [ ["pl op","p li pi"],["pla pa"]])
        self.assertEqual(v.getValue(),["pl","op", "p", "li", "pi","pla","pa"])

    def test_varParsing9(self):#list de list de anything
        v = VarParameter( [ [Anything("pl op"),Anything("p li pi")],[Anything("pla pa")]])
        self.assertEqual(v.getValue(),["pl","op", "p", "li", "pi","pla","pa"])
        
    ## __str__ __repr__ ##
    
    def test_varStr1(self): 
        v = VarParameter("plop plip plap")
        self.assertEqual(str(v), "plop plip plap")
        
    def test_varStr2(self): 
        v = VarParameter("")
        self.assertEqual(str(v), "")
        
    def test_varRepr1(self): 
        v = VarParameter("plop plip plap")
        self.assertEqual(repr(v), "Variable, value: ['plop', 'plip', 'plap']")
        
    def test_varRepr2(self): 
        v = VarParameter("")
        self.assertEqual(repr(v), "Variable (empty)")
    
    ## enableGlobal, enableLocal ##
    
    def test_enableGlobal(self):
        v = VarParameter("plop plip plap")
        self.assertIsInstance(v.settings, VariableLocalSettings)
        v.enableGlobal()
        self.assertIsInstance(v.settings, VariableGlobalSettings)
        s = v.settings
        v.enableGlobal()
        self.assertIs(v.settings, s)
        
    def test_enableLocal(self):
        v = VarParameter("plop plip plap")
        self.assertIsInstance(v.settings, VariableLocalSettings)
        s = v.settings
        v.enableGlobal()
        self.assertIsInstance(v.settings, VariableGlobalSettings)
        v.enableLocal()
        self.assertIsInstance(v.settings, VariableLocalSettings)
        self.assertIsNot(v.settings, s)
        s = v.settings
        v.enableLocal()
        self.assertIs(v.settings, s)
        
        
if __name__ == '__main__':
    unittest.main()
