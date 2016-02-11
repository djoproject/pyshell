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
from pyshell.loader.command import _local_getAndInitCallerModule, _check_boolean, registerSetGlobalPrefix, registerSetTempPrefix, registerResetTempPrefix, registerAnInstanciatedCommand, registerCommand, registerAndCreateEmptyMultiCommand, registerStopHelpTraversalAt, CommandLoader
from pyshell.loader.utils import GlobalLoader
from pyshell.utils.exception  import ListOfException
from pyshell.loader.exception import LoadException, RegisterException
from pyshell.command.command  import MultiCommand, UniCommand
from pyshell.utils.constants  import DEFAULT_PROFILE_NAME, ENVIRONMENT_ATTRIBUTE_NAME, ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.system.container import ParameterContainer
from pyshell.system.environment import EnvironmentParameterManager, EnvironmentParameter
from pyshell.system.settings  import GlobalSettings
from tries import multiLevelTries
from pyshell.arg.argchecker     import defaultInstanceArgChecker

def loader(profile=None):
    return _local_getAndInitCallerModule(profile)

def prePro():
    pass

def proPro():
    pass

def postPro():
    pass

class RegisterCommandTest(unittest.TestCase):
    def setUp(self):
        pass
        
    def tearDown(self):
        global _loaders
        if "_loaders" in globals():
            del _loaders
    
    def preTest(self):
        self.assertFalse("_loaders" in globals())
        
    def postTest(self, profile):
        self.assertTrue("_loaders" in globals())
        self.assertIsInstance(_loaders, GlobalLoader)
        self.assertTrue(hasattr(_loaders, "profileList"))
        self.assertIs(type(_loaders.profileList), dict)
        self.assertIn(profile, _loaders.profileList)
        
        profileTuple = _loaders.profileList[profile]
        self.assertIs(type(profileTuple), tuple)
        self.assertEqual(len(profileTuple), 2)
        
        profileLoaders = profileTuple[0]
        loaderKey = CommandLoader.__module__+"."+CommandLoader.__name__
        self.assertIs(type(profileLoaders), dict)
        self.assertIn(loaderKey, profileLoaders)
        
        l = profileLoaders[loaderKey]
        self.assertIsInstance(l, CommandLoader)
        return l
    
    ## _local_getAndInitCallerModule ##
    
    def test_local_getAndInitCallerModule1(self):#_local_getAndInitCallerModule with None profile
        global _loaders
        self.assertFalse("_loaders" in globals())
        a = loader()
        self.assertTrue("_loaders" in globals())
        self.assertIsInstance(_loaders, GlobalLoader)
        b = loader()
        self.assertIs(a,b)
        self.assertIsInstance(a,CommandLoader)
        
    def test_local_getAndInitCallerModule2(self):#_local_getAndInitCallerModule withouth None profile
        global _loaders
        self.assertFalse("_loaders" in globals())
        a = loader("plop")
        self.assertTrue("_loaders" in globals())
        self.assertIsInstance(_loaders, GlobalLoader)
        b = loader("plop")
        c = loader()
        self.assertIs(a,b)
        self.assertIsNot(a,c)
        self.assertIsInstance(a,CommandLoader)
        self.assertIsInstance(c,CommandLoader)
        
    def test_check_boolean(self): #with valid bool
        _check_boolean(True, "plop", "meth")
        _check_boolean(False, "plop", "meth")

    def test_check_boolean(self): #with unvalid bool
        self.assertRaises(RegisterException, _check_boolean, object(), "plop", "meth")

    ## registering ##
    
    def test_registerSetGlobalPrefix1(self):#registerSetGlobalPrefix with invalid keyList, with profile None
        self.assertRaises(RegisterException, registerSetGlobalPrefix, object(), None)

    def test_registerSetGlobalPrefix2(self):#registerSetGlobalPrefix with invalid keyList, with profile not None
        self.assertRaises(RegisterException, registerSetGlobalPrefix, object(), "None")
        
    def test_registerSetGlobalPrefix3(self):#registerSetGlobalPrefix with valid keyList, with profile None
        self.preTest()
        registerSetGlobalPrefix(("plop", "plip",), None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l, "prefix"))
        self.assertEqual(l.prefix, ("plop", "plip",))
        
    def test_registerSetGlobalPrefix4(self):#registerSetGlobalPrefix with valid keyList, with profile not None
        self.preTest()
        registerSetGlobalPrefix(("plop", "plip",), "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l, "prefix"))
        self.assertEqual(l.prefix, ("plop", "plip",))
        
    
    def test_registerSetTempPrefix1(self):#registerSetTempPrefix with invalid keyList, with profile None
        self.preTest()
        self.assertRaises(RegisterException, registerSetTempPrefix,keyList=object(), profile = None)
        self.assertFalse("_loaders" in globals())
        
    def test_registerSetTempPrefix2(self):#registerSetTempPrefix with invalid keyList, with profile not None
        self.preTest()
        self.assertRaises(RegisterException, registerSetTempPrefix,keyList=object(), profile = "None")
        self.assertFalse("_loaders" in globals())
        
    def test_registerSetTempPrefix3(self):#registerSetTempPrefix with valid keyList, with profile None
        self.preTest()
        registerSetTempPrefix(keyList=("tutu","toto",), profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l,"TempPrefix"))
        self.assertEqual(l.TempPrefix, ("tutu","toto",))
        
    def test_registerSetTempPrefix4(self):#registerSetTempPrefix with valid keyList, with profile not None
        self.preTest()
        registerSetTempPrefix(keyList=("tutu","toto",), profile = "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l,"TempPrefix"))
        self.assertEqual(l.TempPrefix, ("tutu","toto",))
        
    
    def test_registerResetTempPrefix1(self):#registerResetTempPrefix with temp prefix set, with profile None
        self.preTest()
        registerSetTempPrefix(keyList=("tutu","toto",), profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l,"TempPrefix"))
        self.assertEqual(l.TempPrefix, ("tutu","toto",))
        registerResetTempPrefix(profile = None)
        self.assertIs(l.TempPrefix, None)
        
    def test_registerResetTempPrefix2(self):#registerResetTempPrefix with temp prefix set, with profile not None
        self.preTest()
        registerSetTempPrefix(keyList=("tutu","toto",), profile = "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l,"TempPrefix"))
        self.assertEqual(l.TempPrefix, ("tutu","toto",))
        registerResetTempPrefix(profile = "None")
        self.assertIs(l.TempPrefix, None)
        
    def test_registerResetTempPrefix3(self):#registerResetTempPrefix without temp prefix set, with profile None
        self.preTest()
        registerResetTempPrefix(profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l,"TempPrefix"))
        self.assertIs(l.TempPrefix, None)
        
    def test_registerResetTempPrefix4(self):#registerResetTempPrefix without temp prefix set, with profile not None
        self.preTest()
        registerResetTempPrefix(profile = "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l,"TempPrefix"))
        self.assertIs(l.TempPrefix, None)
        
    
    def test_registerAnInstanciatedCommand1(self):#registerAnInstanciatedCommand with invalid command type, with profile None
        self.preTest()
        self.assertRaises(RegisterException, registerAnInstanciatedCommand,keyList=("plop",), cmd="tutu", raiseIfExist=True, override=False, profile = None)
        self.assertFalse("_loaders" in globals())
        
    def test_registerAnInstanciatedCommand2(self):#registerAnInstanciatedCommand with invalid command type, with profile not None
        self.preTest()
        self.assertRaises(RegisterException, registerAnInstanciatedCommand,keyList=("plop",), cmd="tutu", raiseIfExist=True, override=False, profile = "None")
        self.assertFalse("_loaders" in globals())
        
    def test_registerAnInstanciatedCommand3(self):#registerAnInstanciatedCommand with invalid keyList, with profile None
        self.preTest()
        self.assertRaises(RegisterException, registerAnInstanciatedCommand,keyList=object(), cmd=MultiCommand(), raiseIfExist=True, override=False, profile = None)
        self.assertFalse("_loaders" in globals())
        
    def test_registerAnInstanciatedCommand4(self):#registerAnInstanciatedCommand with invalid keyList, with profile not None
        self.preTest()
        self.assertRaises(RegisterException, registerAnInstanciatedCommand,keyList=object(), cmd=MultiCommand(), raiseIfExist=True, override=False, profile = "None")
        self.assertFalse("_loaders" in globals())
        
    def test_registerAnInstanciatedCommand5(self):#registerAnInstanciatedCommand with valid args, with profile None
        self.preTest()
        key = ("plop", "plip",)
        mc = MultiCommand()
        registerAnInstanciatedCommand(keyList=key, cmd=mc, raiseIfExist=True, override=False, profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (mc, True, False,))
        
    def test_registerAnInstanciatedCommand6(self):#registerAnInstanciatedCommand with valid args, with profile not None
        self.preTest()
        key = ("plop", "plip",)
        mc = MultiCommand()
        registerAnInstanciatedCommand(keyList=key, cmd=mc, raiseIfExist=True, override=False, profile = "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (mc, True, False,))
        
    def test_registerAnInstanciatedCommand7(self):#registerAnInstanciatedCommand with valid args and registerSetTempPrefix, with profile None
        self.preTest()
        key = ("plup","plop", "plip",)
        mc = MultiCommand()
        registerSetTempPrefix( ("plup",) )
        registerAnInstanciatedCommand(keyList=("plop", "plip",), cmd=mc, raiseIfExist=True, override=False, profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (mc, True, False,))
        
    def test_registerAnInstanciatedCommand8(self):#registerAnInstanciatedCommand with valid args and registerSetTempPrefix, with profile not None
        self.preTest()
        key = ("plup","plop", "plip",)
        mc = MultiCommand()
        registerSetTempPrefix( ("plup",) , profile = "None")
        registerAnInstanciatedCommand(keyList=("plop", "plip",), cmd=mc, raiseIfExist=True, override=False, profile = "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (mc, True, False,))
        
    def test_registerAnInstanciatedCommand9(self):#registerAnInstanciatedCommand with valid args and registerSetGlobalPrefix, with profile None
        self.preTest()
        key = ("plop", "plip",)
        mc = MultiCommand()
        registerSetGlobalPrefix( ("plup",) , profile = None)
        registerAnInstanciatedCommand(keyList=key, cmd=mc, raiseIfExist=True, override=False, profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (mc, True, False,))
        self.assertTrue(hasattr(l, "prefix"))
        self.assertEqual(l.prefix, ("plup",))
        
    def test_registerAnInstanciatedCommand10(self):#registerAnInstanciatedCommand with valid args and registerSetGlobalPrefix, with profile not None
        self.preTest()
        key = ("plop", "plip",)
        mc = MultiCommand()
        registerSetGlobalPrefix( ("plup",) , profile = "None")
        registerAnInstanciatedCommand(keyList=key, cmd=mc, raiseIfExist=True, override=False, profile = "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (mc, True, False,))
        self.assertTrue(hasattr(l, "prefix"))
        self.assertEqual(l.prefix, ("plup",))
        
    def test_registerAnInstanciatedCommand11(self):#registerAnInstanciatedCommand test raiseIfExist/override valid, with profile None
        self.preTest()
        key = ("plop", "plip",)
        mc = MultiCommand()
        registerAnInstanciatedCommand(keyList=key, cmd=mc, raiseIfExist=True, override=True, profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (mc, True, True,))
        
    def test_registerAnInstanciatedCommand12(self):#registerAnInstanciatedCommand test raiseIfExist/override valid, with profile not None
        self.preTest()
        key = ("plop", "plip",)
        mc = MultiCommand()
        registerAnInstanciatedCommand(keyList=key, cmd=mc, raiseIfExist=False, override=False, profile = "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (mc, False, False,))
        
    def test_registerAnInstanciatedCommand13(self):#registerAnInstanciatedCommand test raiseIfExist/override not valid, with profile None
        self.preTest()
        self.assertRaises(RegisterException,registerAnInstanciatedCommand,keyList=("plop", "plip",), cmd=MultiCommand(), raiseIfExist=object(), override=False, profile = None)
        self.assertFalse("_loaders" in globals())
        
    def test_registerAnInstanciatedCommand14(self):#registerAnInstanciatedCommand test raiseIfExist/override not valid, with profile not None
        self.preTest()
        self.assertRaises(RegisterException,registerAnInstanciatedCommand,keyList=("plop", "plip",), cmd=MultiCommand(), raiseIfExist=False, override=object(), profile = "None")
        self.assertFalse("_loaders" in globals())
        

    def test_registerCommand1(self):#registerCommand with invalid keyList, with profile None
        self.preTest()
        self.assertRaises(RegisterException, registerCommand,keyList=object(), pre=None,pro=proPro,post=None, raiseIfExist=True, override=False, profile = None)
        self.assertFalse("_loaders" in globals())
        
    def test_registerCommand2(self):#registerCommand with invalid keyList, with profile not None
        self.preTest()
        self.assertRaises(RegisterException, registerCommand,keyList=object(), pre=None,pro=proPro,post=None, raiseIfExist=True, override=False, profile = "None")
        self.assertFalse("_loaders" in globals())
                
    def test_registerCommand5(self):#registerCommand test pre/pro/post, with profile None
        self.preTest()
        key = ("plip",)
        c = registerCommand(keyList=key, pre=prePro,pro=proPro,post=postPro, raiseIfExist=True, override=False, profile = None)
        self.postTest(DEFAULT_PROFILE_NAME)

        self.assertIsInstance(c, MultiCommand)
        self.assertEqual(len(c), 1)
        co,a,e = c[0]

        self.assertIs(co.preProcess, prePro)
        self.assertIs(co.process, proPro)
        self.assertIs(co.postProcess, postPro)
        
    def test_registerCommand6(self):#registerCommand test pre/pro/post, with profile not None
        self.preTest()
        key = ("plip",)
        c = registerCommand(keyList=key, pre=prePro,pro=proPro,post=postPro, raiseIfExist=True, override=False, profile = "None")
        self.postTest("None")

        self.assertIsInstance(c, MultiCommand)
        self.assertEqual(len(c), 1)
        co,a,e = c[0]

        self.assertIs(co.preProcess, prePro)
        self.assertIs(co.process, proPro)
        self.assertIs(co.postProcess, postPro)
                
    def test_registerCommand9(self):#registerCommand with valid args and registerSetTempPrefix, with profile None
        self.preTest()
        key = ("plup","plop","plip",)
        registerSetTempPrefix(keyList=("plup","plop",), profile = None)
        c = registerCommand(keyList=("plip",), pre=None,pro=proPro,post=None, raiseIfExist=True, override=False, profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (c, True, False,))
        
    def test_registerCommand10(self):#registerCommand with valid args and registerSetTempPrefix, with profile not None
        self.preTest()
        key = ("plup","plop","plip",)
        registerSetTempPrefix(keyList=("plup","plop",), profile = "None")
        c = registerCommand(keyList=("plip",), pre=None,pro=proPro,post=None, raiseIfExist=True, override=False, profile = "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (c, True, False,))
        
    def test_registerCommand11(self):#registerCommand with valid args and registerSetGlobalPrefix, with profile None
        self.preTest()
        key = ("plip",)
        registerSetGlobalPrefix(keyList=("plup","plop",), profile = None)
        c = registerCommand(keyList=key, pre=None,pro=proPro,post=None, raiseIfExist=True, override=False, profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (c, True, False,))
        
    def test_registerCommand12(self):#registerCommand with valid args and registerSetGlobalPrefix, with profile not None
        self.preTest()
        key = ("plip",)
        registerSetGlobalPrefix(keyList=("plup","plop",), profile = "None")
        c = registerCommand(keyList=key, pre=None,pro=proPro,post=None, raiseIfExist=True, override=False, profile = "None")
        l = self.postTest("None")
        
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (c, True, False,))
        
    def test_registerCommand13(self):#registerCommand test raiseIfExist/override valid, with profile None
        self.preTest()
        key = ("plup","plop","plip",)
        c = registerCommand(keyList=key, pre=None,pro=proPro,post=None, raiseIfExist=True, override=True, profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (c, True, True,))

    def test_registerCommand14(self):#registerCommand test raiseIfExist/override valid, with profile not None
        self.preTest()
        key = ("plup","plop","plip",)
        c = registerCommand(keyList=key, pre=None,pro=proPro,post=None, raiseIfExist=False, override=False, profile = "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (c, False, False,))
        
    def test_registerCommand15(self):#registerCommand test raiseIfExist/override not valid, with profile None
        self.preTest()
        key = ("plup","plop","plip",)
        c = self.assertRaises(RegisterException,registerCommand,keyList=key, pre=None,pro=proPro,post=None, raiseIfExist=object(), override=False, profile = None)
        self.assertFalse("_loaders" in globals())
        
    def test_registerCommand16(self):#registerCommand test raiseIfExist/override not valid, with profile not None
        self.preTest()
        key = ("plup","plop","plip",)
        c = self.assertRaises(RegisterException,registerCommand,keyList=key, pre=None,pro=proPro,post=None, raiseIfExist=True, override=object(), profile = "None")
        self.assertFalse("_loaders" in globals())
        
    
    def test_registerCreateMultiCommand1(self):#registerCreateMultiCommand with invalid keyList, with profile None
        self.preTest()
        self.assertRaises(RegisterException,registerAndCreateEmptyMultiCommand,keyList=object(),raiseIfExist=True, override=False, profile = None)
        self.assertFalse("_loaders" in globals())
        
    def test_registerCreateMultiCommand2(self):#registerCreateMultiCommand with invalid keyList, with profile not None
        self.preTest()
        self.assertRaises(RegisterException,registerAndCreateEmptyMultiCommand,keyList=object(),raiseIfExist=True, override=False, profile = "None")
        self.assertFalse("_loaders" in globals())
        
    def test_registerCreateMultiCommand7(self):#registerCreateMultiCommand with valid args and registerSetTempPrefix, with profile None
        self.preTest()
        key = ("plup","plop","plip",)
        registerSetTempPrefix(keyList=("plup","plop",), profile = None)
        mc = registerAndCreateEmptyMultiCommand(keyList=("plip",),raiseIfExist=True, override=False, profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (mc, True, False,))
        
    def test_registerCreateMultiCommand8(self):#registerCreateMultiCommand with valid args and registerSetTempPrefix, with profile not None
        self.preTest()
        key = ("plup","plop","plip",)
        registerSetTempPrefix(keyList=("plup","plop",), profile = "None")
        mc = registerAndCreateEmptyMultiCommand(keyList=("plip",),raiseIfExist=True, override=False, profile = "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (mc, True, False,))
        
    def test_registerCreateMultiCommand9(self):#registerCreateMultiCommand with valid args and registerSetGlobalPrefix, with profile None
        self.preTest()
        key = ("plip",)
        registerSetGlobalPrefix(keyList=("plup","plop",), profile = None)
        mc = registerAndCreateEmptyMultiCommand(keyList=key,raiseIfExist=True, override=False, profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (mc, True, False,))
        
    def test_registerCreateMultiCommand10(self):#registerCreateMultiCommand with valid args and registerSetGlobalPrefix, with profile not None
        self.preTest()
        key = ("plip",)
        registerSetGlobalPrefix(keyList=("plup","plop",), profile = "None")
        mc = registerAndCreateEmptyMultiCommand(keyList=key,raiseIfExist=True, override=False, profile = "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (mc, True, False,))
        
    def test_registerCreateMultiCommand11(self):#registerCreateMultiCommand test raiseIfExist/override valid, with profile None
        self.preTest()
        key = ("plip",)
        mc = registerAndCreateEmptyMultiCommand(keyList=key,raiseIfExist=True, override=True, profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (mc, True, True,))
        
    def test_registerCreateMultiCommand12(self):#registerCreateMultiCommand test raiseIfExist/override valid, with profile not None
        self.preTest()
        key = ("plip",)
        mc = registerAndCreateEmptyMultiCommand(keyList=key,raiseIfExist=False, override=False, profile = "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l,"cmdDict"))
        self.assertIs(type(l.cmdDict), dict)
        self.assertIn(key, l.cmdDict)
        self.assertEqual(l.cmdDict[key], (mc, False, False,))
        
    def test_registerCreateMultiCommand13(self):#registerCreateMultiCommand test raiseIfExist/override not valid, with profile None
        self.preTest()
        self.assertRaises(RegisterException,registerAndCreateEmptyMultiCommand,keyList=("plip",),raiseIfExist=object(), override=False, profile = None)
        self.assertFalse("_loaders" in globals())
        
    def test_registerCreateMultiCommand14(self):#registerCreateMultiCommand test raiseIfExist/override not valid, with profile not None
        self.preTest()
        self.assertRaises(RegisterException,registerAndCreateEmptyMultiCommand,keyList=("plip",),raiseIfExist=True, override=object(), profile = "None")
        self.assertFalse("_loaders" in globals())
        
    
    def test_registerStopHelpTraversalAt1(self):#registerStopHelpTraversalAt with invalid keyList, with profile None
        self.preTest()
        self.assertRaises(RegisterException,registerStopHelpTraversalAt,keyList=object(),profile = None)
        self.assertFalse("_loaders" in globals())
        
    def test_registerStopHelpTraversalAt2(self):#registerStopHelpTraversalAt with invalid keyList, with profile not None
        self.preTest()
        self.assertRaises(RegisterException,registerStopHelpTraversalAt,keyList=object(),profile = "None")
        self.assertFalse("_loaders" in globals())
        
    def test_registerStopHelpTraversalAt3(self):#registerStopHelpTraversalAt with valid args and NO predefined prefix, with profile None
        self.preTest()
        key = ("kikoo","lol",)
        registerStopHelpTraversalAt(keyList=key,profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l,"stoplist"))
        self.assertIs(type(l.stoplist), set)
        self.assertIn(key, l.stoplist)
        
    def test_registerStopHelpTraversalAt4(self):#registerStopHelpTraversalAt with valid args and NO predefined prefix, with profile not None
        self.preTest()
        key = ("kikoo","lol",)
        registerStopHelpTraversalAt(keyList=key,profile = "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l,"stoplist"))
        self.assertIs(type(l.stoplist), set)
        self.assertIn(key, l.stoplist)
        
    def test_registerStopHelpTraversalAt5(self):#registerStopHelpTraversalAt with valid args and registerSetTempPrefix, with profile None
        self.preTest()
        key = ("plup","kikoo","lol",)
        registerSetTempPrefix(keyList=("plup",), profile = None)
        registerStopHelpTraversalAt(keyList=("kikoo","lol",),profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l,"stoplist"))
        self.assertIs(type(l.stoplist), set)
        self.assertIn(key, l.stoplist)
        
    def test_registerStopHelpTraversalAt6(self):#registerStopHelpTraversalAt with valid args and registerSetTempPrefix, with profile not None
        self.preTest()
        key = ("plup","kikoo","lol",)
        registerSetTempPrefix(keyList=("plup",), profile = "None")
        registerStopHelpTraversalAt(keyList=("kikoo","lol",),profile = "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l,"stoplist"))
        self.assertIs(type(l.stoplist), set)
        self.assertIn(key, l.stoplist)
        
    def test_registerStopHelpTraversalAt7(self):#registerStopHelpTraversalAt with valid args and registerSetGlobalPrefix, with profile None
        self.preTest()
        key = ("kikoo","lol",)
        registerSetGlobalPrefix(keyList=("plup",), profile = None)
        registerStopHelpTraversalAt(keyList=key,profile = None)
        l = self.postTest(DEFAULT_PROFILE_NAME)
        self.assertTrue(hasattr(l,"stoplist"))
        self.assertIs(type(l.stoplist), set)
        self.assertIn(key, l.stoplist)
        
    def test_registerStopHelpTraversalAt8(self):#registerStopHelpTraversalAt with valid args and registerSetGlobalPrefix, with profile not None
        self.preTest()
        key = ("kikoo","lol",)
        registerSetGlobalPrefix(keyList=("plup",), profile = "None")
        registerStopHelpTraversalAt(keyList=key,profile = "None")
        l = self.postTest("None")
        self.assertTrue(hasattr(l,"stoplist"))
        self.assertIs(type(l.stoplist), set)
        self.assertIn(key, l.stoplist)

class CommandLoaderTest(unittest.TestCase):
    ## CommandLoader ##
    
    def setUp(self):
        self.cl  = CommandLoader()
        self.params = ParameterContainer()
        self.params.registerParameterManager(ENVIRONMENT_ATTRIBUTE_NAME, EnvironmentParameterManager(self.params))
        self.mltries = multiLevelTries()
        self.params.environment.setParameter(ENVIRONMENT_LEVEL_TRIES_KEY, EnvironmentParameter(value=self.mltries, typ=defaultInstanceArgChecker.getArgCheckerInstance(), settings=GlobalSettings(transient=True,read_only=True, removable=False)), local_param = False)
        
    def tearDown(self):
        pass
    
    def test_CommandLoader1(self):#__init__, test without args
        CommandLoader()
  
    def test_CommandLoader_addCmd1(self):#addCmd, with temp prefix
        self.cl.TempPrefix = ("plop",)
        mc = self.cl.addCmd( ("plip",), MultiCommand(), raiseIfExist=True, override=False)
        self.assertIn( ("plop","plip",), self.cl.cmdDict )
        self.assertEqual( self.cl.cmdDict[("plop","plip",)], (mc,True,False,) )
        
    def test_CommandLoader_addCmd2(self):#addCmd, whithout temp prefix
        self.cl.TempPrefix = None
        mc = self.cl.addCmd( ("plip",), MultiCommand(), raiseIfExist=True, override=False)
        self.assertIn( ("plip",), self.cl.cmdDict )
        self.assertEqual( self.cl.cmdDict[("plip",)], (mc,True,False,) )
        
    def test_CommandLoader_addCmd3(self):#addCmd, test raiseIfExist/override valid
        mc = self.cl.addCmd( ("plip",), MultiCommand(), raiseIfExist=True, override=True)
        self.assertIn( ("plip",), self.cl.cmdDict )
        self.assertEqual( self.cl.cmdDict[("plip",)], (mc,True,True,) )
        
    def test_CommandLoader_addCmd4(self):#addCmd, test raiseIfExist/override not valid
        mc = self.cl.addCmd( ("plip",), MultiCommand(), raiseIfExist=False, override=False)
        self.assertIn( ("plip",), self.cl.cmdDict )
        self.assertEqual( self.cl.cmdDict[("plip",)], (mc,False,False,) )
                
                
    def test_CommandLoader_load1(self):#load, ENVIRONMENT_LEVEL_TRIES_KEY does not exist
        params = ParameterContainer()
        params.registerParameterManager(ENVIRONMENT_ATTRIBUTE_NAME, EnvironmentParameterManager(params))

        self.assertRaises(LoadException, self.cl.load, parameterManager=params, profile = None)
        
    def test_CommandLoader_load2(self):#load, execute without command and without stopTraversal, no global prefix
        self.cl.load(parameterManager=self.params, profile = None)
        
    def test_CommandLoader_load3(self):#load, execute without command and without stopTraversal, global prefix defined
        self.cl.prefix = ("toto",)
        self.cl.load(parameterManager=self.params, profile = None)
        
    def test_CommandLoader_load4(self):#load, try to insert an existing command, no global prefix
        key = ("plop","plip",)
        self.mltries.insert( key, object() )
        self.cl.addCmd( key, MultiCommand(), raiseIfExist=True, override=False)
        
        self.assertRaises(ListOfException, self.cl.load, parameterManager=self.params, profile = None)
        
    def test_CommandLoader_load5(self):#load, try to insert an existing command, global prefix defined 
        self.cl.prefix = ("toto",)
        key = ("plop","plip",)
        self.mltries.insert( ("toto","plop","plip",), object() )
        uc = self.cl.addCmd( ("plop","plip",), UniCommand(process=proPro), raiseIfExist=True, override=False)
        
        self.assertRaises(ListOfException, self.cl.load, parameterManager=self.params, profile = None)
        
    def test_CommandLoader_load6(self):#load, insert a not existing command, no global prefix
        key = ("plop","plip",)
        uc = self.cl.addCmd( key, UniCommand(process=proPro), raiseIfExist=True, override=False)
        self.cl.load(parameterManager=self.params, profile = None)
        searchResult = self.mltries.searchNode(key, True)
        
        self.assertTrue(searchResult is not None and searchResult.isValueFound())
        self.assertIs(uc, searchResult.getValue())
        
    def test_CommandLoader_load7(self):#load, insert a not existing command, global prefix defined
        self.cl.prefix = ("toto",)
        uc = self.cl.addCmd( ("plop","plip",), UniCommand(process=proPro), raiseIfExist=True, override=False)
        self.cl.load(parameterManager=self.params, profile = None)
        searchResult = self.mltries.searchNode(("toto","plop","plip",), True)
        
        self.assertTrue(searchResult is not None and searchResult.isValueFound())
        self.assertIs(uc, searchResult.getValue())
        
    def test_CommandLoader_load8(self):#load, stopTraversal with command that does not exist, no global prefix
        self.cl.stoplist.add( ("toto",) )
        self.assertRaises(ListOfException, self.cl.load, parameterManager=self.params, profile = None)
        
    def test_CommandLoader_load9(self):#load, stopTraversal with command that does not exist, global prefix defined
        self.cl.prefix = ("plop",)
        self.cl.stoplist.add( ("toto",) )
        self.assertRaises(ListOfException, self.cl.load, parameterManager=self.params, profile = None)
        
    def test_CommandLoader_load10(self):#load, stopTraversal, command exist, no global prefix
        key = ("toto","plop","plip",)
        self.mltries.insert( key, object() )
        self.cl.stoplist.add( key)
        self.assertFalse(self.mltries.isStopTraversal(key))
        self.cl.load(parameterManager=self.params, profile = None)
        self.assertTrue(self.mltries.isStopTraversal(key))
        
    def test_CommandLoader_load11(self):#load, stopTraversal, command exist, global prefix defined
        key = ("toto","plop","plip",)
        self.cl.prefix = ("toto",)
        self.mltries.insert( key, object() )
        self.cl.stoplist.add( ("plop","plip",))
        self.assertFalse(self.mltries.isStopTraversal(key))
        self.cl.load(parameterManager=self.params, profile = None)
        self.assertTrue(self.mltries.isStopTraversal(key))
        
    def test_CommandLoader_load12(self):#load, cmd exist, not raise if exist + not override
        key = ("toto","plop","plip",)
        self.mltries.insert( key, object() )
        uc = self.cl.addCmd( key, UniCommand(process=proPro), raiseIfExist=False, override=False)
        self.cl.load(parameterManager=self.params, profile = None)
        
        searchResult = self.mltries.searchNode(key, True)
        self.assertTrue(searchResult is not None and searchResult.isValueFound())
        self.assertIsNot(uc, searchResult.getValue())
        
    def test_CommandLoader_load13(self):#load, cmd exist, raise if exist + not override
        key = ("toto","plop","plip",)
        self.mltries.insert( key, object() )
        uc = self.cl.addCmd( key, UniCommand(process=proPro), raiseIfExist=True, override=False)
        self.assertRaises(ListOfException, self.cl.load, parameterManager=self.params, profile = None)
        
    def test_CommandLoader_load14(self):#load, cmd exist, not raise if exist + override
        key = ("toto","plop","plip",)
        self.mltries.insert( key, object() )
        uc = self.cl.addCmd( key, UniCommand(process=proPro), raiseIfExist=False, override=True)
        self.cl.load(parameterManager=self.params, profile = None)
        
        searchResult = self.mltries.searchNode(key, True)
        self.assertTrue(searchResult is not None and searchResult.isValueFound())
        self.assertIs(uc, searchResult.getValue())
    
    def test_CommandLoader_load15(self):#load, try to load an empty command
        self.cl.addCmd( ("plop","plip",), MultiCommand(), raiseIfExist=True, override=False)
        self.assertRaises(ListOfException, self.cl.load, parameterManager=self.params, profile = None)
        

    def test_CommandLoader_unload1(self):#unload, ENVIRONMENT_LEVEL_TRIES_KEY does not exist
        params = ParameterContainer()
        params.registerParameterManager(ENVIRONMENT_ATTRIBUTE_NAME, EnvironmentParameterManager(params))

        self.assertRaises(LoadException, self.cl.unload, parameterManager=params, profile = None)
    
    def test_CommandLoader_unload2(self):#unload, nothing to do
        self.cl.loadedCommand = []
        self.cl.loadedStopTraversal = []
        self.cl.unload( parameterManager=self.params, profile = None)
    
    def test_CommandLoader_unload3(self):#unload, command does not exist
        self.cl.loadedCommand = []
        self.cl.loadedStopTraversal = []
        self.cl.loadedCommand.append(("toto","plop","plip",) )
        self.assertRaises(ListOfException, self.cl.unload, parameterManager=self.params, profile = None)
        
    def test_CommandLoader_unload4(self):#unload, command exists
        key = ("toto","plop","plip",)
        self.cl.loadedCommand = []
        self.cl.loadedStopTraversal = []
        self.cl.loadedCommand.append(key)
        self.mltries.insert( key, object() )
        
        self.cl.unload( parameterManager=self.params, profile = None)
        
        searchResult = self.mltries.searchNode(key, True)
        
        self.assertTrue(searchResult is None or not searchResult.isValueFound())
        
    def test_CommandLoader_unload5(self):#unload, stopTraversal, path does not exist
        self.cl.loadedCommand = []
        self.cl.loadedStopTraversal = []
        self.cl.loadedStopTraversal.append(("toto","plop","plip",) )
        self.cl.unload( parameterManager=self.params, profile = None)
        
    def test_CommandLoader_unload6(self):#unload, stopTraversal, path exists
        key = ("toto","plop","plip",)
        self.cl.loadedCommand = []
        self.cl.loadedStopTraversal = []
        self.cl.loadedStopTraversal.append(key)
        self.mltries.insert( key, object() )
        self.mltries.setStopTraversal(key,True)
    
        self.cl.unload( parameterManager=self.params, profile = None)
    
        self.assertFalse(self.mltries.isStopTraversal(key))
                
if __name__ == '__main__':
    unittest.main()
