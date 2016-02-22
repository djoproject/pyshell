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

from pyshell.arg.argchecker import ArgChecker
from pyshell.arg.argchecker import IntegerArgChecker
from pyshell.arg.decorator import shellMethod
from pyshell.command.command import MultiCommand
from pyshell.command.command import MultiOutput
from pyshell.command.command import UniCommand
from pyshell.command.engine import DEFAULT_EXECUTION_LIMIT
from pyshell.command.engine import EngineV3
from pyshell.command.engine import POSTPROCESS_INSTRUCTION
from pyshell.command.engine import PREPROCESS_INSTRUCTION
from pyshell.command.engine import PROCESS_INSTRUCTION
from pyshell.command.exception import ExecutionException
from pyshell.command.exception import ExecutionInitException
from pyshell.system.container import ParameterContainer

# TODO pour l'instant dans les tests, on ne tiens pas compte de
# -args (engine)
# -useArgs (MultiCommand)
# -enable (MultiCommand)

# TODO choses qui ne vont pas dans ces tests :
# -s'il n'y a qu'un argument l'ensemble des args ne lui est pas
# lié automatiquement
#   ok le comportement correcte a avoir
#       s'il n'y a qu'un args, on bind to sur lui
#       s'il n'y a pas d'arg, pas grave
#       s'il y a plusieurs args, on doit faire sauter une exception a
#       l'ajout du process
# -pas vraiment un probleme mais obligation d'avoir un retour dans le
# post pour ce cas ci, sinon l'encapsulation ne marche pas
#   -car arg3 n'a pas de valeur par défaut

# TODO TO TEST
# _computeTheNextChildToExecute
# _executeMethod
#  stopExecution


def noneFun():
    pass


class TestEngineCore(object):

    def setUp(self):
        pass

    def testInit(self):
        # check list
        with pytest.raises(ExecutionInitException):
            EngineV3(None, [], [])
        with pytest.raises(ExecutionInitException):
            EngineV3([], [], [])
        with pytest.raises(ExecutionInitException):
            EngineV3(42, [], [])

        # check command
        mc = MultiCommand()
        with pytest.raises(ExecutionInitException):
            EngineV3([mc], [[]], [[{}, {}, {}]])

        mc.addProcess(noneFun, noneFun, noneFun)
        with pytest.raises(ExecutionInitException):
            EngineV3([mc, 42], [[], []], [[{}, {}, {}], [{}, {}, {}]])

        mc.dymamic_count = 42
        e = EngineV3([mc], [[]], [[{}, {}, {}]])
        assert e.cmd_list[0] is mc
        assert mc.dymamic_count == 0  # check the call on reset

        # because the reset with the dynamic at 42 will remove every command...
        mc.addProcess(noneFun, noneFun, noneFun)

        # empty dict
        assert isinstance(e.env, ParameterContainer)

        # nawak dico
        with pytest.raises(ExecutionInitException):
            EngineV3([mc], 42, [[{}, {}, {}]])

        # non empty dico
        a = ParameterContainer()
        e = EngineV3([mc], [[]], [[{}, {}, {}]], a)
        assert e.env is a

    def testExecuteSimpleOne(self):
        @shellMethod(arg1=IntegerArgChecker())
        def pre(arg1=0):
            self.pre_count += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return 5 + arg1

        @shellMethod(arg2=IntegerArgChecker())
        def pro(arg2):
            self.pro_count += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return arg2 * arg2

        @shellMethod(arg3=ArgChecker())
        def post(arg3):
            assert arg3 == self.valueToTest
            self.post_count += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            # needed to the next post method in case of encapsulation
            return arg3

        # simple test
        self.valueToTest = 25
        self.pre_count = self.pro_count = self.post_count = 0
        uc = UniCommand(pre, pro, post)
        self.engine = EngineV3([uc], [[]], [[{}, {}, {}]])
        self.engine.execute()
        assert self.pre_count == 1
        assert self.pro_count == 1
        assert self.post_count == 1

        self.valueToTest = 100
        self.pre_count = self.pro_count = self.post_count = 0
        # uni command encapsulation test, the most used case
        self.engine = EngineV3([uc, uc], [[], []], [
                               [{}, {}, {}], [{}, {}, {}]])
        self.engine.execute()
        assert self.pre_count == 2
        assert self.pro_count == 1
        assert self.post_count == 2

        self.valueToTest = 225
        self.pre_count = self.pro_count = self.post_count = 0
        self.engine = EngineV3([uc, uc, uc],
                               [[], [], []],
                               [[{}, {}, {}], [{}, {}, {}], [{}, {}, {}]])
        self.engine.execute()
        assert self.pre_count == 3
        assert self.pro_count == 1
        assert self.post_count == 3

        # ...

    # test du mutliOutput
    def testSimpleOneWithMultiOutput(self):
        @shellMethod(arg1=IntegerArgChecker())
        def pre(arg1=0):
            self.pre_count += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return MultiOutput([5 + arg1, 10 + arg1])

        @shellMethod(arg2=IntegerArgChecker())
        def pro(arg2):
            self.pro_count += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return MultiOutput([arg2 * arg2, arg2 * arg2 * arg2])

        @shellMethod(arg3=ArgChecker())
        def post(arg3):
            # print arg3
            assert arg3 in self.valueToTest
            self.post_count += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return MultiOutput([arg3, arg3])

        # simple test
        self.valueToTest = [25, 125, 100, 1000]
        self.pre_count = self.pro_count = self.post_count = 0
        uc = UniCommand(pre, pro, post)
        self.engine = EngineV3([uc], [[]], [[{}, {}, {}]])
        self.engine.execute()
        assert self.pre_count == 1
        assert self.pro_count == 2
        assert self.post_count == 4

        self.valueToTest = [100, 1000, 225, 3375, 400, 8000]
        self.pre_count = self.pro_count = self.post_count = 0
        # uni command encapsulation test, the most used case
        self.engine = EngineV3([uc, uc], [[], []], [
                               [{}, {}, {}], [{}, {}, {}]])
        self.engine.execute()
        assert self.pre_count == 3
        assert self.pro_count == 4
        assert self.post_count == 24

        self.valueToTest = [225, 3375, 400, 8000, 625, 15625, 900, 27000]
        self.pre_count = self.pro_count = self.post_count = 0
        self.engine = EngineV3([uc, uc, uc],
                               [[], [], []],
                               [[{}, {}, {}], [{}, {}, {}], [{}, {}, {}]])
        self.engine.execute()
        assert self.pre_count == 7
        assert self.pro_count == 8
        assert self.post_count == 112

    # test du mutlicommand
    def testMultiCommand(self):
        mc = MultiCommand()
        self.pre_count = [0, 0, 0]
        self.pro_count = [0, 0, 0]
        self.post_count = [0, 0, 0]
        self.valueToTest = [[25], [343], [1]]

        @shellMethod(arg1=IntegerArgChecker())
        def pre1(arg1=0):
            self.pre_count[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return 5 + arg1

        @shellMethod(arg2=IntegerArgChecker())
        def pro1(arg2):
            self.pro_count[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return arg2 * arg2

        @shellMethod(arg3=ArgChecker())
        def post1(arg3):
            self.post_count[0] += 1
            # print "post1", arg3
            assert arg3 in self.valueToTest[0]
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return arg3

        @shellMethod(arg1=IntegerArgChecker())
        def pre2(arg1=0):
            self.pre_count[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return 7 + arg1

        @shellMethod(arg2=IntegerArgChecker())
        def pro2(arg2):
            self.pro_count[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return arg2 * arg2 * arg2

        @shellMethod(arg3=ArgChecker())
        def post2(arg3):
            self.post_count[1] += 1
            # print "post2", arg3
            assert arg3 in self.valueToTest[1]
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return arg3

        @shellMethod(arg1=IntegerArgChecker())
        def pre3(arg1=0):
            self.pre_count[2] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return 1 + arg1

        @shellMethod(arg2=IntegerArgChecker())
        def pro3(arg2):
            self.pro_count[2] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return arg2 * arg2 * arg2 * arg2

        @shellMethod(arg3=ArgChecker())
        def post3(arg3):
            self.post_count[2] += 1
            # print "post3", arg3
            assert arg3 in self.valueToTest[2]
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return arg3

        mc.addProcess(pre1, pro1, post1)
        mc.addProcess(pre2, pro2, post2)
        mc.addProcess(pre3, pro3, post3)

        self.engine = EngineV3([mc], [[]], [[{}, {}, {}]])
        self.engine.execute()

        for c in self.pre_count:
            assert c == 1

        for c in self.pro_count:
            assert c == 1

        for c in self.post_count:
            assert c == 1

        self.pre_count = [0, 0, 0]
        self.pro_count = [0, 0, 0]
        self.post_count = [0, 0, 0]
        self.valueToTest = [[100, 1728, 1296, 144, 36],
                            [1728, 144, 2744, 4096, 512],
                            [1296, 4096, 36, 512, 16]]
        self.engine = EngineV3([mc, mc], [[], []], [
                               [{}, {}, {}], [{}, {}, {}]])
        self.engine.execute()

        for c in self.pre_count:
            assert c == 4

        for c in self.pro_count:
            assert c == 3

        for c in self.post_count:
            assert c == 6

        self.pre_count = [0, 0, 0]
        self.pro_count = [0, 0, 0]
        self.post_count = [0, 0, 0]
        self.valueToTest = [[225, 4913, 14641, 289, 6859, 28561, 121, 2197,
                             2401, 361, 169, 49],
                            [4913, 289, 6859, 28561, 2197, 361, 9261, 50625,
                             169, 3375, 6561, 729],
                            [14641, 28561, 121, 2197, 2401, 28561, 50625,
                             169, 3375, 6561, 49, 729, 81]]
        self.engine = EngineV3([mc, mc, mc],
                               [[], [], []],
                               [[{}, {}, {}], [{}, {}, {}], [{}, {}, {}]])
        self.engine.execute()

        for c in self.pre_count:
            assert c == 13

        for c in self.pro_count:
            assert c == 9

        for c in self.post_count:
            assert c == 27

    # test du mutliOutput avec multicommand
    def testMultiOuputAndMultiCommand(self):
        mc = MultiCommand()
        self.pre_count = [0, 0]
        self.pro_count = [0, 0]
        self.post_count = [0, 0]
        self.valueToTest1 = [[1, 2, 3], [1, 2, 3]]
        self.valueToTest2 = [[6, 7, 8, 4, 5], [8, 9, 10, 2, 3, 4]]
        self.valueToTest3 = [[36, 49, 64, 16, 25, 81, 100, 4, 9, 1296, 2401,
                              4096, 256, 625],
                             [8, 9, 10, 2, 3, 4, 512, 729, 1000, 8, 27, 64]]

        @shellMethod(arg1=IntegerArgChecker())
        def pre1(arg1=0):
            assert arg1 in self.valueToTest1[0]
            self.pre_count[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return MultiOutput([5 + arg1, 3 + arg1])

        @shellMethod(arg2=IntegerArgChecker())
        def pro1(arg2):
            assert arg2 in self.valueToTest2[0]
            self.pro_count[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return MultiOutput([arg2 * arg2, arg2**4])

        @shellMethod(arg3=ArgChecker())
        def post1(arg3):
            assert arg3 in self.valueToTest3[0]
            self.post_count[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return MultiOutput([arg3, arg3])

        @shellMethod(arg1=IntegerArgChecker())
        def pre2(arg1=0):
            assert arg1 in self.valueToTest1[1]
            self.pre_count[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return MultiOutput([7 + arg1, 1 + arg1])

        @shellMethod(arg2=IntegerArgChecker())
        def pro2(arg2):
            assert arg2 in self.valueToTest2[1]
            self.pro_count[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return MultiOutput([arg2**3, arg2])

        @shellMethod(arg3=ArgChecker())
        def post2(arg3):
            assert arg3 in self.valueToTest3[1]
            self.post_count[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return MultiOutput([arg3, arg3])

        mc.addProcess(pre1, pro1, post1)
        mc.addProcess(pre2, pro2, post2)

        self.engine = EngineV3([mc], [[]], [[{}, {}, {}]])
        self.engine.setData(1)
        self.engine.addData(2, 1)
        self.engine.addData(3, 2)

        self.engine.execute()

        for c in self.pre_count:
            assert c == 3

        for c in self.pro_count:
            assert c == 6

        for c in self.post_count:
            assert c == 12

        self.pre_count = [0, 0]
        self.pro_count = [0, 0]
        self.post_count = [0, 0]

        self.valueToTest1 = [[1, 2, 3, 6, 7, 8, 4, 5, 9, 10],
                             [1, 2, 3, 6, 7, 8, 4, 5, 9, 10]]
        self.valueToTest2 = [[5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
                             [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
                              15, 16, 17]]  # 6, 7, 8, 4, 5, 9, 10 #+5 3 7 1
        self.valueToTest3 = [[256, 512, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                              13, 20736, 15, 1296, 28561, 2197, 38416, 25,
                              27, 10000, 6561, 4096, 36, 14641, 169, 3375,
                              49, 1331, 2744, 1728, 64, 50625, 196, 225, 81,
                              14, 83521, 343, 216, 729, 4913, 65536, 2401,
                              100, 16, 17, 1000, 144, 289, 625, 121, 125],
                             [256, 512, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
                              20736, 15, 1296, 28561, 2197, 38416, 25, 27,
                              10000, 6561, 4096, 36, 14641, 169, 3375, 49,
                              1331, 2744, 1728, 64, 50625, 196, 225, 81, 14,
                              83521, 343, 216, 729, 4913, 65536, 2401, 100,
                              16, 17, 1000, 144, 289, 625, 121, 125]]

        self.engine = EngineV3([mc, mc], [[], []], [
                               [{}, {}, {}], [{}, {}, {}]])
        self.engine.setData(1)
        self.engine.addData(2, 1)
        self.engine.addData(3, 2)
        self.engine.execute()

        for c in self.pre_count:
            assert c is 15

        for c in self.pro_count:
            assert c == 24

        for c in self.post_count:
            assert c == 144

        # it's too big with three command...

    # test du multiOutput avec multicommand et limite de commande
    def testMultiOuputAndMultiCommandAmdCommandLimit(self):
        @shellMethod(arg1=IntegerArgChecker())
        def pre1(arg1=0):
            assert arg1 in self.valueToTest1[0]
            self.pre_count[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return MultiOutput([5 + arg1, 3 + arg1])

        @shellMethod(arg2=IntegerArgChecker())
        def pro1(arg2):
            assert arg2 in self.valueToTest2[0]
            self.pro_count[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return MultiOutput([arg2 * arg2, arg2**4])

        @shellMethod(arg3=ArgChecker())
        def post1(arg3):
            assert arg3 in self.valueToTest3[0]
            self.post_count[0] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return MultiOutput([arg3, arg3])

        @shellMethod(arg1=IntegerArgChecker())
        def pre2(arg1=0):
            assert arg1 in self.valueToTest1[1]
            self.pre_count[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return MultiOutput([7 + arg1, 1 + arg1])

        @shellMethod(arg2=IntegerArgChecker())
        def pro2(arg2):
            assert arg2 in self.valueToTest2[1]
            self.pro_count[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return MultiOutput([arg2**3, arg2])

        @shellMethod(arg3=ArgChecker())
        def post2(arg3):
            assert arg3 in self.valueToTest3[1]
            self.post_count[1] += 1
            self.checkStack(self.engine.stack, self.engine.cmd_list)
            return MultiOutput([arg3, arg3])

        mc = MultiCommand()
        mc.addProcess(pre1, pro1, post1)
        mc.addProcess(pre2, pro2, post2)

        self.pre_count = [0, 0]
        self.pro_count = [0, 0]
        self.post_count = [0, 0]
        self.valueToTest1 = [[1, 2, 3], []]
        self.valueToTest2 = [[6, 7, 8, 4, 5], []]
        self.valueToTest3 = [
            [36, 49, 64, 16, 25, 1296, 2401, 4096, 256, 625], []]
        self.engine = EngineV3([mc], [[]], [[{}, {}, {}]])
        self.engine.setData(1)
        self.engine.addData(2, 1)
        self.engine.addData(3, 2)
        # engine.setCmdRange(0,1)
        self.engine.disableSubCommandInCurrentDataBunchMap(1)
        self.engine.execute()

        assert self.pre_count[0] is 3
        assert self.pro_count[0] is 6
        assert self.post_count[0] is 12
        assert self.pre_count[1] is 0
        assert self.pro_count[1] is 0
        assert self.post_count[1] is 0

        # limit the second command
        self.pre_count = [0, 0]
        self.pro_count = [0, 0]
        self.post_count = [0, 0]
        self.valueToTest1 = [[], [1, 2, 3]]
        self.valueToTest2 = [[], [2, 3, 4, 8, 9, 10]]
        self.valueToTest3 = [
            [], [2, 3, 4, 8, 9, 10, 8, 27, 64, 512, 729, 1000]]
        self.engine = EngineV3([mc], [[]], [[{}, {}, {}]])
        self.engine.setData(1)
        self.engine.addData(2, 1)
        self.engine.addData(3, 2)
        # the next command will raise an exception otherwise
        # engine.skipNextCommandOnTheCurrentData()
        # engine.setCmdRange(1,2)
        self.engine.disableSubCommandInCurrentDataBunchMap(0)
        self.engine.execute()

        assert self.pre_count[0] is 0
        assert self.pro_count[0] is 0
        assert self.post_count[0] is 0
        assert self.pre_count[1] is 3
        assert self.pro_count[1] is 6
        assert self.post_count[1] is 12

        # no limit 1
        self.pre_count = [0, 0]
        self.pro_count = [0, 0]
        self.post_count = [0, 0]
        self.valueToTest1 = [[1, 2, 3], [1, 2, 3]]
        self.valueToTest2 = [[6, 7, 8, 4, 5], [2, 3, 4, 8, 9, 10]]
        self.valueToTest3 = [[36, 49, 64, 16, 25, 1296, 2401, 4096, 256, 625],
                             [2, 3, 4, 8, 9, 10, 8, 27, 64, 512, 729, 1000]]
        self.engine = EngineV3([mc], [[]], [[{}, {}, {}]])
        self.engine.setData(1)
        self.engine.addData(2, 1)
        self.engine.addData(3, 2)
        # engine.setCmdRange(0,None)
        self.engine.disableEnablingMapOnDataBunch()
        self.engine.execute()

        assert self.pre_count[0] is 3
        assert self.pro_count[0] is 6
        assert self.post_count[0] is 12
        assert self.pre_count[1] is 3
        assert self.pro_count[1] is 6
        assert self.post_count[1] is 12

        # no limit 2
        self.pre_count = [0, 0]
        self.pro_count = [0, 0]
        self.post_count = [0, 0]
        self.engine = EngineV3([mc], [[]], [[{}, {}, {}]])
        self.engine.setData(1)
        self.engine.addData(2, 1)
        self.engine.addData(3, 2)
        # engine.setCmdRange(0,2)
        self.engine.enableSubCommandInCurrentDataBunchMap(0)
        self.engine.enableSubCommandInCurrentDataBunchMap(1)
        self.engine.execute()

        assert self.pre_count[0] is 3
        assert self.pro_count[0] is 6
        assert self.post_count[0] is 12
        assert self.pre_count[1] is 3
        assert self.pro_count[1] is 6
        assert self.post_count[1] is 12

        # test with two command in the pipe
        self.pre_count = [0, 0]
        self.pro_count = [0, 0]
        self.post_count = [0, 0]

        self.valueToTest1 = [[1, 2, 3, 6, 7, 8, 4, 5], [6, 7, 8, 4, 5]]
        self.valueToTest2 = [[9, 10, 11, 7, 8, 12, 13],
                             [7, 8, 9, 5, 6, 13, 14, 15, 11, 12]]
        self.valueToTest3 = [[81, 6561, 100, 10000, 121, 14641, 49, 2401, 64,
                              4096, 144, 20736, 169, 28561, 343, 512, 729, 125,
                              216, 2197, 2744, 3375, 1331, 1728, 7, 8, 9, 5, 6,
                              13, 14, 15, 11, 12],
                             [343, 512, 729, 125, 216, 2197, 2744, 3375, 1331,
                              1728, 7, 8, 9, 5, 6, 13, 14, 15, 11, 12]]

        self.engine = EngineV3([mc, mc], [[], []], [
                               [{}, {}, {}], [{}, {}, {}]])
        self.engine.setData(1)
        self.engine.addData(2, 1)
        self.engine.addData(3, 2)
        # engine.setCmdRange(0,1)
        self.engine.disableSubCommandInCurrentDataBunchMap(1)
        self.engine.execute()

        assert self.pre_count[0] is 9
        assert self.pro_count[0] is 12
        assert self.post_count[0] is 120

        assert self.pre_count[1] is 6
        assert self.pro_count[1] is 12
        assert self.post_count[1] is 24

        # cas limite où tout est disable
        """self.engine = EngineV3([mc, mc],[[],[]], [[{},{},{}],[{},{},{}]])
        self.engine.stack.setEnableMapOnIndex(-1,[False,False])
        #self.engine.disableSubCommandInCurrentDataBunchMap(0)
        #self.engine.disableSubCommandInCurrentDataBunchMap(1)
        self.assertRaises(ExecutionException, self.engine.execute)"""

    # jeu de test qui verifie la consistence de la pile a chaque iteration
    def checkStack(self, stack, cmd_list):
        for data, path, typ, enablingMap in stack:
            # check data
            assert isinstance(data, list)
            assert len(data) > 0

            # check path
            assert len(path) > 0 and len(path) <= len(cmd_list)
            for i in range(0, len(path)):
                assert path[i] >= 0 and path[i] < len(cmd_list[i])

            cmd = cmd_list[len(path) - 1]

            # check type
            assert (typ == PREPROCESS_INSTRUCTION or
                    typ == PROCESS_INSTRUCTION or
                    typ == POSTPROCESS_INSTRUCTION)

            # check enablingMap
            if enablingMap is not None:
                assert isinstance(enablingMap, list)
                assert len(enablingMap) == len(cmd)
                for b in enablingMap:
                    assert b or not b

            # an index can not be set if it is disabled in map or in cmd
            c, u, e = cmd[path[-1]]
            assert e and (enablingMap is None or enablingMap[path[-1]])

    def test_limitReaching(self):
        @shellMethod(arg1=IntegerArgChecker())
        def pre(arg1=0):
            self.pre_count += 1
            return 5 + arg1

        @shellMethod(arg2=IntegerArgChecker())
        def pro(arg2):
            self.pro_count += 1
            return arg2 * arg2

        @shellMethod(arg3=ArgChecker())
        def post(arg3):
            self.post_count += 1
            # needed to the next post method in case of encapsulation
            return arg3

        # simple test
        self.valueToTest = 25
        self.pre_count = self.pro_count = self.post_count = 0
        uc = UniCommand(pre, pro, post)

        # set a large amount of data for the pre, then the pro, then the post
        engine = EngineV3([uc], [[]], [[{}, {}, {}]])
        engine.stack[0] = ([5] * (DEFAULT_EXECUTION_LIMIT + 1), [0], 0, None)
        with pytest.raises(ExecutionException):
            engine.execute()
        assert uc[0][0].pre_count == 256
        assert uc[0][0].pro_count == 255
        assert uc[0][0].post_count == 255

        engine = EngineV3([uc], [[]], [[{}, {}, {}]])
        engine.stack[0] = ([5] * (DEFAULT_EXECUTION_LIMIT + 1), [0], 1, None)
        with pytest.raises(ExecutionException):
            engine.execute()
        assert uc[0][0].pre_count == 0
        assert uc[0][0].pro_count == 256
        assert uc[0][0].post_count == 255

        engine = EngineV3([uc], [[]], [[{}, {}, {}]])
        engine.stack[0] = ([5] * (DEFAULT_EXECUTION_LIMIT + 1), [0], 2, None)
        with pytest.raises(ExecutionException):
            engine.execute()
        assert uc[0][0].pre_count == 0
        assert uc[0][0].pro_count == 0
        assert uc[0][0].post_count == 256

    # getEnv
    def test_getEnv(self):
        mc = MultiCommand()
        mc.addProcess(noneFun, noneFun, noneFun)

        e = EngineV3([mc], [[]], [[{}, {}, {}]])

        assert e.env is e.getEnv()

        a = ParameterContainer()
        e = EngineV3([mc], [[]], [[{}, {}, {}]], a)

        assert e.env is e.getEnv()
        assert a is e.getEnv()
