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

import pytest

from pyshell.command.command import Command
from pyshell.command.command import MultiCommand
from pyshell.command.command import UniCommand
from pyshell.command.exception import CommandException


class TestCommand(object):

    # init an empty one and check the args
    def testEmptyCommand(self):
        mc = MultiCommand()
        assert mc.help_message is None

    # addProcess
    def testAddProcess(self):
        mc = MultiCommand()
        # add preProcess with/withou checker
        with pytest.raises(CommandException):
            mc.addProcess()  # pre/pro/post process are None

        # test meth insertion and usage_builder set
        def toto():
            "tata"
            pass

        toto.checker = 52
        assert mc.addProcess(toto) is None
        assert mc.usage_builder == 52
        assert mc.help_message == "tata"

        toto.checker = 53
        assert mc.addProcess(None, toto) is None
        # the usage builder is still the builder of the first command inserted
        assert mc.usage_builder == 52

        toto.checker = 54
        assert mc.addProcess(None, None, toto) is None
        # the usage builder is still the builder of the first command inserted
        assert mc.usage_builder == 52

        mc = MultiCommand()
        mc.addProcess(None, None, toto)
        assert mc.usage_builder == 54

        toto.checker = 52
        mc.addProcess(toto)
        assert mc.usage_builder == 54

        toto.checker = 53
        mc.addProcess(None, toto)
        assert mc.usage_builder == 54

        mc = MultiCommand()
        toto.checker = 53
        mc.addProcess(None, toto)
        assert mc.usage_builder == 53

        mc.addProcess(None, None, toto)
        assert mc.usage_builder == 53

        toto.checker = 52
        mc.addProcess(toto)
        assert mc.usage_builder == 53

        # try to insert not callable object
        with pytest.raises(CommandException):
            mc.addProcess(1)
        with pytest.raises(CommandException):
            mc.addProcess(None, 1)
        with pytest.raises(CommandException):
            mc.addProcess(None, None, 1)

        # check the process length
        assert len(mc) == 3

        # check if the useArgs is set in the list
        for (c, u, e,) in mc:
            assert u

    # addStaticCommand
    def testStaticCommand(self):
        mc = MultiCommand()
        c = Command()

        # try to insert anything but cmd instance
        with pytest.raises(CommandException):
            mc.addStaticCommand(23)

        # try to insert a valid cmd
        assert mc.addStaticCommand(c) is None

        # try to insert where there is a dynamic command in in
        mc.dymamic_count = 1
        with pytest.raises(CommandException):
            mc.addStaticCommand(c)

        # check self.usage_builder, and useArgs in the list
        assert mc.usage_builder == c.preProcess.checker

    # usage
    def testUsage(self):
        mc = MultiCommand()
        c = Command()

        # test with and without self.usage_builder
        assert mc.usage() == "no args needed"

        mc.addStaticCommand(c)
        assert mc.usage() == "`[args:(<any> ... <any>)]`"

    # reset
    def testReset(self):
        mc = MultiCommand()
        c = Command()

        # populate
        mc.addStaticCommand(c)
        mc.addDynamicCommand(c, True)
        mc.addDynamicCommand(c, True)
        mc.args = "toto"
        mc.pre_count = 1
        mc.pro_count = 2
        mc.post_count = 3

        # reset and test
        final_count = len(mc) - mc.dymamic_count
        mc.reset()
        # self.assertTrue(mc.args is None)
        assert mc.dymamic_count == 0
        assert len(mc.only_once_dict) == 0
        assert mc.pre_count == mc.pro_count == mc.post_count == 0
        assert final_count == len(mc)

    """# setArgs
    def testArgs(self):
        mc = MultiCommand()
        #try to add anything
        mc.setArgs(42)
        self.assertTrue(isinstance(mc.args, MultiOutput))
        self.assertTrue(mc.args[0] == 42)

        #try to add multioutput
        mo = MultiOutput([1,2,3])
        mc.setArgs(mo)
        self.assertTrue(isinstance(mc.args, MultiOutput))
        self.assertTrue(mc.args[0] == 1)
        self.assertTrue(mc.args[1] == 2)
        self.assertTrue(mc.args[2] == 3)

    # flushArgs
    def testFlus(self):
        mc = MultiCommand()
        #set (anything/multioutput) then flush
        mc.setArgs(42)
        mc.flushArgs()

        #it must always be None
        self.assertTrue(mc.args is None)"""

    # addDynamicCommand
    def testAddDynamicCommand(self):
        mc = MultiCommand()
        c = Command()

        # try to insert anything but command
        with pytest.raises(CommandException):
            mc.addDynamicCommand(42)

        # try to insert the same command twice with onlyAddOnce=True
        mc.addDynamicCommand(c)
        assert len(mc) == 1
        mc.addDynamicCommand(c)
        assert len(mc) == 1
        mc.addDynamicCommand(c, False)  # do the same with onlyAddOnce=False
        assert len(mc) == 2

        # check useArgs in the list
        for (c, u, e,) in mc:
            assert u

    # test unicommand class
    def testUniCommand(self):
        # test to create a basic empty one
        with pytest.raises(CommandException):
            UniCommand()

        def toto():
            pass

        # then with different kind of args
        assert UniCommand(toto) is not None
        assert UniCommand(None, toto) is not None
        assert UniCommand(None, None, toto) is not None

        # try to add another command
        uc = UniCommand(toto)
        assert len(uc) == 1

        uc.addProcess()
        assert len(uc) == 1

        uc.addStaticCommand(42)
        assert len(uc) == 1

    def test_enableDisableCmd(self):
        def plop():
            pass

        mc = MultiCommand()
        mc.addProcess(plop, plop, plop)
        mc.addProcess(plop, plop)
        mc.addProcess(plop)
        mc.addProcess(plop, plop)

        index = 0
        for c, a, e in mc:
            assert e
            assert a

            if (index % 2) == 0:
                mc.disableCmd(index)
            else:
                mc.disableArgUsage(index)

            index += 1

        index = 0
        for c, a, e in mc:
            if (index % 2) == 0:
                assert a
                assert not e
                mc.disableArgUsage(index)
                mc.enableCmd(index)
            else:
                assert e
                assert not a
                mc.disableCmd(index)
                mc.enableArgUsage(index)
            index += 1

        index = 0
        for c, a, e in mc:
            if (index % 2) == 0:
                assert e
                assert not a
            else:
                assert a
                assert not e
            index += 1
