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

from pyshell.command.procedure import FileProcedure
from pyshell.register.loader.abstractloader import AbstractLoader
from pyshell.register.loader.exception import UnloadException
from pyshell.register.profile.file import FileLoaderProfile
from pyshell.register.result.command import CommandResult
from pyshell.utils.constants import DEFAULT_CONFIG_DIRECTORY
from pyshell.utils.constants import ENVIRONMENT_CONFIG_DIRECTORY_KEY


class FileLoader(AbstractLoader):

    @staticmethod
    def createProfileInstance(root_profile):
        return FileLoaderProfile(root_profile)

    @staticmethod
    def getFilePath(parameter_container, profile_object):
        root_profile = profile_object.getRootProfile()
        addon_name = root_profile.getAddonInformations().getName()

        env = None
        if parameter_container is not None:
            env = parameter_container.getEnvironmentManager()
            param = env.getParameter(ENVIRONMENT_CONFIG_DIRECTORY_KEY,
                                     perfect_match=True)
        if env is None or param is None:
            directory = DEFAULT_CONFIG_DIRECTORY
        else:
            directory = param.getValue()

        return os.path.join(directory,
                            "%s.%s.pys" % (addon_name,
                                           root_profile.getName()))

    @classmethod
    def load(cls, profile_object, parameter_container):
        path = cls.getFilePath(parameter_container, profile_object)

        if path is None or not os.path.exists(path):
            return

        afile = FileProcedure(file_path=path, granularity=-1)
        afile.execute(parameter_container=parameter_container, args=())

    @classmethod
    def unload(cls, profile_object, parameter_container):
        path = cls.getFilePath(parameter_container, profile_object)

        if path is None:
            excmsg = ("(FileLoader) unload, undefined path file, not possible "
                      "to generate the parameter file.")
            raise UnloadException(excmsg)

        root_profile = profile_object.getRootProfile()
        results = root_profile.getResult(CommandResult)

        # no result
        if len(results) == 0:
            if os.path.exists(path):
                os.remove(path)
            return

        # compute addons to load
        addons = set()
        for class_key, result in results.items():
            if result.addons_set is None:
                continue

            addons.update(result.addons_set)

        # generate the file
        with open(path, "w") as file_descr:
            for addon_name in sorted(addons):
                file_descr.write("addon load %s\n" % addon_name)

            for class_key, result in results.items():
                if result.section_name is not None:
                    pass  # TODO (issue #82) add result.section_name as comment

                for command in result.command_list:
                    file_descr.write(command + "\n")

            file_descr.flush()
