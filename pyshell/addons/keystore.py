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

import os
import sys

from pyshell.arg.argchecker import IntegerArgChecker
from pyshell.arg.argchecker import booleanValueArgChecker
from pyshell.arg.argchecker import defaultInstanceArgChecker
from pyshell.arg.argchecker import environmentParameterChecker
from pyshell.arg.decorator import shellMethod
from pyshell.loader.command import registerCommand
from pyshell.loader.command import registerSetGlobalPrefix
from pyshell.loader.command import registerStopHelpTraversalAt
from pyshell.loader.keystore import registerKey
from pyshell.utils.constants import ENVIRONMENT_KEY_STORE_FILE_KEY
from pyshell.utils.constants import ENVIRONMENT_SAVE_KEYS_KEY
from pyshell.utils.constants import KEYSTORE_SECTION_NAME
from pyshell.utils.exception import KeyStoreLoadingException
from pyshell.utils.exception import ListOfException
from pyshell.utils.misc import createParentDirectory
from pyshell.utils.postprocess import listFlatResultHandler
from pyshell.utils.postprocess import printColumn
from pyshell.utils.printing import formatBolt
from pyshell.utils.printing import formatGreen

try:
    pyrev = sys.version_info.major
except AttributeError:
    pyrev = sys.version_info[0]

if pyrev == 2:
    import ConfigParser
else:
    import configparser as ConfigParser

# # DECLARATION PART # #


@shellMethod(key_name=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             key_instance=defaultInstanceArgChecker.getKeyChecker(),
             key_store=environmentParameterChecker(KEYSTORE_SECTION_NAME),
             transient=booleanValueArgChecker())
def setKey(key_name, key_instance, key_store=None, transient=False):
    "set a key"
    key_instance.setTransient(transient)
    key_store.getValue().setkey_instance(key_name, key_instance)


@shellMethod(key=defaultInstanceArgChecker.getKeyTranslatorChecker(),
             start=IntegerArgChecker(),
             end=IntegerArgChecker(),
             key_store=environmentParameterChecker(KEYSTORE_SECTION_NAME))
def getKey(key, start=0, end=None, key_store=None):
    "get a key"
    return key.getKey(start, end)


@shellMethod(key_store=environmentParameterChecker(KEYSTORE_SECTION_NAME))
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


@shellMethod(key_name=defaultInstanceArgChecker.getStringArgCheckerInstance(),
             key_store=environmentParameterChecker(KEYSTORE_SECTION_NAME))
def unsetKey(key_name, key_store=None):
    "remove a key from the key_store"
    key_store.getValue().unsetKey(key_name)


@shellMethod(key_store=environmentParameterChecker(KEYSTORE_SECTION_NAME))
def cleanKeyStore(key_store=None):
    "remove every keys from the key_store"
    key_store.getValue().removeAll()


@shellMethod(
    file_path=environmentParameterChecker(ENVIRONMENT_KEY_STORE_FILE_KEY),
    usekey_store=environmentParameterChecker(ENVIRONMENT_SAVE_KEYS_KEY),
    key_store=environmentParameterChecker(KEYSTORE_SECTION_NAME))
def saveKeyStore(file_path, usekey_store, key_store=None):
    "save key_store from file"

    if not usekey_store.getValue():
        return

    file_path = file_path.getValue()
    key_store = key_store.getValue()

    config = ConfigParser.RawConfigParser()
    config.add_section(KEYSTORE_SECTION_NAME)

    key_count = 0
    for k, v in key_store.tries.getKeyValue().items():
        if v.transient:
            continue

        config.set(KEYSTORE_SECTION_NAME, k, str(v))
        key_count += 1

    if key_count == 0 and not os.path.exists(file_path):
        return

    # create config directory
    createParentDirectory(file_path)

    # save key store
    with open(file_path, 'wb') as configfile:
        config.write(configfile)


@shellMethod(
    file_path=environmentParameterChecker(ENVIRONMENT_KEY_STORE_FILE_KEY),
    usekey_store=environmentParameterChecker(ENVIRONMENT_SAVE_KEYS_KEY),
    key_store=environmentParameterChecker(KEYSTORE_SECTION_NAME))
def loadKeyStore(file_path, usekey_store, key_store=None):
    "load key_store from file"

    if not usekey_store.getValue():
        return

    file_path = file_path.getValue()
    key_store = key_store.getValue()

    # if no file, no load, no key_store file, loading not possible but no error
    if not os.path.exists(file_path):
        return

    # try to load the key_store
    config = ConfigParser.RawConfigParser()
    try:
        config.read(file_path)
    except Exception as ex:
        excmsg = ("(key_store) load, fail to read parameter file '" +
                  str(file_path)+"' : "+str(ex))
        raise KeyStoreLoadingException(excmsg)

    # main section available ?
    if not config.has_section(KEYSTORE_SECTION_NAME):
        excmsg = ("(key_store) load, config file '"+str(file_path) +
                  "' is valid but does not hold key_store section")
        raise KeyStoreLoadingException(excmsg)

    exceptions = ListOfException()
    for key_name in config.options(KEYSTORE_SECTION_NAME):
        try:
            key_store.setKey(key_name,
                             config.get(KEYSTORE_SECTION_NAME, key_name),
                             False)
        except Exception as ex:
            excmsg = ("(key_store) load, fail to load key '"+str(key_name) +
                      "' : "+str(ex))
            exceptions.append(KeyStoreLoadingException(excmsg))

    if exceptions.isThrowable():
        raise exceptions


@shellMethod(key=defaultInstanceArgChecker.getKeyTranslatorChecker(),
             state=booleanValueArgChecker())
def setTransient(key, state):
    key.setTransient(state)

# # REGISTER PART # #

# TODO where do come from all the key_store variable, need to load them ?

registerSetGlobalPrefix(("key", ))
registerCommand(("set",), post=setKey)
registerCommand(("get",), pre=getKey, pro=listFlatResultHandler)
registerCommand(("unset",), pro=unsetKey)
registerCommand(("list",), pre=listKey, pro=printColumn)
registerCommand(("save",), pro=saveKeyStore)
registerCommand(("load",), pro=loadKeyStore)
registerCommand(("clean",), pro=cleanKeyStore)
registerCommand(("transient",), pro=setTransient)
registerStopHelpTraversalAt()
registerKey("test", "0x00112233445566778899aabbccddeeff")
