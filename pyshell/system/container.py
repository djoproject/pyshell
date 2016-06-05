#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

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

import threading

from pyshell.utils.abstract.flushable import Flushable
from pyshell.utils.exception import DefaultPyshellException


class AbstractParameterContainer(object):
    def getCurrentId(self):
        pass  # TO OVERRIDE

    def getOrigin(self):
        pass  # TO OVERRIDE

    def setOrigin(self, origin, origin_profile=None):
        pass  # TO OVERRIDE


class DummyParameterContainer(AbstractParameterContainer):
    def getCurrentId(self):
        return threading.current_thread().ident

DEFAULT_DUMMY_PARAMETER_CONTAINER = DummyParameterContainer()
MAIN_LEVEL = "main"
PROCEDURE_LEVEL = "procedure"


class ParameterContainer(AbstractParameterContainer, Flushable):
    def __init__(self):
        self.parameterManagerList = []

        # small explanation about levels: A thread can access to two
        # different level, the main one and the procedure one.  The
        # goal is to force developper to create python procedure
        # in place of shell procedure.
        #
        # In the main thread, the main level is occupied by the shell
        # or by a main script (init script or daemon script), it is
        # possible to run a sub script that will be in the procedure
        # level.  A command in the procedure level won't be allowed
        # to create another procedure level.
        #
        # In any secondary thread, the main level will be occupied
        # by a command started from another thread.  It is not
        # possible to have a procedure in the main level because
        # it needs to be started by a command.  The command in
        # the main level can execute a procedure in the procedure
        # level.  And as for the main thread, the procedure
        # won't be allowed to create another procedure level.
        self.thread_in_procedure = set()

    def registerParameterManager(self, name, obj):
        if not isinstance(obj, Flushable):
            excmsg = ("(ParameterContainer) registerParameterManager, an "
                      "instance of Flushable object was expected, got '" +
                      str(type(obj))+"'")
            raise DefaultPyshellException(excmsg)

        if hasattr(self, name):
            excmsg = ("(ParameterContainer) registerParameterManager, an "
                      "attribute is already registered with this name: '" +
                      str(name)+"'")
            raise DefaultPyshellException(excmsg)

        setattr(self, name, obj)
        self.parameterManagerList.append(name)

    def getCurrentId(self):
        tid = threading.current_thread().ident

        if tid in self.thread_in_procedure:
            return tid, PROCEDURE_LEVEL

        return tid, MAIN_LEVEL

    def isMainThread(self):
        return isinstance(threading.current_thread(), threading._MainThread)

    def decrementLevel(self):
        tid = threading.current_thread().ident

        if tid in self.thread_in_procedure:
            self.thread_in_procedure.remove(tid)

    def incrementLevel(self):
        tid = threading.current_thread().ident

        if tid in self.thread_in_procedure:
            excmsg = ("(ParameterContainer) incrementLevel, this thread"
                      " already executes a procedure, only one level of "
                      "procedure is allowed.  If your design requires"
                      "embedded procedure, this is a mistake.  Write them"
                      "in python language instead.")
            raise DefaultPyshellException(excmsg)

        self.thread_in_procedure.add(tid)

    def flush(self):
        for m in self.parameterManagerList:
            getattr(self, m).flush()
