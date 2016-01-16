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
from pyshell.utils.key import CryptographicKey
from pyshell.utils.exception import KeyStoreException

class MiscTest(unittest.TestCase):
    def setUp(self):
        pass 
        
    def test_notValidKeyString1(self):#not a string and not a unicode
        self.assertRaises(KeyStoreException, CryptographicKey, None)
        
    def test_notValidKeyString2(self):#string but does not start with 0b or 0x
        self.assertRaises(KeyStoreException, CryptographicKey, "plop")
        
    def test_notValidKeyString3(self):#start with 0b or 0x but contains invalid char
        self.assertRaises(KeyStoreException, CryptographicKey, "0bplop")
        self.assertRaises(KeyStoreException, CryptographicKey, "0xplip")

    def test_validKey1(self):#valid binary key
        k = CryptographicKey("0b10101011")
        self.assertNotEqual(k, None)
        self.assertEqual(str(k),"0b10101011")
        self.assertEqual(repr(k),"0b10101011 ( BinaryKey, size=8 bit(s))")
        self.assertEqual(k.getKeyType(), CryptographicKey.KEYTYPE_BIT)
        self.assertEqual(k.getKeySize(), 8)
        self.assertEqual(k.getTypeString(), "bit")
        
    def test_validKey2(self):#valid hexa key
        k = CryptographicKey("0x11223344EEDDFF")
        self.assertNotEqual(k, None)
        self.assertEqual(str(k),"0x11223344eeddff")
        self.assertEqual(repr(k),"0x11223344eeddff ( HexaKey, size=7 byte(s))")
        self.assertEqual(k.getKeyType(), CryptographicKey.KEYTYPE_HEXA)
        self.assertEqual(k.getKeySize(), 7)
        self.assertEqual(k.getTypeString(), "byte")
        
    def test_validKey2(self):#valid hexa key but with odd number of char
        k = CryptographicKey("0x1223344EEDDFF")
        self.assertNotEqual(k, None)
        self.assertEqual(str(k),"0x01223344eeddff")
        self.assertEqual(repr(k),"0x01223344eeddff ( HexaKey, size=7 byte(s))")
        self.assertEqual(k.getKeyType(), CryptographicKey.KEYTYPE_HEXA)
        self.assertEqual(k.getKeySize(), 7)
        self.assertEqual(k.getTypeString(), "byte")
        
    def test_getKeyBinary1(self):#end is lower than start
        k = CryptographicKey("0b10101011")
        r = k.getKey(5,3)
        self.assertEqual(len(r),0)
        
    def test_getKeyBinary2(self):#start is bigger than the size of the key and no end asked
        k = CryptographicKey("0b10101011")
        r = k.getKey(800)
        self.assertEqual(len(r),0)
        
    def test_getKeyBinary3(self):#start is in range with not defined end
        k = CryptographicKey("0b10101011")
        r = k.getKey(3)
        self.assertEqual(len(r),5)
        self.assertEqual(r,[0,1,0,1,1])
        
    def test_getKeyBinary4(self):#start is in range but not end
        k = CryptographicKey("0b10101011")
        r = k.getKey(3, 10)
        self.assertEqual(len(r),7)
        self.assertEqual(r,[0,1,0,1,1,0,0])
        
    def test_getKeyBinary5(self):#start and end are in range
        k = CryptographicKey("0b10101011")
        r = k.getKey(3, 6)
        self.assertEqual(len(r),3)
        self.assertEqual(r,[0,1,0])
        
    def test_getKeyBinary6(self):#start is in range but not end with padding disabled
        k = CryptographicKey("0b10101011")
        r = k.getKey(3, 10, False)
        self.assertEqual(len(r),5)
        self.assertEqual(r,[0,1,0,1,1])
        
    def test_getKeyBinary7(self):#start and end are in range with padding disabled
        k = CryptographicKey("0b10101011")
        r = k.getKey(3, 6, False)
        self.assertEqual(len(r),3)
        self.assertEqual(r,[0,1,0])
        
    def test_getKeyHexa1(self):#end is lower than start
        k = CryptographicKey("0x11223344EEDDFF")
        r = k.getKey(5,3)
        self.assertEqual(len(r),0)
        
    def test_getKeyHexa2(self):#start is bigger than the size of the key and no end asked
        k = CryptographicKey("0x11223344EEDDFF")
        r = k.getKey(800)
        self.assertEqual(len(r),0)
        
    def test_getKeyHexa3(self):#start is in range with not defined end
        k = CryptographicKey("0x11223344EEDDFF")
        r = k.getKey(3)
        self.assertEqual(len(r),4)
        self.assertEqual(r,[0x44,0xee,0xdd,0xff])

    def test_getKeyHexa4(self):#start is in range but not end
        k = CryptographicKey("0x11223344EEDDFF")
        r = k.getKey(3, 10)
        self.assertEqual(len(r),7)
        self.assertEqual(r,[0x44,0xee,0xdd,0xff,0,0,0])
        
    def test_getKeyHexa5(self):#start and end are in range
        k = CryptographicKey("0x11223344EEDDFF")
        r = k.getKey(3, 6)
        self.assertEqual(len(r),3)
        self.assertEqual(r,[0x44,0xee,0xdd])
        
    def test_getKeyHexa6(self):#start is in range but not end with padding disabled
        k = CryptographicKey("0x11223344EEDDFF")
        r = k.getKey(3, 10, False)
        self.assertEqual(len(r),4)
        self.assertEqual(r,[0x44,0xee,0xdd,0xff])
        
    def test_getKeyHexa7(self):#start and end are in range with padding disabled
        k = CryptographicKey("0x11223344EEDDFF")
        r = k.getKey(3, 6, False)
        self.assertEqual(len(r),3)
        self.assertEqual(r,[0x44,0xee,0xdd])
    
        
if __name__ == '__main__':
    unittest.main()
