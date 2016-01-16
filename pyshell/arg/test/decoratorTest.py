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
from pyshell.arg.decorator import *
from pyshell.arg.argchecker import *
from pyshell.arg.argfeeder import *

class decoratorTest(unittest.TestCase):
    def test_funAnalyzer(self):
        #init limit case
        self.assertRaises(decoratorException,funAnalyser,None)
        self.assertRaises(decoratorException,funAnalyser,52)
        self.assertRaises(decoratorException,funAnalyser,"plop")
    
        #empty fun
        def toto():
            pass
        
        fa = funAnalyser(toto)
        self.assertTrue(fa is not None)
        self.assertTrue(fa.lendefault == 0)
        self.assertRaises(decoratorException,fa.has_default,"plop")
        self.assertRaises(decoratorException,fa.get_default,"plop")
        self.assertRaises(decoratorException,fa.setCheckerDefault,"plop", "plip")
        
        #non empty fun
        def toto(plop):
            pass
        
        fa = funAnalyser(toto)
        self.assertTrue(fa is not None)
        self.assertTrue(fa.lendefault == 0)
        self.assertTrue(not fa.has_default("plop"))
        self.assertRaises(decoratorException,fa.get_default,"plop")
        self.assertTrue(fa.setCheckerDefault("plop", "plip") == "plip")

        #non empty fun
        def toto(plop = "plap"):
            pass
        
        fa = funAnalyser(toto)
        self.assertTrue(fa is not None)
        self.assertTrue(fa.lendefault == 1)
        self.assertTrue(fa.has_default("plop"))
        self.assertTrue(fa.get_default("plop") == "plap")
        self.assertTrue(fa.setCheckerDefault("plop", ArgChecker()).getDefaultValue() == "plap")

        def toto(a, plop = "plap"):
            pass
        
        fa = funAnalyser(toto)
        self.assertTrue(fa is not None)
        self.assertTrue(fa.lendefault == 1)
        self.assertTrue(fa.has_default("plop"))
        self.assertTrue(fa.get_default("plop") == "plap")
        self.assertTrue(fa.setCheckerDefault("plop", ArgChecker()).getDefaultValue() == "plap")

    
    def test_decorator(self):
        #try to send no argchecker in the list
        exception = False
        try:
            shellMethod(ghaaa = "toto")
        except decoratorException:
            exception = True
        self.assertTrue(exception)
        
        exception = False
        try:
            shellMethod(ghaaa = ArgChecker())
        except decoratorException:
            exception = True
        self.assertTrue(not exception)
        
        #try to set two decorator on the same function
        exception = False
        try:
            @shellMethod(plop=ArgChecker())
            @shellMethod(plop=ArgChecker())
            def toto(plop = "a"):
                pass
        except decoratorException:
            exception = True
        self.assertTrue(exception)
        
        #try to set two key with the same name
            #will be a python syntax error, no need to check
            
        #set arg checker on unexistant param
        exception = False
        try:
            @shellMethod(b=ArgChecker(), a=ArgChecker())
            def toto(a):
                pass
        except decoratorException:
            exception = True
        self.assertTrue(exception)
        
        #TODO try to not bind param without default value
        """exception = False
        try:
            @shellMethod()
            def toto(plop):
                pass
        except decoratorException:
            exception = True
        self.assertTrue(exception)"""
        
        exception = False
        try:
            @shellMethod()
            def toto(plop=5):
                pass
        except decoratorException:
            exception = True
        self.assertTrue(not exception)
        
        #make a test with class and self
        exception = False
        try:
            class plop(object):
                @shellMethod()
                def toto(self):
                    pass
        except decoratorException:
            exception = True
        self.assertTrue(not exception)
    
        #faire des tests qui aboutissent et verifier les donnees generees
        @shellMethod(a=ArgChecker())
        def toto(a,b=5):
            pass
            
        self.assertTrue( isinstance(toto.checker, ArgFeeder))
        self.assertTrue( "a" in toto.checker.argTypeList and isinstance(toto.checker.argTypeList["a"], ArgChecker))
        self.assertTrue( "b" in toto.checker.argTypeList and isinstance(toto.checker.argTypeList["b"], defaultValueChecker))
        k = list(toto.checker.argTypeList.keys())
        self.assertTrue(k[0] == "a" and k[1] == "b")
    
    
        #TODO test with a class meth static
    
    
if __name__ == '__main__':
    unittest.main()
