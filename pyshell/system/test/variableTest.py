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
from pyshell.system.variable import VarParameter,VariableParameterManager
from pyshell.system.environment import EnvironmentParameter

class Anything(object):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text

class VariableTest(unittest.TestCase):
    def setUp(self):
        pass

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
        self.assertRaises(Exception,manager.setParameter, "test.var", EnvironmentParameter("0x1122ff"))

    def test_noProperties(self):
        v = VarParameter("plop")
        self.assertEqual(len(v.getProperties()),0)

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
        
if __name__ == '__main__':
    unittest.main()
