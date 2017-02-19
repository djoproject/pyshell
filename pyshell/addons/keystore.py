#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.arg.accessor.default import DefaultAccessor
from pyshell.arg.accessor.environment import EnvironmentAccessor
from pyshell.arg.checker.boolean import BooleanValueArgChecker
from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.integer import IntegerArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.register.command import registerCommand
from pyshell.register.command import registerSetGlobalPrefix
from pyshell.register.command import registerStopHelpTraversalAt
from pyshell.register.key import registerKey
from pyshell.utils.constants import KEY_ATTRIBUTE_NAME
from pyshell.utils.postprocess import listFlatResultHandler
from pyshell.utils.postprocess import printColumn
from pyshell.utils.printing import formatBolt
from pyshell.utils.printing import formatGreen


# # DECLARATION PART # #


@shellMethod(key_name=DefaultChecker.getString(),
             key_instance=DefaultChecker.getKey(),
             key_store=EnvironmentAccessor(KEY_ATTRIBUTE_NAME),
             transient=BooleanValueArgChecker())
def setKey(key_name, key_instance, key_store=None, transient=False):
    "set a key"
    key_instance.setTransient(transient)
    key_store.getValue().setkey_instance(key_name, key_instance)


@shellMethod(key=DefaultAccessor.getKey(),
             start=IntegerArgChecker(),
             end=IntegerArgChecker(),
             key_store=EnvironmentAccessor(KEY_ATTRIBUTE_NAME))
def getKey(key, start=0, end=None, key_store=None):
    "get a key"
    return key.getKey(start, end)


@shellMethod(key_store=EnvironmentAccessor(KEY_ATTRIBUTE_NAME))
def listKey(key_store):
    "list available key in the key_store"

    key_store = key_store.getValue()
    to_ret = []

    for k in key_store.getKeyList():
        key = key_store.getKey(k)
        to_ret.append((k,
                      key.getTypeString(),
                      str(key.getKeySize()),
                      formatGreen(str(key)),))

    if len(to_ret) == 0:
        return [("No key available",)]

    to_ret.insert(0,
                  (formatBolt("Key name"),
                   formatBolt("Type"),
                   formatBolt("Size"),
                   formatBolt("Value"),
                   ))
    return to_ret


@shellMethod(key_name=DefaultChecker.getString(),
             key_store=EnvironmentAccessor(KEY_ATTRIBUTE_NAME))
def unsetKey(key_name, key_store=None):
    "remove a key from the key_store"
    key_store.getValue().unsetKey(key_name)


@shellMethod(key_store=EnvironmentAccessor(KEY_ATTRIBUTE_NAME))
def cleanKeyStore(key_store=None):
    "remove every keys from the key_store"
    key_store.getValue().removeAll()


@shellMethod(key=DefaultAccessor.getKey(),
             state=DefaultChecker.getBoolean())
def setTransient(key, state):
    key.setTransient(state)

# # REGISTER PART # #

# TODO where do come from all the key_store variable, need to load them ?

registerSetGlobalPrefix(("key", ))
registerCommand(("set",), post=setKey)
registerCommand(("get",), pre=getKey, pro=listFlatResultHandler)
registerCommand(("unset",), pro=unsetKey)
registerCommand(("list",), pre=listKey, pro=printColumn)
registerCommand(("clean",), pro=cleanKeyStore)
registerCommand(("transient",), pro=setTransient)
registerStopHelpTraversalAt()
registerKey("test", "0x00112233445566778899aabbccddeeff")
