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

from tries.exception import triesException

from pyshell.register.loader.abstractloader import AbstractLoader
from pyshell.register.loader.exception import LoadException
from pyshell.register.loader.exception import UnloadException
from pyshell.register.profile.command import CommandLoaderProfile
from pyshell.utils.constants import ENVIRONMENT_ATTRIBUTE_NAME
from pyshell.utils.constants import ENVIRONMENT_LEVEL_TRIES_KEY
from pyshell.utils.exception import ListOfException


class CommandLoader(AbstractLoader):
    @staticmethod
    def createProfileInstance():
        return CommandLoaderProfile()

    @classmethod
    def load(cls, profile_object, parameter_container):
        profile_object.loadedCommand = []
        profile_object.loadedStopTraversal = []

        if parameter_container is None:
            excmsg = ("("+cls.__name__+") load, parameter "
                      "container is not defined.  It is needed to unload the "
                      "parameters")
            raise LoadException(excmsg)

        if not hasattr(parameter_container, ENVIRONMENT_ATTRIBUTE_NAME):
            excmsg = ("(CommandLoader) load, fail to load command because"
                      "container has not attribute '" +
                      ENVIRONMENT_ATTRIBUTE_NAME+"'")
            raise LoadException(excmsg)

        env_manager = getattr(parameter_container, ENVIRONMENT_ATTRIBUTE_NAME)
        param = env_manager.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY,
                                         perfect_match=True)

        if param is None:
            excmsg = ("(CommandLoader) load, fail to load command because "
                      "parameter has not a levelTries item")
            raise LoadException(excmsg)

        mltries = param.getValue()
        exceptions = ListOfException()

        # add command
        for key_list, cmd in profile_object.cmdDict.items():
            key = list(profile_object.prefix)
            key.extend(key_list)

            if len(cmd) == 0:
                excmsg = ("(CommandLoader) load, fail to insert key '" +
                          str(" ".join(key))+"' in multi tries: empty command")
                exceptions.addException(LoadException(excmsg))
                continue

            # INFO: the following statement uses several method of tries
            # and multiLevelTries, these methods coulds raise exception
            # but it is ensured that it won't be the case, do no need to
            # use a try/catch over this statement
            search_result = mltries.searchNode(key, True)

            if search_result is not None and search_result.isValueFound():
                flat_key = str(" ".join(key))
                excmsg = ("(CommandLoader) load, fail to insert key "
                          "'"+flat_key+"' in multi tries: path already"
                          " exists")
                exceptions.addException(LoadException(excmsg))
            else:
                mltries.insert(key, cmd)
                profile_object.loadedCommand.append(key)

        # stop traversal
        for stop in profile_object.stopList:
            key = list(profile_object.prefix)
            key.extend(stop)

            try:
                if mltries.isStopTraversal(key):
                    continue

                mltries.setStopTraversal(key, True)
                profile_object.loadedStopTraversal.append(key)
            except triesException as te:
                excmsg = ("(CommandLoader) load, fail to disable traversal for"
                          " key list '"+str(" ".join(stop))+"' in multi tries:"
                          " "+str(te))
                exceptions.addException(LoadException(excmsg))

        # raise error list
        if exceptions.isThrowable():
            raise exceptions

    @classmethod
    def unload(cls, profile_object, parameter_container):
        if parameter_container is None:
            excmsg = ("("+cls.__name__+") unload, parameter "
                      "container is not defined.  It is needed to unload the "
                      "parameters")
            raise UnloadException(excmsg)

        if not hasattr(parameter_container, ENVIRONMENT_ATTRIBUTE_NAME):
            excmsg = ("(CommandLoader) unload, fail to unload command because"
                      "container has not attribute '" +
                      ENVIRONMENT_ATTRIBUTE_NAME+"'")
            raise UnloadException(excmsg)

        env_manager = getattr(parameter_container, ENVIRONMENT_ATTRIBUTE_NAME)
        param = env_manager.getParameter(ENVIRONMENT_LEVEL_TRIES_KEY,
                                         perfect_match=True)

        if param is None:
            excmsg = ("(CommandLoader) unload, fail to unload command because"
                      " parameter has not a levelTries item")
            raise UnloadException(excmsg)

        mltries = param.getValue()
        exceptions = ListOfException()

        # remove commands
        for key in profile_object.loadedCommand:
            try:
                mltries.remove(key)
            except triesException as te:
                excmsg = ("(CommandLoader) unload, fail to remove key '" +
                          str(" ".join(key))+"' in multi tries: "+str(te))
                exceptions.addException(UnloadException(excmsg))

        # INFO: the following loop statement uses several method of tries
        # and multiLevelTries, these methods coulds raise exception
        # but it is ensured that it won't be the case, do no need to
        # use a try/catch over this statement

        # remove stop traversal
        for key in profile_object.loadedStopTraversal:

            # if key does not exist, continue
            search_result = mltries.searchNode(key, True)

            if search_result is None or not search_result.isPathFound():
                continue

            mltries.setStopTraversal(key, False)

        # raise error list
        if exceptions.isThrowable():
            raise exceptions
