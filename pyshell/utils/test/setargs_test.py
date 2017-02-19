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

import pytest

from pyshell.system.manager.parent import ParentManager
from pyshell.utils.exception import ParameterException
from pyshell.utils.setargs import setArgs


class TestSetArgs(object):

    def getParams(self, manager):
        assert manager.hasParameter("*",
                                    perfect_match=True,
                                    local_param=True,
                                    explore_other_scope=False)

        assert manager.hasParameter("#",
                                    perfect_match=True,
                                    local_param=True,
                                    explore_other_scope=False)

        assert manager.hasParameter("@",
                                    perfect_match=True,
                                    local_param=True,
                                    explore_other_scope=False)

        assert manager.hasParameter("?",
                                    perfect_match=True,
                                    local_param=True,
                                    explore_other_scope=False)

        assert manager.hasParameter("!",
                                    perfect_match=True,
                                    local_param=True,
                                    explore_other_scope=False)

        assert manager.hasParameter("$",
                                    perfect_match=True,
                                    local_param=True,
                                    explore_other_scope=False)

        dico = {}

        dico["*"] = manager.getParameter("*",
                                         perfect_match=True,
                                         local_param=True,
                                         explore_other_scope=False)

        dico["#"] = manager.getParameter("#",
                                         perfect_match=True,
                                         local_param=True,
                                         explore_other_scope=False)

        dico["@"] = manager.getParameter("@",
                                         perfect_match=True,
                                         local_param=True,
                                         explore_other_scope=False)

        dico["?"] = manager.getParameter("?",
                                         perfect_match=True,
                                         local_param=True,
                                         explore_other_scope=False)

        dico["!"] = manager.getParameter("!",
                                         perfect_match=True,
                                         local_param=True,
                                         explore_other_scope=False)

        dico["$"] = manager.getParameter("$",
                                         perfect_match=True,
                                         local_param=True,
                                         explore_other_scope=False)

        return dico

    def test_noneContainer(self):
        with pytest.raises(ParameterException):
            setArgs(container=None)

    def test_notIterableArgs(self):
        container = ParentManager()
        with pytest.raises(ParameterException):
            setArgs(container=container, args=52)

    def test_noneArgs(self):
        container = ParentManager()
        setArgs(container=container, args=None)
        manager = container.getVariableManager()
        dico = self.getParams(manager)

        assert dico['*'].getValue() == ['']
        assert dico['#'].getValue() == ['0']
        assert dico['@'].getValue() == []
        assert dico['?'].getValue() == []
        assert dico['!'].getValue() == ['']
        assert dico['$'].getValue() == [str(container.getCurrentId())]

    def test_emptyArgs(self):
        container = ParentManager()
        setArgs(container=container, args=())
        manager = container.getVariableManager()
        dico = self.getParams(manager)

        assert dico['*'].getValue() == ['']
        assert dico['#'].getValue() == ['0']
        assert dico['@'].getValue() == []
        assert dico['?'].getValue() == []
        assert dico['!'].getValue() == ['']
        assert dico['$'].getValue() == [str(container.getCurrentId())]

    def test_singleArg(self):
        container = ParentManager()
        setArgs(container=container, args=('toto',))
        manager = container.getVariableManager()
        dico = self.getParams(manager)

        assert dico['*'].getValue() == ['toto']
        assert dico['#'].getValue() == ['1']
        assert dico['@'].getValue() == ['toto']
        assert dico['?'].getValue() == []
        assert dico['!'].getValue() == ['']
        assert dico['$'].getValue() == [str(container.getCurrentId())]

    def test_multipleArgs(self):
        container = ParentManager()
        setArgs(container=container, args=('toto', 'titi', 'tata',))
        manager = container.getVariableManager()
        dico = self.getParams(manager)

        assert dico['*'].getValue() == ['toto titi tata']
        assert dico['#'].getValue() == ['3']
        assert dico['@'].getValue() == ['toto', 'titi', 'tata']
        assert dico['?'].getValue() == []
        assert dico['!'].getValue() == ['']
        assert dico['$'].getValue() == [str(container.getCurrentId())]

    def test_multipleArgsWithDifferentType(self):
        container = ParentManager()
        setArgs(container=container, args=('toto', 23, True, 42.569,))
        manager = container.getVariableManager()
        dico = self.getParams(manager)

        assert dico['*'].getValue() == ['toto 23 True 42.569']
        assert dico['#'].getValue() == ['4']
        assert dico['@'].getValue() == ['toto', '23', 'True', '42.569']
        assert dico['?'].getValue() == []
        assert dico['!'].getValue() == ['']
        assert dico['$'].getValue() == [str(container.getCurrentId())]
