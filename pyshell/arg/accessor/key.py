#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2017  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.arg.accessor.container import ContainerAccessor
from pyshell.arg.accessor.parameter import AbstractParameterAccessor
from pyshell.arg.accessor.parameter import AbstractParameterDynamicAccessor
from pyshell.arg.checker.string43 import StringArgChecker
from pyshell.utils.constants import KEY_ATTRIBUTE_NAME
from pyshell.utils.key import CryptographicKey

ACCESSOR_TYPENAME = "keyTranslator"
DYNAMIC_ACCESSO_TYPENAME = "keyTranslator dynamic"
MANAGER_TYPENAME = "key manager"


class AbstractKeyAccessor(StringArgChecker):
    "retrieve a key from the keystore"

    def __init__(self,
                 key_size=None,
                 byte_key=True,
                 allowdifferentkey_size=False):
        StringArgChecker.__init__(self, 1, None)

        if key_size is not None:
            if type(key_size) != int:
                excmsg = "key_size must be an integer, got '%s'"
                excmsg %= str(type(key_size))
                self._raiseArgInitializationException(excmsg)

            if type(key_size) < 0:
                excmsg = "key_size must be bigger than 0, got <%s>"
                excmsg %= str(key_size)
                self._raiseArgInitializationException(excmsg)

        if (allowdifferentkey_size is None or
           type(allowdifferentkey_size) != bool):
            excmsg = "allowdifferentkey_size must be a boolean, got '%s'"
            excmsg %= str(type(allowdifferentkey_size))
            self._raiseArgInitializationException(excmsg)

        if byte_key is None or type(byte_key) != bool:
            excmsg = "byte_key must be a boolean, got '%s'"
            excmsg %= str(type(byte_key))
            self._raiseArgInitializationException(excmsg)

        self.allowdifferentkey_size = allowdifferentkey_size
        self.key_size = key_size
        self.byte_key = byte_key

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        key_instance = value

        # check type
        if self.byte_key is not None:
            if (self.byte_key and
               key_instance.getKeyType() != CryptographicKey.KEYTYPE_HEXA):
                excmsg = ("the key '%s' is a bit key and the process need a "
                          "byte key")
                excmsg %= str(value)
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

            if (not self.byte_key and
               key_instance.getKeyType() != CryptographicKey.KEYTYPE_BIT):
                excmsg = ("the key '%s' is a byte key and the process need a "
                          "bit key")
                excmsg %= str(value)
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        # check size
        if (self.key_size is not None and
           not self.allowdifferentkey_size and
           key_instance.getkey_size() < self.key_size):
            if CryptographicKey.KEYTYPE_HEXA == key_instance.getKeyType():
                keytype = "byte(s)"
            else:
                keytype = "bit(s)"

            excmsg = ("too short key '%s', need a key of at least <%s> %s, "
                      "got a <%s> %s key")
            excmsg %= (str(value),
                       str(self.key_size),
                       keytype,
                       str(key_instance.getkey_size()),
                       keytype)
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        return key_instance

    def getUsage(self):
        return "<key name>"


class KeyAccessor(AbstractParameterAccessor, AbstractKeyAccessor):
    def __init__(self,
                 environment_string_path,
                 key_size=None,
                 byte_key=True,
                 allowdifferentkey_size=False):
        AbstractParameterAccessor.__init__(self,
                                           environment_string_path,
                                           KEY_ATTRIBUTE_NAME)
        AbstractKeyAccessor.__init__(self,
                                     key_size,
                                     byte_key,
                                     allowdifferentkey_size)

    def getManager(self, container):
        return container.getKeyManager()

    def getValue(self,
                 value,
                 arg_number=None,
                 arg_name_to_bind=None):
        parameter = AbstractParameterAccessor.getValue(value,
                                                       arg_number,
                                                       arg_name_to_bind)
        return AbstractKeyAccessor.getValue(parameter.getValue())

    @classmethod
    def getTypeName(cls):
        return ACCESSOR_TYPENAME


class KeyDynamicAccessor(AbstractParameterDynamicAccessor,
                         AbstractKeyAccessor):
    def __init__(self,
                 key_size=None,
                 byte_key=True,
                 allowdifferentkey_size=False):
        AbstractParameterDynamicAccessor.__init__(self, KEY_ATTRIBUTE_NAME)
        AbstractKeyAccessor.__init__(self,
                                     key_size,
                                     byte_key,
                                     allowdifferentkey_size)

    def getManager(self, container):
        return container.getKeyManager()

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        parameter = AbstractParameterAccessor.getValue(value,
                                                       arg_number,
                                                       arg_name_to_bind)
        return AbstractKeyAccessor.getValue(parameter.getValue())

    @classmethod
    def getTypeName(cls):
        return DYNAMIC_ACCESSO_TYPENAME


class KeyManagerAccessor(ContainerAccessor):
    def hasAccessorValue(self):
        if not ContainerAccessor.hasAccessorValue(self):
            return False

        container = ContainerAccessor.getAccessorValue(self)

        return container.getKeyManager() is not None

    def getAccessorValue(self):
        return ContainerAccessor.getAccessorValue(self).getKeyManager()

    def buildErrorMessage(self):
        if not ContainerAccessor.hasAccessorValue(self):
            return ContainerAccessor.buildErrorMessage(self)
        return "container provided has no key manager defined"

    @classmethod
    def getTypeName(cls):
        return MANAGER_TYPENAME
