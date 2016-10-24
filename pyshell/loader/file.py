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

import os

from pyshell.loader.abstractloader import AbstractLoader
from pyshell.loader.exception import RegisterException
from pyshell.loader.exception import UnloadException
from pyshell.loader.utils import getRootLoader
from pyshell.system.procedure import FileProcedure
from pyshell.utils.constants import DEFAULT_CONFIG_DIRECTORY
from pyshell.utils.constants import DEFAULT_PROFILE_NAME
from pyshell.utils.constants import ENVIRONMENT_CONFIG_DIRECTORY_KEY


def _localGetAndInitCallerModule(profile=None):
    # Because FileLoader is used in the MasterLoader, MasterLoader can not
    # be imported here, and so it can not be initialized
    master = getRootLoader(class_definition=None)
    
    if master is None:
        excmsg = ("(FileRegister) _localGetAndInitCallerModule, nothing is "
                  "yet registered for this addon, before to be able to "
                  "disable the file saving, something must be registered.")
        raise RegisterException(excmsg)
    
    return master.getOrCreateLoader(FileLoader, profile)


def disableConfigSaving(profile=None):
    loader = _localGetAndInitCallerModule(profile)
    loader.disableAtUnload = True


class FileLoader(AbstractLoader):
    def __init__(self, parent):
        AbstractLoader.__init__(self,
                                parent,
                                load_priority=float('inf'),
                                unload_priority=float('inf'))
        self._addons = set()
        self._commands = {}
        self.disableAtUnload = False

    def _getFilePath(self, parameter_container, profile):
        if self.parent is None:
            return None

        if profile is None:
            profile = DEFAULT_PROFILE_NAME

        env = None
        if parameter_container is not None and hasattr(parameter_container, "env"):
            env = parameter_container.environment
            param = env.getParameter(ENVIRONMENT_CONFIG_DIRECTORY_KEY,
                                     perfect_match=True)
        if env is None or param is None:
            directory = DEFAULT_CONFIG_DIRECTORY
        else:
            directory = param.getValue()

        return os.path.join(directory,
                            "%s.%s.pys" % (self.parent.addon_name,
                                           profile))

    def load(self, parameter_container=None, profile=None):
        path = self._getFilePath(parameter_container, profile)

        if path is None or not os.path.exists(path):
            return

        afile = FileProcedure(path)
        afile.neverStopIfErrorOccured()
        afile.execute(args=(), parameters=parameter_container)

    def unload(self, parameter_container=None, profile=None):
        if self.disableAtUnload:
            return

        path = self._getFilePath(parameter_container, profile)

        if path is None:
            excmsg = ("(FileLoader) unload, undefined path file, not possible "
                      "to generate the parameter file.")
            raise UnloadException(excmsg)

        if len(self._commands) == 0:
            if os.path.exists(path):
                os.remove(path)
            return

        try:
            with open(path, "wb") as file_descr:
                for addon_name in self._addons:
                    file_descr.write("addon load %s\n" % addon_name)

                for section_name, command_list in self._commands.items():
                    for command in command_list:
                        file_descr.write(command+"\n")

                file_descr.flush()
        except:
            self._addons.clear()
            self._commands.clear()
            raise

    def saveCommands(self, section_name, command_list, addons_set=None):
        if len(command_list) == 0:
            return

        if addons_set is not None:
            self._addons = self._addons.union(addons_set)

        self._commands[section_name] = command_list
