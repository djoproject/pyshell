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
    
    #TODO test limit
    
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
        print self.checker.getValue("43")
        self.assertTrue(0x43 == self.checker.getValue("43"))
        self.assertTrue(0x34 == self.checker.getValue(52, 23))
        self.assertTrue(0x34 == self.checker.getValue(52.33, 23))
        self.assertTrue(0x52 == self.checker.getValue(0x52, 23))
        self.assertTrue(1 == self.checker.getValue(True, 23))
        self.assertTrue(0 == self.checker.getValue(False, 23))
        
    def test_usage(self):
        self.assertTrue(self.checker.getUsage() == "<hex>")
    
    #TODO test limit
    
class tokenArgCheckerTest(unittest.TestCase):
    pass #TODO
    
class booleanArgCheckerTest(unittest.TestCase):
    pass #TODO
    
class floatArgCheckerTest(unittest.TestCase):
    pass #TODO

class listArgCheckerTest(unittest.TestCase):
    pass #TODO

class environmentArgCheckerTest(unittest.TestCase):
    pass #TODO

class defaultArgCheckerTest(unittest.TestCase):
    pass #TODO
    
class argFeederTest(unittest.TestCase):
    pass #TODO

if __name__ == '__main__':
    unittest.main()
