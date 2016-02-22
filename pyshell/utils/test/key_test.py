#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pytest

from pyshell.utils.exception import KeyStoreException
from pyshell.utils.key import CryptographicKey


class TestKey(object):
    # not a string and not a unicode

    def test_notValidKeyString1(self):
        with pytest.raises(KeyStoreException):
            CryptographicKey(None)

    # string but does not start with 0b or 0x
    def test_notValidKeyString2(self):
        with pytest.raises(KeyStoreException):
            CryptographicKey("plop")

    # start with 0b or 0x but contains invalid char
    def test_notValidKeyString3(self):
        with pytest.raises(KeyStoreException):
            CryptographicKey("0bplop")
        with pytest.raises(KeyStoreException):
            CryptographicKey("0xplip")

    # valid binary key
    def test_validKey1(self):
        k = CryptographicKey("0b10101011")
        assert k is not None
        assert str(k) == "0b10101011"
        assert repr(k) == "0b10101011 ( BinaryKey, size=8 bit(s))"
        assert k.getKeyType() == CryptographicKey.KEYTYPE_BIT
        assert k.getKeySize() == 8
        assert k.getTypeString() == "bit"

    # valid hexa key
    def test_validKey2(self):
        k = CryptographicKey("0x11223344EEDDFF")
        assert k is not None
        assert str(k) == "0x11223344eeddff"
        assert repr(k) == "0x11223344eeddff ( HexaKey, size=7 byte(s))"
        assert k.getKeyType() == CryptographicKey.KEYTYPE_HEXA
        assert k.getKeySize() == 7
        assert k.getTypeString() == "byte"

    # valid hexa key but with odd number of char
    def test_validKey3(self):
        k = CryptographicKey("0x1223344EEDDFF")
        assert k is not None
        assert str(k) == "0x01223344eeddff"
        assert repr(k) == "0x01223344eeddff ( HexaKey, size=7 byte(s))"
        assert k.getKeyType() == CryptographicKey.KEYTYPE_HEXA
        assert k.getKeySize() == 7
        assert k.getTypeString() == "byte"

    # end is lower than start
    def test_getKeyBinary1(self):
        k = CryptographicKey("0b10101011")
        r = k.getKey(5, 3)
        assert len(r) == 0

    # start is bigger than the size of the key and no end asked
    def test_getKeyBinary2(self):
        k = CryptographicKey("0b10101011")
        r = k.getKey(800)
        assert len(r) == 0

    # start is in range with not defined end
    def test_getKeyBinary3(self):
        k = CryptographicKey("0b10101011")
        r = k.getKey(3)
        assert len(r) == 5
        assert r == [0, 1, 0, 1, 1]

    # start is in range but not end
    def test_getKeyBinary4(self):
        k = CryptographicKey("0b10101011")
        r = k.getKey(3, 10)
        assert len(r) == 7
        assert r == [0, 1, 0, 1, 1, 0, 0]

    # start and end are in range
    def test_getKeyBinary5(self):
        k = CryptographicKey("0b10101011")
        r = k.getKey(3, 6)
        assert len(r) == 3
        assert r == [0, 1, 0]

    # start is in range but not end with padding disabled
    def test_getKeyBinary6(self):
        k = CryptographicKey("0b10101011")
        r = k.getKey(3, 10, False)
        assert len(r) == 5
        assert r == [0, 1, 0, 1, 1]

    # start and end are in range with padding disabled
    def test_getKeyBinary7(self):
        k = CryptographicKey("0b10101011")
        r = k.getKey(3, 6, False)
        assert len(r) == 3
        assert r == [0, 1, 0]

    # end is lower than start
    def test_getKeyHexa1(self):
        k = CryptographicKey("0x11223344EEDDFF")
        r = k.getKey(5, 3)
        assert len(r) == 0

    # start is bigger than the size of the key and no end asked
    def test_getKeyHexa2(self):
        k = CryptographicKey("0x11223344EEDDFF")
        r = k.getKey(800)
        assert len(r) == 0

    # start is in range with not defined end
    def test_getKeyHexa3(self):
        k = CryptographicKey("0x11223344EEDDFF")
        r = k.getKey(3)
        assert len(r) == 4
        assert r == [0x44, 0xee, 0xdd, 0xff]

    # start is in range but not end
    def test_getKeyHexa4(self):
        k = CryptographicKey("0x11223344EEDDFF")
        r = k.getKey(3, 10)
        assert len(r) == 7
        assert r == [0x44, 0xee, 0xdd, 0xff, 0, 0, 0]

    # start and end are in range
    def test_getKeyHexa5(self):
        k = CryptographicKey("0x11223344EEDDFF")
        r = k.getKey(3, 6)
        assert len(r) == 3
        assert r == [0x44, 0xee, 0xdd]

    # start is in range but not end with padding disabled
    def test_getKeyHexa6(self):
        k = CryptographicKey("0x11223344EEDDFF")
        r = k.getKey(3, 10, False)
        assert len(r) == 4
        assert r == [0x44, 0xee, 0xdd, 0xff]

    # start and end are in range with padding disabled
    def test_getKeyHexa7(self):
        k = CryptographicKey("0x11223344EEDDFF")
        r = k.getKey(3, 6, False)
        assert len(r) == 3
        assert r == [0x44, 0xee, 0xdd]
