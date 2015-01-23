#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2014  Jonathan Delvaux <pyshell@djoproject.net>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os

#TODO check if every constant are still used

### MISC ###
DEFAULT_CONFIG_DIRECTORY = os.path.join(os.path.expanduser("~"), ".pyshell")
MAIN_CATEGORY            = "main"
SHELL_CATEGORY           = "shell"
PARAMETER_NAME           = "parameter"
DEFAULT_SEPARATOR        = ","
DEFAULT_SUBADDON_NAME    = "default"

### EVENT ###
EVENT__ON_STARTUP     = "_onstartup" #at application launch
EVENT_ON_STARTUP      = "onstartup" #at application launch
EVENT_AT_EXIT         = "atexit" #at application exit
EVENT_AT_ADDON_LOAD   = "onaddonload" #at addon load (args=addon name)
EVENT_AT_ADDON_UNLOAD = "onaddonunload" #at addon unload (args=addon name)

#TODO use it in executer
EVENT_TO_CREATE_ON_STARTUP = (EVENT__ON_STARTUP, EVENT_ON_STARTUP, EVENT_AT_EXIT, EVENT_AT_ADDON_LOAD, EVENT_AT_ADDON_UNLOAD, )

### ENVIRONMENT ###
ENVIRONMENT_ATTRIBUTE_NAME          = "environment"

ENVIRONMENT_PARAMETER_FILE_KEY      = MAIN_CATEGORY+".parameterFile"
DEFAULT_PARAMETER_FILE              = os.path.join(DEFAULT_CONFIG_DIRECTORY, ".pyshellrc")

ENVIRONMENT_PROMPT_KEY              = SHELL_CATEGORY+".prompt"
ENVIRONMENT_PROMPT_DEFAULT          = "pyshell:>"

ENVIRONMENT_TAB_SIZE_KEY            = SHELL_CATEGORY+".tabsize"
TAB_SIZE                            = 4

ENVIRONMENT_LEVEL_TRIES_KEY         = MAIN_CATEGORY+".levelTries"

ENVIRONMENT_KEY_STORE_FILE_KEY      = MAIN_CATEGORY+".keystoreFile"
DEFAULT_KEYSTORE_FILE               = os.path.join(DEFAULT_CONFIG_DIRECTORY, ".pyshell_keystore")

KEYSTORE_SECTION_NAME               = MAIN_CATEGORY+".keystore"

ENVIRONMENT_SAVE_KEYS_KEY           = MAIN_CATEGORY+".saveKeys"
ENVIRONMENT_SAVE_KEYS_DEFAULT       = True

ENVIRONMENT_HISTORY_FILE_NAME_KEY   = SHELL_CATEGORY+".historyFile"
ENVIRONMENT_HISTORY_FILE_NAME_VALUE = os.path.join(DEFAULT_CONFIG_DIRECTORY, ".pyshell_history")

ENVIRONMENT_USE_HISTORY_KEY         = SHELL_CATEGORY+".useHistory"
ENVIRONMENT_USE_HISTORY_VALUE       = True

ENVIRONMENT_ADDON_TO_LOAD_KEY       = MAIN_CATEGORY+".addonToLoad"
ENVIRONMENT_ADDON_TO_LOAD_DEFAULT   = ("pyshell.addons.std","pyshell.addons.keystore","pyshell.addons.parameter")

ADDONLIST_KEY                       = "main.loader_addon"

### CONTEXT ###
CONTEXT_ATTRIBUTE_NAME   = "context"

DEBUG_ENVIRONMENT_NAME   = MAIN_CATEGORY+".debug"

CONTEXT_EXECUTION_KEY    = MAIN_CATEGORY+".execution"
CONTEXT_EXECUTION_SHELL  = "shell"
CONTEXT_EXECUTION_SCRIPT = "script"
CONTEXT_EXECUTION_DAEMON = "daemon"

CONTEXT_COLORATION_KEY   = SHELL_CATEGORY+".coloration"
CONTEXT_COLORATION_LIGHT = "light"
CONTEXT_COLORATION_DARK  = "dark"
CONTEXT_COLORATION_NONE  = "none"

### VARIABLE ###
VARIABLE_ATTRIBUTE_NAME = "variable"


