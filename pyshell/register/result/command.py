#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2017  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.register.loader.exception import UnloadException
from pyshell.register.result.abstractresult import AbstractResult
from pyshell.utils.raises import raiseIfNotString


class CommandResult(AbstractResult):
    def __init__(self, command_list, section_name=None, addons_set=None):
        if (command_list is None or
           not hasattr(command_list, "__iter__") or
           not hasattr(command_list, "__len__")):
            excmsg = "(CommandResult) __init__, command_list is not iterable"
            raise UnloadException(excmsg)

        if len(command_list) == 0:
            excmsg = ("(CommandResult) __init__, empty command_list is not "
                      "allowed")
            raise UnloadException(excmsg)

        index = 0
        for command in command_list:
            raiseIfNotString(command,
                             "command #%s" % index,
                             UnloadException,
                             "__init__",
                             "CommandResult")
            index += 1

        self.command_list = command_list

        if section_name is not None:
            raiseIfNotString(section_name,
                             "section_name",
                             UnloadException,
                             "__init__",
                             "CommandResult")

        self.section_name = section_name

        if addons_set is not None:
            if type(addons_set) is not set:
                excmsg = ("(CommandResult) __init__, addons_set is not a set, "
                          "got '%s'" % str(type(addons_set)))
                raise UnloadException(excmsg)

            index = 0
            for addon in addons_set:
                raiseIfNotString(addon,
                                 "addon #%s" % str(index),
                                 UnloadException,
                                 "__init__",
                                 "CommandResult")
                index += 1

        self.addons_set = addons_set
