#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.arg.argchecker import *

class stringArgCheckerTest(unittest.TestCase):
    def setUp(self):
        self.checker = stringArgChecker()
        
    def test_check(self):
        self.assertRaises(argException, self.checker.checkValue, None, 1)
        self.assertRaises(argException, self.checker.checkValue, 42)
        self.assertRaises(argException, self.checker.checkValue, 43.5, 4)
        self.assertRaises(argException, self.checker.checkValue, True)
        self.assertRaises(argException, self.checker.checkValue, False, 9)
    
    def test_get(self):
        self.assertTrue("toto" == self.checker.getValue("toto"))
        self.assertTrue(u"toto" == self.checker.getValue(u"toto", 23))
    
    def test_usage(self):
        self.assertTrue(self.checker.getUsage() == "<string>")
    
class IntegerArgCheckerTest(unittest.TestCase):
    def setUp(self):
        self.checker = IntegerArgChecker()
        
    def test_check(self):
        self.assertRaises(argException, self.checker.checkValue, None, 1)
        self.assertRaises(argException, self.checker.checkValue, "toto")
        self.assertRaises(argException, self.checker.checkValue, u"toto")
        #self.assertRaises(argException, self.checker.checkValue, 43.5, 4)
        #self.assertRaises(argException, self.checker.checkValue, True)
        #self.assertRaises(argException, self.checker.checkValue, False, 9)
    
    def test_get(self):
        self.assertTrue(43 == self.checker.getValue("43"))
        self.assertTrue(52 == self.checker.getValue(52, 23))
        self.assertTrue(0x52 == self.checker.getValue(0x52, 23))
        self.assertTrue(52 == self.checker.getValue(52.33, 23))
        self.assertTrue(1 == self.checker.getValue(True, 23))
        self.assertTrue(0 == self.checker.getValue(False, 23))
        
    def test_usage(self):
        self.assertTrue(self.checker.getUsage() == "<int>")
    
    def test_limit(self):
        self.checker = IntegerArgChecker(5)
        self.assertRaises(argException, self.checker.checkValue, 3)
        self.assertRaises(argException, self.checker.checkValue, -5)
        self.assertTrue(52 == self.checker.getValue(52, 23))
        
        self.checker = IntegerArgChecker(None,5)
        self.assertRaises(argException, self.checker.checkValue, 52)
        self.assertTrue(3 == self.checker.getValue(3, 23))
        self.assertTrue(-5 == self.checker.getValue(-5, 23))
        
        self.checker = IntegerArgChecker(-5,5)
        self.assertRaises(argException, self.checker.checkValue, 52)
        self.assertRaises(argException, self.checker.checkValue, -52)
        self.assertTrue(3 == self.checker.getValue(3, 23))
        self.assertTrue(-5 == self.checker.getValue(-5, 23))
        
    
class hexaArgCheckerTest(unittest.TestCase):
    def setUp(self):
        self.checker = hexaArgChecker()
        
    def test_check(self):
        self.assertRaises(argException, self.checker.checkValue, None, 1)
        self.assertRaises(argException, self.checker.checkValue, "toto")
        self.assertRaises(argException, self.checker.checkValue, u"toto")
        #self.assertRaises(argException, self.checker.checkValue, 43.5, 4)
        #self.assertRaises(argException, self.checker.checkValue, True)
        #self.assertRaises(argException, self.checker.checkValue, False, 9)
    
    def test_get(self):
        self.assertTrue(0x43 == self.checker.getValue("43"))
        self.assertTrue(0x34 == self.checker.getValue(52, 23))
        self.assertTrue(0x34 == self.checker.getValue(52.33, 23))
        self.assertTrue(0x52 == self.checker.getValue(0x52, 23))
        self.assertTrue(1 == self.checker.getValue(True, 23))
        self.assertTrue(0 == self.checker.getValue(False, 23))
        
    def test_usage(self):
        self.assertTrue(self.checker.getUsage() == "<hex>")

    
class tokenArgCheckerTest(unittest.TestCase):
    def setUp(self):
        self.checker = tokenValueArgChecker({"toto":53, u"plip":"kkk"})
    
    def test_check(self):
        self.assertRaises(argException, self.checker.checkValue, None, 1)
        self.assertRaises(argException, self.checker.checkValue, 42)
        self.assertRaises(argException, self.checker.checkValue, 43.5, 4)
        self.assertRaises(argException, self.checker.checkValue, True)
        self.assertRaises(argException, self.checker.checkValue, False, 9)
        self.assertRaises(argException, self.checker.checkValue, "toti", 9)
        self.assertRaises(argException, self.checker.checkValue, "flofi", 9)
    
    def test_get(self):
        self.assertTrue(53 == self.checker.getValue("t"))
        self.assertTrue(53 == self.checker.getValue("to"))
        self.assertTrue(53 == self.checker.getValue("tot"))
        self.assertTrue(53 == self.checker.getValue("toto"))
        self.assertTrue("kkk" == self.checker.getValue("plip"))
    
class booleanArgCheckerTest(unittest.TestCase):
    def setUp(self):
        self.checker = booleanValueArgChecker()
    
    def test_check(self):
        self.assertRaises(argException, self.checker.checkValue, None, 1)
        self.assertRaises(argException, self.checker.checkValue, 42)
        self.assertRaises(argException, self.checker.checkValue, 43.5, 4)
        self.assertRaises(argException, self.checker.checkValue, True)
        self.assertRaises(argException, self.checker.checkValue, False, 9)
    
    def test_get(self):
        self.assertTrue(True == self.checker.getValue("true"))
        self.assertTrue(False == self.checker.getValue(u"false", 23))
    
    def test_usage(self):
        self.assertTrue(self.checker.getUsage() == "(false|true)")
    
class floatArgCheckerTest(unittest.TestCase):
    def setUp(self):
        self.checker = floatTokenArgChecker()
    
    def test_check(self):
        self.assertRaises(argException, self.checker.checkValue, None, 1)
        self.assertRaises(argException, self.checker.checkValue, "toto")
        self.assertRaises(argException, self.checker.checkValue, u"toto")
    
    def test_get(self):
        self.assertTrue(43 == self.checker.getValue("43"))
        self.assertTrue(52 == self.checker.getValue(52, 23))
        self.assertTrue(0x52 == self.checker.getValue(0x52, 23))
        self.assertTrue(1 == self.checker.getValue(True, 23))
        self.assertTrue(0 == self.checker.getValue(False, 23))
        self.assertTrue(43.542 == self.checker.getValue("43.542"))
        self.assertTrue(52.542 == self.checker.getValue(52.542, 23))
        self.assertTrue(0x52 == self.checker.getValue(0x52, 23))
        self.assertTrue(52.542 == self.checker.getValue(52.542, 23))
    def test_usage(self):
        self.assertTrue(self.checker.getUsage() == "<float>")
    

class listArgCheckerTest(unittest.TestCase):
    pass #TODO

class environmentArgCheckerTest(unittest.TestCase):
    pass #TODO

class defaultArgCheckerTest(unittest.TestCase):
    def setUp(self):
        self.checker = defaultValueChecker("53")
        
    def test_get(self):
        self.assertTrue("53" == self.checker.getValue("43"))
        self.assertTrue("53" == self.checker.getValue(52, 23))
        self.assertTrue("53" == self.checker.getValue(0x52, 23))
        self.assertTrue("53" == self.checker.getValue(52.33, 23))
        self.assertTrue("53" == self.checker.getValue(True, 23))
        self.assertTrue("53" == self.checker.getValue(False, 23))
        
    def test_usage(self):
        self.assertTrue(self.checker.getUsage() == "<any>")
    
class argFeederTest(unittest.TestCase):
    pass #TODO

if __name__ == '__main__':
    unittest.main()
