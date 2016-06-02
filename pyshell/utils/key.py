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

from pyshell.utils.exception import KeyStoreException
from pyshell.utils.string import isString


class CryptographicKey(object):
    KEYTYPE_HEXA = 0
    KEYTYPE_BIT = 1

    def __init__(self, key_string):
        # is it a string ?
        if not isString(key_string):
            raise KeyStoreException("("+self.__class__.__name__+") __init__, "
                                    "invalid key string, expected a string, "
                                    "got '"+str(type(key_string))+"'")

        key_string = key_string.lower()

        # find base
        if key_string.startswith("0x"):
            try:
                int(key_string, 16)
            except ValueError as ve:
                raise KeyStoreException("("+self.__class__.__name__+") "
                                        "__init__, invalid hexa string, start"
                                        " with 0x but is not valid: "+str(ve))

            self.keyType = CryptographicKey.KEYTYPE_HEXA
            self.key = key_string[2:]

            temp_key_size = float(len(key_string) - 2)
            temp_key_size /= 2
            self.keySize = int(temp_key_size)

            if temp_key_size > int(temp_key_size):
                self.keySize += 1
                self.key = "0"+self.key

        elif key_string.startswith("0b"):
            try:
                int(key_string, 2)
            except ValueError as ve:
                raise KeyStoreException("("+self.__class__.__name__+") "
                                        "__init__, invalid binary string, "
                                        "start with 0b but is not valid: " +
                                        str(ve))

            self.keyType = CryptographicKey.KEYTYPE_BIT
            self.key = key_string[2:]
            self.keySize = len(self.key)
        else:
            raise KeyStoreException("("+self.__class__.__name__+") __init__, "
                                    "invalid key string, must start with 0x or"
                                    " 0b, got '"+key_string+"'")

    def __str__(self):
        if self.keyType == CryptographicKey.KEYTYPE_HEXA:
            return "0x"+self.key
        else:
            return "0b"+self.key

    def __repr__(self):
        if self.keyType == CryptographicKey.KEYTYPE_HEXA:
            return ("0x"+self.key+" ( HexaKey, size="+str(self.keySize) +
                    " byte(s))")
        else:
            return ("0b"+self.key+" ( BinaryKey, size="+str(self.keySize) +
                    " bit(s))")

    def getKey(self, start, end=None, padding_enable=True):
        if end is not None and end < start:
            return ()

        # part to extract from key
        if start >= self.keySize:
            if end is None or not padding_enable:
                return ()

            key_part = []
        else:
            limit = self.keySize
            if end is not None and end <= self.keySize:
                limit = end

            key_part = []
            if self.keyType == CryptographicKey.KEYTYPE_HEXA:
                # for b in self.key[start*2:limit*2]:
                for index in range(start*2, limit*2, 2):
                    key_part.append(int(self.key[index:index+2], 16))
            else:
                for b in self.key[start:limit]:
                    key_part.append(int(b, 2))
        # padding part
        if padding_enable and end is not None and end > self.keySize:
            padding_length = end - self.keySize
            if padding_length > 0:
                key_part.extend([0] * padding_length)

        return key_part

    def getKeyType(self):
        return self.keyType

    def getKeySize(self):
        return self.keySize

    def getTypeString(self):
        if self.keyType == CryptographicKey.KEYTYPE_HEXA:
            return "byte"
        else:
            return "bit"

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.keyType == other.keyType and
                self.key == other.key)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self.keyType)+self.key)
