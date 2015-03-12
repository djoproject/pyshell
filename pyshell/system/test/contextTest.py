#!/usr/bin/python
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

#TODO test
    #some of the method internally execute updateOrigin
        #check the method that use it
        #and check the method that does not use it
        
import unittest
from pyshell.system.context import ContextParameter, ContextParameterManager, _convertToSetList
from pyshell.system.environment import EnvironmentParameter
from pyshell.arg.argchecker import listArgChecker, ArgChecker, IntegerArgChecker,environmentParameterChecker, stringArgChecker
from pyshell.utils.exception import ParameterException
from pyshell.arg.exception   import argException, argInitializationException

class ContextTest(unittest.TestCase):
    def setUp(self):
        pass

    ## misc ##
    def test_convertToSetList(self):
        self.assertEqual(_convertToSetList(("aaa","bbb","aaa","ccc","ccc")), ["aaa","bbb","ccc"])

    ## manager ##

    def test_manager1(self):
        self.assertNotEqual(ContextParameterManager(), None)

    def test_manager2(self):#try to set valid value
        manager = ContextParameterManager() 
        param = manager.setParameter( "context.test", ("plop",))
        self.assertEqual(param.getSelectedValue(),"plop")
        self.assertEqual(param.getValue(),["plop"])
    
    def test_manager3(self):#try to set valid parameter
        manager = ContextParameterManager() 
        param = manager.setParameter( "context.test", ContextParameter( ("plop",) ))
        self.assertEqual(param.getSelectedValue(),"plop")
        self.assertEqual(param.getValue(),["plop"])

    def test_manager4(self):#try to set invalid parameter
        manager = ContextParameterManager()
        self.assertRaises(ParameterException,manager.setParameter, "test.var", EnvironmentParameter("0x1122ff"))

    ## parameter ##

    #on constructor
    def test_contextConstructor1(self):#None typ
        c = ContextParameter( ("toto",), typ=None )
        self.assertIsInstance(c.typ, listArgChecker)
        self.assertEqual(c.typ.minimumSize, 1)
        self.assertEqual(c.typ.maximumSize, None)

        self.assertEqual(c.typ.checker.__class__.__name__, ArgChecker.__name__)
        self.assertIsInstance(c.typ.checker, ArgChecker)

    def test_contextConstructor2(self):#arg typ
        c = ContextParameter( (0,), typ=IntegerArgChecker() )
        self.assertIsInstance(c.typ, listArgChecker)
        self.assertEqual(c.typ.minimumSize, 1)
        self.assertEqual(c.typ.maximumSize, None)

        self.assertIsInstance(c.typ.checker, IntegerArgChecker)

    def test_contextConstructor2b(self):#arg typ with min size of 0
        self.assertRaises(argInitializationException, ContextParameter, ("plop", ), environmentParameterChecker("plip"))

    def test_contextConstructor3(self):#list typ + #list typ with size not adapted to context
        lt = listArgChecker(IntegerArgChecker(), 3, 27)
        c = ContextParameter( (0,), typ=lt )
        self.assertIsInstance(c.typ, listArgChecker)
        self.assertEqual(c.typ.minimumSize, 1)
        self.assertEqual(c.typ.maximumSize, 27)
        self.assertIsInstance(c.typ.checker, IntegerArgChecker)

    def test_contextConstructor5(self):#test valid index
        c = ContextParameter( (0,1,2,3,), index=1)
        self.assertEqual(c.getIndex(),1)

    def test_contextConstructor6(self):#test invalid index
        c = ContextParameter( (0,1,2,3,), index=23)
        self.assertEqual(c.getIndex(),0)

    def test_contextConstructor7(self):#test valid default index
        c = ContextParameter( (0,1,2,3,), defaultIndex=1)
        self.assertEqual(c.getDefaultIndex(),1)

    def test_contextConstructor8(self):#test invalid default index
        c = ContextParameter( (0,1,2,3,), defaultIndex=42)
        self.assertEqual(c.getDefaultIndex(),0)

    def test_contextConstructor9(self):#test both invalid index AND invalid default index
        c = ContextParameter( (0,1,2,3,), index=23, defaultIndex=42)
        self.assertEqual(c.getDefaultIndex(),0)
        self.assertEqual(c.getIndex(),0)

    def test_contextConstructor10(self):#test transientIndex
        c = ContextParameter( (0,1,2,3,) ,index=2, transientIndex=False)
        self.assertFalse(c.isTransientIndex())
        self.assertEqual(c.getProperties(), (('defaultIndex', 0), ('removable', True), ('readonly', False), ('index', 2),))
        
        c = ContextParameter( (0,1,2,3,) ,index=2, transientIndex=True)
        self.assertTrue(c.isTransientIndex())
        self.assertEqual(c.getProperties(), (('defaultIndex', 0), ('removable', True), ('readonly', False),))

    #test method
    def test_context1(self):#test getProperties
        c = ContextParameter( (0,1,2,3,) ,index=2, defaultIndex=3, removable=False, readonly=True)
        self.assertEqual(c.getProperties(), (('defaultIndex', 3), ('removable', False), ('readonly', True), ('index', 2),))

    def test_context2(self):#setValue with valid value
        c = ContextParameter( (0,), typ=IntegerArgChecker() )
        c.setValue((1,2,3,"4",))
        self.assertEqual(c.getValue(), [1,2,3,4,])

    def test_context3(self):#setValue with invalid value
        c = ContextParameter( (0,), typ=IntegerArgChecker() )
        self.assertRaises(argException,c.setValue, (1,2,3,"plop",) )

    def test_context4(self):#setIndex with correct value
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2,index=1  )
        self.assertEqual(c.getSelectedValue(),1)
        c.setIndex(2)
        self.assertEqual(c.getSelectedValue(),2)

    def test_context5(self):#setIndex with incorrect value
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2,index=1  )
        self.assertEqual(c.getSelectedValue(),1)
        self.assertRaises(ParameterException,c.setIndex,23)

    def test_context6(self):#setIndex with invalid value
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2,index=1  )
        self.assertEqual(c.getSelectedValue(),1)
        self.assertRaises(ParameterException,c.setIndex,"plop")

    def test_context7(self):#setIndex with valid value and readonly
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),readonly=True  )
        self.assertRaises(ParameterException, )

    def test_context8(self):#tryToSetIndex with correct value
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2 )
        self.assertEqual(c.getSelectedValue(),0)
        c.tryToSetIndex(3)
        self.assertEqual(c.getSelectedValue(),3)

    def test_context9(self):#tryToSetIndex with incorrect value
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2 )
        self.assertEqual(c.getSelectedValue(),0)
        c.tryToSetIndex(23)
        self.assertEqual(c.getSelectedValue(),2)

    def test_context10(self):#tryToSetIndex with invalid value
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2 )
        self.assertEqual(c.getSelectedValue(),0)
        c.tryToSetIndex("plop")
        self.assertEqual(c.getSelectedValue(),2)

    def test_context11(self):#tryToSetIndex with incorrect value and default value recomputing
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2, index=1 )
        self.assertEqual(c.getSelectedValue(),1)
        c.defaultIndex = 45
        c.tryToSetIndex(80)
        self.assertEqual(c.getSelectedValue(),0)

    def test_context12(self):#tryToSetIndex with valid value and readonly
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2,readonly=True )
        self.assertEqual(c.getSelectedValue(),0)
        c.tryToSetIndex(3)
        self.assertEqual(c.getSelectedValue(),3)

    def test_context13(self):#setIndexValue with a valid value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker() )
        self.assertEqual(c.getSelectedValue(),"aa")
        c.setIndexValue("cc")
        self.assertEqual(c.getSelectedValue(),"cc")

    def test_context14(self):#setIndexValue with a valid value but inexisting
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker() )
        self.assertEqual(c.getSelectedValue(),"aa")
        self.assertRaises(ParameterException,c.setIndexValue, "ee")

    def test_context15(self):#setIndexValue with an invalid value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker() )
        self.assertEqual(c.getSelectedValue(),"aa")
        self.assertRaises(ParameterException,c.setIndexValue, object())

    def test_context16(self):#setIndexValue with valid value and readonly
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(),readonly=True )
        self.assertEqual(c.getSelectedValue(),"aa")
        c.setIndexValue("cc")
        self.assertEqual(c.getSelectedValue(),"cc")

    def test_context17(self):#test setTransientIndex in readonly mode
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(),readonly=True )
        self.assertRaises(ParameterException,c.setTransientIndex, True)

    def test_context18(self):#test setTransientIndex with invalid bool
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker() )
        self.assertRaises(ParameterException,c.setTransientIndex, "plop")

    def test_context19(self):#test setTransientIndex with valid bool
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker())
        self.assertFalse(c.isTransientIndex())
        c.setTransientIndex(True)
        self.assertTrue(c.isTransientIndex())

    def test_context21(self):#setDefaultIndex with correct value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2)
        self.assertEqual(c.getDefaultIndex(), 2)
        c.setDefaultIndex(1)
        self.assertEqual(c.getDefaultIndex(), 1)

    def test_context22(self):#setDefaultIndex with incorrect value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2)
        self.assertRaises(ParameterException,c.setDefaultIndex, 23)

    def test_context23(self):#setDefaultIndex with invalid value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2)
        self.assertRaises(ParameterException,c.setDefaultIndex, "plop")

    def test_context24(self):#setDefaultIndex with valid value and readonly
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2,readonly=True)
        self.assertRaises(ParameterException,c.setDefaultIndex, 1)

    def test_context25(self):#tryToSetDefaultIndex with correct value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2)
        self.assertEqual(c.getDefaultIndex(), 2)
        c.tryToSetDefaultIndex(1)
        self.assertEqual(c.getDefaultIndex(), 1)

    def test_context26(self):#tryToSetDefaultIndex with incorrect value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2)
        self.assertEqual(c.getDefaultIndex(), 2)
        c.tryToSetDefaultIndex(100)
        self.assertEqual(c.getDefaultIndex(), 0)

    def test_context27(self):#tryToSetDefaultIndex with invalid value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2)
        self.assertEqual(c.getDefaultIndex(), 2)
        c.tryToSetDefaultIndex("toto")
        self.assertEqual(c.getDefaultIndex(), 0)

    def test_context28(self):#tryToSetDefaultIndex with valid value and readonly
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2,readonly=True)
        self.assertRaises(ParameterException,c.tryToSetDefaultIndex, 1)

    def test_context29(self):#test reset
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2, index=1)
        self.assertEqual(c.getDefaultIndex(), 2)
        self.assertEqual(c.getIndex(), 1)
        c.reset()
        self.assertEqual(c.getDefaultIndex(), 2)
        self.assertEqual(c.getIndex(), 2)

    def test_context30(self):#test addValues to add valid 
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker())
        c.addValues( (4,5,6,) )
        self.assertEqual(c.getValue(), [0,1,2,3,4,5,6])

    def test_context31(self):#test addValues to add invalid value
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker())
        self.assertRaises(argException, c.addValues, (4,5,"plop",) )

    def test_context32(self):#removeValues, remove all value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker())
        self.assertRaises(ParameterException, c.removeValues, ("aa","bb","cc","dd",) )

    def test_context33(self):#removeValues, remove unexisting value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker())
        self.assertEqual(c.getValue(), ["aa","bb","cc","dd"])
        c.removeValues( ("aa","aa","ee","ff",) )
        self.assertEqual(c.getValue(), ["bb","cc","dd"])
    
    def test_context34(self):#removeValues, try to remove with read only
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(),readonly=True)
        self.assertEqual(c.getValue(), ["aa","bb","cc","dd"])
        self.assertRaises(ParameterException, c.removeValues, ("aa","aa","ee","ff",) )
        
    def test_context35(self):#removeValues, success remove
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker())
        self.assertEqual(c.getValue(), ["aa","bb","cc","dd"])
        c.removeValues( ("aa",) )
        self.assertEqual(c.getValue(), ["bb","cc","dd"])
        
    def test_context36(self):#removeValues, success remove with index computation
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2, index=3)
        self.assertEqual(c.getValue(), ["aa","bb","cc","dd"])
        self.assertEqual(c.getDefaultIndex(), 2)
        self.assertEqual(c.getIndex(), 3)
        c.removeValues( ("cc","dd",) )
        self.assertEqual(c.getValue(), ["aa","bb"])
        self.assertEqual(c.getDefaultIndex(), 0)
        self.assertEqual(c.getIndex(), 0)

    def test_context37(self):#test repr
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2, index=1)
        self.assertEqual(repr(c), "Context, available values: ['aa', 'bb', 'cc', 'dd'], selected index: 1, selected value: bb")

    def test_context38(self):#test str
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2, index=1)
        self.assertEqual(str(c), "bb")
        
if __name__ == '__main__':
    unittest.main()
