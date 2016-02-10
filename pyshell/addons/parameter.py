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

import os

from pyshell.arg.argchecker import booleanValueArgChecker
from pyshell.arg.argchecker import defaultInstanceArgChecker as defaultArgs
from pyshell.arg.argchecker import environmentParameterChecker
from pyshell.arg.argchecker import listArgChecker
from pyshell.arg.argchecker import stringArgChecker
from pyshell.arg.argchecker import tokenValueArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.loader.command import registerCommand
from pyshell.loader.command import registerSetTempPrefix
from pyshell.loader.command import registerStopHelpTraversalAt
from pyshell.system.context import ContextParameter
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.procedure import ProcedureFromFile
from pyshell.system.variable import VarParameter
from pyshell.utils.constants import CONTEXT_ATTRIBUTE_NAME
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME
from pyshell.utils.constants import ENVIRONMENT_PARAMETER_FILE_KEY
from pyshell.utils.constants import PARAMETER_NAME
from pyshell.utils.constants import VARIABLE_ATTRIBUTE_NAME
from pyshell.utils.misc import createParentDirectory
from pyshell.utils.parsing import escapeString
from pyshell.utils.postprocess import listFlatResultHandler
from pyshell.utils.postprocess import listResultHandler
from pyshell.utils.postprocess import printColumn
from pyshell.utils.postprocess import printColumnWithouHeader
from pyshell.utils.printing import formatBolt
from pyshell.utils.printing import formatOrange

# # CONSTANT SECTION # #

AVAILABLE_TYPE = {
    "any":  defaultArgs.getArgCheckerInstance,
    "string":  defaultArgs.getStringArgCheckerInstance,
    "integer":  defaultArgs.getIntegerArgCheckerInstance,
    "boolean":  defaultArgs.getbooleanValueArgCheckerInstance,
    "float":  defaultArgs.getFloatTokenArgCheckerInstance,
    "filePath":  defaultArgs.getFileChecker}

ENVIRONMENT_SET_PROPERTIES = {
    "readOnly": ("setReadOnly",
                 defaultArgs.getbooleanValueArgCheckerInstance(),),
    "removable": ("setRemovable",
                  defaultArgs.getbooleanValueArgCheckerInstance(),),
    "transient": ("setTransient",
                  defaultArgs.getbooleanValueArgCheckerInstance(),)}

CONTEXT_SET_PROPERTIES = {
    "transientIndex": ("setTransientIndex",
                       defaultArgs.getbooleanValueArgCheckerInstance(),),
    "defaultIndex": ("setDefaultIndex",
                     defaultArgs.getIntegerArgCheckerInstance(),),
    "index": ("setIndex",
              defaultArgs.getIntegerArgCheckerInstance(),)}
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
                 explore_other_level=True,
                 perfect_match=False):
    if not hasattr(parameters, attribute_type):
        raise Exception("Unknow parameter type '" + str(attribute_type) + "'")

    container = getattr(parameters, attribute_type)
    param = container.getParameter(key,
                                   perfectMatch=perfect_match,
                                   localParam=start_with_local,
                                   exploreOtherLevel=explore_other_level)

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
                  explore_other_level=True,
                  perfect_match=False):

    property_name, propertyChecker = property_info
    param = getParameter(key,
                         parameters,
                         attribute_type,
                         start_with_local,
                         explore_other_level,
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
                  explore_other_level=True,
                  perfect_match=False):
    param = getParameter(key,
                         parameters,
                         attribute_type,
                         start_with_local,
                         explore_other_level,
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
                   explore_other_level=True,
                   perfect_match=False):
    param = getParameter(key,
                         parameters,
                         attribute_type,
                         start_with_local,
                         explore_other_level,
                         perfect_match)
    prop = list(param.settings.getProperties())
    prop.insert(0, (formatBolt("Key"), formatBolt("Value")))
    return prop


def removeParameter(key,
                    parameters,
                    attribute_type,
                    start_with_local=True,
                    explore_other_level=True):
    if not hasattr(parameters, attribute_type):
        raise Exception("Unknow parameter type '" + str(attribute_type) + "'")

    container = getattr(parameters, attribute_type)

    if not container.hasParameter(key,
                                  perfectMatch=True,
                                  localParam=start_with_local,
                                  exploreOtherLevel=explore_other_level):
        return  # no job to do

    container.unsetParameter(
        key,
        localParam=start_with_local,
        exploreOtherLevel=explore_other_level)


def _listGeneric(parameters,
                 attribute_type,
                 key,
                 format_value_fun,
                 get_title_fun,
                 start_with_local=True,
                 explore_other_level=True):
    # TODO re-apply a width limit on the printing, too big value will show a
    # really big print on the terminal
    #   use it in printing ?
    #       nope because we maybe want to print something on the several line

    #   an util function allow to retrieve the terminal width
    #       if in shell only
    #       or script ? without output redirection

    # TODO try to display if global or local
    #   don't print that column if explore_other_level == false

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
                                      explore_other_level)

    to_ret = []
    for subk, subv in dico.items():
        to_ret.append(format_value_fun(subk, subv, formatOrange))

    if len(to_ret) == 0:
        return [("No item available",)]

    to_ret.insert(0, get_title_fun(formatBolt))
    return to_ret


def _parameterRowFormating(key, param_item, value_formating_fun):

    if param_item.isAListType():
        value = ', '.join(str(x) for x in param_item.getValue())
    else:
        value = str(param_item.getValue())

    return ("  " + key, value_formating_fun(value), )


def _parameterGetTitle(title_formating_fun):
    return (" "+title_formating_fun("Name"), title_formating_fun("Value"),)


@shellMethod(
    parameters=defaultArgs.getCompleteEnvironmentChecker(),
    key=stringArgChecker())
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


@shellMethod(
    file_path=environmentParameterChecker(ENVIRONMENT_PARAMETER_FILE_KEY),
    parameters=defaultArgs.getCompleteEnvironmentChecker())
def loadParameter(file_path, parameters):
    "load parameters from the settings file"

    if os.path.exists(file_path.getValue()):
        afile = ProcedureFromFile(file_path.getValue())
        afile.neverStopIfErrorOccured()
        # TODO yeaah, never stop execution BUT there is a problem
        # if a parameter creation trigger an exception, the "set properties"
        # will still be executed
        # think about that

        # need to jump over these setProperties if any exception occurs, create
        # a method "jumpOverNextXlineIfPreviousCommandWasOnError"

        afile.execute(parameters=parameters)
    else:
        saveParameter(file_path, parameters)


@shellMethod(
    file_path=environmentParameterChecker(ENVIRONMENT_PARAMETER_FILE_KEY),
    parameters=defaultArgs.getCompleteEnvironmentChecker())
def saveParameter(file_path, parameters):
    "save not transient parameters to the settings file"

    # TODO is there something to save ?
    # SOLUTION1 should compare the content of the file, the memory and the
    #   starting parameter...
    # SOLUTION2 historized parameters
    # store old value, when it has been change and by what

    file_path = file_path.getValue()

    # create directory if needed
    createParentDirectory(file_path)

    with open(file_path, 'wb') as configfile:
        for subcontainername in parameters.parameterManagerList:
            container = getattr(parameters, subcontainername)
            dico = container.buildDictionnary("",
                                              localParam=False,
                                              exploreOtherLevel=False)

            for key, parameter in dico.items():
                if parameter.settings.isTransient():
                    continue

                if parameter.isAListType():
                    values = " ".join(
                        escapeString(str(x)) for x in parameter.getValue())
                    configfile.write(subcontainername+" create " +
                                     parameter.typ.checker.getTypeName() +
                                     " "+key+" "+values +
                                     " -no_creation_if_exist true"
                                     " -local_var false\n")
                else:
                    configfile.write(subcontainername +
                                     " create "+parameter.typ.getTypeName() +
                                     " "+key+" " +
                                     escapeString(str(parameter.getValue())) +
                                     " -is_list false"
                                     " -no_creation_if_exist true"
                                     " -local_var false\n")

                properties = parameter.settings.getProperties()

                if len(properties) > 0:
                    # disable readOnly
                    configfile.write(
                        subcontainername +
                        " properties set " +
                        key +
                        " readOnly false\n")

                    # set value
                    if parameter.isAListType():
                        configfile.write(
                            subcontainername +
                            " set " +
                            key +
                            " " +
                            " ".join(
                                str(x) for x in parameter.getValue()) +
                            "\n")
                    else:
                        configfile.write(subcontainername +
                                         " set " +
                                         key +
                                         " " +
                                         str(parameter.getValue()) +
                                         "\n")

                    read_only_value = False
                    settings = parameter.settings
                    for propName, propValue in settings.getProperties():
                        # TODO skip transient properties, no need to be
                        # saved...

                        # readonly should always be written on last
                        if propName.lower() == "readonly":
                            read_only_value = propValue
                            continue

                        configfile.write(subcontainername+" properties set " +
                                         key+" "+propName+" "+str(propValue) +
                                         "\n")
                    # TODO don't disable again if already disabled
                    configfile.write(subcontainername+" properties set " +
                                     key+" readOnly "+str(read_only_value) +
                                     "\n")
                configfile.write("\n")


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
        checker = listArgChecker(value_type(), 1)
    else:
        checker = value_type()

    if (container.hasParameter(key,
                               perfectMatch=True,
                               localParam=local_param,
                               exploreOtherLevel=False) and
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


@shellMethod(key=defaultArgs.getStringArgCheckerInstance(),
             values=listArgChecker(defaultArgs.getArgCheckerInstance()),
             parameters=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def subtractEnvironmentValuesFun(key,
                                 values,
                                 parameters,
                                 start_with_local=True,
                                 explore_other_level=True):
    "remove some elements from an environment parameter"
    param = getParameter(key,
                         parameters,
                         ENVIRONMENT_ATTRIBUTE_NAME,
                         start_with_local,
                         explore_other_level)
    param.removeValues(values)


@shellMethod(key=defaultArgs.getStringArgCheckerInstance(),
             parameters=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def removeEnvironmentContextValues(key,
                                   parameters,
                                   start_with_local=True,
                                   explore_other_level=True):
    "remove an environment parameter"
    removeParameter(key,
                    parameters,
                    ENVIRONMENT_ATTRIBUTE_NAME,
                    start_with_local,
                    explore_other_level)


@shellMethod(key=defaultArgs.getStringArgCheckerInstance(),
             parameters=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def getEnvironmentValues(key,
                         parameters,
                         start_with_local=True,
                         explore_other_level=True):
    "get an environment parameter value"
    return getParameter(key,
                        parameters,
                        ENVIRONMENT_ATTRIBUTE_NAME,
                        start_with_local,
                        explore_other_level).getValue()


@shellMethod(key=defaultArgs.getStringArgCheckerInstance(),
             values=listArgChecker(defaultArgs.getArgCheckerInstance(), 1),
             parameters=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def setEnvironmentValuesFun(key,
                            values,
                            parameters,
                            start_with_local=True,
                            explore_other_level=True):
    "set an environment parameter value"

    env_param = getParameter(key,
                             parameters,
                             ENVIRONMENT_ATTRIBUTE_NAME,
                             start_with_local,
                             explore_other_level)

    if env_param.isAListType():
        env_param.setValue(values)
    else:
        env_param.setValue(values[0])


@shellMethod(value_type=tokenValueArgChecker(AVAILABLE_TYPE),
             key=defaultArgs.getStringArgCheckerInstance(),
             value=listArgChecker(defaultArgs.getArgCheckerInstance()),
             is_list=booleanValueArgChecker(),
             no_creation_if_exist=booleanValueArgChecker(),
             parameters=defaultArgs.getCompleteEnvironmentChecker(),
             local_var=booleanValueArgChecker())
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


@shellMethod(key=defaultArgs.getStringArgCheckerInstance(),
             values=listArgChecker(defaultArgs.getArgCheckerInstance()),
             parameters=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def addEnvironmentValuesFun(key,
                            values,
                            parameters,
                            start_with_local=True,
                            explore_other_level=True):
    "add values to an environment parameter list"
    param = getParameter(key,
                         parameters,
                         ENVIRONMENT_ATTRIBUTE_NAME,
                         start_with_local,
                         explore_other_level)
    param.addValues(values)


def _envRowFormating(key, env_item, value_formating_fun):
    if env_item.isAListType():
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


@shellMethod(parameter=defaultArgs.getCompleteEnvironmentChecker(),
             key=stringArgChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def listEnvs(parameter,
             key=None,
             start_with_local=True,
             explore_other_level=True):
    "list every existing contexts"
    return _listGeneric(parameter,
                        ENVIRONMENT_ATTRIBUTE_NAME,
                        key,
                        _envRowFormating,
                        _envGetTitle,
                        start_with_local,
                        explore_other_level)


@shellMethod(key=stringArgChecker(),
             property_name=tokenValueArgChecker(ENVIRONMENT_SET_PROPERTIES),
             property_value=defaultArgs.getbooleanValueArgCheckerInstance(),
             parameter=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def setEnvironmentProperties(key,
                             property_name,
                             property_value,
                             parameter,
                             start_with_local=True,
                             explore_other_level=True):
    "set environment property"
    setProperties(key,
                  property_name,
                  property_value,
                  parameter,
                  ENVIRONMENT_ATTRIBUTE_NAME,
                  start_with_local,
                  explore_other_level)


@shellMethod(key=stringArgChecker(),
             property_name=tokenValueArgChecker(ENVIRONMENT_GET_PROPERTIES),
             parameter=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def getEnvironmentProperties(key,
                             property_name,
                             parameter,
                             start_with_local=True,
                             explore_other_level=True):
    "get environment property"
    return getProperties(key,
                         property_name,
                         parameter,
                         ENVIRONMENT_ATTRIBUTE_NAME,
                         start_with_local,
                         explore_other_level)


@shellMethod(key=stringArgChecker(),
             parameter=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def listEnvironmentProperties(key,
                              parameter,
                              start_with_local=True,
                              explore_other_level=True):
    "list every properties from a specific environment object"
    return listProperties(key,
                          parameter,
                          ENVIRONMENT_ATTRIBUTE_NAME,
                          start_with_local,
                          explore_other_level)

# ################################### context management ######################


@shellMethod(key=defaultArgs.getStringArgCheckerInstance(),
             values=listArgChecker(defaultArgs.getArgCheckerInstance()),
             parameters=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def subtractContextValuesFun(key,
                             values,
                             parameters,
                             start_with_local=True,
                             explore_other_level=True):
    "remove some elements from a context parameter"
    param = getParameter(key,
                         parameters,
                         CONTEXT_ATTRIBUTE_NAME,
                         start_with_local,
                         explore_other_level)
    param.removeValues(values)


@shellMethod(value_type=tokenValueArgChecker(AVAILABLE_TYPE),
             key=defaultArgs.getStringArgCheckerInstance(),
             values=listArgChecker(defaultArgs.getArgCheckerInstance()),
             no_creation_if_exist=booleanValueArgChecker(),
             parameter=defaultArgs.getCompleteEnvironmentChecker(),
             local_var=booleanValueArgChecker())
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


@shellMethod(key=defaultArgs.getStringArgCheckerInstance(),
             parameter=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def removeContextValues(key,
                        parameter,
                        start_with_local=True,
                        explore_other_level=True):
    "remove a context parameter"
    removeParameter(key,
                    parameter,
                    CONTEXT_ATTRIBUTE_NAME,
                    start_with_local,
                    explore_other_level)


@shellMethod(key=defaultArgs.getStringArgCheckerInstance(),
             parameter=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def getContextValues(key,
                     parameter,
                     start_with_local=True,
                     explore_other_level=True):
    "get a context parameter value"
    return getParameter(key,
                        parameter,
                        CONTEXT_ATTRIBUTE_NAME,
                        start_with_local, explore_other_level).getValue()


@shellMethod(key=defaultArgs.getStringArgCheckerInstance(),
             values=listArgChecker(defaultArgs.getArgCheckerInstance(), 1),
             parameter=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def setContextValuesFun(key,
                        values,
                        parameter,
                        start_with_local=True,
                        explore_other_level=True):
    "set a context parameter value"
    getParameter(key,
                 parameter,
                 CONTEXT_ATTRIBUTE_NAME,
                 start_with_local,
                 explore_other_level).setValue(values)


@shellMethod(key=defaultArgs.getStringArgCheckerInstance(),
             values=listArgChecker(defaultArgs.getArgCheckerInstance()),
             parameters=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def addContextValuesFun(key,
                        values,
                        parameters,
                        start_with_local=True,
                        explore_other_level=True):
    "add values to a context parameter list"
    param = getParameter(key,
                         parameters,
                         CONTEXT_ATTRIBUTE_NAME,
                         start_with_local,
                         explore_other_level)
    param.addValues(values)


@shellMethod(key=defaultArgs.getStringArgCheckerInstance(),
             value=defaultArgs.getArgCheckerInstance(),
             parameter=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def selectValue(key,
                value,
                parameter,
                start_with_local=True,
                explore_other_level=True):
    "select the value for the current context"
    getParameter(key,
                 parameter,
                 CONTEXT_ATTRIBUTE_NAME,
                 start_with_local,
                 explore_other_level).settings.setIndexValue(value)


@shellMethod(key=defaultArgs.getStringArgCheckerInstance(),
             index=defaultArgs.getIntegerArgCheckerInstance(),
             parameter=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def selectValueIndex(key,
                     index,
                     parameter,
                     start_with_local=True,
                     explore_other_level=True):
    "select the value index for the current context"
    getParameter(key,
                 parameter,
                 CONTEXT_ATTRIBUTE_NAME,
                 start_with_local,
                 explore_other_level).settings.setIndex(index)


@shellMethod(key=defaultArgs.getStringArgCheckerInstance(),
             parameter=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def getSelectedContextValue(key,
                            parameter,
                            start_with_local=True,
                            explore_other_level=True):
    "get the selected value for the current context"
    return getParameter(key,
                        parameter,
                        CONTEXT_ATTRIBUTE_NAME,
                        start_with_local,
                        explore_other_level).getSelectedValue()


@shellMethod(key=defaultArgs.getStringArgCheckerInstance(),
             parameter=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def getSelectedContextIndex(key,
                            parameter,
                            start_with_local=True,
                            explore_other_level=True):
    "get the selected value index for the current context"
    return getParameter(key,
                        parameter,
                        CONTEXT_ATTRIBUTE_NAME,
                        start_with_local,
                        explore_other_level).settings.getIndex()


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


@shellMethod(parameter=defaultArgs.getCompleteEnvironmentChecker(),
             key=stringArgChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def listContexts(parameter,
                 key=None,
                 start_with_local=True,
                 explore_other_level=True):
    "list every existing contexts"
    return _listGeneric(parameter,
                        CONTEXT_ATTRIBUTE_NAME, key,
                        _conRowFormating,
                        _conGetTitle,
                        start_with_local,
                        explore_other_level)


@shellMethod(key=stringArgChecker(),
             property_name=tokenValueArgChecker(CONTEXT_SET_PROPERTIES),
             property_value=defaultArgs.getArgCheckerInstance(),
             parameter=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def setContextProperties(key,
                         property_name,
                         property_value,
                         parameter,
                         start_with_local=True,
                         explore_other_level=True):
    "set a context property"
    setProperties(key,
                  property_name,
                  property_value,
                  parameter,
                  CONTEXT_ATTRIBUTE_NAME,
                  start_with_local,
                  explore_other_level)


@shellMethod(key=stringArgChecker(),
             property_name=tokenValueArgChecker(CONTEXT_GET_PROPERTIES),
             parameter=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def getContextProperties(key,
                         property_name,
                         parameter,
                         start_with_local=True,
                         explore_other_level=True):
    "get a context property"
    return getProperties(key,
                         property_name,
                         parameter,
                         CONTEXT_ATTRIBUTE_NAME,
                         start_with_local,
                         explore_other_level)


@shellMethod(key=stringArgChecker(),
             parameter=defaultArgs.getCompleteEnvironmentChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def listContextProperties(key,
                          parameter,
                          start_with_local=True,
                          explore_other_level=True):
    "list every properties of a specific context object"
    return listProperties(key,
                          parameter,
                          CONTEXT_ATTRIBUTE_NAME,
                          start_with_local,
                          explore_other_level)

# ################################### var management ##########################

# beginning OF POC


@shellMethod(key=defaultArgs.getStringArgCheckerInstance(),
             values=listArgChecker(defaultArgs.getArgCheckerInstance()),
             engine=defaultArgs.getEngineChecker(),
             start_with_local=booleanValueArgChecker(),
             explore_other_level=booleanValueArgChecker())
def preAddValues(key, values, engine=None,
                 start_with_local=True, explore_other_level=True):

    cmd = engine.getCurrentCommand()
    cmd.dynamicParameter["key"] = key
    cmd.dynamicParameter["disabled"] = False
    cmd.dynamicParameter["start_with_local"] = start_with_local
    cmd.dynamicParameter["explore_other_level"] = explore_other_level

    return values


@shellMethod(values=listArgChecker(defaultArgs.getArgCheckerInstance()),
             engine=defaultArgs.getEngineChecker())
def proAddValues(values, engine):

    # if no previous command, default behaviour
    if not engine.hasPreviousCommand():
        return values

    # if not, clone this command and add it at the end of cmd list
    cmd = engine.getCurrentCommand()
    cmd_clone = cmd.clone()
    engine.addCommand(cmd_clone, convertProcessToPreProcess=True)

    for k, v in cmd.dynamicParameter.items():
        cmd_clone.dynamicParameter[k] = v

    cmd.dynamicParameter["disabled"] = True
    cmd_clone.dynamicParameter["disabled"] = True

    # TODO execute previous

    return values


@shellMethod(
    values=listArgChecker(defaultArgs.getArgCheckerInstance()),
    parameters=defaultArgs.getCompleteEnvironmentChecker(),
    engine=defaultArgs.getEngineChecker())
def postAddValues(values, parameters=None, engine=None):
    "add values to a var"

    cmd = engine.getCurrentCommand()

    if cmd.dynamicParameter["disabled"]:
        return values

    key = cmd.dynamicParameter["key"]

    if parameters.variable.hasParameter(
          key,
          cmd.dynamicParameter["start_with_local"],
          cmd.dynamicParameter["explore_other_level"]):
        param = getParameter(key,
                             parameters,
                             VARIABLE_ATTRIBUTE_NAME,
                             cmd.dynamicParameter["start_with_local"],
                             cmd.dynamicParameter["explore_other_level"])
        param.addValues(values)
    else:
        parameters.variable.setParameter(key, VarParameter(
            values), cmd.dynamicParameter["start_with_local"])

    return values

# END OF POC


@shellMethod(
    key=defaultArgs.getStringArgCheckerInstance(),
    values=listArgChecker(
         defaultArgs.getArgCheckerInstance()),
    parameters=defaultArgs.getCompleteEnvironmentChecker(),
    start_with_local=booleanValueArgChecker(),
    explore_other_level=booleanValueArgChecker())
def subtractValuesVar(key, values, parameters=None,
                      start_with_local=True, explore_other_level=True):
    "remove existing value from a variable, remove first occurence met"
    param = getParameter(
        key,
        parameters,
        VARIABLE_ATTRIBUTE_NAME,
        start_with_local,
        explore_other_level)
    param.removeValues(values)


@shellMethod(
    key=defaultArgs.getStringArgCheckerInstance(),
    values=listArgChecker(
         defaultArgs.getArgCheckerInstance()),
    parameter=defaultArgs.getCompleteEnvironmentChecker(),
    local_var=booleanValueArgChecker())
def setVar(key, values, parameter, local_var=True):
    "assign a value to a variable"
    parameter.variable.setParameter(key, VarParameter(values), local_var)


@shellMethod(
    key=defaultArgs.getStringArgCheckerInstance(),
    parameter=defaultArgs.getCompleteEnvironmentChecker(),
    start_with_local=booleanValueArgChecker(),
    explore_other_level=booleanValueArgChecker())
def getVar(key, parameter, start_with_local=True, explore_other_level=True):
    "get the value of a variable"
    return getParameter(key, parameter, VARIABLE_ATTRIBUTE_NAME,
                        start_with_local, explore_other_level).getValue()


@shellMethod(
    key=defaultArgs.getStringArgCheckerInstance(),
    parameter=defaultArgs.getCompleteEnvironmentChecker(),
    start_with_local=booleanValueArgChecker(),
    explore_other_level=booleanValueArgChecker())
def unsetVar(key, parameter, start_with_local=True, explore_other_level=True):
    "unset a variable, no error if does not exist"
    removeParameter(
        key,
        parameter,
        VARIABLE_ATTRIBUTE_NAME,
        start_with_local,
        explore_other_level)


def _varRowFormating(key, var_item, value_formating_fun):
    return (key, value_formating_fun(', '.join(str(x)
                                               for x in var_item.getValue())),)


def _varGetTitle(title_formating_fun):
    return (title_formating_fun("Name"), title_formating_fun("Values"), )


@shellMethod(
    parameter=defaultArgs.getCompleteEnvironmentChecker(),
    key=stringArgChecker(),
    start_with_local=booleanValueArgChecker(),
    explore_other_level=booleanValueArgChecker())
def listVars(parameter,
             key=None,
             start_with_local=True,
             explore_other_level=True):
    "list every existing variables"
    return _listGeneric(parameter,
                        VARIABLE_ATTRIBUTE_NAME,
                        key,
                        _varRowFormating,
                        _varGetTitle,
                        start_with_local,
                        explore_other_level)

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
registerCommand(("save",), pro=saveParameter)
registerCommand(("load",), pro=loadParameter)
registerCommand(("list",), pro=listParameter, post=printColumnWithouHeader)
registerStopHelpTraversalAt()
