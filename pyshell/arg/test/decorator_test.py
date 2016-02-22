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
from pyshell.arg.argchecker import DefaultValueChecker
from pyshell.arg.argfeeder import ArgFeeder
from pyshell.arg.decorator import FunAnalyser
from pyshell.arg.decorator import shellMethod
from pyshell.arg.exception import DecoratorException


class TestDecorator(object):

    def test_funAnalyzer(self):
        # init limit case
        with pytest.raises(DecoratorException):
            FunAnalyser(None)
        with pytest.raises(DecoratorException):
            FunAnalyser(52)
        with pytest.raises(DecoratorException):
            FunAnalyser("plop")

        # empty fun
        def toto():
            pass

        fa = FunAnalyser(toto)
        assert fa is not None
        assert fa.lendefault == 0
        with pytest.raises(DecoratorException):
            fa.hasDefault("plop")
        with pytest.raises(DecoratorException):
            fa.getDefault("plop")
        with pytest.raises(DecoratorException):
            fa.setCheckerDefault("plop", "plip")

        # non empty fun
        def toto(plop):
            pass

        fa = FunAnalyser(toto)
        assert fa is not None
        assert fa.lendefault == 0
        assert not fa.hasDefault("plop")
        with pytest.raises(DecoratorException):
            fa.getDefault("plop")
        assert fa.setCheckerDefault("plop", "plip") == "plip"

        # non empty fun
        def toto(plop="plap"):
            pass

        fa = FunAnalyser(toto)
        assert fa is not None
        assert fa.lendefault == 1
        assert fa.hasDefault("plop")
        assert fa.getDefault("plop") == "plap"
        assert fa.setCheckerDefault("plop",
                                    ArgChecker()).getDefaultValue() == "plap"

        def toto(a, plop="plap"):
            pass

        fa = FunAnalyser(toto)
        assert fa is not None
        assert fa.lendefault == 1
        assert fa.hasDefault("plop")
        assert fa.getDefault("plop") == "plap"
        assert fa.setCheckerDefault("plop",
                                    ArgChecker()).getDefaultValue() == "plap"

    def test_decorator(self):
        # try to send no argchecker in the list
        exception = False
        try:
            shellMethod(ghaaa="toto")
        except DecoratorException:
            exception = True
        assert exception

        exception = False
        try:
            shellMethod(ghaaa=ArgChecker())
        except DecoratorException:
            exception = True
        assert not exception

        # try to set two decorator on the same function
        exception = False
        try:
            @shellMethod(plop=ArgChecker())
            @shellMethod(plop=ArgChecker())
            def tete(plop="a"):
                pass
        except DecoratorException:
            exception = True
        assert exception

        # try to set two key with the same name
        # will be a python syntax error, no need to check

        # set arg checker on unexistant param
        exception = False
        try:
            @shellMethod(b=ArgChecker(), a=ArgChecker())
            def titi(a):
                pass
        except DecoratorException:
            exception = True
        assert exception

        # TODO try to not bind param without default value
        """exception = False
        try:
            @shellMethod()
            def tata(plop):
                pass
        except DecoratorException:
            exception = True
        self.assertTrue(exception)"""

        exception = False
        try:
            @shellMethod()
            def tyty(plop=5):
                pass
        except DecoratorException:
            exception = True
        assert not exception

        # make a test with class and self
        exception = False
        try:
            class Plop(object):

                @shellMethod()
                def toto(self):
                    pass
        except DecoratorException:
            exception = True
        assert not exception

        # faire des tests qui aboutissent et verifier les donnees generees
        @shellMethod(a=ArgChecker())
        def toto(a, b=5):
            pass

        assert isinstance(toto.checker, ArgFeeder)
        assert "a" in toto.checker.arg_type_list
        assert isinstance(toto.checker.arg_type_list["a"], ArgChecker)
        assert "b" in toto.checker.arg_type_list
        assert isinstance(toto.checker.arg_type_list["b"], DefaultValueChecker)
        k = list(toto.checker.arg_type_list.keys())
        assert k[0] == "a" and k[1] == "b"

        # TODO test with a class meth static
