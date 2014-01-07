#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.arg.argchecker import *
from pyshell.arg.argfeeder import *

class ArgCheckerTest(unittest.TestCase):
    def test_init(self):
        self.assertRaises(argInitializationException, ArgFeeder, None)
        self.assertRaises(argInitializationException, ArgFeeder, "toto")
        self.assertRaises(argInitializationException, ArgFeeder, 52)
        
        self.assertTrue(ArgFeeder([]) != None)
        
    def test_checkArgs(self):
        #test a list of 1 arg without limit size
        af = ArgFeeder([("toto1",ArgChecker(None, None),)])
        self.assertTrue(af.checkArgs(["1", "2", "3"])["toto1"] == ["1", "2", "3"])

        #test a list of 2 arg, the first one without limit size and the second one need at least one token but without default value
        af = ArgFeeder([("toto1",ArgChecker(None, None),), ("toto2",ArgChecker(),)])
        self.assertRaises(argException,af.checkArgs, ["1", "2", "3"])
        
        #test a list of 2 arg, the first one without limit size and the second one need at least one token but has a default value
        ac = ArgChecker()
        ac.setDefaultValue("plop")
        af = ArgFeeder([("toto1",ArgChecker(None, None),), ("toto2",ac,)])
        r = af.checkArgs(["1", "2", "3"])
        self.assertTrue(r["toto1"] == ["1", "2", "3"])
        self.assertTrue(r["toto2"] == "plop")
        
        #test a list of 3 arg, the first one without limit size and the two last need at least one token
        af = ArgFeeder([("toto1",ArgChecker(None, None),), ("toto2",ArgChecker(),), ("toto3",ArgChecker(),)])
        self.assertRaises(argException,af.checkArgs, ["1", "2", "3"])

        #test a list of 1 arg with a maximum limit size
        af = ArgFeeder([("toto1",ArgChecker(None, 5),),])
        self.assertTrue(argException,af.checkArgs(["1", "2", "3"]) == ["1", "2", "3"])
        
        af = ArgFeeder([("toto1",ArgChecker(None, 2),),])
        self.assertTrue(argException,af.checkArgs(["1", "2", "3"]) == ["1", "2"])
        
        #TODO test a list of 2 arg the first one with a maximum limit size and the second one without
        #TODO make the two previous test with arg of fixed size 1, and with variable size
    
        #TODO test also with too many string token
            #not possible when there is a checker without limit
    
        pass
        
    def test_usage(self):
        f = ArgFeeder([("toto1",ArgChecker(),)])
        self.assertTrue(f.usage() == "toto1:<any>")
    
        #test with only mandatory arg
        f = ArgFeeder([("toto1",ArgChecker(),) , ("toto2",ArgChecker(),), ("toto3",ArgChecker(),)])
        self.assertTrue(f.usage() == "toto1:<any> toto2:<any> toto3:<any>")
        
        #test with only not mandatory arg
        a = ArgChecker()
        a.setDefaultValue("plop")
        f = ArgFeeder([("toto1",a,) , ("toto2",a,), ("toto3",a,)])
        self.assertTrue(f.usage() == "[toto1:<any> toto2:<any> toto3:<any>]")
        
        f = ArgFeeder([("toto1",a,)])
        self.assertTrue(f.usage() == "[toto1:<any>]")
        
        #test with both mandatory and not mandatory arg
        f = ArgFeeder([("toto1",ArgChecker(),) , ("toto2",a,), ("toto3",a,)])
        self.assertTrue(f.usage() == "toto1:<any> [toto2:<any> toto3:<any>]")
        
        f = ArgFeeder([("toto1",ArgChecker(),), ("toto1b",ArgChecker(),) , ("toto2",a,), ("toto3",a,)])
        self.assertTrue(f.usage() == "toto1:<any> toto1b:<any> [toto2:<any> toto3:<any>]")
        
        f = ArgFeeder([("toto1",ArgChecker(),) , ("toto2",a,)])
        self.assertTrue(f.usage() == "toto1:<any> [toto2:<any>]")
        
        f = ArgFeeder([("toto1",ArgChecker(),), ("toto1b",ArgChecker(),) , ("toto2",a,)])
        self.assertTrue(f.usage() == "toto1:<any> toto1b:<any> [toto2:<any>]")
                
if __name__ == '__main__':
    unittest.main()
