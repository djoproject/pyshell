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
        
import unittest
from pyshell.system.context import ContextParameter, ContextParameterManager, _convertToSetList, LocalContextSettings, GlobalContextSettings
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

    ## ContextSettings and LocalContextSettings ##
    
    def test_localSettings1(self):
        lcs = LocalContextSettings(readOnly = False, removable = False)
        self.assertFalse(lcs.isReadOnly())
        self.assertFalse(lcs.isRemovable())

    def test_localSettings2(self):
        lcs = LocalContextSettings(readOnly = True, removable = True)
        self.assertTrue(lcs.isReadOnly())
        self.assertTrue(lcs.isRemovable())
    
    def test_localSettings3(self):#setIndex with correct value
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2,index=1  )
        self.assertEqual(c.getSelectedValue(),1)
        c.settings.setIndex(2)
        self.assertEqual(c.getSelectedValue(),2)

    def test_localSettings4(self):#setIndex with incorrect value
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2,index=1  )
        self.assertEqual(c.getSelectedValue(),1)
        self.assertRaises(ParameterException,c.settings.setIndex,23)

    def test_localSettings5(self):#setIndex with invalid value
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2,index=1  )
        self.assertEqual(c.getSelectedValue(),1)
        self.assertRaises(ParameterException,c.settings.setIndex,"plop")

    def test_localSettings6(self):#setIndex with valid value and readonly
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(), settings=LocalContextSettings(readOnly=True))
        self.assertRaises(ParameterException, )

    def test_localSettings7(self):#tryToSetIndex with correct value
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2 )
        self.assertEqual(c.getSelectedValue(),0)
        c.settings.tryToSetIndex(3)
        self.assertEqual(c.getSelectedValue(),3)

    def test_localSettings8(self):#tryToSetIndex with incorrect value
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2 )
        self.assertEqual(c.getSelectedValue(),0)
        c.settings.tryToSetIndex(23)
        self.assertEqual(c.getSelectedValue(),0)

    def test_localSettings9(self):#tryToSetIndex with invalid value
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2 )
        self.assertEqual(c.getSelectedValue(),0)
        c.settings.tryToSetIndex("plop")
        self.assertEqual(c.getSelectedValue(),0)

    def test_localSettings10(self):#tryToSetIndex with incorrect value and default value recomputing
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2, index=1 )
        self.assertEqual(c.getSelectedValue(),1)
        c.defaultIndex = 45
        c.settings.tryToSetIndex(80)
        self.assertEqual(c.getSelectedValue(),1)

    def test_localSettings11(self):#tryToSetIndex with valid value and readonly
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(),defaultIndex=2, settings=LocalContextSettings(readOnly=True ))
        self.assertEqual(c.getSelectedValue(),0)
        c.settings.tryToSetIndex(3)
        self.assertEqual(c.getSelectedValue(),3)
        
    def test_localSettings12(self):#tryToSetIndex, create a test to set defaultIndex
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(), index = 3, defaultIndex = 1)
        self.assertEqual(c.getSelectedValue(), 3)
        EnvironmentParameter.setValue(c, (11,22,33,) )
        c.settings.tryToSetIndex(23)
        self.assertEqual(c.getSelectedValue(), 22)

    def test_localSettings13(self):#setIndexValue with a valid value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker() )
        self.assertEqual(c.getSelectedValue(),"aa")
        c.settings.setIndexValue("cc")
        self.assertEqual(c.getSelectedValue(),"cc")

    def test_localSettings14(self):#setIndexValue with a valid value but inexisting
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker() )
        self.assertEqual(c.getSelectedValue(),"aa")
        self.assertRaises(ParameterException,c.settings.setIndexValue, "ee")

    def test_localSettings15(self):#setIndexValue with an invalid value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker() )
        self.assertEqual(c.getSelectedValue(),"aa")
        self.assertRaises(ParameterException,c.settings.setIndexValue, object())

    def test_localSettings16(self):#setIndexValue with valid value and readonly
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), settings=LocalContextSettings(readOnly=True ))
        self.assertEqual(c.getSelectedValue(),"aa")
        c.settings.setIndexValue("cc")
        self.assertEqual(c.getSelectedValue(),"cc")

    def test_localSettings17(self):#setDefaultIndex with correct value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2)
        self.assertEqual(c.settings.getDefaultIndex(), 2)
        c.settings.setDefaultIndex(1)
        self.assertEqual(c.settings.getDefaultIndex(), 1)

    def test_localSettings18(self):#setDefaultIndex with incorrect value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2)
        self.assertRaises(ParameterException,c.settings.setDefaultIndex, 23)

    def test_localSettings19(self):#setDefaultIndex with invalid value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2)
        self.assertRaises(ParameterException,c.settings.setDefaultIndex, "plop")

    def test_localSettings20(self):#setDefaultIndex with valid value and readonly
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2, settings=LocalContextSettings(readOnly=True))
        self.assertRaises(ParameterException,c.settings.setDefaultIndex, 1)

    def test_localSettings21(self):#tryToSetDefaultIndex with correct value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2)
        self.assertEqual(c.settings.getDefaultIndex(), 2)
        c.settings.tryToSetDefaultIndex(1)
        self.assertEqual(c.settings.getDefaultIndex(), 1)

    def test_localSettings22(self):#tryToSetDefaultIndex with incorrect value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2)
        self.assertEqual(c.settings.getDefaultIndex(), 2)
        c.settings.tryToSetDefaultIndex(100)
        self.assertEqual(c.settings.getDefaultIndex(), 2)

    def test_localSettings23(self):#tryToSetDefaultIndex with invalid value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2)
        self.assertEqual(c.settings.getDefaultIndex(), 2)
        c.settings.tryToSetDefaultIndex("toto")
        self.assertEqual(c.settings.getDefaultIndex(), 2)

    def test_localSettings24(self):#tryToSetDefaultIndex with valid value and readonly
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2, settings=LocalContextSettings(readOnly=True))
        self.assertRaises(ParameterException,c.settings.tryToSetDefaultIndex, 1)
        
    def test_localSettings25(self): #tryToSetDefaultIndex, create a test to set defaultIndex to zero
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker(), defaultIndex = 3)
        self.assertEqual(c.settings.getDefaultIndex(), 3)
        EnvironmentParameter.setValue(c, (11,22,33,) )
        c.settings.tryToSetDefaultIndex(23)
        self.assertEqual(c.settings.getDefaultIndex(), 0)

    def test_localSettings26(self):#test reset
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2, index=1)
        self.assertEqual(c.settings.getDefaultIndex(), 2)
        self.assertEqual(c.settings.getIndex(), 1)
        c.settings.reset()
        self.assertEqual(c.settings.getDefaultIndex(), 2)
        self.assertEqual(c.settings.getIndex(), 2)
        
    def test_localSettings27(self):#test getProperties
        c = ContextParameter( (0,1,2,3,) ,index=2, defaultIndex=3, settings=LocalContextSettings( removable=False, readOnly=True))
        self.assertEqual(c.settings.getProperties(), (('removable', False), ('readOnly', True), ('transient', True), ('transientIndex', True), ('defaultIndex', 3)))
    
    ## GlobalContextSettings ##

    def test_globalSettings1(self): #__init__ test each properties, True
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), settings=GlobalContextSettings(readOnly = True, removable = True, transient = True, transientIndex = True ))
        self.assertTrue(c.settings.isReadOnly())
        self.assertTrue(c.settings.isRemovable())
        self.assertTrue(c.settings.isTransient())
        self.assertTrue(c.settings.isTransientIndex())

    def test_globalSettings2(self): #__init__ test each properties, False
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), settings=GlobalContextSettings(readOnly = False, removable = False, transient = False, transientIndex = False ))
        self.assertFalse(c.settings.isReadOnly())
        self.assertFalse(c.settings.isRemovable())
        self.assertFalse(c.settings.isTransient())
        self.assertFalse(c.settings.isTransientIndex())
        
    def test_globalSettings3(self):#test setTransientIndex in readonly mode
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), settings=GlobalContextSettings(readOnly=True ))
        self.assertRaises(ParameterException,c.settings.setTransientIndex, True)

    def test_globalSettings4(self):#test setTransientIndex with invalid bool
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker() , settings=GlobalContextSettings())
        self.assertRaises(ParameterException,c.settings.setTransientIndex, "plop")

    def test_globalSettings5(self):#test setTransientIndex with valid bool
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), settings=GlobalContextSettings())
        self.assertFalse(c.settings.isTransientIndex())
        c.settings.setTransientIndex(True)
        self.assertTrue(c.settings.isTransientIndex())

    def test_globalSettings6(self):#test getProperties not transient index
        c = ContextParameter( (0,1,2,3,) ,index=2, defaultIndex=3, settings=GlobalContextSettings(transientIndex = False))
        self.assertEqual(c.settings.getProperties(), (('removable', True), ('readOnly', False), ('transient', False), ('transientIndex', False), ('defaultIndex', 3), ('index', 2)))
    
    def test_globalSettings7(self):#test getProperties transient index
        c = ContextParameter( (0,1,2,3,) ,index=2, defaultIndex=3, settings=GlobalContextSettings( transientIndex=True))
        self.assertEqual(c.settings.getProperties(), (('removable', True), ('readOnly', False), ('transient', False), ('transientIndex', True), ('defaultIndex', 3)))

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
        self.assertEqual(c.settings.getIndex(),1)

    def test_contextConstructor6(self):#test invalid index
        c = ContextParameter( (0,1,2,3,), index=23)
        self.assertEqual(c.settings.getIndex(),0)

    def test_contextConstructor7(self):#test valid default index
        c = ContextParameter( (0,1,2,3,), defaultIndex=1)
        self.assertEqual(c.settings.getDefaultIndex(),1)

    def test_contextConstructor8(self):#test invalid default index
        c = ContextParameter( (0,1,2,3,), defaultIndex=42)
        self.assertEqual(c.settings.getDefaultIndex(),0)

    def test_contextConstructor9(self):#test both invalid index AND invalid default index
        c = ContextParameter( (0,1,2,3,), index=23, defaultIndex=42)
        self.assertEqual(c.settings.getDefaultIndex(),0)
        self.assertEqual(c.settings.getIndex(),0)

    def test_contextConstructor10(self):#test transientIndex
        c = ContextParameter( (0,1,2,3,) ,index=2, settings=GlobalContextSettings(transientIndex=False))
        self.assertFalse(c.settings.isTransientIndex())
        self.assertEqual(c.settings.getProperties(),(('removable', True), ('readOnly', False), ('transient', False), ('transientIndex', False), ('defaultIndex', 0), ('index', 2)))
        
        c = ContextParameter( (0,1,2,3,) ,index=2, settings=GlobalContextSettings(transientIndex=True))
        self.assertTrue(c.settings.isTransientIndex())
        self.assertEqual(c.settings.getProperties(), (('removable', True), ('readOnly', False), ('transient', False), ('transientIndex', True), ('defaultIndex', 0)))

    #test method

    def test_context1(self):#setValue with valid value
        c = ContextParameter( (0,), typ=IntegerArgChecker() )
        c.setValue((1,2,3,"4",))
        self.assertEqual(c.getValue(), [1,2,3,4,])

    def test_context2(self):#setValue with invalid value
        c = ContextParameter( (0,), typ=IntegerArgChecker() )
        self.assertRaises(argException,c.setValue, (1,2,3,"plop",) )

    def test_context3(self):#test addValues to add valid 
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker())
        c.addValues( (4,5,6,) )
        self.assertEqual(c.getValue(), [0,1,2,3,4,5,6])

    def test_context4(self):#test addValues to add invalid value
        c = ContextParameter( (0,1,2,3,), typ=IntegerArgChecker())
        self.assertRaises(argException, c.addValues, (4,5,"plop",) )

    def test_context5(self):#removeValues, remove all value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker())
        self.assertRaises(ParameterException, c.removeValues, ("aa","bb","cc","dd",) )

    def test_context6(self):#removeValues, remove unexisting value
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker())
        self.assertEqual(c.getValue(), ["aa","bb","cc","dd"])
        c.removeValues( ("aa","aa","ee","ff",) )
        self.assertEqual(c.getValue(), ["bb","cc","dd"])
    
    def test_context7(self):#removeValues, try to remove with read only
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), settings=LocalContextSettings(readOnly=True))
        self.assertEqual(c.getValue(), ["aa","bb","cc","dd"])
        self.assertRaises(ParameterException, c.removeValues, ("aa","aa","ee","ff",) )
        
    def test_context8(self):#removeValues, success remove
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker())
        self.assertEqual(c.getValue(), ["aa","bb","cc","dd"])
        c.removeValues( ("aa",) )
        self.assertEqual(c.getValue(), ["bb","cc","dd"])
        
    def test_context9(self):#removeValues, success remove with index computation
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2, index=3)
        self.assertEqual(c.getValue(), ["aa","bb","cc","dd"])
        self.assertEqual(c.settings.getDefaultIndex(), 2)
        self.assertEqual(c.settings.getIndex(), 3)
        c.removeValues( ("cc","dd",) )
        self.assertEqual(c.getValue(), ["aa","bb"])
        self.assertEqual(c.settings.getDefaultIndex(), 0)
        self.assertEqual(c.settings.getIndex(), 0)

    def test_context10(self):#test repr
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2, index=1)
        self.assertEqual(repr(c), "Context, available values: ['aa', 'bb', 'cc', 'dd'], selected index: 1, selected value: bb")

    def test_context11(self):#test str
        c = ContextParameter( ("aa","bb","cc","dd",), typ=stringArgChecker(), defaultIndex=2, index=1)
        self.assertEqual(str(c), "bb")

    def test_context12(self):#test enableGlobal
        c = ContextParameter( ("aa","bb","cc","dd",) )

        self.assertIsInstance(c.settings, LocalContextSettings)
        c.enableGlobal()
        self.assertIsInstance(c.settings, GlobalContextSettings)
        s = c.settings
        c.enableGlobal()
        self.assertIs(c.settings, s)

    def test_context13(self):#test enableLocal
        c = ContextParameter( ("aa","bb","cc","dd",) )

        self.assertIsInstance(c.settings, LocalContextSettings)
        s = c.settings
        c.enableGlobal()
        self.assertIsInstance(c.settings, GlobalContextSettings)
        c.enableLocal()
        self.assertIsInstance(c.settings, LocalContextSettings)
        self.assertIsNot(c.settings, s)
        s = c.settings
        c.enableLocal()
        self.assertIs(c.settings, s)

    def test_context14(self):
        c = ContextParameter( ("aa","bb","cc","dd",), settings=LocalContextSettings(readOnly = True, removable = True), index=2, defaultIndex=3)
        c.enableGlobal()
        self.assertIsInstance(c.settings, GlobalContextSettings)
        self.assertTrue(c.settings.isReadOnly())
        self.assertTrue(c.settings.isRemovable())
        self.assertEqual(c.settings.getIndex(),2)
        self.assertEqual(c.settings.getDefaultIndex(),3)

    def test_context15(self):
        c = ContextParameter( ("aa","bb","cc","dd",), settings=LocalContextSettings(readOnly = False, removable = False), index=3, defaultIndex=2)
        c.enableGlobal()
        self.assertIsInstance(c.settings, GlobalContextSettings)
        self.assertFalse(c.settings.isReadOnly())
        self.assertFalse(c.settings.isRemovable())
        self.assertEqual(c.settings.getIndex(),3)
        self.assertEqual(c.settings.getDefaultIndex(),2)

    def test_context15(self):
        c = ContextParameter( ("aa","bb","cc","dd",), settings=LocalContextSettings(readOnly = True, removable = True), index=2, defaultIndex=3)
        c.enableGlobal()
        self.assertIsInstance(c.settings, GlobalContextSettings)
        c.enableLocal()
        self.assertIsInstance(c.settings, LocalContextSettings)
        
        self.assertTrue(c.settings.isReadOnly())
        self.assertTrue(c.settings.isRemovable())
        self.assertEqual(c.settings.getIndex(),2)
        self.assertEqual(c.settings.getDefaultIndex(),3)

    def test_context16(self):
        c = ContextParameter( ("aa","bb","cc","dd",), settings=LocalContextSettings(readOnly = False, removable = False), index=3, defaultIndex=2)
        c.enableGlobal()
        self.assertIsInstance(c.settings, GlobalContextSettings)
        c.enableLocal()
        self.assertIsInstance(c.settings, LocalContextSettings)

        self.assertFalse(c.settings.isReadOnly())
        self.assertFalse(c.settings.isRemovable())
        self.assertEqual(c.settings.getIndex(),3)
        self.assertEqual(c.settings.getDefaultIndex(),2)
                
if __name__ == '__main__':
    unittest.main()
