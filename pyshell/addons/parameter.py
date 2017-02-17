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
#   don't save property that still have default value

from pyshell.arg.argchecker import BooleanValueArgChecker
from pyshell.arg.argchecker import DefaultInstanceArgChecker as DefaultArgs
from pyshell.arg.argchecker import ListArgChecker
from pyshell.arg.argchecker import StringArgChecker
from pyshell.arg.argchecker import TokenValueArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.register.command import registerCommand
from pyshell.register.command import registerSetTempPrefix
from pyshell.register.command import registerStopHelpTraversalAt
from pyshell.system.context import ContextParameter
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.variable import VariableParameter
from pyshell.utils.constants import CONTEXT_ATTRIBUTE_NAME
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME
from pyshell.utils.constants import PARAMETER_NAME
from pyshell.utils.constants import VARIABLE_ATTRIBUTE_NAME
from pyshell.utils.postprocess import listFlatResultHandler
from pyshell.utils.postprocess import listResultHandler
from pyshell.utils.postprocess import printColumn
from pyshell.utils.postprocess import printColumnWithouHeader
from pyshell.utils.printing import formatBolt
from pyshell.utils.printing import formatOrange

# # CONSTANT SECTION # #
# TODO use settings constants from util.constant

AVAILABLE_TYPE = {
    "any":  DefaultArgs.getArgCheckerInstance,
    "string":  DefaultArgs.getStringArgCheckerInstance,
    "integer":  DefaultArgs.getIntegerArgCheckerInstance,
    "boolean":  DefaultArgs.getBooleanValueArgCheckerInstance,
    "float":  DefaultArgs.getFloatTokenArgCheckerInstance,
    "filePath":  DefaultArgs.getFileChecker}

ENVIRONMENT_SET_PROPERTIES = {
    "readOnly": ("setReadOnly",
                 DefaultArgs.getBooleanValueArgCheckerInstance(),),
    "removable": ("setRemovable",
                  DefaultArgs.getBooleanValueArgCheckerInstance(),),
    "transient": ("setTransient",
                  DefaultArgs.getBooleanValueArgCheckerInstance(),)}

CONTEXT_SET_PROPERTIES = {
    "transientIndex": ("setTransientIndex",
                       DefaultArgs.getBooleanValueArgCheckerInstance(),),
    "defaultIndex": ("setDefaultIndex",
                     DefaultArgs.getIntegerArgCheckerInstance(),),
    "index": ("setIndex",
              DefaultArgs.getIntegerArgCheckerInstance(),)}
CONTEXT_SET_PROPERTIES.update(ENVIRONMENT_SET_PROPERTIES)

ENVIRONMENT_GET_PROPERTIES = {"readOnly": "isReadOnly",
                              "removable": "isRemovable",
                              "transient": "isTransient"}

CONTEXT_GET_PROPERTIES = {"transientIndex": "isTransientIndex",
                          "defaultIndex": "getDefaultIndex",
                          "index": "getIndex"}
CONTEXT_GET_PROPERTIES.update(ENVIRONMENT_GET_PROPERTIES)

# # FUNCTION SECTION # #

# ################################### GENERIC METHOD ##########################


def getParameter(key,
                 parameters,
                 attribute_type,
                 start_with_local=True,
                 explore_other_scope=True,
                 perfect_match=False):
    if not hasattr(parameters, attribute_type):
        raise Exception("Unknow parameter type '" + str(attribute_type) + "'")

    container = getattr(parameters, attribute_type)
    param = container.getParameter(key,
                                   perfect_match=perfect_match,
                                   local_param=start_with_local,
                                   explore_other_scope=explore_other_scope)

    if param is None:
        raise Exception("Unknow parameter of type '"+str(attribute_type) +
                        "' with key '"+str(key)+"'")

    return param


def setProperties(key,
                  property_info,
                  property_value,
                  parameters,
                  attribute_type,
                  start_with_local=True,
                  explore_other_scope=True,
                  perfect_match=False):

    property_name, propertyChecker = property_info
    param = getParameter(key,
                         parameters,
                         attribute_type,
                         start_with_local,
                         explore_other_scope,
                         perfect_match)

    # TODO does not work for index and defaultIndex
    meth = getattr(param.settings, property_name)

    if meth is None:
        # TODO the list is not complete for context
        raise Exception("Unknown property '"+str(property_name)+"', one of "
                        "these was expected: readonly/removable/transient/"
                        "index_transient")

    meth(propertyChecker.getValue(property_value, "value", 0))


def getProperties(key,
                  property_name,
                  parameters,
                  attribute_type,
                  start_with_local=True,
                  explore_other_scope=True,
                  perfect_match=False):
    param = getParameter(key,
                         parameters,
                         attribute_type,
                         start_with_local,
                         explore_other_scope,
                         perfect_match)

    meth = getattr(param, property_name)

    if meth is None:
        raise Exception("Unknown property '"+str(property_name)+"', one of "
                        "these was expected: readonly/removable/transient/"
                        "index_transient")

    return meth()


def listProperties(key,
                   parameters,
                   attribute_type,
                   start_with_local=True,
                   explore_other_scope=True,
                   perfect_match=False):
    param = getParameter(key,
                         parameters,
                         attribute_type,
                         start_with_local,
                         explore_other_scope,
                         perfect_match)
    prop = list(param.settings.getProperties())
    prop.insert(0, (formatBolt("Key"), formatBolt("Value")))
    return prop


def removeParameter(key,
                    parameters,
                    attribute_type,
                    start_with_local=True,
                    explore_other_scope=True):
    if not hasattr(parameters, attribute_type):
        raise Exception("Unknow parameter type '" + str(attribute_type) + "'")

    container = getattr(parameters, attribute_type)

    if not container.hasParameter(key,
                                  perfect_match=True,
                                  local_param=start_with_local,
                                  explore_other_scope=explore_other_scope):
        return  # no job to do

    container.unsetParameter(
        key,
        local_param=start_with_local,
        explore_other_scope=explore_other_scope)


def _listGeneric(parameters,
                 attribute_type,
                 key,
                 format_value_fun,
                 get_title_fun,
                 start_with_local=True,
                 explore_other_scope=True):
    # TODO re-apply a width limit on the printing, too big value will show a
    # really big print on the terminal
    #   use it in printing ?
    #       nope because we maybe want to print something on the several line

    #   an util function allow to retrieve the terminal width
    #       if in shell only
    #       or script ? without output redirection

    # TODO try to display if global or local
    #   don't print that column if explore_other_scope == false

    #   for context and env, use the boolean lockEnabled
    #       but for the var ?

    if not hasattr(parameters, attribute_type):
        raise Exception("Unknow parameter type '" + str(attribute_type) + "'")

    container = getattr(parameters, attribute_type)

    if key is None:
        key = ""

    # retrieve all value from corresponding mltries
    dico = container.buildDictionnary(key,
                                      start_with_local,
                                      explore_other_scope)

    to_ret = []
    for subk, subv in dico.items():
        to_ret.append(format_value_fun(subk, subv, formatOrange))

    if len(to_ret) == 0:
        return [("No item available",)]

    to_ret.insert(0, get_title_fun(formatBolt))
    return to_ret


def _parameterRowFormating(key, param_item, value_formating_fun):

    if param_item.settings.isListChecker():
        value = ', '.join(str(x) for x in param_item.getValue())
    else:
        value = str(param_item.getValue())

    return ("  " + key, value_formating_fun(value), )


def _parameterGetTitle(title_formating_fun):
    return (" "+title_formating_fun("Name"), title_formating_fun("Value"),)


@shellMethod(
    parameters=DefaultArgs.getCompleteEnvironmentChecker(),
    key=StringArgChecker())
def listParameter(parameters, key=None):
    to_print = []
    for subcontainername in parameters.parameterManagerList:
        if not hasattr(parameters, subcontainername):
            raise Exception("Unknow parameter type '"+str(subcontainername) +
                            "'")

        to_print.append(formatBolt(subcontainername.upper()))
        to_print.extend(_listGeneric(parameters,
                                     subcontainername,
                                     key,
                                     _parameterRowFormating,
                                     _parameterGetTitle))

    return to_print


def _createValuesFun(value_type,
                     key,
                     values,
                     class_def,
                     attribute_type,
                     no_creation_if_exist,
                     parameters,
                     list_enabled,
                     local_param=True):
    if not hasattr(parameters, attribute_type):
        raise Exception("Unknow parameter type '" + str(attribute_type) + "'")

    container = getattr(parameters, attribute_type)

    # build checker
    if list_enabled:
        checker = ListArgChecker(value_type(), 1)
    else:
        checker = value_type()

    if (container.hasParameter(key,
                               perfect_match=True,
                               local_param=local_param,
                               explore_other_scope=False) and
       no_creation_if_exist):
        return
        # no need to manage readonly or removable setting here, it will be
        # checked in setParameter

    # check value
    value = checker.getValue(values,
                             None,
                             str(attribute_type).title()+" "+key)
    container.setParameter(key, class_def(value, checker))

# ################################### env management###########################


@shellMethod(key=DefaultArgs.getStringArgCheckerInstance(),
             values=ListArgChecker(DefaultArgs.getArgCheckerInstance()),
             parameters=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def subtractEnvironmentValuesFun(key,
                                 values,
                                 parameters,
                                 start_with_local=True,
                                 explore_other_scope=True):
    "remove some elements from an environment parameter"
    param = getParameter(key,
                         parameters,
                         ENVIRONMENT_ATTRIBUTE_NAME,
                         start_with_local,
                         explore_other_scope)
    param.removeValues(values)


@shellMethod(key=DefaultArgs.getStringArgCheckerInstance(),
             parameters=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def removeEnvironmentContextValues(key,
                                   parameters,
                                   start_with_local=True,
                                   explore_other_scope=True):
    "remove an environment parameter"
    removeParameter(key,
                    parameters,
                    ENVIRONMENT_ATTRIBUTE_NAME,
                    start_with_local,
                    explore_other_scope)


@shellMethod(key=DefaultArgs.getStringArgCheckerInstance(),
             parameters=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def getEnvironmentValues(key,
                         parameters,
                         start_with_local=True,
                         explore_other_scope=True):
    "get an environment parameter value"
    return getParameter(key,
                        parameters,
                        ENVIRONMENT_ATTRIBUTE_NAME,
                        start_with_local,
                        explore_other_scope).getValue()


@shellMethod(key=DefaultArgs.getStringArgCheckerInstance(),
             values=ListArgChecker(DefaultArgs.getArgCheckerInstance(), 1),
             parameters=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def setEnvironmentValuesFun(key,
                            values,
                            parameters,
                            start_with_local=True,
                            explore_other_scope=True):
    "set an environment parameter value"

    env_param = getParameter(key,
                             parameters,
                             ENVIRONMENT_ATTRIBUTE_NAME,
                             start_with_local,
                             explore_other_scope)

    if env_param.settings.isListChecker():
        env_param.setValue(values)
    else:
        env_param.setValue(values[0])


@shellMethod(value_type=TokenValueArgChecker(AVAILABLE_TYPE),
             key=DefaultArgs.getStringArgCheckerInstance(),
             value=ListArgChecker(DefaultArgs.getArgCheckerInstance()),
             is_list=BooleanValueArgChecker(),
             no_creation_if_exist=BooleanValueArgChecker(),
             parameters=DefaultArgs.getCompleteEnvironmentChecker(),
             local_var=BooleanValueArgChecker())
def createEnvironmentValueFun(value_type,
                              key,
                              value,
                              is_list=True,
                              no_creation_if_exist=False,
                              parameters=None,
                              local_var=True):
    "create an environment parameter value"
    _createValuesFun(value_type,
                     key,
                     value,
                     EnvironmentParameter,
                     ENVIRONMENT_ATTRIBUTE_NAME,
                     no_creation_if_exist,
                     parameters,
                     is_list,
                     local_var)


@shellMethod(key=DefaultArgs.getStringArgCheckerInstance(),
             values=ListArgChecker(DefaultArgs.getArgCheckerInstance()),
             parameters=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def addEnvironmentValuesFun(key,
                            values,
                            parameters,
                            start_with_local=True,
                            explore_other_scope=True):
    "add values to an environment parameter list"
    param = getParameter(key,
                         parameters,
                         ENVIRONMENT_ATTRIBUTE_NAME,
                         start_with_local,
                         explore_other_scope)
    param.addValues(values)


def _envRowFormating(key, env_item, value_formating_fun):
    if env_item.settings.isListChecker():
        return (key,
                "true",
                value_formating_fun(
                    ', '.join(str(x) for x in env_item.getValue())),)
    else:
        return (key, "false", value_formating_fun(str(env_item.getValue())),)


def _envGetTitle(title_formating_fun):
    return (title_formating_fun("Name"),
            title_formating_fun("is_list"),
            title_formating_fun("Value(s)"),)


@shellMethod(parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             key=StringArgChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def listEnvs(parameter,
             key=None,
             start_with_local=True,
             explore_other_scope=True):
    "list every existing contexts"
    return _listGeneric(parameter,
                        ENVIRONMENT_ATTRIBUTE_NAME,
                        key,
                        _envRowFormating,
                        _envGetTitle,
                        start_with_local,
                        explore_other_scope)


@shellMethod(key=StringArgChecker(),
             property_name=TokenValueArgChecker(ENVIRONMENT_SET_PROPERTIES),
             property_value=DefaultArgs.getBooleanValueArgCheckerInstance(),
             parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def setEnvironmentProperties(key,
                             property_name,
                             property_value,
                             parameter,
                             start_with_local=True,
                             explore_other_scope=True):
    "set environment property"
    setProperties(key,
                  property_name,
                  property_value,
                  parameter,
                  ENVIRONMENT_ATTRIBUTE_NAME,
                  start_with_local,
                  explore_other_scope)


@shellMethod(key=StringArgChecker(),
             property_name=TokenValueArgChecker(ENVIRONMENT_GET_PROPERTIES),
             parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def getEnvironmentProperties(key,
                             property_name,
                             parameter,
                             start_with_local=True,
                             explore_other_scope=True):
    "get environment property"
    return getProperties(key,
                         property_name,
                         parameter,
                         ENVIRONMENT_ATTRIBUTE_NAME,
                         start_with_local,
                         explore_other_scope)


@shellMethod(key=StringArgChecker(),
             parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def listEnvironmentProperties(key,
                              parameter,
                              start_with_local=True,
                              explore_other_scope=True):
    "list every properties from a specific environment object"
    return listProperties(key,
                          parameter,
                          ENVIRONMENT_ATTRIBUTE_NAME,
                          start_with_local,
                          explore_other_scope)

# ################################### context management ######################


@shellMethod(key=DefaultArgs.getStringArgCheckerInstance(),
             values=ListArgChecker(DefaultArgs.getArgCheckerInstance()),
             parameters=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def subtractContextValuesFun(key,
                             values,
                             parameters,
                             start_with_local=True,
                             explore_other_scope=True):
    "remove some elements from a context parameter"
    param = getParameter(key,
                         parameters,
                         CONTEXT_ATTRIBUTE_NAME,
                         start_with_local,
                         explore_other_scope)
    param.removeValues(values)


@shellMethod(value_type=TokenValueArgChecker(AVAILABLE_TYPE),
             key=DefaultArgs.getStringArgCheckerInstance(),
             values=ListArgChecker(DefaultArgs.getArgCheckerInstance()),
             no_creation_if_exist=BooleanValueArgChecker(),
             parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             local_var=BooleanValueArgChecker())
def createContextValuesFun(value_type,
                           key,
                           values,
                           no_creation_if_exist=False,
                           parameter=None,
                           local_var=True):
    "create a context parameter value list"
    _createValuesFun(value_type,
                     key,
                     values,
                     ContextParameter,
                     CONTEXT_ATTRIBUTE_NAME,
                     no_creation_if_exist,
                     parameter,
                     True,
                     local_var)


@shellMethod(key=DefaultArgs.getStringArgCheckerInstance(),
             parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def removeContextValues(key,
                        parameter,
                        start_with_local=True,
                        explore_other_scope=True):
    "remove a context parameter"
    removeParameter(key,
                    parameter,
                    CONTEXT_ATTRIBUTE_NAME,
                    start_with_local,
                    explore_other_scope)


@shellMethod(key=DefaultArgs.getStringArgCheckerInstance(),
             parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def getContextValues(key,
                     parameter,
                     start_with_local=True,
                     explore_other_scope=True):
    "get a context parameter value"
    return getParameter(key,
                        parameter,
                        CONTEXT_ATTRIBUTE_NAME,
                        start_with_local, explore_other_scope).getValue()


@shellMethod(key=DefaultArgs.getStringArgCheckerInstance(),
             values=ListArgChecker(DefaultArgs.getArgCheckerInstance(), 1),
             parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def setContextValuesFun(key,
                        values,
                        parameter,
                        start_with_local=True,
                        explore_other_scope=True):
    "set a context parameter value"
    getParameter(key,
                 parameter,
                 CONTEXT_ATTRIBUTE_NAME,
                 start_with_local,
                 explore_other_scope).setValue(values)


@shellMethod(key=DefaultArgs.getStringArgCheckerInstance(),
             values=ListArgChecker(DefaultArgs.getArgCheckerInstance()),
             parameters=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def addContextValuesFun(key,
                        values,
                        parameters,
                        start_with_local=True,
                        explore_other_scope=True):
    "add values to a context parameter list"
    param = getParameter(key,
                         parameters,
                         CONTEXT_ATTRIBUTE_NAME,
                         start_with_local,
                         explore_other_scope)
    param.addValues(values)


@shellMethod(key=DefaultArgs.getStringArgCheckerInstance(),
             value=DefaultArgs.getArgCheckerInstance(),
             parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def selectValue(key,
                value,
                parameter,
                start_with_local=True,
                explore_other_scope=True):
    "select the value for the current context"
    getParameter(key,
                 parameter,
                 CONTEXT_ATTRIBUTE_NAME,
                 start_with_local,
                 explore_other_scope).setSelectedValue(value)


@shellMethod(key=DefaultArgs.getStringArgCheckerInstance(),
             index=DefaultArgs.getIntegerArgCheckerInstance(),
             parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def selectValueIndex(key,
                     index,
                     parameter,
                     start_with_local=True,
                     explore_other_scope=True):
    "select the value index for the current context"
    getParameter(key,
                 parameter,
                 CONTEXT_ATTRIBUTE_NAME,
                 start_with_local,
                 explore_other_scope).settings.setIndex(index)


@shellMethod(key=DefaultArgs.getStringArgCheckerInstance(),
             parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def getSelectedContextValue(key,
                            parameter,
                            start_with_local=True,
                            explore_other_scope=True):
    "get the selected value for the current context"
    return getParameter(key,
                        parameter,
                        CONTEXT_ATTRIBUTE_NAME,
                        start_with_local,
                        explore_other_scope).getSelectedValue()


@shellMethod(key=DefaultArgs.getStringArgCheckerInstance(),
             parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def getSelectedContextIndex(key,
                            parameter,
                            start_with_local=True,
                            explore_other_scope=True):
    "get the selected value index for the current context"
    return getParameter(key,
                        parameter,
                        CONTEXT_ATTRIBUTE_NAME,
                        start_with_local,
                        explore_other_scope).settings.getIndex()


def _conRowFormating(key, con_item, value_formating_fun):
    return (key,
            str(con_item.settings.getIndex()),
            value_formating_fun(str(con_item.getSelectedValue())),
            ', '.join(str(x) for x in con_item.getValue()),)


def _conGetTitle(title_formating_fun):
    return (title_formating_fun("Name"),
            title_formating_fun("Index"),
            title_formating_fun("Value"),
            title_formating_fun("Values"), )


@shellMethod(parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             key=StringArgChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def listContexts(parameter,
                 key=None,
                 start_with_local=True,
                 explore_other_scope=True):
    "list every existing contexts"
    return _listGeneric(parameter,
                        CONTEXT_ATTRIBUTE_NAME, key,
                        _conRowFormating,
                        _conGetTitle,
                        start_with_local,
                        explore_other_scope)


@shellMethod(key=StringArgChecker(),
             property_name=TokenValueArgChecker(CONTEXT_SET_PROPERTIES),
             property_value=DefaultArgs.getArgCheckerInstance(),
             parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def setContextProperties(key,
                         property_name,
                         property_value,
                         parameter,
                         start_with_local=True,
                         explore_other_scope=True):
    "set a context property"
    setProperties(key,
                  property_name,
                  property_value,
                  parameter,
                  CONTEXT_ATTRIBUTE_NAME,
                  start_with_local,
                  explore_other_scope)


@shellMethod(key=StringArgChecker(),
             property_name=TokenValueArgChecker(CONTEXT_GET_PROPERTIES),
             parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def getContextProperties(key,
                         property_name,
                         parameter,
                         start_with_local=True,
                         explore_other_scope=True):
    "get a context property"
    return getProperties(key,
                         property_name,
                         parameter,
                         CONTEXT_ATTRIBUTE_NAME,
                         start_with_local,
                         explore_other_scope)


@shellMethod(key=StringArgChecker(),
             parameter=DefaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def listContextProperties(key,
                          parameter,
                          start_with_local=True,
                          explore_other_scope=True):
    "list every properties of a specific context object"
    return listProperties(key,
                          parameter,
                          CONTEXT_ATTRIBUTE_NAME,
                          start_with_local,
                          explore_other_scope)

# ################################### var management ##########################

# beginning OF POC


@shellMethod(key=DefaultArgs.getStringArgCheckerInstance(),
             values=ListArgChecker(DefaultArgs.getArgCheckerInstance()),
             engine=DefaultArgs.getEngineChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def preAddValues(key, values, engine=None,
                 start_with_local=True, explore_other_scope=True):

    cmd = engine.getCurrentCommand()
    cmd.dynamic_parameter["key"] = key
    cmd.dynamic_parameter["disabled"] = False
    cmd.dynamic_parameter["start_with_local"] = start_with_local
    cmd.dynamic_parameter["explore_other_scope"] = explore_other_scope

    return values


@shellMethod(values=ListArgChecker(DefaultArgs.getArgCheckerInstance()),
             engine=DefaultArgs.getEngineChecker())
def proAddValues(values, engine):

    # if no previous command, default behaviour
    if not engine.hasPreviousCommand():
        return values

    # if not, clone this command and add it at the end of cmd list
    cmd = engine.getCurrentCommand()
    cmd_clone = cmd.clone()
    engine.addCommand(cmd_clone, convertProcessToPreProcess=True)

    for k, v in cmd.dynamic_parameter.items():
        cmd_clone.dynamic_parameter[k] = v

    cmd.dynamic_parameter["disabled"] = True
    cmd_clone.dynamic_parameter["disabled"] = True

    # TODO execute previous

    return values


@shellMethod(
    values=ListArgChecker(DefaultArgs.getArgCheckerInstance()),
    parameters=DefaultArgs.getCompleteEnvironmentChecker(),
    engine=DefaultArgs.getEngineChecker())
def postAddValues(values, parameters=None, engine=None):
    "add values to a var"

    cmd = engine.getCurrentCommand()

    if cmd.dynamic_parameter["disabled"]:
        return values

    key = cmd.dynamic_parameter["key"]

    if parameters.variable.hasParameter(
          key,
          cmd.dynamic_parameter["start_with_local"],
          cmd.dynamic_parameter["explore_other_scope"]):
        param = getParameter(key,
                             parameters,
                             VARIABLE_ATTRIBUTE_NAME,
                             cmd.dynamic_parameter["start_with_local"],
                             cmd.dynamic_parameter["explore_other_scope"])
        param.addValues(values)
    else:
        parameters.variable.setParameter(key, VariableParameter(
            values), cmd.dynamic_parameter["start_with_local"])

    return values

# END OF POC


@shellMethod(
    key=DefaultArgs.getStringArgCheckerInstance(),
    values=ListArgChecker(
         DefaultArgs.getArgCheckerInstance()),
    parameters=DefaultArgs.getCompleteEnvironmentChecker(),
    start_with_local=BooleanValueArgChecker(),
    explore_other_scope=BooleanValueArgChecker())
def subtractValuesVar(key, values, parameters=None,
                      start_with_local=True, explore_other_scope=True):
    "remove existing value from a variable, remove first occurence met"
    param = getParameter(
        key,
        parameters,
        VARIABLE_ATTRIBUTE_NAME,
        start_with_local,
        explore_other_scope)
    param.removeValues(values)


@shellMethod(
    key=DefaultArgs.getStringArgCheckerInstance(),
    values=ListArgChecker(
         DefaultArgs.getArgCheckerInstance()),
    parameter=DefaultArgs.getCompleteEnvironmentChecker(),
    local_var=BooleanValueArgChecker())
def setVar(key, values, parameter, local_var=True):
    "assign a value to a variable"
    parameter.variable.setParameter(key, VariableParameter(values), local_var)


@shellMethod(
    key=DefaultArgs.getStringArgCheckerInstance(),
    parameter=DefaultArgs.getCompleteEnvironmentChecker(),
    start_with_local=BooleanValueArgChecker(),
    explore_other_scope=BooleanValueArgChecker())
def getVar(key, parameter, start_with_local=True, explore_other_scope=True):
    "get the value of a variable"
    return getParameter(key, parameter, VARIABLE_ATTRIBUTE_NAME,
                        start_with_local, explore_other_scope).getValue()


@shellMethod(
    key=DefaultArgs.getStringArgCheckerInstance(),
    parameter=DefaultArgs.getCompleteEnvironmentChecker(),
    start_with_local=BooleanValueArgChecker(),
    explore_other_scope=BooleanValueArgChecker())
def unsetVar(key, parameter, start_with_local=True, explore_other_scope=True):
    "unset a variable, no error if does not exist"
    removeParameter(
        key,
        parameter,
        VARIABLE_ATTRIBUTE_NAME,
        start_with_local,
        explore_other_scope)


def _varRowFormating(key, var_item, value_formating_fun):
    return (key, value_formating_fun(', '.join(str(x)
                                               for x in var_item.getValue())),)


def _varGetTitle(title_formating_fun):
    return (title_formating_fun("Name"), title_formating_fun("Values"), )


@shellMethod(
    parameter=DefaultArgs.getCompleteEnvironmentChecker(),
    key=StringArgChecker(),
    start_with_local=BooleanValueArgChecker(),
    explore_other_scope=BooleanValueArgChecker())
def listVars(parameter,
             key=None,
             start_with_local=True,
             explore_other_scope=True):
    "list every existing variables"
    return _listGeneric(parameter,
                        VARIABLE_ATTRIBUTE_NAME,
                        key,
                        _varRowFormating,
                        _varGetTitle,
                        start_with_local,
                        explore_other_scope)

# ################################### REGISTER SECTION ########################

# var
registerSetTempPrefix((VARIABLE_ATTRIBUTE_NAME, ))
registerCommand(("set",), post=setVar)
registerCommand(("create",), post=setVar)  # compatibility issue
registerCommand(("get",), pre=getVar, pro=listResultHandler)
registerCommand(("unset",), pro=unsetVar)
registerCommand(("list",), pre=listVars, pro=printColumn)
registerCommand(("add",), pre=preAddValues,
                pro=proAddValues, post=postAddValues)
registerCommand(("subtract",), post=subtractValuesVar)
registerStopHelpTraversalAt()

# context
registerSetTempPrefix((CONTEXT_ATTRIBUTE_NAME, ))
registerCommand(("unset",), pro=removeContextValues)
registerCommand(("get",), pre=getContextValues, pro=listResultHandler)
registerCommand(("set",), post=setContextValuesFun)
registerCommand(("create",), post=createContextValuesFun)
registerCommand(("add",), post=addContextValuesFun)
registerCommand(("subtract",), post=subtractContextValuesFun)
registerCommand(("value",), pre=getSelectedContextValue,
                pro=listFlatResultHandler)
registerCommand(("index",), pre=getSelectedContextIndex,
                pro=listFlatResultHandler)
registerCommand(("select", "index",), post=selectValueIndex)
registerCommand(("select", "value",), post=selectValue)
registerStopHelpTraversalAt(("select",))
registerCommand(("properties", "list"),
                pre=listContextProperties, pro=printColumn)
registerCommand(("list",), pre=listContexts, pro=printColumn)
registerCommand(("properties", "set"), pro=setContextProperties)
registerCommand(("properties", "get"), pre=getContextProperties,
                pro=listFlatResultHandler)
registerStopHelpTraversalAt(("properties",))
registerStopHelpTraversalAt()

# env
registerSetTempPrefix((ENVIRONMENT_ATTRIBUTE_NAME, ))
registerCommand(("list",), pro=listEnvs, post=printColumn)
registerCommand(("create",), post=createEnvironmentValueFun)
registerCommand(("get",), pre=getEnvironmentValues, pro=listResultHandler)
registerCommand(("unset",), pro=removeEnvironmentContextValues)
registerCommand(("set",), post=setEnvironmentValuesFun)
registerCommand(("add",), post=addEnvironmentValuesFun)
registerCommand(("subtract",), post=subtractEnvironmentValuesFun)
registerCommand(("properties", "set"), pro=setEnvironmentProperties)
registerCommand(("properties", "get"),
                pre=getEnvironmentProperties, pro=listFlatResultHandler)
registerCommand(("properties", "list"),
                pre=listEnvironmentProperties, pro=printColumn)
registerStopHelpTraversalAt(("properties",))
registerStopHelpTraversalAt()

# parameter
registerSetTempPrefix((PARAMETER_NAME, ))
registerCommand(("list",), pro=listParameter, post=printColumnWithouHeader)
registerStopHelpTraversalAt()
