#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.arg.argchecker import *

class ArgCheckerTest(unittest.TestCase):
    def test_initLimitCase(self):
        self.assertRaises(argInitializationException, ArgChecker, "plop")
        self.assertRaises(argInitializationException, ArgChecker, 1, "plop")
        self.assertRaises(argInitializationException, ArgChecker, -1)
        self.assertRaises(argInitializationException, ArgChecker, 1, -1)
        self.assertRaises(argInitializationException, ArgChecker, 5, 1)
        self.assertTrue(ArgChecker() is not None)
    
    def test_defaultValue(self):
        a = ArgChecker()
        self.assertFalse(a.hasDefaultValue())
        self.assertRaises(argException, a.getDefaultValue)
        
        a.setDefaultValue("plop")
        self.assertTrue(a.hasDefaultValue())
        self.assertTrue(a.getDefaultValue() == "plop")
        
        a.erraseDefaultValue()
        self.assertFalse(a.hasDefaultValue())
        self.assertRaises(argException, a.getDefaultValue)
        
    def test_misc(self):
        a = ArgChecker()
        self.assertTrue(a.getUsage() == "<any>")
        self.assertTrue(a.getValue(28000) == 28000)
    
class stringArgCheckerTest(unittest.TestCase):
    def setUp(self):
        self.checker = stringArgChecker()
        
    def test_check(self):
        self.assertRaises(argException, self.checker.getValue, None, 1)
        self.assertEqual(self.checker.getValue(42),"42")
        self.assertEqual(self.checker.getValue(43.5, 4),"43.5")
        self.assertEqual(self.checker.getValue(True),"True")
        self.assertEqual(self.checker.getValue(False, 9),"False")
    
    def test_get(self):
        self.assertTrue("toto" == self.checker.getValue("toto"))
        self.assertTrue(u"toto" == self.checker.getValue(u"toto", 23))
    
    def test_usage(self):
        self.assertTrue(self.checker.getUsage() == "<string>")
    
class IntegerArgCheckerTest(unittest.TestCase):
    def setUp(self):
        self.checker = IntegerArgChecker()
    
    def test_init(self):
        self.assertRaises(argInitializationException, IntegerArgChecker, "plop")
        self.assertRaises(argInitializationException, IntegerArgChecker, 1, "plop")
        self.assertRaises(argInitializationException, IntegerArgChecker, None, "plop")
        self.assertRaises(argInitializationException, IntegerArgChecker, 5, 1)
        self.assertRaises(argInitializationException, IntegerArgChecker, 5.5, 1.0)
        
        self.assertTrue(IntegerArgChecker(None) is not None)
        self.assertTrue(IntegerArgChecker(1, None) is not None)
        self.assertTrue(IntegerArgChecker(None, 1) is not None)
        
    def test_check(self):
        self.assertRaises(argException, self.checker.getValue, None, 1)
        self.assertRaises(argException, self.checker.getValue, "toto")
        self.assertRaises(argException, self.checker.getValue, u"toto")
        #self.assertRaises(argException, self.checker.getValue, 43.5, 4)
        #self.assertRaises(argException, self.checker.getValue, True)
        #self.assertRaises(argException, self.checker.getValue, False, 9)
    
    def test_get(self):
        self.assertTrue(43 == self.checker.getValue("43"))
        self.assertTrue(52 == self.checker.getValue(52, 23))
        self.assertTrue(0x52 == self.checker.getValue(0x52, 23))
        self.assertTrue(52 == self.checker.getValue(52.33, 23))
        self.assertTrue(1 == self.checker.getValue(True, 23))
        self.assertTrue(0 == self.checker.getValue(False, 23))
        self.assertTrue(0b0101001 == self.checker.getValue(0b0101001, 23))
        
    def test_usage(self):
        self.assertTrue(self.checker.getUsage() == "<int>")
        c = IntegerArgChecker(None, 1)
        self.assertTrue(c.getUsage() == "<int *-1>")
        c = IntegerArgChecker(1)
        self.assertTrue(c.getUsage() == "<int 1-*>")
    
    def test_limit(self):
        self.checker = IntegerArgChecker(5)
        self.assertRaises(argException, self.checker.getValue, 3)
        self.assertRaises(argException, self.checker.getValue, -5)
        self.assertTrue(52 == self.checker.getValue(52, 23))
        
        self.checker = IntegerArgChecker(None,5)
        self.assertRaises(argException, self.checker.getValue, 52)
        self.assertTrue(3 == self.checker.getValue(3, 23))
        self.assertTrue(-5 == self.checker.getValue(-5, 23))
        
        self.checker = IntegerArgChecker(-5,5)
        self.assertRaises(argException, self.checker.getValue, 52)
        self.assertRaises(argException, self.checker.getValue, -52)
        self.assertTrue(3 == self.checker.getValue(3, 23))
        self.assertTrue(-5 == self.checker.getValue(-5, 23))


class LimitedIntegerTest(unittest.TestCase):
    def test_init(self):
        self.assertRaises(argInitializationException, LimitedInteger, 5)
        self.assertRaises(argInitializationException, LimitedInteger, 23)
        
        l = LimitedInteger(8, True)
        self.assertTrue(l.minimum == -0x80)
        self.assertTrue(l.maximum == 0x7f)
        l = LimitedInteger(8)
        self.assertTrue(l.minimum == 0)
        self.assertTrue(l.maximum == 0xff)
        
        l = LimitedInteger(16, True)
        self.assertTrue(l.minimum == -0x8000)
        self.assertTrue(l.maximum == 0x7fff)
        l = LimitedInteger(16)
        self.assertTrue(l.minimum == 0)
        self.assertTrue(l.maximum == 0xffff)
        
        l = LimitedInteger(32, True)
        self.assertTrue(l.minimum == -0x80000000)
        self.assertTrue(l.maximum == 0x7fffffff)
        l = LimitedInteger(32)
        self.assertTrue(l.minimum == 0)
        self.assertTrue(l.maximum == 0xffffffff)
    
class hexaArgCheckerTest(unittest.TestCase):
    def setUp(self):
        self.checker = hexaArgChecker()
        
    def test_check(self):
        self.assertRaises(argException, self.checker.getValue, None, 1)
        self.assertRaises(argException, self.checker.getValue, "toto")
        self.assertRaises(argException, self.checker.getValue, u"toto")
        #self.assertRaises(argException, self.checker.getValue, 43.5, 4)
        #self.assertRaises(argException, self.checker.getValue, True)
        #self.assertRaises(argException, self.checker.getValue, False, 9)
    
    def test_get(self):
        self.assertTrue(0x43 == self.checker.getValue("43"))
        self.assertTrue(0x34 == self.checker.getValue(52, 23))
        self.assertTrue(0x34 == self.checker.getValue(52.33, 23))
        self.assertTrue(0x52 == self.checker.getValue(0x52, 23))
        self.assertTrue(1 == self.checker.getValue(True, 23))
        self.assertTrue(0 == self.checker.getValue(False, 23))
        
    def test_usage(self):
        self.assertTrue(self.checker.getUsage() == "<hex>")

class binaryArgCheckerTest(unittest.TestCase):
    def setUp(self):
        self.checker = binaryArgChecker()
        
    def test_check(self):
        self.assertRaises(argException, self.checker.getValue, None, 1)
        self.assertRaises(argException, self.checker.getValue, "toto")
        self.assertRaises(argException, self.checker.getValue, u"toto")
        #self.assertRaises(argException, self.checker.getValue, 43.5, 4)
        #self.assertRaises(argException, self.checker.getValue, True)
        #self.assertRaises(argException, self.checker.getValue, False, 9)
    
    def test_get(self):
        self.assertTrue(0b10 == self.checker.getValue("10"))
        self.assertTrue(0b10010101 == self.checker.getValue(0b10010101, 23))
        self.assertTrue(52 == self.checker.getValue(52.33, 23))
        #self.assertTrue(0x52 == self.checker.getValue(0x52, 23))
        self.assertTrue(1 == self.checker.getValue(True, 23))
        self.assertTrue(0 == self.checker.getValue(False, 23))
        
    def test_usage(self):
        self.assertTrue(self.checker.getUsage() == "<bin>")
    
class tokenArgCheckerTest(unittest.TestCase):
    def setUp(self):
        self.checker = tokenValueArgChecker({"toto":53, u"plip":"kkk"})
    
    def test_init(self):
        self.assertRaises(argInitializationException, tokenValueArgChecker, "toto")
        self.assertRaises(argInitializationException, tokenValueArgChecker, {"toto":53, 23:"kkk"})
        
    def test_check(self):
        self.assertRaises(argException, self.checker.getValue, None, 1)
        self.assertRaises(argException, self.checker.getValue, 42)
        self.assertRaises(argException, self.checker.getValue, 43.5, 4)
        self.assertRaises(argException, self.checker.getValue, True)
        self.assertRaises(argException, self.checker.getValue, False, 9)
        self.assertRaises(argException, self.checker.getValue, "toti", 9)
        self.assertRaises(argException, self.checker.getValue, "flofi", 9)
    
    def test_get(self):
        self.assertTrue(53 == self.checker.getValue("t"))
        self.assertTrue(53 == self.checker.getValue("to"))
        self.assertTrue(53 == self.checker.getValue("tot"))
        self.assertTrue(53 == self.checker.getValue("toto"))
        self.assertTrue("kkk" == self.checker.getValue("plip"))
        
    def test_ambiguous(self):
        checker = tokenValueArgChecker({"toto":53, "tota":"kkk"})
        self.assertRaises(argException, checker.getValue, "to", 1)
        
    def test_usage(self):
        self.assertTrue(self.checker.getUsage() == "(plip|toto)")

   
class booleanArgCheckerTest(unittest.TestCase):
    def setUp(self):
        self.checker = booleanValueArgChecker()
    
    def test_check(self):
        self.assertRaises(argException, self.checker.getValue, None, 1)
        self.assertRaises(argException, self.checker.getValue, 42)
        self.assertRaises(argException, self.checker.getValue, 43.5, 4)
        #self.assertRaises(argException, self.checker.getValue, True)
        #self.assertRaises(argException, self.checker.getValue, False, 9)
    
    def test_get(self):
        self.assertTrue(True == self.checker.getValue("true"))
        self.assertTrue(False == self.checker.getValue(u"false", 23))
        self.assertTrue(True == self.checker.getValue(True))
        self.assertTrue(False == self.checker.getValue(False, 23))
    
    def test_usage(self):
        self.assertTrue(self.checker.getUsage() == "(false|true)")


class floatArgCheckerTest(unittest.TestCase):
    def setUp(self):
        self.checker = floatTokenArgChecker()
    
    def test_init(self):
        self.assertRaises(argInitializationException, floatTokenArgChecker, "plop")
        self.assertRaises(argInitializationException, floatTokenArgChecker, 1, "plop")
        self.assertRaises(argInitializationException, floatTokenArgChecker, None, "plop")
        self.assertRaises(argInitializationException, floatTokenArgChecker, 5, 1)
        self.assertRaises(argInitializationException, floatTokenArgChecker, 5.5, 1.0)
        
        self.assertTrue(floatTokenArgChecker(None) is not None)
        self.assertTrue(floatTokenArgChecker(1.2, None) is not None)
        self.assertTrue(floatTokenArgChecker(None, 1.5) is not None)
    
    def test_check(self):
        self.assertRaises(argException, self.checker.getValue, None, 1)
        self.assertRaises(argException, self.checker.getValue, "toto")
        self.assertRaises(argException, self.checker.getValue, u"toto")
    
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
    
    def test_limit(self):
        self.checker = floatTokenArgChecker(5)
        self.assertRaises(argException, self.checker.getValue, 3)
        self.assertRaises(argException, self.checker.getValue, -5)
        self.assertTrue(52 == self.checker.getValue(52, 23))
        
        self.checker = floatTokenArgChecker(None,5)
        self.assertRaises(argException, self.checker.getValue, 52)
        self.assertTrue(3 == self.checker.getValue(3, 23))
        self.assertTrue(-5 == self.checker.getValue(-5, 23))
        
        self.checker = floatTokenArgChecker(-5,5)
        self.assertRaises(argException, self.checker.getValue, 52)
        self.assertRaises(argException, self.checker.getValue, -52)
        self.assertTrue(3 == self.checker.getValue(3, 23))
        self.assertTrue(-5 == self.checker.getValue(-5, 23))

class littleEngine(object):
    def __init__(self, d):
        self.d = d
        
    def getEnv(self):
        return self.d

"""class environmentArgCheckerTest(unittest.TestCase):
    def test_init(self):
        #self.assertRaises(argInitializationException,environmentChecker, None)
        self.assertRaises(argInitializationException,environmentChecker, {})

    #TODO test les conditions qui testent la validité du dictionnaire dans getDefault, getValue, ...

    def test_key(self):
        checker = environmentChecker("plop")
        checker.setEngine(littleEngine({"toto":53, u"plip":"kkk"}))
        self.assertRaises(argException,checker.getValue, [])
        
        checker = environmentChecker("toto")
        checker.setEngine(littleEngine({"toto":53, u"plip":"kkk"}))
        self.assertTrue(checker.getValue([]) == 53)
        
        d = {"toto":53, u"plip":"kkk"}
        checker = environmentChecker("plop")
        checker.setEngine(littleEngine(d))
        d["plop"] = 33
        self.assertTrue(checker.getValue([]) == 33)
        
        #arg in the env
        #arg not in the env
        #..."""

"""class environmentDynamicCheckerTest(unittest.TestCase):
    #def test_init(self):
    #    self.assertRaises(argInitializationException,environmentDynamicChecker)

    #TODO test les conditions qui testent la validité du dictionnaire dans getDefault, getValue, ...

    def test_key(self):
        checker = environmentDynamicChecker()
        checker.setEngine(littleEngine({"toto":53, u"plip":"kkk"}))
        self.assertRaises(argException,checker.getValue, [])
        
        checker = environmentDynamicChecker()
        checker.setEngine(littleEngine({"toto":53, u"plip":"kkk"}))
        self.assertTrue(checker.getValue("toto") == 53)
        
        d = {"toto":53, u"plip":"kkk"}
        checker = environmentDynamicChecker()
        checker.setEngine(littleEngine(d))
        d["plop"] = 33
        self.assertTrue(checker.getValue("plop") == 33)"""

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

class listArgCheckerTest(unittest.TestCase):
    def test_init(self):
        self.assertRaises(argInitializationException, listArgChecker, None)
        self.assertRaises(argInitializationException, listArgChecker, listArgChecker(IntegerArgChecker()))
        self.assertRaises(argInitializationException, listArgChecker, 23)
        self.assertRaises(argInitializationException, listArgChecker, defaultValueChecker(42))
        self.assertRaises(argInitializationException, listArgChecker, "plop")
        
        self.assertTrue(listArgChecker(IntegerArgChecker()) is not None)
        self.assertTrue(listArgChecker(stringArgChecker()) is not None)
        
    def test_get(self):
        #check/get, test special case with 1 item
        #c = listArgChecker(IntegerArgChecker(), 1,1)
        #self.assertTrue(c.getValue("53") == 53)
        
        #check/get, test case without a list
        c = listArgChecker(IntegerArgChecker())
        self.assertEqual(c.getValue("53"),[53])
            
        #check/get, test normal case
        self.assertTrue(c.getValue(["1", "2","3"]) == [1,2,3])
        
    def test_default(self):
        #getDefault, test the 3 valid case and the error case
        c = listArgChecker(IntegerArgChecker(),1,23)
        self.assertFalse(c.hasDefaultValue()) 
    
        c = listArgChecker(IntegerArgChecker())
        self.assertTrue(c.hasDefaultValue())
    
        c = listArgChecker(IntegerArgChecker(),1,23)
        c.setDefaultValue([1,2,3])
        self.assertTrue(c.hasDefaultValue())
        
        i = IntegerArgChecker()
        i.setDefaultValue(42)
        c = listArgChecker(i,3,23)
        self.assertTrue(c.hasDefaultValue())
        defv = c.getDefaultValue()
        self.assertTrue(len(defv) == c.minimumSize)
        for v in defv:
            self.assertTrue(v == 42)
    
        #test the completion of the list with default value
        defv = c.getValue(["42"])
        self.assertTrue(len(defv) == c.minimumSize)
        for v in defv:
            self.assertTrue(v == 42)
    
    def test_setDefault(self):
        #setDefaultValue, test special case with value, with empty list, with normal list
        c = listArgChecker(IntegerArgChecker(),1,1)
        
        self.assertIsNone(c.setDefaultValue(["1", "2","3"]))
        self.assertRaises(argException, c.setDefaultValue, [])
        self.assertEqual(c.getValue("53"),[53])
        
        #setDefaultValue, test without special case, without list, with too small list, with bigger list, with list between size
        c = listArgChecker(IntegerArgChecker(),5,7)
        self.assertRaises(argException, c.setDefaultValue, "plop")
        self.assertRaises(argException, c.setDefaultValue, [1,2,3])
        self.assertIsNone(c.setDefaultValue([1,2,3,4,5,6,7,8,9,10]))
        self.assertTrue(len(c.getDefaultValue()) == 7)
        self.assertIsNone(c.setDefaultValue([1,2,3,4,5,6]))
        
    def test_usage(self):
        c = listArgChecker(IntegerArgChecker())
        self.assertTrue(c.getUsage() == "(<int> ... <int>)")
        
        c = listArgChecker(IntegerArgChecker(), None, 5)
        self.assertTrue(c.getUsage() == "(<int>0 ... <int>4)")
        c = listArgChecker(IntegerArgChecker(),None, 1)
        self.assertTrue(c.getUsage() == "(<int>)")
        c = listArgChecker(IntegerArgChecker(),None, 2)
        self.assertTrue(c.getUsage() == "(<int>0 <int>1)")
        
        c = listArgChecker(IntegerArgChecker(),1)
        self.assertTrue(c.getUsage() == "<int>0 (... <int>)")
        c = listArgChecker(IntegerArgChecker(),2)
        self.assertTrue(c.getUsage() == "<int>0 <int>1 (... <int>)")
        c = listArgChecker(IntegerArgChecker(),23)
        self.assertTrue(c.getUsage() == "<int>0 ... <int>22 (... <int>)")
        
        c = listArgChecker(IntegerArgChecker(),1,1)
        self.assertTrue(c.getUsage() == "<int>")

        c = listArgChecker(IntegerArgChecker(),1,2)
        self.assertTrue(c.getUsage() == "<int>0 (<int>1)")
        c = listArgChecker(IntegerArgChecker(),2,2)
        self.assertTrue(c.getUsage() == "<int>0 <int>1")

        c = listArgChecker(IntegerArgChecker(),1, 23)
        self.assertTrue(c.getUsage() == "<int>0 (<int>1 ... <int>22)")
        c = listArgChecker(IntegerArgChecker(),2, 23)
        self.assertTrue(c.getUsage() == "<int>0 <int>1 (<int>2 ... <int>22)")
        c = listArgChecker(IntegerArgChecker(),23, 23)
        self.assertTrue(c.getUsage() == "<int>0 ... <int>22")
        
        c = listArgChecker(IntegerArgChecker(),23, 56)
        self.assertTrue(c.getUsage() == "<int>0 ... <int>22 (<int>23 ... <int>55)")

class argFeederTest(unittest.TestCase):
    pass #TODO

if __name__ == '__main__':
    unittest.main()
