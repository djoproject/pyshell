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
from pyshell.system.parameter import synchronous, isAValidStringPath, _buildExistingPathFromError, ParameterManager, Parameter
from pyshell.system.container import DummyParameterContainer
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.settings  import LocalSettings, GlobalSettings
from pyshell.utils.exception  import ParameterException
from pyshell.utils.constants import ORIGIN_PROCESS
from tries     import multiLevelTries
from threading import current_thread

class ParameterTest(unittest.TestCase):
    def setUp(self):
        self.params = ParameterManager()
        self.params.setParameter("aa.bb.cc", Parameter("plop"))
        self.params.setParameter("ab.bc.cd", Parameter("plip"))

    ## misc ##
            
    def test_ParameterMisc2(self):#isAValidStringPath, with invalid string
        state, message = isAValidStringPath(object())
        self.assertFalse(state)
        self.assertEqual(message, "invalid stringPath, a string was expected, got '<type 'object'>'")
    
    def test_ParameterMisc3(self):#isAValidStringPath with empty string
        state, path = isAValidStringPath("")
        self.assertTrue(state)
        self.assertEqual(len(path), 0)
        
    def test_ParameterMisc4(self):#isAValidStringPath with no char between two point
        state, path = isAValidStringPath("plop..plap")
        self.assertTrue(state)
        self.assertEqual(len(path), 2)
        self.assertEqual(path, ("plop","plap",))
        
    def test_ParameterMisc5(self):#isAValidStringPath with no point in string 
        state, path = isAValidStringPath("plop")
        self.assertTrue(state)
        self.assertEqual(len(path), 1)
        self.assertEqual(path, ("plop",))
        
    def test_ParameterMisc6(self):#isAValidStringPath with point in string
        state, path = isAValidStringPath("plop.plap.plip")
        self.assertTrue(state)
        self.assertEqual(len(path), 3)
        self.assertEqual(path, ("plop","plap","plip",))
        
    ## ParameterManager constructor ##
    
    def test_ParameterManagerConstructor1(self):#with parent None + test getCurrentId
        params = ParameterManager(parent = None)
        self.assertEqual(params.parentContainer.getCurrentId(), (current_thread().ident, None,) )
        self.assertEqual(params.parentContainer.getOrigin(), (ORIGIN_PROCESS, None,) )
        
    def test_ParameterManagerConstructor2(self):#with valid parent + test getCurrentId
        params = ParameterManager(parent = DummyParameterContainer())
        self.assertEqual(params.parentContainer.getCurrentId(), (current_thread().ident, None,) )
        self.assertEqual(params.parentContainer.getOrigin(), (ORIGIN_PROCESS, None,) )
        
    def test_ParameterManagerConstructor3(self):#with parent without getCurrentId + test getCurrentId
        self.assertRaises(ParameterException, ParameterManager, object())
    
    ## ParameterManager methods ##
    
    def test_ParameterManager1(self):#_buildExistingPathFromError, with 0 token found and some wrong token
        path = ("plop", "plip", "plap",)
        mltries = multiLevelTries()
        advancedResult =  mltries.advancedSearch(path)
        self.assertEqual(_buildExistingPathFromError(path, advancedResult), ['plop', 'plip', 'plap'])
    
    def test_ParameterManager2(self):#_buildExistingPathFromError, with some token found and 0 wrong token
        path = ("plop", "plip", "plap",)
        mltries = multiLevelTries()
        mltries.insert( ("plop", "plip", "plap","plup",), object() )
        advancedResult =  mltries.advancedSearch(path)
        self.assertEqual(_buildExistingPathFromError(path, advancedResult), ['plop', 'plip', 'plap'])
    
    def test_ParameterManager3(self):#_buildExistingPathFromError, with some token found and some wrong token
        path = ("plop", "plip", "plap",)
        mltries = multiLevelTries()
        mltries.insert( ("plop", "plip", "plyp","plup",), object() )
        advancedResult =  mltries.advancedSearch(path)
        self.assertEqual(_buildExistingPathFromError(path, advancedResult), ['plop', 'plip', 'plap'])
    
    ##
    
    def test_ParameterManager4(self):#_getAdvanceResult, search a invalid path
        self.assertRaises(ParameterException, self.params._getAdvanceResult, "test",object())
    
    def test_ParameterManager5(self):#_getAdvanceResult, raiseIfAmbiguous=True and ambiguous
        self.assertRaises(ParameterException, self.params._getAdvanceResult, "test","a.b.c", raiseIfAmbiguous = True, raiseIfNotFound=False)
    
    def test_ParameterManager6(self):#_getAdvanceResult, raiseIfAmbiguous=True and not ambiguous
        result = self.params._getAdvanceResult("test","aa.bb.cc", raiseIfAmbiguous = True, raiseIfNotFound=False)
        self.assertTrue(result.isValueFound())
    
    def test_ParameterManager7(self):#_getAdvanceResult, raiseIfAmbiguous=False and ambiguous
        result = self.params._getAdvanceResult("test","a.b.c", raiseIfAmbiguous = False, raiseIfNotFound=False)
        self.assertFalse(result.isValueFound())
        self.assertTrue(result.isAmbiguous())
    
    def test_ParameterManager8(self):#_getAdvanceResult, raiseIfNotFound=True and not found
        self.assertRaises(ParameterException, self.params._getAdvanceResult, "test","plop", raiseIfNotFound = True, raiseIfAmbiguous=False)
    
    def test_ParameterManager9(self):#_getAdvanceResult, raiseIfNotFound=True and found
        self.assertRaises(ParameterException, self.params._getAdvanceResult, "test","plop", raiseIfNotFound = True, raiseIfAmbiguous=False)
    
    def test_ParameterManager10(self):#_getAdvanceResult, raiseIfNotFound=False and not found
        result = self.params._getAdvanceResult("test","plop", raiseIfAmbiguous = False, raiseIfNotFound=False)
        self.assertFalse(result.isValueFound())
        self.assertFalse(result.isAmbiguous())
    
    def test_ParameterManager11(self):#_getAdvanceResult, with perfect_match
        result = self.params._getAdvanceResult("test","a.b.c", raiseIfAmbiguous = False, raiseIfNotFound=False, perfect_match=True)
        self.assertFalse(result.isValueFound())
        self.assertFalse(result.isAmbiguous())

    def test_ParameterManager11b(self):#_getAdvanceResult, with perfect_match
        result = self.params._getAdvanceResult("test","aa.bb.cc", raiseIfAmbiguous = False, raiseIfNotFound=False, perfect_match=True)
        self.assertTrue(result.isValueFound())
        self.assertFalse(result.isAmbiguous())
    
    ##
    
    def test_ParameterManager12(self):#test getAllowedType
        self.assertIs(self.params.getAllowedType(), Parameter)
    
    def test_ParameterManager13(self):#test isAnAllowedType, should not allow inherited type
        self.assertFalse(self.params.isAnAllowedType(EnvironmentParameter("plop")))
        self.assertTrue(self.params.isAnAllowedType(Parameter("titi")))
    
    def test_ParameterManager14(self):#test extractParameter, with a valid type
        p = Parameter(42)
        self.assertIs(self.params.extractParameter(p), p)
    
    def test_ParameterManager15(self):#test extractParameter, with another parameter type
        self.assertIsInstance(self.params.extractParameter(42), Parameter)
    
    def test_ParameterManager16(self):#test extractParameter, with something else (to try to instanciate an allowed type)
        self.assertRaises(ParameterException, self.params.extractParameter, EnvironmentParameter("plop"))
    
    ##
    
    def test_ParameterManager17(self):#setParameter, local exists + local + existing is readonly
        param = self.params.setParameter("plop", Parameter("toto"), local_param=True)
        self.assertIn("plop",self.params.threadLocalVar[self.params.parentContainer.getCurrentId()])
        self.assertIsInstance(param.settings,LocalSettings)
        param.settings.setReadOnly(True)
        self.assertRaises(ParameterException, self.params.setParameter, "plop", Parameter("titi"), local_param=True)

    def test_ParameterManager18(self):#setParameter, local exists + local + existing is removable
        param1 = self.params.setParameter("plop", Parameter("toto"), local_param=True)
        self.assertIn("plop",self.params.threadLocalVar[self.params.parentContainer.getCurrentId()])
        self.assertIsInstance(param1.settings,LocalSettings)
        param1.settings.setRemovable(True)

        param2 = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        self.assertIn("plop",self.params.threadLocalVar[self.params.parentContainer.getCurrentId()])
        self.assertIsInstance(param2.settings,LocalSettings)
        self.assertIsNot(param1, param2)
    
    def test_ParameterManager19(self):#setParameter, global exists (not local) + local + existing is readonly
        param1 = self.params.setParameter("plop", Parameter("toto"), local_param=False)
        self.assertIsInstance(param1.settings,GlobalSettings)
        param1.settings.setReadOnly(True)

        param2 = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        self.assertIn("plop",self.params.threadLocalVar[self.params.parentContainer.getCurrentId()])
        self.assertIsInstance(param2.settings,LocalSettings)
        self.assertIsNot(param1, param2)
    
    def test_ParameterManager20(self):#setParameter, global exists (not local) + local + existing is removable
        param1 = self.params.setParameter("plop", Parameter("toto"), local_param=False)
        self.assertIsInstance(param1.settings,GlobalSettings)
        param1.settings.setRemovable(True)

        param2 = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        self.assertIn("plop",self.params.threadLocalVar[self.params.parentContainer.getCurrentId()])
        self.assertIsInstance(param2.settings,LocalSettings)
        self.assertIsNot(param1, param2)
    
    def test_ParameterManager21(self):#setParameter, nothing exists + local
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        self.assertIn("plop",self.params.threadLocalVar[self.params.parentContainer.getCurrentId()])
        self.assertIsInstance(param.settings,LocalSettings)
        self.assertIs(self.params.getParameter("plop"), param)
    
    
    def test_ParameterManager22(self):#setParameter, local exists + global + existing is readonly
        param1 = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        self.assertIn("plop",self.params.threadLocalVar[self.params.parentContainer.getCurrentId()])
        self.assertIsInstance(param1.settings,LocalSettings)
        param1.settings.setReadOnly(True)

        param2 = self.params.setParameter("plop", Parameter("toto"), local_param=False)
        self.assertIsInstance(param2.settings,GlobalSettings)

        self.assertIsNot(param1, param2)
    
    def test_ParameterManager23(self):#setParameter, local exists + global + existing is removable
        param1 = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        self.assertIn("plop",self.params.threadLocalVar[self.params.parentContainer.getCurrentId()])
        self.assertIsInstance(param1.settings,LocalSettings)
        param1.settings.setRemovable(True)

        param2 = self.params.setParameter("plop", Parameter("toto"), local_param=False)
        self.assertIsInstance(param2.settings,GlobalSettings)

        self.assertIsNot(param1, param2)

    def test_ParameterManager24(self):#setParameter, global exists (not local) + global + existing is readonly
        param1 = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        self.assertIsInstance(param1.settings,GlobalSettings)
        param1.settings.setReadOnly(True)

        self.assertRaises(ParameterException, self.params.setParameter, "plop", Parameter("toto"), local_param=False)
    
    def test_ParameterManager25(self):#setParameter, global exists (not local) + global + existing is removable
        param1 = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        self.assertIsInstance(param1.settings,GlobalSettings)
        param1.settings.setRemovable(True)

        param2 = self.params.setParameter("plop", Parameter("toto"), local_param=False)
        self.assertIsInstance(param2.settings,GlobalSettings)

        self.assertIsNot(param1, param2)
    
    def test_ParameterManager26(self):#setParameter, nothing exists + global
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        self.assertIsInstance(param.settings,GlobalSettings)
        self.assertIs(self.params.getParameter("plop"), param)
    
    def test_ParameterManagerSetParameter1(self):#setParameter, on global overwritte ONLY, setting has to be transfered/merged from old to new
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        param.settings.addLoader("uhuh")
        param.settings.addLoader("ahah")
        param.settings.addLoader("uhuh")
        
        self.assertTrue(hasattr(param.settings, "origin"))
        self.assertTrue(hasattr(param.settings, "originArg"))
        self.assertTrue(hasattr(param.settings, "startingHash"))
        
        param.settings.origin = "aaa"
        param.settings.originArg = "bbb"
        has = param.settings.startingHash
        
        param = self.params.setParameter("plop", Parameter("tata"), local_param=False)
        
        self.assertEqual(param.settings.origin, "aaa")
        self.assertEqual(param.settings.originArg, "bbb")
        self.assertEqual(param.settings.startingHash, has)
        
        self.assertEqual(param.settings.getLoaderSet(), set( ("uhuh", "ahah",)) )
    
    ##
    
    def test_ParameterManager27(self):#getParameter, local exists + local_param=True + explore_other_level=True
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        pget  = self.params.getParameter("plop", local_param = True, explore_other_level=True)
        self.assertIs(param, pget)
    
    def test_ParameterManager28(self):#getParameter, local exists + local_param=True + explore_other_level=False
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        pget  = self.params.getParameter("plop", local_param = True, explore_other_level=False)
        self.assertIs(param, pget)
    
    def test_ParameterManager29(self):#getParameter, global exists + local_param=True + explore_other_level=True
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        pget  = self.params.getParameter("plop", local_param = True, explore_other_level=True)
        self.assertIs(param, pget)
    
    def test_ParameterManager30(self):#getParameter, global exists + local_param=True + explore_other_level=False
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        pget  = self.params.getParameter("plop", local_param = True, explore_other_level=False)
        self.assertIs(pget, None)
    
    def test_ParameterManager31(self):#getParameter, local exists + local_param=False + explore_other_level=True
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        pget  = self.params.getParameter("plop", local_param = False, explore_other_level=True)
        self.assertIs(param, pget)
    
    def test_ParameterManager32(self):#getParameter, local exists + local_param=False + explore_other_level=False
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        pget  = self.params.getParameter("plop", local_param = False, explore_other_level=False)
        self.assertIs(pget, None)
    
    def test_ParameterManager33(self):#getParameter, global exists + local_param=False + explore_other_level=True
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        pget  = self.params.getParameter("plop", local_param = False, explore_other_level=True)
        self.assertIs(param, pget)
    
    def test_ParameterManager34(self):#getParameter, global exists + local_param=False + explore_other_level=False
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        pget  = self.params.getParameter("plop", local_param = False, explore_other_level=False)
        self.assertIs(param, pget)
    
    def test_ParameterManager35(self):#getParameter, nothing exists + local_param=True + explore_other_level=True
        pget  = self.params.getParameter("plop", local_param = True, explore_other_level=True)
        self.assertIs(pget, None)
    
    def test_ParameterManager36(self):#getParameter, nothing exists + local_param=True + explore_other_level=False
        pget  = self.params.getParameter("plop", local_param = True, explore_other_level=False)
        self.assertIs(pget, None)
    
    def test_ParameterManager37(self):#getParameter, nothing exists + local_param=False + explore_other_level=True
        pget  = self.params.getParameter("plop", local_param = False, explore_other_level=True)
        self.assertIs(pget, None)
    
    def test_ParameterManager38(self):#getParameter, nothing exists + local_param=False + explore_other_level=False
        pget  = self.params.getParameter("plop", local_param = False, explore_other_level=False)
        self.assertIs(pget, None)
    
    ##
    
    def test_ParameterManager39(self):#hasParameter, local exists + local_param=True + explore_other_level=True
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        self.assertTrue(self.params.hasParameter("plop", local_param=True, explore_other_level=True))
    
    def test_ParameterManager40(self):#hasParameter, local exists + local_param=True + explore_other_level=False
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        self.assertTrue(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
    
    def test_ParameterManager41(self):#hasParameter, global exists + local_param=True + explore_other_level=True
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        self.assertTrue(self.params.hasParameter("plop", local_param=True, explore_other_level=True))
    
    def test_ParameterManager42(self):#hasParameter, global exists + local_param=True + explore_other_level=False
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        self.assertFalse(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
    
    def test_ParameterManager43(self):#hasParameter, local exists + local_param=False + explore_other_level=True
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        self.assertTrue(self.params.hasParameter("plop", local_param=False, explore_other_level=True))
    
    def test_ParameterManager44(self):#hasParameter, local exists + local_param=False + explore_other_level=False
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        self.assertFalse(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
    
    def test_ParameterManager45(self):#hasParameter, global exists + local_param=False + explore_other_level=True
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        self.assertTrue(self.params.hasParameter("plop", local_param=False, explore_other_level=True))
    
    def test_ParameterManager46(self):#hasParameter, global exists + local_param=False + explore_other_level=False
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        self.assertTrue(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
    
    def test_ParameterManager47(self):#hasParameter, nothing exists + local_param=True + explore_other_level=True
        self.assertFalse(self.params.hasParameter("plop", local_param=True, explore_other_level=True))
    
    def test_ParameterManager48(self):#hasParameter, nothing exists + local_param=True + explore_other_level=False
        self.assertFalse(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
    
    def test_ParameterManager49(self):#hasParameter, nothing exists + local_param=False + explore_other_level=True
        self.assertFalse(self.params.hasParameter("plop", local_param=False, explore_other_level=True))
    
    def test_ParameterManager50(self):#hasParameter, nothing exists + local_param=False + explore_other_level=False
        self.assertFalse(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
    
    ##
    
    def test_ParameterManager51(self):#unsetParameter, local exists + local_param=True + explore_other_level=True
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        self.assertTrue(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
        self.params.unsetParameter("plop", local_param=True, explore_other_level=True)
        self.assertFalse(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
    
    def test_ParameterManager52(self):#unsetParameter, local exists + local_param=True + explore_other_level=False
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        self.assertTrue(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
        self.params.unsetParameter("plop", local_param=True, explore_other_level=False)
        self.assertFalse(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
    
    def test_ParameterManager53(self):#unsetParameter, global exists + local_param=True + explore_other_level=True
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        self.assertTrue(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
        self.params.unsetParameter("plop", local_param=True, explore_other_level=True)
        self.assertFalse(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
    
    def test_ParameterManager54(self):#unsetParameter, global exists + local_param=True + explore_other_level=False
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        self.assertTrue(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
        self.assertRaises(ParameterException, self.params.unsetParameter,"plop", local_param=True, explore_other_level=False)
        self.assertTrue(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
    
    def test_ParameterManager55(self):#unsetParameter, local exists + local_param=False + explore_other_level=True
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        self.assertTrue(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
        self.params.unsetParameter("plop", local_param=False, explore_other_level=True)
        self.assertFalse(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
    
    def test_ParameterManager56(self):#unsetParameter, local exists + local_param=False + explore_other_level=False
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        self.assertTrue(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
        self.assertRaises(ParameterException,self.params.unsetParameter, "plop", local_param=False, explore_other_level=False)
        self.assertTrue(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
    
    def test_ParameterManager57(self):#unsetParameter, global exists + local_param=False + explore_other_level=True
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        self.assertTrue(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
        self.params.unsetParameter("plop", local_param=False, explore_other_level=True)
        self.assertFalse(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
    
    def test_ParameterManager58(self):#unsetParameter, global exists + local_param=False + explore_other_level=False
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        self.assertTrue(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
        self.params.unsetParameter("plop", local_param=False, explore_other_level=False)
        self.assertFalse(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
    
    def test_ParameterManager59(self):#unsetParameter, local + global exists + local_param=False + explore_other_level=True
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        
        self.assertTrue(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
        self.assertTrue(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
        
        self.params.unsetParameter("plop", local_param=False, explore_other_level=True)
        
        self.assertFalse(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
        self.assertTrue(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
    
    def test_ParameterManager60(self):#unsetParameter, local + global exists + local_param=False + explore_other_level=False
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        
        self.assertTrue(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
        self.assertTrue(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
        
        self.params.unsetParameter("plop", local_param=False, explore_other_level=False)
        
        self.assertFalse(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
        self.assertTrue(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
    
    def test_ParameterManager61(self):#unsetParameter, global + local exists + local_param=True + explore_other_level=True
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        
        self.assertTrue(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
        self.assertTrue(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
        
        self.params.unsetParameter("plop", local_param=True, explore_other_level=True)
        
        self.assertTrue(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
        self.assertFalse(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
    
    def test_ParameterManager62(self):#unsetParameter, global + local exists + local_param=True + explore_other_level=False
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        
        self.assertTrue(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
        self.assertTrue(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
        
        self.params.unsetParameter("plop", local_param=True, explore_other_level=True)
        
        self.assertTrue(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
        self.assertFalse(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
    
    def test_ParameterManager63(self):#unsetParameter, nothing exists + local_param=True + explore_other_level=True
        self.assertRaises(ParameterException, self.params.unsetParameter,"plop", local_param=True, explore_other_level=True)
    
    def test_ParameterManager64(self):#unsetParameter, nothing exists + local_param=True + explore_other_level=False
        self.assertRaises(ParameterException, self.params.unsetParameter,"plop", local_param=True, explore_other_level=False)
    
    def test_ParameterManager65(self):#unsetParameter, nothing exists + local_param=False + explore_other_level=True
        self.assertRaises(ParameterException, self.params.unsetParameter,"plop", local_param=False, explore_other_level=True)
    
    def test_ParameterManager66(self):#unsetParameter, nothing exists + local_param=False + explore_other_level=False
        self.assertRaises(ParameterException, self.params.unsetParameter,"plop", local_param=False, explore_other_level=False)
    
    def test_ParameterManagerUnsetParameter1(self):#unsetParameter, try to remove an existing global one, not removable with loader dependancies
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        param.settings.addLoader("load1")
        param.settings.setRemovable(False)
        self.assertRaises(ParameterException, self.params.unsetParameter,"plop", local_param=False, explore_other_level=False)
    
    def test_ParameterManagerUnsetParameter2(self):#unsetParameter, try to remove an existing global one, with loader dependancies and force
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        param.settings.addLoader("load1")
        self.params.unsetParameter("plop", local_param=False, explore_other_level=False, force=True)
        self.assertFalse(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
    
    def test_ParameterManagerUnsetParameter3(self):#unsetParameter, try to remove an existing global one, not removable and force
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        param.settings.setRemovable(False)
        self.params.unsetParameter("plop", local_param=False, explore_other_level=False, force=True)
        self.assertFalse(self.params.hasParameter("plop", local_param=False, explore_other_level=False))
    
    def test_ParameterManagerUnsetParameter4(self):#unsetParameter, try to remove an existing local one, not removable and force
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        param.settings.setRemovable(False)
        self.params.unsetParameter("plop", local_param=True, explore_other_level=False, force=True)
        self.assertFalse(self.params.hasParameter("plop", local_param=True, explore_other_level=False))
    
    def test_ParameterManagerUnsetParameter5(self):#unsetParameter, try to remove an existing global one, not removable
        param = self.params.setParameter("plop", Parameter("titi"), local_param=False)
        param.settings.setRemovable(False)
        self.assertRaises(ParameterException, self.params.unsetParameter,"plop", local_param=False, explore_other_level=False)
    
    def test_ParameterManagerUnsetParameter6(self):#unsetParameter, try to remove an existing local one, not removable
        param = self.params.setParameter("plop", Parameter("titi"), local_param=True)
        param.settings.setRemovable(False)
        self.assertRaises(ParameterException, self.params.unsetParameter,"plop", local_param=True, explore_other_level=False)
    
    ##
    
    def test_ParameterManager67(self):#flushVariableLevelForThisThread, nothing for the current thread
        params = ParameterManager()
        params.setParameter("plop", Parameter("titi"), local_param=False)
        self.assertNotIn(params.parentContainer.getCurrentId(), params.threadLocalVar)
        params.flush()
        self.assertNotIn(params.parentContainer.getCurrentId(), params.threadLocalVar)
    
    def test_ParameterManager68(self):#flushVariableLevelForThisThread, flush parameter that only exists for the current thread
        params = ParameterManager()
        params.setParameter("plop", Parameter("titi"), local_param=True)
        
        self.assertTrue(params.hasParameter("plop", local_param=True, explore_other_level=False))
        self.assertIn(params.parentContainer.getCurrentId(), params.threadLocalVar)
        
        params.flush()
        
        self.assertFalse(params.hasParameter("plop", local_param=True, explore_other_level=False))
        self.assertNotIn(params.parentContainer.getCurrentId(), params.threadLocalVar)
    
    def test_ParameterManager69(self):#flushVariableLevelForThisThread, flush parameter that exist for the current thread and at global level
        params = ParameterManager()
        params.setParameter("plap", Parameter("tata"), local_param=False)
        params.setParameter("plop", Parameter("titi"), local_param=True)
        
        self.assertTrue(params.hasParameter("plap", local_param=False, explore_other_level=False))
        self.assertTrue(params.hasParameter("plop", local_param=True, explore_other_level=False))
        self.assertIn(params.parentContainer.getCurrentId(), params.threadLocalVar)
        
        params.flush()
        
        self.assertTrue(params.hasParameter("plap", local_param=False, explore_other_level=False))
        self.assertFalse(params.hasParameter("plop", local_param=True, explore_other_level=False))
        self.assertNotIn(params.parentContainer.getCurrentId(), params.threadLocalVar)
    
    def test_ParameterManager70(self):#flushVariableLevelForThisThread, flush parameter that exist for the current thread and for others thread
        params = ParameterManager()
        
        #construct fake other var
        params.setParameter("plop", Parameter("titi"), local_param=True)
        (tid, empty,) = params.parentContainer.getCurrentId()
        name_set = params.threadLocalVar[(tid, empty,)]
        del params.threadLocalVar[(tid, empty,)]
        params.threadLocalVar[(tid+1, empty,)] = name_set
        
        result = params.mltries.advancedSearch( ("plop",), True)
        g,l = result.getValue()
        param = l[(tid, empty,)]
        del l[(tid, empty,)]
        l[(tid+1, empty,)] = param
        
        params.setParameter("plip", Parameter("tutu"), local_param=True)
        
        self.assertTrue(params.hasParameter("plip", local_param=True, explore_other_level=True))
        self.assertFalse(params.hasParameter("plop", local_param=True, explore_other_level=True))
        self.assertIn(params.parentContainer.getCurrentId(), params.threadLocalVar)
    
        params.flush()
        
        self.assertFalse(params.hasParameter("plip", local_param=True, explore_other_level=True))
        self.assertFalse(params.hasParameter("plop", local_param=True, explore_other_level=True))
        self.assertNotIn(params.parentContainer.getCurrentId(), params.threadLocalVar)
        
        result = params.mltries.advancedSearch( ("plop",), True)
        g,l = result.getValue()
        self.assertIn( (tid+1, empty,), l)
        
    ##
    
    def test_ParameterManager71(self):#buildDictionnary, search with invalid string
        params = ParameterManager()
        self.assertRaises(ParameterException, params.buildDictionnary, object())
    
    def test_ParameterManager72(self):#buildDictionnary, local exists + local_param=True + explore_other_level=True
        params = ParameterManager()
        p1 = params.setParameter("aa.bb.cc", Parameter("titi"), local_param=True)
        p2 = params.setParameter("ab.ac.cd", Parameter("tata"), local_param=True)
        p3 = params.setParameter("aa.plop", Parameter("toto"), local_param=True)
        
        result = params.buildDictionnary("", local_param = True, explore_other_level=True)
        
        self.assertEqual(result, { "aa.bb.cc":p1, "ab.ac.cd":p2, "aa.plop":p3})
    
    def test_ParameterManager73(self):#buildDictionnary, local exists + local_param=True + explore_other_level=False
        params = ParameterManager()
        p1 = params.setParameter("aa.bb.cc", Parameter("titi"), local_param=True)
        p2 = params.setParameter("ab.ac.cd", Parameter("tata"), local_param=True)
        p3 = params.setParameter("aa.plop", Parameter("toto"), local_param=True)
        
        result = params.buildDictionnary("", local_param = True, explore_other_level=False)
        
        self.assertEqual(result, { "aa.bb.cc":p1, "ab.ac.cd":p2, "aa.plop":p3})
    
    def test_ParameterManager74(self):#buildDictionnary, global exists + local_param=True + explore_other_level=True
        params = ParameterManager()
        p1 = params.setParameter("uu.vv.ww", Parameter("plap"), local_param=False)
        p2 = params.setParameter("uv.vw.wx", Parameter("plop"), local_param=False)
        p3 = params.setParameter("uu.titi", Parameter("plup"), local_param=False)
        
        result = params.buildDictionnary("", local_param = True, explore_other_level=True)
        
        self.assertEqual(result, { "uu.vv.ww":p1, "uv.vw.wx":p2, "uu.titi":p3})
    
    def test_ParameterManager75(self):#buildDictionnary, global exists + local_param=True + explore_other_level=False
        params = ParameterManager()
        p1 = params.setParameter("uu.vv.ww", Parameter("plap"), local_param=False)
        p2 = params.setParameter("uv.vw.wx", Parameter("plop"), local_param=False)
        p3 = params.setParameter("uu.titi", Parameter("plup"), local_param=False)
        
        result = params.buildDictionnary("", local_param = True, explore_other_level=False)
        
        self.assertEqual(result, {})
    
    def test_ParameterManager76(self):#buildDictionnary, local exists + local_param=False + explore_other_level=True
        params = ParameterManager()
        p1 = params.setParameter("aa.bb.cc", Parameter("titi"), local_param=True)
        p2 = params.setParameter("ab.ac.cd", Parameter("tata"), local_param=True)
        p3 = params.setParameter("aa.plop", Parameter("toto"), local_param=True)
        
        result = params.buildDictionnary("", local_param = False, explore_other_level=True)
        
        self.assertEqual(result, { "aa.bb.cc":p1, "ab.ac.cd":p2, "aa.plop":p3})
    
    def test_ParameterManager77(self):#buildDictionnary, local exists + local_param=False + explore_other_level=False
        params = ParameterManager()
        p1 = params.setParameter("aa.bb.cc", Parameter("titi"), local_param=True)
        p2 = params.setParameter("ab.ac.cd", Parameter("tata"), local_param=True)
        p3 = params.setParameter("aa.plop", Parameter("toto"), local_param=True)
        
        result = params.buildDictionnary("", local_param = False, explore_other_level=False)
        
        self.assertEqual(result, {})
    
    def test_ParameterManager78(self):#buildDictionnary, global exists + local_param=False + explore_other_level=True
        params = ParameterManager()
        p1 = params.setParameter("uu.vv.ww", Parameter("plap"), local_param=False)
        p2 = params.setParameter("uv.vw.wx", Parameter("plop"), local_param=False)
        p3 = params.setParameter("uu.titi", Parameter("plup"), local_param=False)
        
        result = params.buildDictionnary("", local_param = False, explore_other_level=True)
        
        self.assertEqual(result, { "uu.vv.ww":p1, "uv.vw.wx":p2, "uu.titi":p3})
    
    def test_ParameterManager79(self):#buildDictionnary, global exists + local_param=False + explore_other_level=False
        params = ParameterManager()
        p1 = params.setParameter("uu.vv.ww", Parameter("plap"), local_param=False)
        p2 = params.setParameter("uv.vw.wx", Parameter("plop"), local_param=False)
        p3 = params.setParameter("uu.titi", Parameter("plup"), local_param=False)
        
        result = params.buildDictionnary("", local_param = False, explore_other_level=False)
        
        self.assertEqual(result, { "uu.vv.ww":p1, "uv.vw.wx":p2, "uu.titi":p3})
    
    def test_ParameterManager80(self):#buildDictionnary, nothing exists + local_param=True + explore_other_level=True
        params = ParameterManager()
        result = params.buildDictionnary("", local_param = True, explore_other_level=True)
        self.assertEqual(result, {})
    
    def test_ParameterManager81(self):#buildDictionnary, nothing exists + local_param=True + explore_other_level=False
        params = ParameterManager()
        result = params.buildDictionnary("", local_param = True, explore_other_level=False)
        self.assertEqual(result, {})
    
    def test_ParameterManager82(self):#buildDictionnary, nothing exists + local_param=False + explore_other_level=True
        params = ParameterManager()
        result = params.buildDictionnary("", local_param = False, explore_other_level=True)
        self.assertEqual(result, {})
    
    def test_ParameterManager83(self):#buildDictionnary, nothing exists + local_param=False + explore_other_level=False
        params = ParameterManager()
        result = params.buildDictionnary("", local_param = False, explore_other_level=False)
        self.assertEqual(result, {})
    
    def test_ParameterManager84(self):#buildDictionnary, local + global exists + local_param=False + explore_other_level=True  (mixe several cases)
        params = ParameterManager()
        p1 = params.setParameter("aa.bb.cc", Parameter("titi"), local_param=True)
        p2 = params.setParameter("ab.ac.cd", Parameter("tata"), local_param=True)
        p3 = params.setParameter("aa.plop", Parameter("toto"), local_param=True)
        p4 = params.setParameter("aa.bb.cc", Parameter("plap"), local_param=False)
        p5 = params.setParameter("uv.vw.wx", Parameter("plop"), local_param=False)
        p6 = params.setParameter("uu.titi", Parameter("plup"), local_param=False)
        
        result = params.buildDictionnary("", local_param = False, explore_other_level=True)
        
        self.assertEqual(result, { "aa.bb.cc":p4, "ab.ac.cd":p2, "aa.plop":p3, "uv.vw.wx":p5, "uu.titi":p6})
    
    def test_ParameterManager85(self):#buildDictionnary, local + global exists + local_param=False + explore_other_level=False (mixe several cases)
        params = ParameterManager()
        p1 = params.setParameter("aa.bb.cc", Parameter("titi"), local_param=True)
        p2 = params.setParameter("ab.ac.cd", Parameter("tata"), local_param=True)
        p3 = params.setParameter("aa.plop", Parameter("toto"), local_param=True)
        p4 = params.setParameter("aa.bb.cc", Parameter("plap"), local_param=False)
        p5 = params.setParameter("uv.vw.wx", Parameter("plop"), local_param=False)
        p6 = params.setParameter("uu.titi", Parameter("plup"), local_param=False)
        
        result = params.buildDictionnary("", local_param = False, explore_other_level=False)
        
        self.assertEqual(result, { "aa.bb.cc":p4, "uv.vw.wx":p5, "uu.titi":p6})
    
    def test_ParameterManager86(self):#buildDictionnary, global + local exists + local_param=True + explore_other_level=True   (mixe several cases)
        params = ParameterManager()
        p1 = params.setParameter("aa.bb.cc", Parameter("titi"), local_param=True)
        p2 = params.setParameter("ab.ac.cd", Parameter("tata"), local_param=True)
        p3 = params.setParameter("aa.plop", Parameter("toto"), local_param=True)
        p4 = params.setParameter("aa.bb.cc", Parameter("plap"), local_param=False)
        p5 = params.setParameter("uv.vw.wx", Parameter("plop"), local_param=False)
        p6 = params.setParameter("uu.titi", Parameter("plup"), local_param=False)
        
        result = params.buildDictionnary("", local_param = True, explore_other_level=True)
        
        self.assertEqual(result, { "aa.bb.cc":p1, "ab.ac.cd":p2, "aa.plop":p3, "uv.vw.wx":p5, "uu.titi":p6})
    
    def test_ParameterManager87(self):#buildDictionnary, global + local exists + local_param=True + explore_other_level=False  (mixe several cases)
        params = ParameterManager()
        p1 = params.setParameter("aa.bb.cc", Parameter("titi"), local_param=True)
        p2 = params.setParameter("ab.ac.cd", Parameter("tata"), local_param=True)
        p3 = params.setParameter("aa.plop", Parameter("toto"), local_param=True)
        p4 = params.setParameter("aa.bb.cc", Parameter("plap"), local_param=False)
        p5 = params.setParameter("uv.vw.wx", Parameter("plop"), local_param=False)
        p6 = params.setParameter("uu.titi", Parameter("plup"), local_param=False)
        
        result = params.buildDictionnary("", local_param = True, explore_other_level=False)
        
        self.assertEqual(result, { "aa.bb.cc":p1, "ab.ac.cd":p2, "aa.plop":p3})
    
        
    ## parameters test ##

    def test_ParameterConstructor1(self):#test value/getvalue on constructor
        self.assertRaises(ParameterException, Parameter, None, object())
        
    def test_ParameterConstructor2(self):
        p = Parameter(None)
        self.assertIsInstance(p.settings, LocalSettings)
        
    def test_ParameterConstructor3(self):
        ls = LocalSettings()
        p = Parameter(None, settings=ls)
        self.assertIs(p.settings, ls)
        
    def test_ParameterConstructor3(self):
        ls = LocalSettings()
        ls.setReadOnly(True)
        o = object()
        p = Parameter(o, settings=ls)
        self.assertIs(p.getValue(), o)
        self.assertRaises(ParameterException, p.setValue, "plop")
    
    def test_Parameter1(self):#test setValue/getValue
        p = Parameter(None)
        self.assertIs(p.getValue(), None)
        p.setValue(42)
        self.assertEqual(p.getValue(), 42)
        
    def test_Parameter2(self):#test enableLocal
        p = Parameter(None)
        sett = p.settings
        self.assertIsInstance(sett, LocalSettings)
        p.enableLocal()
        self.assertIs(sett, p.settings)

    def test_Parameter3(self):#test enableGlobal
        p = Parameter(None)
        p.enableGlobal()
        sett = p.settings
        self.assertIsInstance(sett, GlobalSettings)
        p.enableGlobal()
        self.assertIs(sett, p.settings)
        
    def test_Parameter4(self):#test from local to global
        p = Parameter(None)
        p.settings.setRemovable(True)
        p.settings.setReadOnly(True)
        p.enableGlobal()
        self.assertIsInstance(p.settings, GlobalSettings)
        self.assertTrue(p.settings.isReadOnly())
        self.assertTrue(p.settings.isRemovable())
        
    def test_Parameter5(self):#test from local to global
        p = Parameter(None)
        p.settings.setRemovable(False)
        p.settings.setReadOnly(False)
        p.enableGlobal()
        self.assertIsInstance(p.settings, GlobalSettings)
        self.assertFalse(p.settings.isReadOnly())
        self.assertFalse(p.settings.isRemovable())
        
    def test_Parameter6(self):#test from global to local
        p = Parameter(None)
        p.enableGlobal()
        self.assertIsInstance(p.settings, GlobalSettings)
        p.settings.setRemovable(False)
        p.settings.setReadOnly(False)
        p.enableLocal()
        self.assertIsInstance(p.settings, LocalSettings)
        self.assertFalse(p.settings.isReadOnly())
        self.assertFalse(p.settings.isRemovable())
        
    def test_Parameter7(self):#test from global to local
        p = Parameter(None)
        p.enableGlobal()
        self.assertIsInstance(p.settings, GlobalSettings)
        p.settings.setRemovable(True)
        p.settings.setReadOnly(True)
        p.enableLocal()
        self.assertIsInstance(p.settings, LocalSettings)
        self.assertTrue(p.settings.isReadOnly())
        self.assertTrue(p.settings.isRemovable())

    def test_Parameter8(self):#test str
        p = Parameter(42)
        self.assertEqual(str(p), "42")
    
    def test_Parameter9(self):#test repr
        p = Parameter(42)
        self.assertEqual(repr(p), "Parameter: 42")
    
    def test_Parameter10(self):#test hash
        p1 = Parameter(42)
        p2 = Parameter(42)
        self.assertEqual(hash(p1), hash(p2))
        p3 = Parameter(43)
        self.assertNotEqual(hash(p1), hash(p3))
        p4 = Parameter(42)
        p4.settings.setReadOnly(True)
        self.assertNotEqual(hash(p1), hash(p4))
        
if __name__ == '__main__':
    unittest.main()
