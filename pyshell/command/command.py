#!/usr/bin/env python -t
# -*- coding: utf-8 -*-

# Copyright (C) 2012  Jonathan Delvaux <pyshell@djoproject.net>

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

from pyshell.arg.argchecker import ArgChecker
from pyshell.arg.argchecker import listArgChecker
from pyshell.arg.decorator import defaultMethod
from pyshell.arg.decorator import shellMethod
from pyshell.command.exception import CommandException
from pyshell.command.utils import isAValidIndex


# just a marker class to differentiate an standard list from a multiple output
class MultiOutput(list):
    pass


class Command(object):
    # default preProcess
    @shellMethod(args=listArgChecker(ArgChecker()))
    @defaultMethod()
    def preProcess(self, args):
        return args

    # default process
    @shellMethod(args=listArgChecker(ArgChecker()))
    @defaultMethod()
    def process(self, args):
        return args

    # default postProcess
    @shellMethod(args=listArgChecker(ArgChecker()))
    @defaultMethod()
    def postProcess(self, args):
        return args

    # this method is called on every processing to reset the internal state
    def reset(self):
        pass  # TO OVERRIDE if needed

    def clone(self, parent=None):
        if parent is None:
            parent = Command()

        parent.preProcess = self.preProcess
        parent.process = self.process
        parent.postProcess = self.postProcess

        return parent


#
# a multicommand will produce several process with only one call
#
class MultiCommand(list):
    def __init__(self):
        # message to show in the help context
        self.help_message = None

        # which (pre/pro/post) process of the first command must be used to
        # create the usage.
        self.usage_builder = None

        # this dict is used to prevent the insertion of the an existing
        # dynamic sub command
        self.only_once_dict = {}
        self.dymamic_count = 0

        self.pre_count = self.pro_count = self.post_count = 0

        self.dynamic_parameter = {}

    def addProcess(self,
                   pre_process=None,
                   process=None,
                   post_process=None,
                   use_args=True):
        c = Command()

        if pre_process == process == post_process is None:
            raise CommandException("(MultiCommand) addProcess, at least one of"
                                   " the three callable pre/pro/post object "
                                   "must be different of None")

        if pre_process is not None:
            # preProcess must be callable
            if not hasattr(pre_process, "__call__"):
                raise CommandException("(MultiCommand) addProcess, the given "
                                       "preProcess is not a callable object")

            # set preProcess
            c.preProcess = pre_process

            # check if this callable object has an usage builder
            if self.usage_builder is None and hasattr(pre_process, "checker"):
                self.usage_builder = pre_process.checker

            if self.help_message is None and \
               hasattr(pre_process, "__doc__") and \
               pre_process.__doc__ is not None and \
               len(pre_process.__doc__) > 0:
                self.help_message = pre_process.__doc__

        if process is not None:
            # process must be callable
            if not hasattr(process, "__call__"):
                raise CommandException("(MultiCommand) addProcess, the given "
                                       "process is not a callable object")

            # set process
            c.process = process

            # check if this callable object has an usage builder
            if self.usage_builder is None and hasattr(process, "checker"):
                self.usage_builder = process.checker

            if self.help_message is None and hasattr(process, "__doc__") and \
               process.__doc__ is not None and len(process.__doc__) > 0:
                self.help_message = process.__doc__

        if post_process is not None:
            # postProcess must be callable
            if not hasattr(post_process, "__call__"):
                raise CommandException("(MultiCommand) addProcess, the given "
                                       "post_process is not a callable object")

            # set postProcess
            c.postProcess = post_process

            if self.usage_builder is None and hasattr(post_process, "checker"):
                self.usage_builder = post_process.checker

            if self.help_message is None and \
               hasattr(post_process, "__doc__") and \
               post_process.__doc__ is not None and \
               len(post_process.__doc__) > 0:
                self.help_message = post_process.__doc__

        self.append((c, use_args, True,))

    def addStaticCommand(self, cmd, use_args=True):
        # cmd must be an instance of Command
        if not isinstance(cmd, Command):
            raise CommandException("(MultiCommand) addStaticCommand, try to "
                                   "insert a non command object")

        # can't add static if dynamic in the list
        if self.dymamic_count > 0:
            raise CommandException("(MultiCommand) addStaticCommand, can't "
                                   "insert static command while dynamic "
                                   "command are present, reset the "
                                   "MultiCommand then insert static command")

        # if usage_builder is not set, take the preprocess builder of the cmd
        if self.usage_builder is None and hasattr(cmd.preProcess, "checker"):
            self.usage_builder = cmd.preProcess.checker

        # build help message
        if self.help_message is None and \
           hasattr(cmd.preProcess, "__doc__") and \
           cmd.preProcess.__doc__ is not None and \
           len(cmd.preProcess.__doc__) > 0:
            self.help_message = cmd.preProcess.__doc__

        # add the command
        self.append((cmd, use_args, True,))

    def usage(self):
        # TODO should not return the usage of one of the default
        # pre/pro/post process of a basic cmd (see implementation at the
        # beginning of the file)
        #   should return the first custom pre/pro/post process of the command
        #   make some test
        #       normaly only the case if we use addStaticCommand or
        #           addDynamicCommand
        #       normaly no problem with addProcess

        if self.usage_builder is None:
            return "no args needed"
        else:
            return "`"+self.usage_builder.usage()+"`"

    # TODO is it still usefull ? reset become deprecated because of
    # cloning, no?
    def reset(self):
        # remove dynamic command
        del self[len(self)-self.dymamic_count:]
        self.dymamic_count = 0

        # reset self.only_once_dict
        self.only_once_dict = {}

        # reset counter
        self.pre_count = self.pro_count = self.post_count = 0

        self.dynamic_parameter = {}

        # reset every sub command
        for i in range(0, len(self)):
            c, a, e = self[i]
            # these counters are used to prevent an infinite execution of
            # the pre/pro/post process
            c.pre_count = 0
            c.pro_count = 0
            c.post_count = 0
            c.reset()
            self[i] = (c, a, True,)

    def clone(self, parent=None):
        if parent is None:
            parent = MultiCommand()

        parent.help_message = self.help_message
        parent.usage_builder = self.usage_builder
        del parent[:]
        parent.reset()

        for i in range(0, len(self)-self.dymamic_count):
            c, a, e = self[i]
            cmd_clone = c.clone()
            cmd_clone.pre_count = 0
            cmd_clone.pro_count = 0
            cmd_clone.post_count = 0
            cmd_clone.reset()
            parent.append((cmd_clone, a, e,))

        return parent

    def addDynamicCommand(self,
                          c,
                          only_add_once=True,
                          use_args=True,
                          enabled=True):
        # cmd must be an instance of Command
        if not isinstance(c, Command):
            raise CommandException("(MultiCommand) addDynamicCommand, try to "
                                   "insert a non command object")

        # check if the method already exist in the dynamic
        h = hash(c)
        if only_add_once and h in self.only_once_dict:
            return

        self.only_once_dict[h] = True

        # add the command
        self.append((c, use_args, enabled,))
        self.dymamic_count += 1

    def enableCmd(self, index=0):
        isAValidIndex(self,
                      index,
                      "enableCmd",
                      "Command list",
                      "MultiCommand",
                      CommandException)
        c, a, e = self[index]
        self[index] = (c, a, True,)

    def disableCmd(self, index=0):
        isAValidIndex(self,
                      index,
                      "disableCmd",
                      "Command list",
                      "MultiCommand",
                      CommandException)
        c, a, e = self[index]
        self[index] = (c, a, False,)

    def enableArgUsage(self, index=0):
        isAValidIndex(self,
                      index,
                      "enableArgUsage",
                      "Command list",
                      "MultiCommand",
                      CommandException)
        c, a, e = self[index]
        self[index] = (c, True, e,)

    def disableArgUsage(self, index=0):
        isAValidIndex(self,
                      index,
                      "disableArgUsage",
                      "Command list",
                      "MultiCommand",
                      CommandException)
        c, a, e = self[index]
        self[index] = (c, False, e,)

    def isdisabledCmd(self, index=0):
        isAValidIndex(self,
                      index,
                      "isdisabledCmd",
                      "Command list",
                      "MultiCommand",
                      CommandException)
        c, a, e = self[index]
        return not e

    def isArgUsage(self, index=0):
        isAValidIndex(self,
                      index,
                      "isArgUsage",
                      "Command list",
                      "MultiCommand",
                      CommandException)
        c, a, e = self[index]
        return a


#
# special command class, with only one command (the starting point)
#
class UniCommand(MultiCommand):
    def __init__(self, pre_process=None, process=None, post_process=None):
        MultiCommand.__init__(self)
        MultiCommand.addProcess(self, pre_process, process, post_process)

    def addProcess(self,
                   pre_process=None,
                   process=None,
                   post_process=None,
                   use_args=True):
        pass  # block the procedure to add more commands

    def addStaticCommand(self, cmd, use_args=True):
        pass  # block the procedure to add more commands

    def clone(self, parent=None):
        if parent is None:
            cmd, useArg, enabled = self[0]
            parent = UniCommand(cmd.preProcess, cmd.process, cmd.postProcess)

        return MultiCommand.clone(self, parent)
