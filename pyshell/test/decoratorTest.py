#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.arg.decorator import *
from pyshell.arg.argchecker import *

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
        pass #TODO
        #try to send no argchecker in the list
    
        
        #try to set two decorator on the same function
        #try to set two key with the same name
        #set arg checker on unexistant param
        #try to not bind param without default value (?)
        
        
    
if __name__ == '__main__':
    unittest.main()
