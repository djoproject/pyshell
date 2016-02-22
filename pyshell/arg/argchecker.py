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

# TODO
#   create an argchecker to check if the value is an instance of
#   create an argchecker to check if the value is a type of
#   and when it will be done, look after ListArgChecker(defaultargchecker())
#   and replace them if possible
#
#   create a checker to instanciate a class instance from a number of parameter

import collections
import os
from math import log
from threading import Lock

from tries import tries
from tries.exception import ambiguousPathException

from pyshell.arg.exception import ArgException
from pyshell.arg.exception import ArgInitializationException
from pyshell.utils.constants import CONTEXT_ATTRIBUTE_NAME
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME
from pyshell.utils.constants import KEY_ATTRIBUTE_NAME
from pyshell.utils.constants import VARIABLE_ATTRIBUTE_NAME
from pyshell.utils.key import CryptographicKey

try:
    from collections import OrderedDict
except:
    from pyshell.utils.ordereddict import OrderedDict

# string argchecker definition
ARGCHECKER_TYPENAME = "any"
STRINGCHECKER_TYPENAME = "string"
INTEGERCHECKER_TYPENAME = "integer"
LIMITEDINTEGERCHECKER_TYPENAME = "limited integer"
HEXACHECKER_TYPENAME = "hexadecimal"
BINARYCHECKER_TYPENAME = "binary"
FILEPATHCHECKER_TYPENAME = "filePath"
LISTCHECKER_TYPENAME = "list"
DEFAULTVALUE_TYPENAME = "default"
ENVIRONMENTDYNAMICCHECKER_TYPENAME = "environment dynamic"
CONTEXTDYNAMICCHECKER_TYPENAME = "context dynamic"
VARIABLEDYNAMICCHECKER_TYPENAME = "variable dynamic"
ENVIRONMENTCHECKER_TYPENAME = "environment"
CONTEXTCHECKER_TYPENAME = "context"
VARIABLECHECKER_TYPENAME = "variable"
PARAMETERDYNAMICCHECKER_TYPENAME = "parameter dynamic"
PARAMETERCHECKER_TYPENAME = "parameter"
COMPLETEENVIRONMENTCHECKER_TYPENAME = "complete Environment"
ENGINECHECKER_TYPENAME = "engine"
FLOATCHECKER_TYPENAME = "float"
BOOLEANCHECKER_TYPENAME = "boolean"
TOKENCHECKER_TYPENAME = "token"
KEYCHECKER_TYPENAME = "key"
KEYTRANSLATORCHECKER_TYPENAME = "keyTranslator"
KEYTRASNLATORCHECKER_TYPENAME = "keyTranslator"
KEYTRANSLATORDYNAMICCHECKER_TYPENAME = "keyTranslator dynamic"


class DefaultInstanceArgChecker(object):
    _lock = Lock()
    ARGCHECKER = None
    StringArgChecker = None
    INTEGERARGCHECKER = None
    BOOLEANCHECKER = None
    FLOATCHECKER = None
    ENVCHECKER = None
    KEYCHECKER = None
    KEYTRANSLATORCHECKER = None
    ENGINECHECKER = None
    FILECHECKER = None

    DEFAULTCHECKER_DICO = {ARGCHECKER_TYPENAME: None,
                           STRINGCHECKER_TYPENAME: None,
                           INTEGERCHECKER_TYPENAME: None,
                           BOOLEANCHECKER_TYPENAME: None,
                           FLOATCHECKER_TYPENAME: None,
                           ENVIRONMENTCHECKER_TYPENAME: None,
                           KEYCHECKER_TYPENAME: None,
                           ENGINECHECKER_TYPENAME: None,
                           FILEPATHCHECKER_TYPENAME: None}

    @classmethod
    def _getCheckerInstance(cls, key, classdef):
        if cls.DEFAULTCHECKER_DICO[key] is None:
            with cls._lock:
                if cls.DEFAULTCHECKER_DICO[key] is None:
                    cls.DEFAULTCHECKER_DICO[key] = classdef()
                    cls.DEFAULTCHECKER_DICO[key].setDefaultValueEnable(False)

        return cls.DEFAULTCHECKER_DICO[key]

    @classmethod
    def getArgCheckerInstance(cls):
        return cls._getCheckerInstance(ARGCHECKER_TYPENAME, ArgChecker)

    @classmethod
    def getStringArgCheckerInstance(cls):
        return cls._getCheckerInstance(STRINGCHECKER_TYPENAME,
                                       StringArgChecker)

    @classmethod
    def getIntegerArgCheckerInstance(cls):
        return cls._getCheckerInstance(INTEGERCHECKER_TYPENAME,
                                       IntegerArgChecker)

    @classmethod
    def getBooleanValueArgCheckerInstance(cls):
        return cls._getCheckerInstance(BOOLEANCHECKER_TYPENAME,
                                       BooleanValueArgChecker)

    @classmethod
    def getFloatTokenArgCheckerInstance(cls):
        return cls._getCheckerInstance(FLOATCHECKER_TYPENAME,
                                       FloatTokenArgChecker)

    @classmethod
    def getCompleteEnvironmentChecker(cls):
        return cls._getCheckerInstance(ENVIRONMENTCHECKER_TYPENAME,
                                       CompleteEnvironmentChecker)

    @classmethod
    def getKeyChecker(cls):
        return cls._getCheckerInstance(KEYCHECKER_TYPENAME,
                                       KeyArgChecker)

    @classmethod
    def getEngineChecker(cls):
        return cls._getCheckerInstance(ENGINECHECKER_TYPENAME,
                                       EngineChecker)

    @classmethod
    def getFileChecker(cls):
        return cls._getCheckerInstance(FILEPATHCHECKER_TYPENAME,
                                       FilePathArgChecker)


# #############################################################################
# #### ArgChecker #############################################################
# #############################################################################

class ArgChecker(object):
    def __init__(self,
                 minimum_size=1,
                 maximum_size=1,
                 show_in_usage=True,
                 type_name=ARGCHECKER_TYPENAME):
        self.type_name = type_name
        self.setSize(minimum_size, maximum_size)
        self.defaultValueEnabled = True
        self.hasDefault = False
        self.default = None
        self.show_in_usage = show_in_usage
        self.engine = None

    def setSize(self, minimum_size=None, maximum_size=None):
        self.checkSize(minimum_size, maximum_size)
        self.minimum_size = minimum_size
        self.maximum_size = maximum_size

    def checkSize(self, minimum_size, maximum_size):
        if minimum_size is not None:
            if type(minimum_size) != int:
                excmsg = ("("+self.type_name+") Minimum size must be an "
                          "integer, got type '"+str(type(minimum_size))+"' "
                          "with the following value <"+str(minimum_size)+">")
                raise ArgInitializationException(excmsg)

            if minimum_size < 0:
                excmsg = ("("+self.type_name+") Minimum size must be a "
                          "positive value, got <"+str(minimum_size)+">")
                raise ArgInitializationException(excmsg)

        if maximum_size is not None:
            if type(maximum_size) != int:
                excmsg = ("("+self.type_name+") Maximum size must be an "
                          "integer, got type '"+str(type(maximum_size))+"' "
                          "with the following value <"+str(maximum_size)+">")
                raise ArgInitializationException(excmsg)

            if maximum_size < 0:
                excmsg = ("("+self.type_name+") Maximum size must be a "
                          "positive value, got <"+str(maximum_size)+">")
                raise ArgInitializationException(excmsg)

        if (minimum_size is not None and
           maximum_size is not None and
           maximum_size < minimum_size):
            excmsg = ("("+self.type_name+") Maximum size <"+str(maximum_size) +
                      "> can not be smaller than Minimum size <" +
                      str(minimum_size)+">")
            raise ArgInitializationException(excmsg)

    def isVariableSize(self):
        return ((self.minimum_size == self.maximum_size is None) or
                self.minimum_size != self.maximum_size)

    def needData(self):
        return self.minimum_size is not None and self.minimum_size > 0

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        return value

    def getUsage(self):
        return "<any>"

    def getDefaultValue(self, arg_name_to_bind=None):
        if not self.hasDefaultValue(arg_name_to_bind):
            self._raiseArgException("there is no default value")

        return self.default

    def hasDefaultValue(self, arg_name_to_bind=None):
        if not self.defaultValueEnabled:
            return False

        return self.hasDefault

    def setDefaultValue(self, value, arg_name_to_bind=None):
        if not self.defaultValueEnabled:
            excmsg = ("("+self.type_name+") default value is not allowed with "
                      "this kind of checker, probably because it is a default "
                      "instance checker")
            raise ArgInitializationException(excmsg)

        self.hasDefault = True

        if value is None:
            self.default = None
            return

        # will convert the value if needed
        self.default = self.getValue(value, None, arg_name_to_bind)

    def setDefaultValueEnable(self, state):
        self.defaultValueEnabled = state

    def erraseDefaultValue(self):
        self.hasDefault = False
        self.default = None

    def setEngine(self, engine):
        self.engine = engine

    def _raiseIfEnvIsNotAvailable(self,
                                  arg_number=None,
                                  arg_name_to_bind=None):
        if self.engine is None:
            excmsg = ("can not get Environment, no engine linked to this "
                      "argument instance")
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        if not hasattr(self.engine, "getEnv"):
            excmsg = ("can not get Environment, linked engine does not have a "
                      "method to get the environment")
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        if self.engine.getEnv() is None:
            excmsg = ("can not get Environment, no environment linked to the "
                      "engine")
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

    def _isEnvAvailable(self):
        return (not (self.engine is None or
                not hasattr(self.engine, "getEnv") or
                self.engine.getEnv() is None))

    def _raiseArgException(self,
                           message,
                           arg_number=None,
                           arg_name_to_bind=None):
        prefix = ""

        if arg_number is not None:
            prefix += "Token <"+str(arg_number)+">"

        if arg_name_to_bind is not None:
            if len(prefix) > 0:
                prefix += " "

            prefix += "at argument '"+str(arg_name_to_bind)+"'"

        if len(prefix) > 0:
            prefix += ": "

        raise ArgException("("+self.type_name+") "+prefix+message)

    def getTypeName(self):
        return self.type_name


class StringArgChecker(ArgChecker):
    def __init__(self,
                 minimum_string_size=0,
                 maximum_string_size=None,
                 type_name=STRINGCHECKER_TYPENAME):
        ArgChecker.__init__(self, 1, 1, True, type_name)

        if type(minimum_string_size) != int:
            excmsg = ("("+self.type_name+") Minimum string size must be an "
                      "integer, got type '"+str(type(minimum_string_size)) +
                      "' with the following value <"+str(minimum_string_size) +
                      ">")
            raise ArgInitializationException(excmsg)

        if minimum_string_size < 0:
            excmsg = ("("+self.type_name+") Minimum string size must be a "
                      "positive value bigger or equal to 0, got <" +
                      str(minimum_string_size)+">")
            raise ArgInitializationException()

        if maximum_string_size is not None:
            if type(maximum_string_size) != int:
                excmsg = ("("+self.type_name+") Maximum string size must be an"
                          " integer, got type '" +
                          str(type(maximum_string_size))+"' with the following"
                          " value <"+str(maximum_string_size)+">")
                raise ArgInitializationException(excmsg)

            if maximum_string_size < 1:
                excmsg = ("("+self.type_name+") Maximum string size must be a "
                          "positive value bigger than 0, got <" +
                          str(maximum_string_size)+">")
                raise ArgInitializationException(excmsg)

        if (minimum_string_size is not None and
           maximum_string_size is not None and
           maximum_string_size < minimum_string_size):
            excmsg = ("("+self.type_name+") Maximum string size <" +
                      str(maximum_string_size) + "> can not be smaller than "
                      "Minimum string size <"+str(minimum_string_size)+">")
            raise ArgInitializationException(excmsg)

        self.minimum_string_size = minimum_string_size
        self.maximum_string_size = maximum_string_size

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        value = ArgChecker.getValue(self, value, arg_number, arg_name_to_bind)

        if value is None:
            self._raiseArgException("the string arg can't be None",
                                    arg_number,
                                    arg_name_to_bind)

        if type(value) != str and type(value) != unicode:
            if not hasattr(value, "__str__"):
                excmsg = ("this value '"+str(value)+"' is not a valid string, "
                          "got type '"+str(type(value))+"'")
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

            value = str(value)

        if len(value) < self.minimum_string_size:
            excmsg = ("this value '"+str(value)+"' is a too small string, got"
                      " size '"+str(len(value))+"' with value '"+str(value) +
                      "', minimal allowed size is '" +
                      str(self.minimum_string_size)+"'")
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        if (self.maximum_string_size is not None and
           len(value) > self.maximum_string_size):
            excmsg = ("this value '"+str(value)+"' is a too big string, got "
                      "size '"+str(len(value))+"' with value '"+str(value) +
                      "', maximal allowed size is '" +
                      str(self.maximum_string_size)+"'")
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        return value

    def getUsage(self):
        return "<string>"


class IntegerArgChecker(ArgChecker):
    def __init__(self,
                 minimum=None,
                 maximum=None,
                 show_in_usage=True,
                 type_name=INTEGERCHECKER_TYPENAME):
        ArgChecker.__init__(self, 1, 1, True, type_name)

        if not hasattr(self, "shortType"):
            self.shortType = "int"

        if not hasattr(self, "bases"):
            self.bases = [10, 16, 2]

        if (minimum is not None and
           type(minimum) != int and
           type(minimum) != float):
            excmsg = ("("+self.type_name+") Minimum must be an integer or None"
                      ", got <"+str(type(minimum))+">")
            raise ArgInitializationException(excmsg)

        if (maximum is not None and
           type(maximum) != int and
           type(maximum) != float):
            excmsg = ("("+self.type_name+") Maximum must be an integer or None"
                      ", got <"+str(type(maximum))+">")
            raise ArgInitializationException(excmsg)

        if minimum is not None and maximum is not None and maximum < minimum:
            excmsg = ("("+self.type_name+") Maximum size <"+str(maximum)+"> "
                      "can not be smaller than Minimum size <"+str(minimum) +
                      ">")
            raise ArgInitializationException(excmsg)

        self.minimum = minimum
        self.maximum = maximum

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        value = ArgChecker.getValue(self, value, arg_number, arg_name_to_bind)

        if value is None:
            excmsg = "the "+self.type_name.lower()+" arg can't be None"
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        casted_value = None
        if type(value) == int or type(value) == float or type(value) == bool:
            casted_value = int(value)
        elif type(value) == str or type(value) == unicode:
            for b in self.bases:
                try:
                    casted_value = int(value, b)
                    break
                except ValueError:
                    continue

        if casted_value is None:

            if len(self.bases) == 1:
                message = ("Only a number in base <"+str(self.bases[0])+"> is "
                           "allowed")
            else:
                message = ("Only a number in bases <" +
                           ", ".join(str(x) for x in self.bases) +
                           "> is allowed")

            excmsg = ("this arg is not a valid "+self.type_name.lower() +
                      ", got <"+str(value)+">. "+message)
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        if self.minimum is not None:
            if casted_value < self.minimum:
                excmsg = ("the lowest value must be bigger or equal than <" +
                          str(self.minimum)+">, got <"+str(value)+">")
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        if self.maximum is not None:
            if casted_value > self.maximum:
                excmsg = ("the biggest value must be lower or equal than <" +
                          str(self.maximum)+">, got <"+str(value)+">")
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        return casted_value

    def getUsage(self):
        if self.minimum is not None:
            if self.maximum is not None:
                return ("<"+self.shortType+" "+str(self.minimum)+"-" +
                        str(self.maximum)+">")
            return "<"+self.shortType+" "+str(self.minimum)+"-*>"
        else:
            if self.maximum is not None:
                return "<"+self.shortType+" *-"+str(self.maximum)+">"
        return "<"+self.shortType+">"


class LimitedInteger(IntegerArgChecker):
    def __init__(self, amount_of_bit=8, signed=False):
        if amount_of_bit < 8:
            excmsg = ("("+LIMITEDINTEGERCHECKER_TYPENAME+") the amount of bit "
                      "must at least be 8, got <"+str(amount_of_bit)+">")
            raise ArgInitializationException(excmsg)

        if log(amount_of_bit, 2) % 1 != 0:
            excmsg = ("("+LIMITEDINTEGERCHECKER_TYPENAME+") only powers of 2 "
                      "are allowed, 8, 16, 32, 64, ..., got <" +
                      str(amount_of_bit)+">")
            raise ArgInitializationException(excmsg)

        if signed:
            IntegerArgChecker.__init__(self,
                                       -(2**(amount_of_bit-1)),
                                       (2**(amount_of_bit-1))-1,
                                       True,
                                       LIMITEDINTEGERCHECKER_TYPENAME)
        else:
            IntegerArgChecker.__init__(self,
                                       0x0,
                                       (2**amount_of_bit)-1,
                                       True,
                                       LIMITEDINTEGERCHECKER_TYPENAME)


class HexaArgChecker(IntegerArgChecker):
    def __init__(self, minimum=None, maximum=None):
        self.bases = [16]
        self.shortType = "hex"
        IntegerArgChecker.__init__(self,
                                   minimum,
                                   maximum,
                                   True,
                                   HEXACHECKER_TYPENAME)


class BinaryArgChecker(IntegerArgChecker):
    def __init__(self, minimum=None, maximum=None):
        self.bases = [2]
        self.shortType = "bin"
        IntegerArgChecker.__init__(self,
                                   minimum,
                                   maximum,
                                   True,
                                   BINARYCHECKER_TYPENAME)


class TokenValueArgChecker(StringArgChecker):
    def __init__(self, token_dict, typename=TOKENCHECKER_TYPENAME):
        StringArgChecker.__init__(self, 1, None, typename)
        if not isinstance(token_dict, dict):
            excmsg = ("("+self.type_name+") token_dict must be a dictionary, "
                      "got '"+str(type(token_dict))+"'")
            raise ArgInitializationException(excmsg)

        self.localtries = tries()
        for k, v in token_dict.items():
            # key must be non empty string, value can be anything
            if type(k) != str and type(k) != unicode:
                excmsg = ("("+self.type_name+") a key in the dictionary is not"
                          " a string: '"+str(k)+"', type: '"+str(type(k))+"'")
                raise ArgInitializationException(excmsg)

            self.localtries.insert(k, v)

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        value = StringArgChecker.getValue(self,
                                          value,
                                          arg_number,
                                          arg_name_to_bind)

        try:
            node = self.localtries.search(value)
            if node is None:
                excmsg = ("this arg '"+str(value)+"' is not an existing token,"
                          " valid token are (" +
                          ("|".join(self.localtries.getKeyList()))+")")
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)
            return node.value

        except ambiguousPathException:
            excmsg = ("this arg '"+str(value)+"' is ambiguous, valid token are"
                      " ("+("|".join(self.localtries.getKeyList()))+")")
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

    def getUsage(self):
        return "("+("|".join(self.localtries.getKeyList()))+")"


class BooleanValueArgChecker(TokenValueArgChecker):
    def __init__(self, true_name=None, false_name=None):
        if true_name is None:
            true_name = "true"

        if false_name is None:
            false_name = "false"

        # the constructor of TokenValueArgChecker will check if every keys are
        ordered_items = OrderedDict([(true_name, True,), (false_name, False)])
        TokenValueArgChecker.__init__(self,
                                      ordered_items,
                                      BOOLEANCHECKER_TYPENAME)
        self.true_name = true_name
        self.false_name = false_name

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        if type(value) == bool:
            if value:
                value = self.true_name
            else:
                value = self.false_name
        else:
            value = str(value).lower()

        return TokenValueArgChecker.getValue(self,
                                             value,
                                             arg_number,
                                             arg_name_to_bind)


class FloatTokenArgChecker(ArgChecker):
    def __init__(self, minimum=None, maximum=None):
        ArgChecker.__init__(self, 1, 1, True, FLOATCHECKER_TYPENAME)

        if (minimum is not None and
           type(minimum) != float and
           type(minimum) != int):
            excmsg = ("("+self.type_name+") Minimum must be a float or None, "
                      "got '"+str(type(minimum))+"'")
            raise ArgInitializationException(excmsg)

        if (maximum is not None and
           type(maximum) != float and
           type(maximum) != int):
            excmsg = ("("+self.type_name+") Maximum must be a float or None, "
                      "got '"+str(type(maximum))+"'")
            raise ArgInitializationException(excmsg)

        if minimum is not None and maximum is not None and maximum < minimum:
            excmsg = ("("+self.type_name+") Maximum <"+str(maximum)+"> can not"
                      " be smaller than Minimum <"+str(minimum)+">")
            raise ArgInitializationException(excmsg)

        self.minimum = minimum
        self.maximum = maximum

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        value = ArgChecker.getValue(self, value, arg_number, arg_name_to_bind)

        if value is None:
            self._raiseArgException("the float arg can't be None",
                                    arg_number,
                                    arg_name_to_bind)

        try:
            casted_value = float(value)
        except ValueError:
            excmsg = ("this arg is not a valid float or hexadecimal, got <" +
                      str(value)+">")
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        if self.minimum is not None:
            if casted_value < self.minimum:
                excmsg = ("the lowest value must be bigger or equal than <" +
                          str(self.minimum) + ">, got <"+str(value)+">")
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        if self.maximum is not None:
            if casted_value > self.maximum:
                excmsg = ("the biggest value must be lower or equal than <" +
                          str(self.maximum)+">, got <"+str(value)+">")
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        return casted_value

    def getUsage(self):
        if self.minimum is not None:
            if self.maximum is not None:
                return "<float "+str(self.minimum)+"-"+str(self.maximum)+">"
            return "<float "+str(self.minimum)+"-*.*>"
        else:
            if self.maximum is not None:
                return "<float *.*-"+str(self.maximum)+">"
        return "<float>"


class EngineChecker(ArgChecker):
    def __init__(self):
        ArgChecker.__init__(self, 0, 0, False, ENGINECHECKER_TYPENAME)

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        return self.engine

    def usage(self):
        return ""

    def getDefaultValue(self, arg_name_to_bind=None):
        return self.engine

    def hasDefaultValue(self, arg_name_to_bind=None):
        return True

    def setDefaultValue(self, value, arg_name_to_bind=None):
        pass

    def erraseDefaultValue(self):
        pass


class CompleteEnvironmentChecker(ArgChecker):
    def __init__(self):
        ArgChecker.__init__(self,
                            0,
                            0,
                            False,
                            COMPLETEENVIRONMENTCHECKER_TYPENAME)

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        self._raiseIfEnvIsNotAvailable(arg_number, arg_name_to_bind)
        return self.engine.getEnv()

    def usage(self):
        return ""

    def getDefaultValue(self, arg_name_to_bind=None):
        self._raiseIfEnvIsNotAvailable(None, arg_name_to_bind)
        return self.engine.getEnv()

    def hasDefaultValue(self, arg_name_to_bind=None):
        return self._isEnvAvailable()

    def setDefaultValue(self, value, arg_name_to_bind=None):
        pass

    def erraseDefaultValue(self):
        pass


# TODO this checker should not be use anywhere, use contextParameterChecker
# or environmentParameterChecker
class AbstractParameterChecker(ArgChecker):
    def __init__(self,
                 keyname,
                 container_attribute,
                 type_name=PARAMETERCHECKER_TYPENAME):
        ArgChecker.__init__(self, 0, 0, False, type_name)

        if (keyname is None or
           (type(keyname) != str and type(keyname) != unicode) or
           not isinstance(keyname, collections.Hashable)):
            excmsg = ("("+self.type_name+") keyname must be hashable string, "
                      "got '"+str(keyname)+"'")
            raise ArgInitializationException(excmsg)

        self.keyname = keyname

        if (container_attribute is None or
           (type(container_attribute) != str and
                type(container_attribute) != unicode)):
            excmsg = ("("+self.type_name+") container_attribute must be a "
                      "valid string, got '"+str(type(container_attribute))+"'")
            raise ArgInitializationException(excmsg)

        self.container_attribute = container_attribute

    def _getContainer(self, arg_number=None, arg_name_to_bind=None):
        self._raiseIfEnvIsNotAvailable(arg_number, arg_name_to_bind)
        env = self.engine.getEnv()

        if not hasattr(env, self.container_attribute):
            excmsg = ("environment container does not have the attribute '" +
                      str(self.container_attribute)+"'")
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        return getattr(env, self.container_attribute)

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        container = self._getContainer(arg_number, arg_name_to_bind)

        param = container.getParameter(self.keyname)
        if param is None:
            excmsg = "the key '"+self.keyname+"' is not available but needed"
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        return param

    def usage(self):
        return ""

    # TODO est ce qu'il existe vraiment un cas de figure ou les valeurs par
    # defaut peuvent être appellée avec un argument de taille min=0, max=0 ?
    def getDefaultValue(self, arg_name_to_bind=None):
        container = self._getContainer(None, arg_name_to_bind)

        param = container.getParameter(self.keyname)
        if param is None:
            excmsg = "the key '"+self.keyname+"' is not available but needed"
            self._raiseArgException(excmsg, None, arg_name_to_bind)

        return param

    def hasDefaultValue(self, arg_name_to_bind=None):
        container = self._getContainer(None, arg_name_to_bind)
        return container.hasParameter(self.keyname)

    def setDefaultValue(self, value, arg_name_to_bind=None):
        pass

    def erraseDefaultValue(self):
        pass


class AbstractParameterDynamicChecker(ArgChecker):
    def __init__(self,
                 container_attribute,
                 type_name=PARAMETERDYNAMICCHECKER_TYPENAME):
        ArgChecker.__init__(self, 1, 1, False, type_name)

        if (container_attribute is None or
           (type(container_attribute) != str and
                type(container_attribute) != unicode)):
            excmsg = ("("+self.type_name+") container_attribute must be a "
                      "valid string, got '"+str(type(container_attribute))+"'")
            raise ArgInitializationException(excmsg)

        self.container_attribute = container_attribute

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        self._raiseIfEnvIsNotAvailable(arg_number, arg_name_to_bind)
        if not isinstance(value, collections.Hashable):
            excmsg = "keyname must be hashable, got '"+str(value)+"'"
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        env = self.engine.getEnv()

        if not hasattr(env, self.container_attribute):
            excmsg = ("environment container does not have the attribute '" +
                      str(self.container_attribute)+"'")
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        container = getattr(env, self.container_attribute)

        param = container.getParameter(value)
        if param is None:
            excmsg = "the key '"+str(value)+"' is not available but needed"
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        return param

    def hasDefaultValue(self, arg_name_to_bind=None):
        return False

    def setDefaultValue(self, value, arg_name_to_bind=None):
        pass

    def erraseDefaultValue(self):
        pass

# TODO use constant name


class ContextParameterChecker(AbstractParameterChecker):
    def __init__(self, context_string_path):
        AbstractParameterChecker.__init__(self,
                                          context_string_path,
                                          CONTEXT_ATTRIBUTE_NAME,
                                          CONTEXTCHECKER_TYPENAME)


class EnvironmentParameterChecker(AbstractParameterChecker):
    def __init__(self, environment_string_path):
        AbstractParameterChecker.__init__(self,
                                          environment_string_path,
                                          ENVIRONMENT_ATTRIBUTE_NAME,
                                          ENVIRONMENTCHECKER_TYPENAME)


class VariableParameterChecker(AbstractParameterChecker):
    def __init__(self, variable_string_path):
        AbstractParameterChecker.__init__(self,
                                          variable_string_path,
                                          VARIABLE_ATTRIBUTE_NAME,
                                          VARIABLECHECKER_TYPENAME)


class ContextParameterDynamicChecker(AbstractParameterDynamicChecker):
    def __init__(self):
        AbstractParameterDynamicChecker.__init__(
            self,
            CONTEXT_ATTRIBUTE_NAME,
            CONTEXTDYNAMICCHECKER_TYPENAME)


class EnvironmentParameterDynamicChecker(AbstractParameterDynamicChecker):
    def __init__(self):
        AbstractParameterDynamicChecker.__init__(
            self,
            ENVIRONMENT_ATTRIBUTE_NAME,
            ENVIRONMENTDYNAMICCHECKER_TYPENAME)


class VariableParameterDynamicChecker(AbstractParameterDynamicChecker):
    def __init__(self):
        AbstractParameterDynamicChecker.__init__(
            self,
            VARIABLE_ATTRIBUTE_NAME,
            VARIABLEDYNAMICCHECKER_TYPENAME)


class DefaultValueChecker(ArgChecker):
    def __init__(self, value):
        ArgChecker.__init__(self, 0, 0, False, DEFAULTVALUE_TYPENAME)
        self.setDefaultValue(value)

    def setDefaultValue(self, value, arg_name_to_bind=None):
        self.hasDefault = True
        self.default = value  # no check on the value...

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        return self.getDefaultValue(arg_name_to_bind)


class ListArgChecker(ArgChecker):
    def __init__(self, checker, minimum_size=None, maximum_size=None):
        if (not isinstance(checker, ArgChecker) or
           isinstance(checker, ListArgChecker)):
            excmsg = ("("+LISTCHECKER_TYPENAME+") checker must be an instance "
                      "of ArgChecker but can not be an instance of "
                      "ListArgChecker, got '"+str(type(checker))+"'")
            raise ArgInitializationException(excmsg)

        # checker must have a fixed size
        if (checker.minimum_size != checker.maximum_size or
           checker.minimum_size is None or
           checker.minimum_size == 0):
            if checker.minimum_size is None:
                checker_size = "]-Inf,"
            else:
                checker_size = "["+str(checker.minimum_size)+","

            if checker.maximum_size is None:
                checker_size += "+Inf["
            else:
                checker_size += str(checker.maximum_size)+"]"

            excmsg = ("("+LISTCHECKER_TYPENAME+") checker must have a fixed "
                      "size bigger than zero, got this sizer : "+checker_size)
            raise ArgInitializationException(excmsg)

        self.checker = checker
        ArgChecker.__init__(self,
                            minimum_size,
                            maximum_size,
                            True,
                            LISTCHECKER_TYPENAME)

    def checkSize(self, minimum_size, maximum_size):
        ArgChecker.checkSize(self, minimum_size, maximum_size)

        if (minimum_size is not None and
           (minimum_size % self.checker.minimum_size) != 0):
            excmsg = ("("+LISTCHECKER_TYPENAME+") the minimum size of the "
                      "list <"+str(minimum_size)+"> is not a multiple of the "
                      "checker size <"+str(self.checker.minimum_size)+">")
            raise ArgInitializationException(excmsg)

        if (maximum_size is not None and
           (maximum_size % self.checker.minimum_size) != 0):
            excmsg = ("("+LISTCHECKER_TYPENAME+") the maximum size of the list"
                      " <"+str(maximum_size)+"> is not a multiple of the "
                      "checker size <"+str(self.checker.minimum_size)+">")
            raise ArgInitializationException(excmsg)

    def getValue(self, values, arg_number=None, arg_name_to_bind=None):
        # check if it's a list
        if not hasattr(values, "__iter__"):  # if not isinstance(values,list):
            values = (values,)

        # len(values) must always be a multiple of self.checker.minimum_size
        #   even if there is to much data, it is a sign of anomalies
        if (len(values) % self.checker.minimum_size) != 0:
            excmsg = ("the size of the value list <"+str(len(values))+"> is "
                      "not a multiple of the checker size <" +
                      str(self.checker.minimum_size)+">")
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        # check the minimal size
        add_at_end = []
        if self.minimum_size is not None and len(values) < self.minimum_size:
            # checker has default value ?
            if self.checker.hasDefaultValue(arg_name_to_bind):
                # build the missing part with the default value
                add_at_end = ((self.minimum_size - len(values) /
                              self.checker.minimum_size) *
                              [self.checker.getDefaultValue(arg_name_to_bind)])
            else:
                excmsg = ("need at least "+str(self.minimum_size)+" items, "
                          "got "+str(len(values)))
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        # build range limite and manage max size
        if self.maximum_size is not None:
            if len(values) < self.maximum_size:
                msize = len(values)
            else:
                msize = self.maximum_size
        else:
            msize = len(values)

        # check every args
        ret = []
        if arg_number is not None:
            for i in range(0, msize, self.checker.minimum_size):
                if self.checker.minimum_size == 1:
                    ret.append(self.checker.getValue(values[i],
                                                     arg_number,
                                                     arg_name_to_bind))
                else:
                    value_max_index = i+self.checker.minimum_size
                    ret.append(self.checker.getValue(values[i:value_max_index],
                                                     arg_number,
                                                     arg_name_to_bind))

                arg_number += 1
        else:
            for i in range(0, msize, self.checker.minimum_size):
                if self.checker.minimum_size == 1:
                    ret.append(self.checker.getValue(values[i],
                                                     None,
                                                     arg_name_to_bind))
                else:
                    value_max_index = i+self.checker.minimum_size
                    ret.append(self.checker.getValue(values[i:value_max_index],
                                                     None,
                                                     arg_name_to_bind))

        # add the missing part
        ret.extend(add_at_end)
        return ret

    def getDefaultValue(self, arg_name_to_bind=None):
        if self.hasDefault:
            return self.default

        if self.minimum_size is None:
            return []

        if self.checker.hasDefaultValue(arg_name_to_bind):
            return ([self.checker.getDefaultValue(arg_name_to_bind)] *
                    self.minimum_size)

        excmsg = "getDefaultValue, there is no default value"
        self._raiseArgException(excmsg, None, arg_name_to_bind)

    def hasDefaultValue(self, arg_name_to_bind=None):
        return (self.hasDefault or
                self.minimum_size is None or
                self.checker.hasDefaultValue(arg_name_to_bind))

    def getUsage(self):
        if self.minimum_size is None:
            if self.maximum_size is None:
                return ("("+self.checker.getUsage()+" ... " +
                        self.checker.getUsage()+")")
            elif self.maximum_size == 1:
                return "("+self.checker.getUsage()+")"
            elif self.maximum_size == 2:
                return ("("+self.checker.getUsage()+"0 " +
                        self.checker.getUsage()+"1)")

            return ("("+self.checker.getUsage()+"0 ... " +
                    self.checker.getUsage()+str(self.maximum_size-1)+")")
        else:
            if self.minimum_size == 0 and self.maximum_size == 1:
                return "("+self.checker.getUsage()+")"

            if self.minimum_size == 1:
                if self.maximum_size == 1:
                    return self.checker.getUsage()

                part1 = self.checker.getUsage()+"0"
            elif self.minimum_size == 2:
                part1 = (self.checker.getUsage()+"0 "+self.checker.getUsage() +
                         "1")
            else:
                part1 = (self.checker.getUsage()+"0 ... " +
                         self.checker.getUsage()+str(self.minimum_size-1))

            if self.maximum_size is None:
                return part1 + " (... "+self.checker.getUsage()+")"
            else:
                not_mandatory_space = self.maximum_size - self.minimum_size
                if not_mandatory_space == 0:
                    return part1
                if not_mandatory_space == 1:
                    return (part1 + " ("+self.checker.getUsage() +
                            str(self.maximum_size-1)+")")
                elif not_mandatory_space == 2:
                    return (part1 + " ("+self.checker.getUsage() +
                            str(self.maximum_size-2)+"" +
                            self.checker.getUsage() +
                            str(self.maximum_size-1)+")")
                else:
                    return (part1+" ("+self.checker.getUsage() +
                            str(self.minimum_size)+" ... " +
                            self.checker.getUsage() +
                            str(self.maximum_size-1)+")")

    def __str__(self):
        return "ListArgChecker : "+str(self.checker)

    def setEngine(self, engine):
        ArgChecker.setEngine(self, engine)
        self.checker.setEngine(engine)


class FilePathArgChecker(StringArgChecker):
    # just check a path, no operation are executed here,
    # it is the job of the addon to perform change

    def __init__(self,
                 exist=None,
                 readable=None,
                 writtable=None,
                 is_file=None):
        StringArgChecker.__init__(self, 1, None, FILEPATHCHECKER_TYPENAME)

        if exist is not None and type(exist) != bool:
            excmsg = ("("+self.type_name+") exist must be None or a boolean, "
                      "got '"+str(type(exist))+"'")
            raise ArgInitializationException(excmsg)

        if readable is not None and type(readable) != bool:
            excmsg = ("("+self.type_name+") readable must be None or a boolean"
                      ", got '"+str(type(readable))+"'")
            raise ArgInitializationException(excmsg)

        if writtable is not None and type(writtable) != bool:
            excmsg = ("("+self.type_name+") writtable must be None or a "
                      "boolean, got '"+str(type(writtable))+"'")
            raise ArgInitializationException(excmsg)

        if is_file is not None and type(is_file) != bool:
            excmsg = ("("+self.type_name+") is_file must be None or a boolean,"
                      " got '"+str(type(is_file))+"'")
            raise ArgInitializationException(excmsg)

        self.exist = exist
        self.readable = readable
        self.writtable = writtable
        self.is_file = is_file

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        path = StringArgChecker.getValue(self,
                                         value,
                                         arg_number,
                                         arg_name_to_bind)

        # prepare path
        path = os.path.abspath(os.path.expandvars(os.path.expanduser(path)))

        file_exist = None

        # exist
        if self.exist is not None:
            file_exist = os.access(path, os.F_OK)

            if self.exist and not file_exist:
                excmsg = "Path '"+str(path)+"' does not exist and must exist"
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

            if not self.exist and file_exist:
                excmsg = "Path '"+str(path)+"' exists and must not exist"
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        # is_file
        if self.is_file is not None:
            if file_exist is None:
                file_exist = os.access(path, os.F_OK)

            if file_exist:
                is_file = os.path.isfile(path)

                if self.is_file and not is_file:
                    excmsg = ("Path '"+str(path)+"' is a directory and must be"
                              " a file")
                    self._raiseArgException(excmsg,
                                            arg_number,
                                            arg_name_to_bind)

                if not self.is_file and is_file:
                    excmsg = ("Path '"+str(path)+"' is a file and must be a "
                              "directory")
                    self._raiseArgException(excmsg,
                                            arg_number,
                                            arg_name_to_bind)
            # else: #if not exist, do not care, no way to know if it is a
            #        file or a directory

        # readable
        if self.readable is not None:
            if file_exist is None:
                file_exist = os.access(path, os.F_OK)

            if not file_exist:
                if self.exist is not None and self.exist:
                    excmsg = ("Path '"+str(path)+"' does not exist and so it "
                              "is not readable")
                    self._raiseArgException(excmsg,
                                            arg_number,
                                            arg_name_to_bind)

            else:
                readable = os.access(path, os.R_OK)

                if self.readable and not readable:
                    excmsg = ("Path '"+str(path)+"' is not readable and must "
                              "be readable")
                    self._raiseArgException(excmsg,
                                            arg_number,
                                            arg_name_to_bind)

                if not self.readable and readable:
                    excmsg = ("Path '"+str(path)+"' is readable and must not "
                              "be readable")
                    self._raiseArgException(excmsg,
                                            arg_number,
                                            arg_name_to_bind)

        # writtable
        if self.writtable is not None:
            if file_exist is None:
                file_exist = os.access(path, os.F_OK)

            if not file_exist:
                # first existing parent must be writtable
                curent_path = path
                parent_path = os.path.abspath(os.path.join(curent_path,
                                                           os.pardir))

                # until we reach the root
                while not os.path.samefile(parent_path, curent_path):
                    # this parent exists ?
                    if os.access(parent_path, os.F_OK):
                        # do we have write access on it ?
                        if not os.access(parent_path, os.W_OK):
                            # no writing access to the first existing
                            # directory, go to else clause of the loop
                            curent_path = parent_path
                            continue

                        # we have writing access, break the boucle
                        break

                    # go to a upper parent
                    curent_path = parent_path
                    parent_path = os.path.abspath(os.path.join(curent_path,
                                                               os.pardir))
                else:
                    excmsg = ("Path '"+str(path)+"' does not exist and the "
                              "first existing parent directory '" +
                              str(parent_path)+"' is not writtable")
                    self._raiseArgException(excmsg,
                                            arg_number,
                                            arg_name_to_bind)

            else:
                # return False if path does not exist...
                writtable = os.access(path, os.W_OK)

                if self.writtable and not writtable:
                    excmsg = ("Path '"+str(path)+"' is not writtable and must "
                              "be writtable")
                    self._raiseArgException(excmsg,
                                            arg_number,
                                            arg_name_to_bind)

                if not self.writtable and writtable:
                    excmsg = ("Path '"+str(path)+"' is writtable and must not "
                              "be writtable")
                    self._raiseArgException(excmsg,
                                            arg_number,
                                            arg_name_to_bind)

        # don't open a file, because not sure the addon will close it...
        return value

    def getUsage(self):
        return "<file_path>"


class AbstractKeyStoreTranslatorArgChecker(StringArgChecker):
    "retrieve a key from the keystore"

    def __init__(self,
                 key_size=None,
                 byte_key=True,
                 allowdifferentkey_size=False):
        StringArgChecker.__init__(self, 1, None, KEYTRANSLATORCHECKER_TYPENAME)

        if key_size is not None:
            if type(key_size) != int:
                excmsg = ("("+self.type_name+") key_size must be an integer, "
                          "got '"+str(type(key_size))+"'")
                raise ArgInitializationException(excmsg)

            if type(key_size) < 0:
                excmsg = ("("+self.type_name+") key_size must be bigger than 0"
                          ", got <"+str(key_size)+">")
                raise ArgInitializationException(excmsg)

        if (allowdifferentkey_size is None or
           type(allowdifferentkey_size) != bool):
            excmsg = ("("+self.type_name+") allowdifferentkey_size must be a "
                      "boolean, got '"+str(type(allowdifferentkey_size))+"'")
            raise ArgInitializationException(excmsg)

        if byte_key is None or type(byte_key) != bool:
            excmsg = ("("+self.type_name+") byte_key must be a boolean, got " +
                      "'"+str(type(byte_key))+"'")
            raise ArgInitializationException(excmsg)

        self.allowdifferentkey_size = allowdifferentkey_size
        self.key_size = key_size
        self.byte_key = byte_key

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        key_instance = value

        # check type
        if self.byte_key is not None:
            if (self.byte_key and
               key_instance.getKeyType() != CryptographicKey.KEYTYPE_HEXA):
                excmsg = ("the key '"+str(value)+"' is a bit key and the "
                          "process need a byte key")
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

            if (not self.byte_key and
               key_instance.getKeyType() != CryptographicKey.KEYTYPE_BIT):
                excmsg = ("the key '"+str(value)+"' is a byte key and the "
                          "process need a bit key")
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        # check size
        if (self.key_size is not None and
           not self.allowdifferentkey_size and
           key_instance.getkey_size() < self.key_size):
            if CryptographicKey.KEYTYPE_HEXA == key_instance.getKeyType():
                keytype = "byte(s)"
            else:
                keytype = "bit(s)"

            excmsg = ("too short key '"+str(value)+"', need a key of at least "
                      "<"+str(self.key_size)+" "+keytype+", got a <" +
                      str(key_instance.getkey_size())+"> "+keytype+" key")
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        return key_instance

    def getUsage(self):
        return "<key name>"


class KeyParameterChecker(AbstractParameterChecker,
                          AbstractKeyStoreTranslatorArgChecker):
    def __init__(self,
                 environment_string_path,
                 key_size=None,
                 byte_key=True,
                 allowdifferentkey_size=False):
        AbstractParameterChecker.__init__(self,
                                          environment_string_path,
                                          KEY_ATTRIBUTE_NAME,
                                          KEYTRASNLATORCHECKER_TYPENAME)
        AbstractKeyStoreTranslatorArgChecker.__init__(self,
                                                      key_size,
                                                      byte_key,
                                                      allowdifferentkey_size)

    def getValue(self,
                 value,
                 arg_number=None,
                 arg_name_to_bind=None):
        parameter = AbstractParameterChecker.getValue(value,
                                                      arg_number,
                                                      arg_name_to_bind)
        return AbstractKeyStoreTranslatorArgChecker.getValue(
            parameter.getValue())


class KeyParameterDynamicChecker(AbstractParameterDynamicChecker,
                                 AbstractKeyStoreTranslatorArgChecker):
    def __init__(self,
                 key_size=None,
                 byte_key=True,
                 allowdifferentkey_size=False):
        AbstractParameterDynamicChecker.__init__(
            self,
            KEY_ATTRIBUTE_NAME,
            KEYTRANSLATORDYNAMICCHECKER_TYPENAME)
        AbstractKeyStoreTranslatorArgChecker.__init__(self,
                                                      key_size,
                                                      byte_key,
                                                      allowdifferentkey_size)

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        parameter = AbstractParameterChecker.getValue(value,
                                                      arg_number,
                                                      arg_name_to_bind)
        return AbstractKeyStoreTranslatorArgChecker.getValue(
            parameter.getValue())


class KeyArgChecker(IntegerArgChecker):
    "create a key from the input"
    def __init__(self):
        self.bases = [2, 16]
        self.shortType = "key"
        IntegerArgChecker.__init__(self, 0, None, True, KEYCHECKER_TYPENAME)

    def getValue(self, value, arg_number=None, arg_name_to_bind=None):
        IntegerArgChecker.getValue(self, value, arg_number, arg_name_to_bind)

        try:
            return CryptographicKey(value)
        except Exception as e:
            excmsg = "Fail to resolve key: "+str(e)
            self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

    def getUsage(self):
        return "<key>"
