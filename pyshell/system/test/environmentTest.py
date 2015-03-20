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
from pyshell.system.environment import EnvironmentParameter, EnvironmentParameterManager, _lockSorter, ParametersLocker
from pyshell.utils.exception import ParameterException
from pyshell.system.context  import ContextParameter
from pyshell.system.settings import LocalSettings
from pyshell.arg.argchecker  import listArgChecker, ArgChecker, IntegerArgChecker
from pyshell.arg.exception   import argException
from threading import Lock
from thread import LockType

class DummyLock(object):
    def __init__(self,value):
        self.value = value
        self.lock = Lock()
        
    def getLockID(self):
        return self.value
        
    def getLock(self):
        return self.lock

class EnvironmentTest(unittest.TestCase):
    def setUp(self):
        pass

    ## misc ##
    def test_misc1(self):#test lockSorter
        sortedList = sorted([DummyLock(5), DummyLock(1), DummyLock(4),DummyLock(0), DummyLock(888)], cmp=_lockSorter)
        self.assertEqual(sortedList[0].value,0)
        self.assertEqual(sortedList[1].value,1)
        self.assertEqual(sortedList[2].value,4)
        self.assertEqual(sortedList[3].value,5)
        self.assertEqual(sortedList[4].value,888)
        
    def test_misc2(self):#test ParametersLocker, just try a lock in a single thread with several lock
        lockers = ParametersLocker([DummyLock(5), DummyLock(1), DummyLock(4),DummyLock(0), DummyLock(888)])
        with lockers:
            pass

    ## manager ##

    def test_manager1(self):
        self.assertNotEqual(EnvironmentParameterManager(), None)

    def test_manager2(self):#try to set valid value
        manager = EnvironmentParameterManager() 
        param = manager.setParameter( "env.test", ("plop",))
        self.assertEqual(param.getValue(),["plop"])
    
    def test_manager3(self):#try to set valid parameter
        manager = EnvironmentParameterManager() 
        param = manager.setParameter( "env.test", EnvironmentParameter( ("plop",) ))
        self.assertEqual(param.getValue(),["plop"])

    def test_manager4(self):#try to set invalid parameter
        manager = EnvironmentParameterManager()
        self.assertRaises(ParameterException,manager.setParameter, "env.test", ContextParameter("0x1122ff"))

    ## parameter constructor ##
    
    def test_environmentConstructor1(self): #test removable boolean
        e = EnvironmentParameter("plop", settings=LocalSettings(removable = True))
        self.assertTrue(e.settings.isRemovable())
        self.assertEqual(e.settings.getProperties(), (("removable", True),("readOnly",False), ('transient', True)) )
        
        e = EnvironmentParameter("plop", settings=LocalSettings(removable = False))
        self.assertFalse(e.settings.isRemovable())
        self.assertEqual(e.settings.getProperties(), (("removable", False),("readOnly",False), ('transient', True)) )
        
    def test_environmentConstructor2(self): #test readonly boolean
        e = EnvironmentParameter("plop", settings=LocalSettings(readOnly = True))
        self.assertTrue(e.settings.isReadOnly())
        self.assertEqual(e.settings.getProperties(), (("removable", True),("readOnly",True), ('transient', True)) )
        
        e = EnvironmentParameter("plop", settings=LocalSettings(readOnly = False))
        self.assertFalse(e.settings.isReadOnly())
        self.assertEqual(e.settings.getProperties(), (("removable", True),("readOnly",False), ('transient', True)) )
        
    def test_environmentConstructor3(self): #test typ None
        e = EnvironmentParameter("plop")
        self.assertIsInstance(e.typ, listArgChecker)
        self.assertEqual(e.typ.minimumSize, None)
        self.assertEqual(e.typ.maximumSize, None)

        self.assertEqual(e.typ.checker.__class__.__name__, ArgChecker.__name__)
        self.assertIsInstance(e.typ.checker, ArgChecker)
        
    def test_environmentConstructor4(self): #test typ not an argchecker
        self.assertRaises(ParameterException, EnvironmentParameter, "plop", object())
        
    def test_environmentConstructor5(self): #test typ valid argchecker not a list + isAListType
        e = EnvironmentParameter(42, IntegerArgChecker())
        self.assertIsInstance(e.typ, IntegerArgChecker)
        self.assertFalse(e.isAListType())
        
    def test_environmentConstructor6(self): #test typ valid argchecker list + isAListType
        e = EnvironmentParameter(42, listArgChecker(IntegerArgChecker()))
        self.assertIsInstance(e.typ, listArgChecker)
        self.assertEqual(e.typ.minimumSize, None)
        self.assertEqual(e.typ.maximumSize, None)
        self.assertEqual(e.typ.checker.__class__.__name__, IntegerArgChecker.__name__)
        self.assertIsInstance(e.typ.checker, IntegerArgChecker)
        self.assertTrue(e.isAListType())
        
    ## parameter method ##
            
    def test_environmentMethod2(self): #_raiseIfReadOnly with not readonly
        e = EnvironmentParameter("plop", settings=LocalSettings(readOnly = False))
        self.assertEqual(e.settings._raiseIfReadOnly(),None)
        
    def test_environmentMethod3(self): #_raiseIfReadOnly with readonly and method name
        e = EnvironmentParameter("plop", settings=LocalSettings(readOnly = True))
        self.assertRaises(ParameterException,e.settings._raiseIfReadOnly,"meth")
        
    def test_environmentMethod4(self): #_raiseIfReadOnly with readonly and no method name
        e = EnvironmentParameter("plop", settings=LocalSettings(readOnly = True))
        self.assertRaises(ParameterException,e.settings._raiseIfReadOnly)
        
    def test_environmentMethod5(self): #getLock with lock disabled
        e = EnvironmentParameter("plop")
        e.enableLocal()
        self.assertEqual(e.getLock(),None)
        self.assertEqual(e.getLockID(),-1)
        self.assertFalse(e.isLockEnable())
        
    def test_environmentMethod6(self): #getLock without lock disabled
        e = EnvironmentParameter("plop")
        e.enableGlobal()
        self.assertEqual(type(e.getLock()),LockType)
        self.assertEqual(e.getLockID(),0)
        self.assertTrue(e.isLockEnable())
        
    def test_environmentMethod10(self): #addValues readonly
        e = EnvironmentParameter("plop", settings=LocalSettings(readOnly=True))
        self.assertRaises(ParameterException, e.addValues, ("aa", "bb", "cc",))
        
    def test_environmentMethod11(self): #addValues with non list typ
        e = EnvironmentParameter(42, IntegerArgChecker())
        self.assertRaises(ParameterException, e.addValues, (1, 23, 69,))
        
    def test_environmentMethod12(self): #addValues with not iterable value
        e = EnvironmentParameter(42)
        e.addValues(33)
        self.assertEqual(e.getValue(), [42,33])
        
    def test_environmentMethod13(self): #addValues with invalid values in front of the checker
        e = EnvironmentParameter(42, listArgChecker(IntegerArgChecker()))
        self.assertRaises(argException, e.addValues, ("plop", "plip", "plap",))

    def test_environmentMethod13b(self): #addValues success
        e = EnvironmentParameter("plop")
        e.addValues( ("aa", "bb", "cc",))
        self.assertEqual(e.getValue(), ["plop", "aa", "bb", "cc"])
        
    def test_environmentMethod14(self): #removeValues readonly
        e = EnvironmentParameter("plop", settings=LocalSettings(readOnly=True))
        self.assertRaises(ParameterException, e.removeValues,"plop" )
        
    def test_environmentMethod15(self): #removeValues with non list typ
        e = EnvironmentParameter(42, IntegerArgChecker())
        self.assertRaises(ParameterException, e.removeValues,42 )
        
    def test_environmentMethod16(self): #removeValues with not iterable value
        e = EnvironmentParameter("plop")
        e.removeValues("plop" )
        self.assertEqual(e.getValue(),[])
        
    def test_environmentMethod17(self): #removeValues with existing and not existing value
        e = EnvironmentParameter(["plop","plip","plap","plup"])
        e.removeValues( ("plip", "plip", "ohoh", "titi", "plop",))
        self.assertEqual(e.getValue(),["plap","plup"])
        
    def test_environmentMethod18(self): #setValue valid
        e = EnvironmentParameter("plop")
        self.assertEqual(e.getValue(),["plop"])
        e.setValue("plip")
        self.assertEqual(e.getValue(),["plip"])
        e.setValue( ("aa","bb","cc",))
        self.assertEqual(e.getValue(),["aa","bb","cc"])

        e = EnvironmentParameter(42, IntegerArgChecker())
        self.assertEqual(e.getValue(),42)
        e.setValue(23)
        self.assertEqual(e.getValue(),23)
        
    def test_environmentMethod19(self): #setValue unvalid 
        e = EnvironmentParameter(42, IntegerArgChecker())
        self.assertRaises(argException, e.setValue, "plop")

        e = EnvironmentParameter(42, listArgChecker(IntegerArgChecker()))
        self.assertRaises(argException, e.setValue, ("plop","plap",))
                
    def test_environmentMethod22(self): #setReadOnly with not valid bool
        e = EnvironmentParameter("plop")
        self.assertRaises(ParameterException, e.settings.setReadOnly, object())
        
    def test_environmentMethod23(self): #setReadOnly with valid bool + getProp
        e = EnvironmentParameter("plop")
        self.assertFalse(e.settings.isReadOnly())
        self.assertEqual(e.settings.getProperties(), (("removable", True),("readOnly",False), ('transient', True)) )

        e.settings.setReadOnly(True)
        self.assertTrue(e.settings.isReadOnly())
        self.assertEqual(e.settings.getProperties(), (("removable", True),("readOnly",True), ('transient', True)) )

        e.settings.setReadOnly(False)
        self.assertFalse(e.settings.isReadOnly())
        self.assertEqual(e.settings.getProperties(), (("removable", True),("readOnly",False), ('transient', True)) )
        
    def test_environmentMethod24(self): #setRemovable readonly
        e = EnvironmentParameter("plop", settings=LocalSettings(readOnly = True))
        self.assertRaises(ParameterException, e.settings.setRemovable, True)
        
    def test_environmentMethod25(self): #setRemovable with not valid bool
        e = EnvironmentParameter("plop")
        self.assertRaises(ParameterException, e.settings.setRemovable, object())
        
    def test_environmentMethod26(self): #setRemovable with valid bool + getProp
        e = EnvironmentParameter("plop")
        self.assertTrue(e.settings.isRemovable())
        self.assertEqual(e.settings.getProperties(), (("removable", True),("readOnly",False), ('transient', True)) )

        e.settings.setRemovable(False)
        self.assertFalse(e.settings.isRemovable())
        self.assertEqual(e.settings.getProperties(), (("removable", False),("readOnly",False), ('transient', True)) )

        e.settings.setRemovable(True)
        self.assertTrue(e.settings.isRemovable())
        self.assertEqual(e.settings.getProperties(), (("removable", True),("readOnly",False), ('transient', True)) )
        
    def test_environmentMethod27(self): #repr
        e = EnvironmentParameter("plop")
        self.assertEqual(repr(e),"Environment, value:['plop']")

    def test_environmentMethod28(self): #str
        e = EnvironmentParameter("plop")
        self.assertEqual(str(e),"['plop']")
        
    #TODO test hash, enableGlobal, enableLocal
        
if __name__ == '__main__':
    unittest.main()
