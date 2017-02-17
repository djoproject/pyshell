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

from pyshell.register.profile.default import DefaultProfile


class FileLoaderProfile(DefaultProfile):
    """
        The file loader must always be the last to be executed at load because
        it needs to wait every element to be loaded before to update them
        with the config file.

        And the file loader must always be the last to be executed at unload
        because it needs to wait every other loaders to be unloaded before
        to create the config file.
    """

    def __init__(self):
        DefaultProfile.__init__(self,
                                load_priority=float('inf'),
                                unload_priority=float('inf'))
