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

import os

from pyshell.arg.checker.string43 import StringArgChecker

TYPENAME = "filePath"


class FilePathArgChecker(StringArgChecker):
    # just check a path, no operation are executed here,
    # it is the job of the addon to perform change

    def __init__(self,
                 exist=None,
                 readable=None,
                 writtable=None,
                 is_file=None):
        StringArgChecker.__init__(self, 1, None)

        if exist is not None and type(exist) != bool:
            excmsg = "exist must be None or a boolean, got '%s'"
            excmsg %= str(type(exist))
            self._raiseArgInitializationException(excmsg)

        if readable is not None and type(readable) != bool:
            excmsg = "readable must be None or a boolean, got '%s'"
            excmsg %= str(type(readable))
            self._raiseArgInitializationException(excmsg)

        if writtable is not None and type(writtable) != bool:
            excmsg = "writtable must be None or a boolean, got '%s'"
            excmsg %= str(type(writtable))
            self._raiseArgInitializationException(excmsg)

        if is_file is not None and type(is_file) != bool:
            excmsg = "is_file must be None or a boolean, got '%s'"
            excmsg %= str(type(is_file))
            self._raiseArgInitializationException(excmsg)

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
                excmsg = "Path '%s' does not exist and must exist" % str(path)
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

            if not self.exist and file_exist:
                excmsg = "Path '%s' exists and must not exist" % str(path)
                self._raiseArgException(excmsg, arg_number, arg_name_to_bind)

        # is_file
        if self.is_file is not None:
            if file_exist is None:
                file_exist = os.access(path, os.F_OK)

            if file_exist:
                is_file = os.path.isfile(path)

                if self.is_file and not is_file:
                    excmsg = "Path '%s' is a directory and must be a file"
                    excmsg %= str(path)
                    self._raiseArgException(excmsg,
                                            arg_number,
                                            arg_name_to_bind)

                if not self.is_file and is_file:
                    excmsg = "Path '%s' is a file and must be a directory"
                    excmsg %= str(path)
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
                    excmsg = ("Path '%s' does not exist and so it is not "
                              "readable")
                    excmsg %= str(path)
                    self._raiseArgException(excmsg,
                                            arg_number,
                                            arg_name_to_bind)

            else:
                readable = os.access(path, os.R_OK)

                if self.readable and not readable:
                    excmsg = "Path '%s' is not readable and must be readable"
                    excmsg %= str(path)
                    self._raiseArgException(excmsg,
                                            arg_number,
                                            arg_name_to_bind)

                if not self.readable and readable:
                    excmsg = "Path '%s' is readable and must not be readable"
                    excmsg %= str(path)
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
                    excmsg = ("Path '%s' does not exist and the first existing"
                              " parent directory '%s' is not writtable")
                    excmsg %= (str(path), str(parent_path),)
                    self._raiseArgException(excmsg,
                                            arg_number,
                                            arg_name_to_bind)

            else:
                # return False if path does not exist...
                writtable = os.access(path, os.W_OK)

                if self.writtable and not writtable:
                    excmsg = "Path '%s' is not writtable and must be writtable"
                    excmsg %= str(path)
                    self._raiseArgException(excmsg,
                                            arg_number,
                                            arg_name_to_bind)

                if not self.writtable and writtable:
                    excmsg = "Path '%s' is writtable and must not be writtable"
                    excmsg %= str(path)
                    self._raiseArgException(excmsg,
                                            arg_number,
                                            arg_name_to_bind)

        # don't open a file, because not sure the addon will close it...
        return value

    def getUsage(self):
        return "<file_path>"

    @classmethod
    def getTypeName(cls):
        return TYPENAME
