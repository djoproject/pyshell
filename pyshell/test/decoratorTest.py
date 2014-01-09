#!/usr/bin/python
# -*- coding: utf-8 -*-

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
        self.assertTrue(fa != None)
        self.assertTrue(fa.lendefault == 0)
        self.assertRaises(decoratorException,fa.has_default,"plop")
        self.assertRaises(decoratorException,fa.get_default,"plop")
        self.assertRaises(decoratorException,fa.setCheckerDefault,"plop", "plip")
        
        #non empty fun
        def toto(plop):
            pass
        
        fa = funAnalyser(toto)
        self.assertTrue(fa != None)
        self.assertTrue(fa.lendefault == 0)
        self.assertTrue(not fa.has_default("plop"))
        self.assertRaises(decoratorException,fa.get_default,"plop")
        self.assertTrue(fa.setCheckerDefault("plop", "plip") == "plip")

        #non empty fun
        def toto(plop = "plap"):
            pass
        
        fa = funAnalyser(toto)
        self.assertTrue(fa != None)
        self.assertTrue(fa.lendefault == 1)
        self.assertTrue(fa.has_default("plop"))
        self.assertTrue(fa.get_default("plop") == "plap")
        self.assertTrue(fa.setCheckerDefault("plop", ArgChecker()).getDefaultValue() == "plap")

        def toto(a, plop = "plap"):
            pass
        
        fa = funAnalyser(toto)
        self.assertTrue(fa != None)
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
        
        #try to not bind param without default value
        exception = False
        try:
            @shellMethod()
            def toto(plop):
                pass
        except decoratorException:
            exception = True
        self.assertTrue(exception)
        
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
        self.assertTrue( toto.checker.argTypeList[0][0] == "a" and isinstance(toto.checker.argTypeList[0][1], ArgChecker))
        self.assertTrue( toto.checker.argTypeList[1][0] == "b" and isinstance(toto.checker.argTypeList[1][1], defaultValueChecker))
    
if __name__ == '__main__':
    unittest.main()
