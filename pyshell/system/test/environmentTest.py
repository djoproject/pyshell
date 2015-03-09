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
from pyshell.system.context import ContextParameter
from pyshell.arg.argchecker import listArgChecker, ArgChecker, IntegerArgChecker
from threading import Lock

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
        e = EnvironmentParameter("plop", removable = True)
        self.assertTrue(e.isRemovable())
        self.assertEqual(e.getProperties(), (("removable", True),("readonly",False),) )
        
        e = EnvironmentParameter("plop", removable = False)
        self.assertFalse(e.isRemovable())
        self.assertEqual(e.getProperties(), (("removable", False),("readonly",False),) )
        
    def test_environmentConstructor2(self): #test readonly boolean
        e = EnvironmentParameter("plop", readonly = True)
        self.assertTrue(e.isReadOnly())
        self.assertEqual(e.getProperties(), (("removable", True),("readonly",True),) )
        
        e = EnvironmentParameter("plop", readonly = False)
        self.assertFalse(e.isReadOnly())
        self.assertEqual(e.getProperties(), (("removable", True),("readonly",False),) )
        
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
        
    def test_environmentMethod1(self): #test getProperties
        pass #TODO
        
    def test_environmentMethod2(self): #_raiseIfReadOnly with not readonly
        pass #TODO
        
    def test_environmentMethod3(self): #_raiseIfReadOnly with readonly and method name
        pass #TODO
        
    def test_environmentMethod4(self): #_raiseIfReadOnly with readonly and no method name
        pass #TODO
        
    def test_environmentMethod5(self): #getLock with lock disabled
        pass #TODO
        
    def test_environmentMethod6(self): #getLock without lock disabled
        pass #TODO
        
    def test_environmentMethod7(self): #getLockID with lock disabled
        pass #TODO
        
    def test_environmentMethod8(self): #getLockID without lock disabled
        pass #TODO
        
    def test_environmentMethod9(self): #isLockEnable
        pass #TODO
        
    def test_environmentMethod10(self): #addValues readonly
        pass #TODO
        
    def test_environmentMethod11(self): #addValues with non list typ
        pass #TODO
        
    def test_environmentMethod12(self): #addValues with not iterable value
        pass #TODO
        
    def test_environmentMethod13(self): #addValues with invalid values in front of the checker
        pass #TODO
        
    def test_environmentMethod14(self): #removeValues readonly
        pass #TODO
        
    def test_environmentMethod15(self): #removeValues with non list typ
        pass #TODO
        
    def test_environmentMethod16(self): #removeValues with not iterable value
        pass #TODO
        
    def test_environmentMethod17(self): #removeValues with existing and not existing value
        pass #TODO
        
    def test_environmentMethod18(self): #setValue valid
        pass #TODO
        
    def test_environmentMethod19(self): #setValue unvalid
        pass #TODO
        
    def test_environmentMethod20(self): #isReadOnly from consctructor
        pass #TODO
        
    def test_environmentMethod21(self): #isRemovable from consctructor
        pass #TODO
        
    def test_environmentMethod22(self): #setReadOnly with not valid bool
        pass #TODO
        
    def test_environmentMethod23(self): #setReadOnly with valid bool
        pass #TODO
        
    def test_environmentMethod24(self): #setRemovable readonly
        pass #TODO
        
    def test_environmentMethod25(self): #setRemovable with not valid bool
        pass #TODO
        
    def test_environmentMethod26(self): #setRemovable with valid bool
        pass #TODO
        
    def test_environmentMethod27(self): #repr
        pass #TODO
        
if __name__ == '__main__':
    unittest.main()
