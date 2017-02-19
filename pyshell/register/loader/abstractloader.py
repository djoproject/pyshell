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

from pyshell.register.exception import LoaderException


class AbstractLoader(object):

    def __init__(self, *args, **kwargs):
        raise LoaderException("Not allowed to instanciate.")

    @classmethod
    def getLoaderSignature(cls):
        return cls.__module__ + "." + cls.__name__

    @staticmethod
    def createProfileInstance(root_profile):
        pass

    @classmethod
    def load(cls, profile_object, parameter_container):
        pass

    @classmethod
    def unload(cls, profile_object, parameter_container):
        pass
