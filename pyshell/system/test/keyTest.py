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
from pyshell.system.key import CryptographicKeyParameter, CryptographicKeyParameterManager
from pyshell.utils.key import CryptographicKey
from pyshell.system.environment import EnvironmentParameter

class KeyTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_manager(self):
        self.assertNotEqual(CryptographicKeyParameterManager(), None)
        
    def test_addNotYetParametrizedButValidKey(self):
        manager = CryptographicKeyParameterManager()
        manager.setParameter("test.key", "0x1122ff")
        self.assertTrue(manager.hasParameter("t.k"))
        param = manager.getParameter("te.ke")
        self.assertTrue(isinstance(param, CryptographicKeyParameter))
        self.assertTrue(isinstance(param.getValue(), CryptographicKey))
        self.assertEqual(str(param.getValue()), "0x1122ff")
        
    def test_addNotYetParametrizedAndInValidKey(self):
        manager = CryptographicKeyParameterManager()
        self.assertRaises(Exception,manager.setParameter, "test.key", "0xplop")
        
    def test_addValidParameter(self):
        manager = CryptographicKeyParameterManager()
        manager.setParameter("test.key", CryptographicKeyParameter("0x1122ff"))
        self.assertTrue(manager.hasParameter("t.k"))
        param = manager.getParameter("te.ke")
        self.assertTrue(isinstance(param, CryptographicKeyParameter))
        self.assertTrue(isinstance(param.getValue(), CryptographicKey))
        self.assertEqual(str(param.getValue()), "0x1122ff")
        
    def test_addNotAllowedParameter(self):
        manager = CryptographicKeyParameterManager()
        self.assertRaises(Exception,manager.setParameter, "test.key", EnvironmentParameter("0x1122ff"))
        
if __name__ == '__main__':
    unittest.main()
