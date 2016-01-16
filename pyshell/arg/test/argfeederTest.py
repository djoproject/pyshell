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
from pyshell.arg.argchecker import *
from pyshell.arg.argfeeder import *

class ArgCheckerTest(unittest.TestCase):
    def test_init(self):
        self.assertRaises(argInitializationException, ArgFeeder, None)
        self.assertRaises(argInitializationException, ArgFeeder, "toto")
        self.assertRaises(argInitializationException, ArgFeeder, 52)
        
        self.assertTrue(ArgFeeder({}) is not None)
        
    def test_checkArgs(self):
        #test a list of 1 arg without limit size
        d          = OrderedDict()
        d["toto1"] = ArgChecker(None, None)
        af = ArgFeeder(d)
        self.assertTrue(af.checkArgs(["1", "2", "3"])["toto1"] == ["1", "2", "3"])

        #test a list of 2 arg, the first one without limit size and the second one need at least one token but without default value
        d          = OrderedDict()
        d["toto1"] = ArgChecker(None, None)
        d["toto2"] = ArgChecker()
        af = ArgFeeder(d)
        self.assertRaises(argException,af.checkArgs, ["1", "2", "3"])
        
        #test a list of 2 arg, the first one without limit size and the second one need at least one token but has a default value
        ac = ArgChecker()
        ac.setDefaultValue("plop")
        
        d          = OrderedDict()
        d["toto1"] = ArgChecker(None, None)
        d["toto2"] = ac
        
        af = ArgFeeder(d)
        r = af.checkArgs(["1", "2", "3"])
        self.assertTrue(r["toto1"] == ["1", "2", "3"])
        self.assertTrue(r["toto2"] == "plop")
        
        #test a list of 3 arg, the first one without limit size and the two last need at least one token
        d          = OrderedDict()
        d["toto1"] = ArgChecker(None, None)
        d["toto2"] = ArgChecker()
        d["toto3"] = ArgChecker()
        af = ArgFeeder(d)
        self.assertRaises(argException,af.checkArgs, ["1", "2", "3"])

        #test a list of 1 arg with a maximum limit size
        d          = OrderedDict()
        d["toto1"] = ArgChecker(None, 5)
        af = ArgFeeder(d)
        self.assertTrue(argException,af.checkArgs(["1", "2", "3"]) == ["1", "2", "3"])
        
        d          = OrderedDict()
        d["toto1"] = ArgChecker(None, 2)
        af = ArgFeeder(d)
        self.assertTrue(argException,af.checkArgs(["1", "2", "3"]) == ["1", "2"])
        
        d          = OrderedDict()
        d["toto1"] = ArgChecker(None, 1)
        af = ArgFeeder(d)
        self.assertTrue(argException,af.checkArgs(["1", "2", "3"]) == ["1"])
        
        d          = OrderedDict()
        d["toto1"] = ArgChecker()
        af = ArgFeeder(d)
        self.assertTrue(argException,af.checkArgs(["1", "2", "3"]) == "1")
        
        #test a list of 2 arg the first one with a maximum limit size and the second one without
        d          = OrderedDict()
        d["toto1"] = ArgChecker(None, 2)
        d["toto2"] = ArgChecker(None, None)
        af = ArgFeeder(d)
        r = af.checkArgs(["1", "2", "3"])
        self.assertTrue(r["toto1"] == ["1", "2"])
        self.assertTrue(r["toto2"] == ["3"])
        
        d          = OrderedDict()
        d["toto1"] = ArgChecker()
        d["toto2"] = ArgChecker(None, None)
        af = ArgFeeder(d)
        r = af.checkArgs(["1", "2", "3"])
        self.assertTrue(r["toto1"] == "1")
        self.assertTrue(r["toto2"] == ["2","3"])
        
    def test_usage(self):
        d          = OrderedDict()
        d["toto1"] = ArgChecker()
        f = ArgFeeder(d)
        self.assertTrue(f.usage() == "toto1:<any>")
    
        #test with only mandatory arg
        d          = OrderedDict()
        d["toto1"] = ArgChecker()
        d["toto2"] = ArgChecker()
        d["toto3"] = ArgChecker()
        f = ArgFeeder(d)
        self.assertTrue(f.usage() == "toto1:<any> toto2:<any> toto3:<any>")
        
        #test with only not mandatory arg
        a = ArgChecker()
        a.setDefaultValue("plop")
        d          = OrderedDict()
        d["toto1"] = a
        d["toto2"] = a
        d["toto3"] = a
        f = ArgFeeder(d)
        self.assertTrue(f.usage() == "[toto1:<any> toto2:<any> toto3:<any>]")
        
        d          = OrderedDict()
        d["toto1"] = a
        f = ArgFeeder(d)
        self.assertTrue(f.usage() == "[toto1:<any>]")
        
        #test with both mandatory and not mandatory arg
        d          = OrderedDict()
        d["toto1"] = ArgChecker()
        d["toto2"] = a
        d["toto3"] = a
        f = ArgFeeder(d)
        self.assertTrue(f.usage() == "toto1:<any> [toto2:<any> toto3:<any>]")
        
        d          = OrderedDict()
        d["toto1"] = ArgChecker()
        d["toto1b"]= ArgChecker()
        d["toto2"] = a
        d["toto3"] = a
        f = ArgFeeder(d)
        self.assertTrue(f.usage() == "toto1:<any> toto1b:<any> [toto2:<any> toto3:<any>]")
        
        d          = OrderedDict()
        d["toto1"] = ArgChecker()
        d["toto2"] = a
        f = ArgFeeder(d)
        self.assertTrue(f.usage() == "toto1:<any> [toto2:<any>]")
        
        d          = OrderedDict()
        d["toto1"] = ArgChecker()
        d["toto1b"]= ArgChecker()
        d["toto2"] = a
        f = ArgFeeder(d)
        self.assertTrue(f.usage() == "toto1:<any> toto1b:<any> [toto2:<any>]")
                
if __name__ == '__main__':
    unittest.main()
