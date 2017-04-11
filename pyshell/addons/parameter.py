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

from types import FunctionType

from pyshell.arg.accessor.default import DefaultAccessor
from pyshell.arg.checker.boolean import BooleanValueArgChecker
from pyshell.arg.checker.default import DefaultChecker
from pyshell.arg.checker.fixedvalue import FixedValueChecker
from pyshell.arg.checker.list import ListArgChecker
from pyshell.arg.checker.string43 import StringArgChecker
from pyshell.arg.checker.token43 import TokenValueArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.register.command import registerCommand
from pyshell.register.command import registerSetTempPrefix
from pyshell.register.command import registerStopHelpTraversalAt
from pyshell.system.setting.procedure import DEFAULT_CHECKER as PROC_CHECKER
from pyshell.utils.constants import CONTEXT_ATTRIBUTE_NAME
from pyshell.utils.constants import ENABLE_ON_POST_PROCESS
from pyshell.utils.constants import ENABLE_ON_PRE_PROCESS
from pyshell.utils.constants import ENABLE_ON_PROCESS
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME
from pyshell.utils.constants import KEY_ATTRIBUTE_NAME
from pyshell.utils.constants import PROCEDURE_ATTRIBUTE_NAME
from pyshell.utils.constants import SETTING_PROPERTY_CHECKER
from pyshell.utils.constants import SETTING_PROPERTY_CHECKERLIST
from pyshell.utils.constants import SETTING_PROPERTY_DEFAULTINDEX
from pyshell.utils.constants import SETTING_PROPERTY_ENABLEON
from pyshell.utils.constants import SETTING_PROPERTY_GRANULARITY
from pyshell.utils.constants import SETTING_PROPERTY_INDEX
from pyshell.utils.constants import SETTING_PROPERTY_READONLY
from pyshell.utils.constants import SETTING_PROPERTY_REMOVABLE
from pyshell.utils.constants import SETTING_PROPERTY_TRANSIENT
from pyshell.utils.constants import SETTING_PROPERTY_TRANSIENTINDEX
from pyshell.utils.constants import VARIABLE_ATTRIBUTE_NAME
from pyshell.utils.postprocess import listFlatResultHandler
from pyshell.utils.postprocess import listResultHandler
from pyshell.utils.postprocess import printColumn
from pyshell.utils.printing import formatBolt
from pyshell.utils.printing import formatGreen
from pyshell.utils.printing import formatOrange
from pyshell.utils.printing import formatRed

# # CONSTANT SECTION # #
AVAILABLE_TYPE = {
    DefaultChecker.getArg().getTypeName(): DefaultChecker.getArg(),
    DefaultChecker.getBoolean().getTypeName(): DefaultChecker.getBoolean(),
    DefaultChecker.getFile().getTypeName(): DefaultChecker.getFile(),
    DefaultChecker.getFloat().getTypeName(): DefaultChecker.getFloat(),
    DefaultChecker.getInteger().getTypeName(): DefaultChecker.getInteger(),
    DefaultChecker.getString().getTypeName(): DefaultChecker.getString()}

DEFAULT_BOOL = DefaultChecker.getBoolean()
DEFAULT_INT = DefaultChecker.getInteger()
DEFAULT_STR = DefaultChecker.getString()

PARAMETER_PROPERTIES = {
    SETTING_PROPERTY_READONLY: ("setReadOnly", "isReadOnly", DEFAULT_BOOL,),
    SETTING_PROPERTY_REMOVABLE: ("setRemovable", "isRemovable", DEFAULT_BOOL,),
    SETTING_PROPERTY_TRANSIENT: ("setTransient", "isTransient", DEFAULT_BOOL,),
}

ENVIRONMENT_PROPERTIES = {
    SETTING_PROPERTY_CHECKER:
        ("setChecker", "getChecker", TokenValueArgChecker(AVAILABLE_TYPE),),
    SETTING_PROPERTY_CHECKERLIST:
        ("setListChecker", "isListChecker", DEFAULT_BOOL,)}

ENVIRONMENT_PROPERTIES.update(PARAMETER_PROPERTIES)

CONTEXT_PROPERTIES = {
    SETTING_PROPERTY_TRANSIENTINDEX:
        ("setTransientIndex", "isTransientIndex", DEFAULT_BOOL,),
    SETTING_PROPERTY_DEFAULTINDEX:
        ("setDefaultIndex", "getDefaultIndex", DEFAULT_INT,),
    SETTING_PROPERTY_INDEX: ("setIndex", "getIndex", DEFAULT_INT,)}

CONTEXT_PROPERTIES.update(ENVIRONMENT_PROPERTIES)

_ENABLED_ON = {ENABLE_ON_PRE_PROCESS: ENABLE_ON_PRE_PROCESS,
               ENABLE_ON_PROCESS: ENABLE_ON_PROCESS,
               ENABLE_ON_POST_PROCESS: ENABLE_ON_POST_PROCESS}

PROCEDURE_PROPERTIES = {
    SETTING_PROPERTY_ENABLEON:
        ("setEnableOn", "getEnableOn", TokenValueArgChecker(_ENABLED_ON),),
    SETTING_PROPERTY_GRANULARITY:
        ("setErrorGranularity", "getErrorGranularity", DEFAULT_INT,)}

PROCEDURE_PROPERTIES.update(PARAMETER_PROPERTIES)


def _clone(origin_fun, new_fun_name, name, extra=None):
    # update the checkers/accessors dico
    original_checkers = origin_fun.checker.arg_type_list
    new_dict = dict(original_checkers)

    if extra is not None:
        new_dict.update(extra)

    # clone the function
    new_fun = FunctionType(code=origin_fun.__code__,
                           globals=origin_fun.__globals__,
                           name=new_fun_name,
                           argdefs=origin_fun.__defaults__,
                           closure=origin_fun.__closure__)

    # apply decorator
    fun_decorator = shellMethod(**new_dict)
    fun_decorator(new_fun)

    # updat the docstring
    new_fun.__doc__ = new_fun.__doc__.replace("environment", name)

    return new_fun

# ################################### GENERIC METHOD ##########################


@shellMethod(key=DEFAULT_STR,
             manager=DefaultAccessor.getEnvironmentManager(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker(),
             perfect_match=BooleanValueArgChecker())
def getParameter(key,
                 manager,
                 start_with_local=True,
                 explore_other_scope=True,
                 perfect_match=False):
    """get an environment parameter value"""
    param = manager.getParameter(key,
                                 perfect_match=perfect_match,
                                 local_param=start_with_local,
                                 explore_other_scope=explore_other_scope)

    if param is None:
        excmsg = "Unknow parameter of type '%s' with key '%s'"
        excmsg %= (manager.getLoaderName(), str(key),)
        raise Exception(excmsg)

    return param


@shellMethod(key=DEFAULT_STR,
             property_info=TokenValueArgChecker(ENVIRONMENT_PROPERTIES),
             property_value=DefaultChecker.getArg(),
             manager=DefaultAccessor.getEnvironmentManager(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker(),
             perfect_match=BooleanValueArgChecker())
def setProperties(key,
                  property_info,
                  property_value,
                  manager,
                  start_with_local=True,
                  explore_other_scope=True,
                  perfect_match=False):
    """set environment property"""

    property_setter, property_getter, propertyChecker = property_info
    param = getParameter(key,
                         manager,
                         start_with_local,
                         explore_other_scope,
                         perfect_match)

    try:
        meth = getattr(param.settings, property_setter)
    except AttributeError:
        excmsg = "The parameter object '%s' does not have the method '%s'"
        excmsg %= (key, property_getter,)
        raise Exception(excmsg)

    meth(propertyChecker.getValue(property_value, "property_value", 2))


@shellMethod(key=DEFAULT_STR,
             property_info=TokenValueArgChecker(ENVIRONMENT_PROPERTIES),
             manager=DefaultAccessor.getEnvironmentManager(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker(),
             perfect_match=BooleanValueArgChecker())
def getProperties(key,
                  property_info,
                  manager,
                  start_with_local=True,
                  explore_other_scope=True,
                  perfect_match=False):
    """get environment property"""

    param = getParameter(key,
                         manager,
                         start_with_local,
                         explore_other_scope,
                         perfect_match)

    property_setter, property_getter, propertyChecker = property_info

    try:
        meth = getattr(param.settings, property_getter)
    except AttributeError:
        excmsg = "The parameter object '%s' does not have the method '%s'"
        excmsg %= (key, property_getter,)
        raise Exception(excmsg)

    return meth()


# TODO FIXME when there is an ambiguity on the second level tries
#   e.g. with pcsc.autoload and pcsc.autoconnect.
#   list pc.a will raise ambiguityException, the expected result is the two
#   keys
# TODO FIXME same issue with properties stat
@shellMethod(key=DEFAULT_STR,
             manager=DefaultAccessor.getEnvironmentManager(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker(),
             perfect_match=BooleanValueArgChecker())
def listProperties(key,
                   manager,
                   start_with_local=True,
                   explore_other_scope=True,
                   perfect_match=False):
    """list every properties from a specific environment object"""
    param = getParameter(key,
                         manager,
                         start_with_local,
                         explore_other_scope,
                         perfect_match)
    prop = list(param.settings.getProperties().items())
    prop.insert(0, (formatBolt("Key"), formatBolt("Value")))
    return prop


@shellMethod(key=DEFAULT_STR,
             manager=DefaultAccessor.getEnvironmentManager(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def removeParameter(key,
                    manager,
                    start_with_local=True,
                    explore_other_scope=True):
    """remove an environment parameter"""
    if not manager.hasParameter(key,
                                perfect_match=True,
                                local_param=start_with_local,
                                explore_other_scope=explore_other_scope):
        return  # no job to do

    manager.unsetParameter(string_path=key,
                           local_param=start_with_local,
                           explore_other_scope=explore_other_scope)


@shellMethod(manager=DefaultAccessor.getEnvironmentManager(),
             key=StringArgChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def listParameter(manager,
                  key=None,
                  start_with_local=True,
                  explore_other_scope=True):
    """list every existing environments"""
    if key is None:
        key = ""

    # retrieve all value from corresponding mltries
    dico = manager.buildDictionnary(key,
                                    start_with_local,
                                    explore_other_scope)

    if len(dico) == 0:
        return [(formatOrange("No item available"),)]

    columns = [(formatBolt("Name"), formatBolt("Value"),)]

    for subk in sorted(dico.keys()):
        subv = dico[subk]
        if subv.settings.isListChecker():
            value = ', '.join(str(x) for x in subv.getValue())
        else:
            value = str(subv.getValue())

        columns.append((subk, formatOrange(value),))

    return columns


def _mergeDico(final_dico, dico_to_merge, scope):
    for key, value in dico_to_merge.items():
        if key in final_dico:
            continue
        final_dico[key] = (value, scope,)


@shellMethod(manager=DefaultAccessor.getEnvironmentManager(),
             key=StringArgChecker(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def statParameter(manager,
                  key=None,
                  start_with_local=True,
                  explore_other_scope=True):
    """This command list every settings of every environment parameters"""
    if key is None:
        key = ""

    final_dico = {}
    for case in range(0, 2):
        if start_with_local:
            dico = manager.buildDictionnary(key,
                                            local_param=True,
                                            explore_other_scope=False)

            _mergeDico(final_dico, dico, formatGreen("local"))

            if not explore_other_scope:
                break
        else:
            dico = manager.buildDictionnary(key,
                                            local_param=False,
                                            explore_other_scope=False)

            _mergeDico(final_dico, dico, formatRed("global"))

            if not explore_other_scope:
                break

        start_with_local = not start_with_local

    if len(final_dico) == 0:
        return [(formatOrange("No item available"),)]

    # retrieve every existing keys
    title = set()
    for subk, (subv, scope,) in final_dico.items():
        title.update(subv.settings.getProperties().keys())

    # build the table
    to_ret = []
    title = sorted(title)
    for subk in sorted(final_dico.keys()):
        (subv, scope,) = final_dico[subk]
        properties = subv.settings.getProperties()
        line = [subk, scope]

        # properties
        for k in title:
            if k in properties:
                value = properties[k]
                if type(value) is bool:
                    if value:
                        value = formatGreen(str(value))
                    else:
                        value = formatRed(str(value))
                else:
                    value = formatOrange(str(value))
            else:
                value = "-"
            line.append(value)
        to_ret.append(line)

    # prepare the titles
    title.insert(0, "Scope")
    title.insert(0, "Name")
    for i in range(0, len(title)):
        title[i] = formatBolt(title[i])

    to_ret.insert(0, title)

    return to_ret


@shellMethod(key=DEFAULT_STR,
             values=ListArgChecker(DefaultChecker.getArg(), 1),
             manager=DefaultAccessor.getEnvironmentManager(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def subtractValues(key,
                   values,
                   manager,
                   start_with_local=True,
                   explore_other_scope=True):
    """remove some elements from an environment parameter"""
    param = getParameter(key, manager, start_with_local, explore_other_scope)
    param.removeValues(values)


@shellMethod(key=DEFAULT_STR,
             values=ListArgChecker(DefaultChecker.getArg(), 1),
             manager=DefaultAccessor.getEnvironmentManager(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def addValues(key,
              values,
              manager,
              start_with_local=True,
              explore_other_scope=True):
    """add values to an environment parameter list"""
    param = getParameter(key, manager, start_with_local, explore_other_scope)
    param.addValues(values)


@shellMethod(key=DEFAULT_STR,
             values=ListArgChecker(DefaultChecker.getArg()),
             value_type=TokenValueArgChecker(AVAILABLE_TYPE),
             manager=DefaultAccessor.getEnvironmentManager(),
             list_enabled=BooleanValueArgChecker(),
             local_param=BooleanValueArgChecker())
def createValues(key,
                 values,
                 value_type=DefaultChecker.getArg().getTypeName(),
                 manager=None,
                 list_enabled=True,
                 local_param=True,
                 min_size=0):
    """create an environment parameter value"""

    if not list_enabled:
        if len(values) == 0:
            excmsg = "No value provided for the parameter '%s'"
            excmsg %= key
            raise Exception(excmsg)

        values = values[0]

    if value_type is not None:
        if list_enabled:
            value_type = ListArgChecker(value_type, min_size)

        origin_checker = "%s %s" % (manager.getLoaderName().title(), key,)
        values = value_type.getValue(values, None, origin_checker)

    param = manager.setParameter(string_path=key,
                                 param=values,
                                 local_param=local_param)
    if value_type is not None:
        # XXX if a different checker from the default one is used, the value
        #   need to be rechecked, because it is not checker in the setChecker
        #   method of settings, settings does not have access to the parameter
        #   value to check them
        param.settings.setChecker(value_type)

    if not list_enabled:
        param.settings.setListChecker(list_enabled)

    if value_type is not None or not list_enabled:
        param.setValue(values)


@shellMethod(key=DEFAULT_STR,
             value=DefaultChecker.getArg(),
             value_type=TokenValueArgChecker(AVAILABLE_TYPE),
             manager=DefaultAccessor.getEnvironmentManager(),
             local_param=BooleanValueArgChecker())
def createValue(key,
                value,
                value_type=DefaultChecker.getArg().getTypeName(),
                manager=None,
                local_param=True):
    """create an environment parameter value"""
    if value_type is not None:
        origin_checker = "%s %s" % (manager.getLoaderName().title(), key,)
        value = value_type.getValue(value, None, origin_checker)

    param = manager.setParameter(string_path=key,
                                 param=value,
                                 local_param=local_param)
    if value_type is not None:
        # XXX see explanations in createValues
        param.settings.setChecker(value_type)

    param.settings.setListChecker(False)
    param.setValue(value)


@shellMethod(key=DEFAULT_STR,
             values=ListArgChecker(DefaultChecker.getArg()),
             manager=DefaultAccessor.getEnvironmentManager(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def setValues(key,
              values,
              manager,
              start_with_local=True,
              explore_other_scope=True):
    """set environment parameter values"""

    param = getParameter(key, manager, start_with_local, explore_other_scope)

    if param.settings.isListChecker():
        param.setValue(values)
    else:
        if len(values) < 1:
            excmsg = "need a value for the parameter '%s'"
            excmsg %= key
            raise Exception(excmsg)

        param.setValue(values[0])


@shellMethod(key=DEFAULT_STR,
             value=DefaultChecker.getArg(),
             manager=DefaultAccessor.getEnvironmentManager(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def setValue(key,
             value,
             manager,
             start_with_local=True,
             explore_other_scope=True):
    """set an environment parameter value"""
    param = getParameter(key, manager, start_with_local, explore_other_scope)
    param.setValue(value)


# ################################### env management ##########################

registerSetTempPrefix((ENVIRONMENT_ATTRIBUTE_NAME, ))
registerCommand(("list",), pro=listParameter, post=printColumn)
registerCommand(("properties", "stat",), pro=statParameter, post=printColumn)
registerCommand(("create",), post=createValues)
registerCommand(("get",), pre=getParameter, pro=listResultHandler)
registerCommand(("unset",), pro=removeParameter)
registerCommand(("set",), post=setValues)
registerCommand(("add",), post=addValues)
registerCommand(("subtract",), post=subtractValues)
registerCommand(("properties", "set"), pro=setProperties)
registerCommand(("properties", "get"),
                pre=getProperties,
                pro=listFlatResultHandler)
registerCommand(("properties", "list"), pre=listProperties, pro=printColumn)
registerStopHelpTraversalAt(("properties",))
registerStopHelpTraversalAt()

# ################################### context management ######################

extra = {'manager': DefaultAccessor.getContextManager()}
registerSetTempPrefix((CONTEXT_ATTRIBUTE_NAME, ))

fun = _clone(removeParameter, "removeContextValues", "context", extra=extra)
registerCommand(("unset",), pro=fun)

fun = _clone(getParameter, "getContextValues", "context", extra=extra)
registerCommand(("get",), pre=fun, pro=listResultHandler)

extra["values"] = ListArgChecker(DefaultChecker.getArg(), 1)
fun = _clone(setValues, "setContextValues", "context", extra=extra)
registerCommand(("set",), post=fun)

extra["list_enabled"] = FixedValueChecker(True)
extra["min_size"] = FixedValueChecker(1)
fun = _clone(createValues, "createContextValues", "context", extra=extra)
registerCommand(("create",), post=fun)
del extra["min_size"]
del extra["values"]
del extra["list_enabled"]

fun = _clone(addValues, "addContextValues", "context", extra=extra)
registerCommand(("add",), post=fun)

fun_name = "subtractContextValuesFun"
fun = _clone(subtractValues, fun_name, "context", extra=extra)
registerCommand(("subtract",), post=fun)

fun = _clone(listParameter, "listContexts", "context", extra=extra)
registerCommand(("list",), pre=fun, pro=printColumn)

fun = _clone(statParameter, "statContexts", "context", extra=extra)
registerCommand(("properties", "stat",), pre=fun, pro=printColumn)

fun_name = "listContextProperties"
fun = _clone(listProperties, fun_name, "context", extra=extra)
registerCommand(("properties", "list"), pre=fun, pro=printColumn)

extra['property_info'] = TokenValueArgChecker(CONTEXT_PROPERTIES)
fun = _clone(setProperties, "setContextProperties", "context", extra=extra)
registerCommand(("properties", "set"), pro=fun)

fun = _clone(getProperties, "getContextProperties", "context", extra=extra)
registerCommand(("properties", "get"), pre=fun, pro=listFlatResultHandler)


@shellMethod(key=DEFAULT_STR,
             value=DefaultChecker.getArg(),
             manager=DefaultAccessor.getContextManager(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def selectValue(key,
                value,
                manager,
                start_with_local=True,
                explore_other_scope=True):
    "select the value for the current context"
    param = getParameter(key, manager, start_with_local, explore_other_scope)
    param.setSelectedValue(value)


@shellMethod(key=DEFAULT_STR,
             manager=DefaultAccessor.getContextManager(),
             start_with_local=BooleanValueArgChecker(),
             explore_other_scope=BooleanValueArgChecker())
def getSelectedValue(key,
                     manager,
                     start_with_local=True,
                     explore_other_scope=True):
    "get the selected value for the current context"
    param = getParameter(key, manager, start_with_local, explore_other_scope)
    return param.getSelectedValue()

registerCommand(("value", "get",),
                pre=getSelectedValue,
                pro=listFlatResultHandler)
registerCommand(("value", "select",), post=selectValue)

registerStopHelpTraversalAt(("value",))
registerStopHelpTraversalAt(("properties",))
registerStopHelpTraversalAt()

# ################################### var management ##########################

extra = {'manager': DefaultAccessor.getVariableManager()}
registerSetTempPrefix((VARIABLE_ATTRIBUTE_NAME, ))

fun = _clone(getParameter, "getVar", "variable", extra=extra)
registerCommand(("get",), pre=fun, pro=listResultHandler)

fun = _clone(removeParameter, "unsetVar", "variable", extra=extra)
registerCommand(("unset",), pro=fun)

fun = _clone(listParameter, "listVars", "variable", extra=extra)
registerCommand(("list",), pre=fun, pro=printColumn)

fun = _clone(addValues, "variableAddValues", "variable", extra=extra)
registerCommand(("add",), post=fun)

fun_name = "variableSubtractValues"
fun = _clone(subtractValues, fun_name, "variable", extra=extra)
registerCommand(("subtract",), post=fun)

extra["value_type"] = FixedValueChecker(None)
extra["list_enabled"] = FixedValueChecker(True)
fun = _clone(createValues, "setVar", "variable", extra=extra)
registerCommand(("set",), post=fun)
registerCommand(("create",), post=fun)  # compatibility issue

registerStopHelpTraversalAt()

# ################################### key management ##########################

extra = {'manager': DefaultAccessor.getKeyManager()}
registerSetTempPrefix((KEY_ATTRIBUTE_NAME, ))

extra["value"] = DefaultChecker.getKey()
fun = _clone(setValue, "setKey", "key", extra=extra)
registerCommand(("set",), post=fun)
del extra["value"]

fun = _clone(getParameter, "getKey", "key", extra=extra)
registerCommand(("get",), pre=fun, pro=listFlatResultHandler)

fun = _clone(removeParameter, "unsetKey", "key", extra=extra)
registerCommand(("unset",), pro=fun)

fun = _clone(listParameter, "listKey", "key", extra=extra)
registerCommand(("list",), pre=fun, pro=printColumn)

fun = _clone(statParameter, "statKey", "key", extra=extra)
registerCommand(("properties", "stat",), pre=fun, pro=printColumn)

extra['property_info'] = TokenValueArgChecker(PARAMETER_PROPERTIES)
fun = _clone(setProperties, "setKeyProperties", "key", extra=extra)
registerCommand(("properties", "set"), pro=fun)

fun = _clone(getProperties, "getKeyProperties", "key", extra=extra)
registerCommand(("properties", "get"), pre=fun, pro=listFlatResultHandler)
del extra['property_info']

fun = _clone(listProperties, "listKeyProperties", "key", extra=extra)
registerCommand(("properties", "list"), pre=fun, pro=printColumn)


@shellMethod(manager=DefaultAccessor.getKeyManager(),
             remove_locals=BooleanValueArgChecker(),
             remove_globals=BooleanValueArgChecker())
def cleanKeyStore(manager, remove_locals=True, remove_globals=False):
    if remove_locals:
        manager.flush()

    if remove_globals:
        dico = manager.buildDictionnary(string_path="",
                                        local_param=False,
                                        explore_other_scope=False)
        for key, value in dico.items():
            manager.unsetParameter(key,
                                   local_param=False,
                                   explore_other_scope=False)


registerCommand(("clean",), pro=cleanKeyStore)

extra["value_type"] = FixedValueChecker(None)
fun = _clone(createValue, "createKey", "key", extra=extra)
registerCommand(("create",), post=fun)

registerStopHelpTraversalAt(("properties",))
registerStopHelpTraversalAt()

# ################################### procedure management ####################

extra = {'manager': DefaultAccessor.getProcedureManager()}
registerSetTempPrefix((PROCEDURE_ATTRIBUTE_NAME, ))

extra["value"] = PROC_CHECKER
fun = _clone(setValue, "setProcedure", "procedure", extra=extra)
registerCommand(("set",), post=fun)
del extra["value"]

fun = _clone(getParameter, "getProcedure", "procedure", extra=extra)
registerCommand(("get",), pre=fun, pro=listFlatResultHandler)

fun = _clone(removeParameter, "unsetProcedure", "procedure", extra=extra)
registerCommand(("unset",), pro=fun)

fun = _clone(listParameter, "listProcedure", "procedure", extra=extra)
registerCommand(("list",), pre=fun, pro=printColumn)

fun = _clone(statParameter, "statProcedure", "procedure", extra=extra)
registerCommand(("properties", "stat",), pre=fun, pro=printColumn)

extra['property_info'] = TokenValueArgChecker(PROCEDURE_PROPERTIES)
fun = _clone(setProperties, "setProcedureProperties", "procedure", extra=extra)
registerCommand(("properties", "set"), pro=fun)

fun = _clone(getProperties, "getProcedureProperties", "procedure", extra=extra)
registerCommand(("properties", "get"), pre=fun, pro=listFlatResultHandler)
del extra['property_info']

fun = _clone(
    listProperties, "listProcedureProperties", "procedure", extra=extra)
registerCommand(("properties", "list"), pre=fun, pro=printColumn)

extra["value_type"] = FixedValueChecker(None)
fun = _clone(createValue, "createProcedure", "procedure", extra=extra)
registerCommand(("create",), post=fun)

registerStopHelpTraversalAt(("properties",))
registerStopHelpTraversalAt()
