#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2016  Jonathan Delvaux <pyshell@djoproject.net>

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

from tries import multiLevelTries

from pyshell.arg.argchecker import CompleteEnvironmentChecker
from pyshell.arg.argchecker import DefaultInstanceArgChecker
from pyshell.arg.argchecker import EnvironmentParameterChecker
from pyshell.arg.argchecker import FilePathArgChecker
from pyshell.arg.argchecker import IntegerArgChecker
from pyshell.arg.argchecker import ListArgChecker
from pyshell.arg.argchecker import StringArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.loader.command import registerCommand
from pyshell.loader.context import registerSetContext
from pyshell.loader.environment import registerSetEnvironment
from pyshell.system.context import ContextParameter
from pyshell.system.context import GlobalContextSettings
from pyshell.system.environment import EnvironmentParameter
from pyshell.system.settings import GlobalSettings
from pyshell.utils.constants import ADDONLIST_KEY
from pyshell.utils.constants import CONTEXT_COLORATION_DARK
from pyshell.utils.constants import CONTEXT_COLORATION_KEY
from pyshell.utils.constants import CONTEXT_COLORATION_LIGHT
from pyshell.utils.constants import CONTEXT_COLORATION_NONE
from pyshell.utils.constants import CONTEXT_EXECUTION_DAEMON
from pyshell.utils.constants import CONTEXT_EXECUTION_KEY
from pyshell.utils.constants import CONTEXT_EXECUTION_SCRIPT
from pyshell.utils.constants import CONTEXT_EXECUTION_SHELL
from pyshell.utils.constants import DEBUG_ENVIRONMENT_NAME
from pyshell.utils.constants import DEFAULT_PARAMETER_FILE
from pyshell.utils.constants import ENVIRONMENT_ADDON_TO_LOAD_DEFAULT
from pyshell.utils.constants import ENVIRONMENT_ADDON_TO_LOAD_KEY
from pyshell.utils.constants import ENVIRONMENT_HISTORY_FILE_NAME_KEY
from pyshell.utils.constants import ENVIRONMENT_HISTORY_FILE_NAME_VALUE
from pyshell.utils.constants import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.constants import ENVIRONMENT_PARAMETER_FILE_KEY
from pyshell.utils.constants import ENVIRONMENT_PROMPT_DEFAULT
from pyshell.utils.constants import ENVIRONMENT_PROMPT_KEY
from pyshell.utils.constants import ENVIRONMENT_SAVE_KEYS_DEFAULT
from pyshell.utils.constants import ENVIRONMENT_SAVE_KEYS_KEY
from pyshell.utils.constants import ENVIRONMENT_TAB_SIZE_KEY
from pyshell.utils.constants import ENVIRONMENT_USE_HISTORY_KEY
from pyshell.utils.constants import ENVIRONMENT_USE_HISTORY_VALUE
from pyshell.utils.constants import TAB_SIZE
from pyshell.utils.exception import ListOfException
from pyshell.utils.printing import notice


default_global_setting = GlobalSettings(transient=False,
                                        read_only=False,
                                        removable=False)

default_string_arg_checker = DefaultInstanceArgChecker.\
    getStringArgCheckerInstance()
default_arg_checker = DefaultInstanceArgChecker.\
    getArgCheckerInstance()
default_boolean_arg_checker = DefaultInstanceArgChecker.\
    getBooleanValueArgCheckerInstance()
default_integer_arg_checker = DefaultInstanceArgChecker.\
    getIntegerArgCheckerInstance()

# # init original params # #
param = EnvironmentParameter(value=DEFAULT_PARAMETER_FILE,
                             typ=FilePathArgChecker(exist=None,
                                                    readable=True,
                                                    writtable=None,
                                                    is_file=True),
                             settings=GlobalSettings(transient=True,
                                                     read_only=False,
                                                     removable=False))
registerSetEnvironment(ENVIRONMENT_PARAMETER_FILE_KEY, param)

param = EnvironmentParameter(value=ENVIRONMENT_PROMPT_DEFAULT,
                             typ=default_string_arg_checker,
                             settings=default_global_setting.clone())
registerSetEnvironment(ENVIRONMENT_PROMPT_KEY, param)

param = EnvironmentParameter(value=TAB_SIZE,
                             typ=IntegerArgChecker(0),
                             settings=default_global_setting.clone())
registerSetEnvironment(ENVIRONMENT_TAB_SIZE_KEY, param)

param = EnvironmentParameter(value=multiLevelTries(),
                             typ=default_arg_checker,
                             settings=GlobalSettings(transient=True,
                                                     read_only=True,
                                                     removable=False))
registerSetEnvironment(ENVIRONMENT_LEVEL_TRIES_KEY, param)

param = EnvironmentParameter(value=ENVIRONMENT_SAVE_KEYS_DEFAULT,
                             typ=default_boolean_arg_checker,
                             settings=default_global_setting.clone())
registerSetEnvironment(ENVIRONMENT_SAVE_KEYS_KEY, param)

param = EnvironmentParameter(value=ENVIRONMENT_HISTORY_FILE_NAME_VALUE,
                             typ=FilePathArgChecker(exist=None,
                                                    readable=True,
                                                    writtable=None,
                                                    is_file=True),
                             settings=default_global_setting.clone())
registerSetEnvironment(ENVIRONMENT_HISTORY_FILE_NAME_KEY, param)

param = EnvironmentParameter(value=ENVIRONMENT_USE_HISTORY_VALUE,
                             typ=default_boolean_arg_checker,
                             settings=default_global_setting.clone())
registerSetEnvironment(ENVIRONMENT_USE_HISTORY_KEY, param)

typ = ListArgChecker(default_string_arg_checker)
param = EnvironmentParameter(value=ENVIRONMENT_ADDON_TO_LOAD_DEFAULT,
                             typ=typ,
                             settings=default_global_setting.clone())
registerSetEnvironment(ENVIRONMENT_ADDON_TO_LOAD_KEY, param)

param = EnvironmentParameter(value={},
                             typ=default_arg_checker,
                             settings=GlobalSettings(transient=True,
                                                     read_only=True,
                                                     removable=False))
registerSetEnvironment(ADDONLIST_KEY, param)

default_context_setting = GlobalContextSettings(removable=False,
                                                read_only=True,
                                                transient=False,
                                                transient_index=False)

param = ContextParameter(value=tuple(range(0, 5)),
                         typ=default_integer_arg_checker,
                         default_index=0,
                         index=1,
                         settings=default_context_setting.clone())
registerSetContext(DEBUG_ENVIRONMENT_NAME, param)

settings = GlobalContextSettings(removable=False,
                                 read_only=True,
                                 transient=True,
                                 transient_index=True)
values = (CONTEXT_EXECUTION_SHELL,
          CONTEXT_EXECUTION_SCRIPT,
          CONTEXT_EXECUTION_DAEMON,)
param = ContextParameter(value=values,
                         typ=default_string_arg_checker,
                         default_index=0,
                         settings=settings)
registerSetContext(CONTEXT_EXECUTION_KEY, param)

values = (CONTEXT_COLORATION_LIGHT,
          CONTEXT_COLORATION_DARK,
          CONTEXT_COLORATION_NONE,)
param = ContextParameter(value=values,
                         typ=default_string_arg_checker,
                         default_index=0,
                         settings=default_context_setting.clone())
registerSetContext(CONTEXT_COLORATION_KEY, param)


@shellMethod(name=DefaultInstanceArgChecker.getStringArgCheckerInstance(),
             sub_addon=StringArgChecker(),
             parameters=CompleteEnvironmentChecker(),
             addon_dico=EnvironmentParameterChecker(ADDONLIST_KEY))
def loadAddonFun(name, parameters, sub_addon=None, addon_dico=None):
    "load an addon"

    try:
        mod = __import__(name, fromlist=["_loaders"])
    except ImportError as ie:
        raise Exception("fail to load addon '"+str(name)+"', reason: "+str(ie))

    if not hasattr(mod, "_loaders"):
        raise Exception("invalid addon '"+str(name)+"', no loader found. "
                        "don't forget to register something in the addon")
    loader = mod._loaders

    # load and register
    addon_dico.getValue()[name] = loader
    loader.load(parameters, sub_addon)

    notice(name + " loaded !")


@shellMethod(
    addon_list_on_start_up=EnvironmentParameterChecker(
        ENVIRONMENT_ADDON_TO_LOAD_KEY),
    params=DefaultInstanceArgChecker.getCompleteEnvironmentChecker(),
    addon_dico=EnvironmentParameterChecker(ADDONLIST_KEY))
def loadAddonOnStartUp(addon_list_on_start_up, params, addon_dico=None):

    addon_list = addon_list_on_start_up.getValue()

    error_list = ListOfException()
    for addon_name in addon_list:
        try:
            loadAddonFun(addon_name, params, addon_dico=addon_dico)
        except Exception as ex:
            # TODO the information about the failing addon is lost here...
            # E.G. if an addon is already loaded, only the profile name will be
            # printed, not the addon name...
            error_list.addException(ex)

    if error_list.isThrowable():
        raise error_list


registerCommand(("addon", "load",), pro=loadAddonFun)
registerCommand(("addon", "onstartup", "load",), pro=loadAddonOnStartUp)
