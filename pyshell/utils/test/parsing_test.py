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

from pyshell.utils.parsing import Parser, escapeString


class TestParser(object):

    # ###### ONE COMMAND ##### #

    def test_singleCommand1(self):
        p = Parser("abc def ghi")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),)]

    def test_singleCommand2(self):
        p = Parser("abc def ghi | ")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),)]

    def test_singleCommand3(self):
        p = Parser("abc def ghi | |")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),)]

    def test_singleCommand4(self):
        p = Parser("abc def ghi | ||")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),)]

    def test_singleCommand5(self):
        p = Parser("|abc def ghi")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),)]

    def test_singleCommand6(self):
        p = Parser("| |abc def ghi")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),)]

    def test_singleCommand7(self):
        p = Parser("||| abc def ghi ")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),)]

    # ### TWO COMMAND ### #

    def test_multipleCommand1(self):
        p = Parser("abc def ghi | jkl mno pqr")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),)]

    def test_multipleCommand2(self):
        p = Parser("| |abc def ghi | jkl mno pqr|")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),)]

    def test_multipleCommand3(self):
        p = Parser("abc def ghi | jkl mno pqr|")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),)]

    def test_multipleCommand4(self):
        p = Parser("abc def ghi | jkl mno pqr| |")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),)]

    def test_multipleCommand5(self):
        p = Parser("abc def ghi || jkl mno pqr")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),)]

    def test_multipleCommand6(self):
        p = Parser("abc def ghi | | | jkl mno pqr")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),)]

    def test_multipleCommand7(self):
        p = Parser("| abc def ghi | jkl mno pqr|")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),)]

    def test_multipleCommand8(self):
        p = Parser("||abc def ghi | jkl mno pqr| |")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),)]

    # #### THREE COMMAND ##### #

    def test_multipleCommand9(self):
        p = Parser("abc def ghi | jkl mno pqr | stu vwx yz")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),),
                     (("stu", "vwx", "yz"), (), (),)]

    def test_multipleCommand10(self):
        p = Parser("|||abc def ghi |||| jkl mno pqr |||| stu vwx yz|||")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),),
                     (("stu", "vwx", "yz"), (), (),)]

    def test_multipleCommand11(self):
        p = Parser("abc def ghi ||| jkl mno pqr ||| stu vwx yz")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),), ((
            'jkl', 'mno', 'pqr'), (), (),), (("stu", "vwx", "yz"), (), (),)]

    def test_multipleCommand12(self):
        p = Parser("||||abc def ghi | jkl mno pqr | stu vwx yz")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),),
                     (("stu", "vwx", "yz"), (), (),)]

    def test_multipleCommand13(self):
        p = Parser("abc def ghi | jkl mno pqr | stu vwx yz|||")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),),
                     (("stu", "vwx", "yz"), (), (),)]

    def test_multipleCommand14(self):
        p = Parser("abc def ghi | jkl mno pqr |||| stu vwx yz")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),),
                     (("stu", "vwx", "yz"), (), (),)]

    def test_multipleCommand15(self):
        p = Parser("abc def ghi |||| jkl mno pqr | stu vwx yz")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),),
                     (("stu", "vwx", "yz"), (), (),)]

    def test_multipleCommand16(self):
        p = Parser("|||abc def ghi | jkl mno pqr | stu vwx yz|")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),),
                     (("stu", "vwx", "yz"), (), (),)]

    def test_multipleCommand17(self):
        p = Parser("|abc def ghi | jkl mno pqr | stu vwx yz|")
        p.parse()
        assert p == [(('abc', 'def', 'ghi'), (), (),),
                     (('jkl', 'mno', 'pqr'), (), (),),
                     (("stu", "vwx", "yz"), (), (),)]

    # #### WRAPPED AREA ###### #

    def test_wrapped1(self):
        p = Parser("aa \"$ | \"")
        p.parse()
        assert p == [(('aa', '$ | ',), (), (),)]

    def test_wrapped2(self):
        p = Parser("aa\"$ | \"")
        p.parse()
        assert p == [(('aa$ | ',), (), (),)]

    def test_wrapped3(self):
        p = Parser("aa\\\"$ | \"")
        p.parse()
        assert p == [(('aa"$',), (), (),)]

    def test_wrapped4(self):
        p = Parser("aa\"$ | \"bb")
        p.parse()
        assert p == [(('aa$ | bb',), (), (),)]

    # #### ESCAPE CHAR ####### #

    def test_escape1(self):
        p = Parser("a\|")
        p.parse()
        assert p == [(('a|',), (), (),)]

    def test_escape2(self):
        p = Parser("a\|bc\de\\\\ plip| plop")
        p.parse()
        assert p == [(('a|bcde\\', 'plip',), (), (),), (('plop',), (), (),)]

    # ### VAR CHAR ### #

    def test_var1(self):
        p = Parser("aa bb cc $\\d")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '$d',), (3,), (),)]

    def test_var2(self):
        p = Parser("aa bb cc $d")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '$d',), (3,), (),)]

    def test_var3(self):
        p = Parser("aa bb cc \"$\\d\"")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '$d',), (3,), (),)]

    def test_var4(self):
        p = Parser("aa bb cc \"$d\"")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '$d',), (3,), (),)]

    def test_var5(self):
        p = Parser("aa bb cc \"$ d\"")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '$ d',), (), (),)]

    def test_var6(self):
        p = Parser("aa bb cc $\\ d")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '$ d',), (), (),)]

    def test_var7(self):
        p = Parser("aa bb cc \"$\"")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '$',), (), (),)]

    def test_var8(self):
        p = Parser("aa bb cc $")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '$',), (), (),)]

    # ### PARAM CHAR ### #

    def test_param1(self):
        p = Parser("aa bb cc -\\d")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '-d',), (), (3,),)]

    def test_param2(self):
        p = Parser("aa bb cc -d")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '-d',), (), (3,),)]

    def test_param3(self):
        p = Parser("aa bb cc \"-\\d\"")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '-d',), (), (3,),)]

    def test_param4(self):
        p = Parser("aa bb cc \"-d\"")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '-d',), (), (3,),)]

    def test_param5(self):
        p = Parser("aa bb cc \"- d\"")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '- d',), (), (),)]

    def test_param6(self):
        p = Parser("aa bb cc -\\ d")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '- d',), (), (),)]

    def test_param7(self):
        p = Parser("aa bb cc \"-\"")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '-',), (), (),)]

    def test_param8(self):
        p = Parser("aa bb cc -")
        p.parse()
        assert p == [(('aa', 'bb', 'cc', '-',), (), (),)]

    # ## BACKGROUND ## #

    def test_background1(self):
        p = Parser("")
        p.parse()
        assert not p.isToRunInBackground()

    def test_background2(self):
        p = Parser("&")
        p.parse()
        assert len(p) == 0
        assert p.isToRunInBackground()

    def test_background3(self):
        p = Parser("& | a")
        p.parse()
        assert len(p) == 2
        assert not p.isToRunInBackground()

    def test_background4(self):
        p = Parser("aaa&")
        p.parse()
        assert len(p) == 1
        assert p == [(('aaa',), (), (),)]
        assert p.isToRunInBackground()

    def test_background5(self):
        p = Parser("aaa &")
        p.parse()
        assert len(p) == 1
        assert p == [(('aaa',), (), (),)]
        assert p.isToRunInBackground()

    def test_background6(self):
        p = Parser("aaa bbb &")
        p.parse()
        assert len(p) == 1
        assert p == [(('aaa', 'bbb'), (), (),)]
        assert p.isToRunInBackground()

    def test_background7(self):
        p = Parser("aaa bbb&")
        p.parse()
        assert len(p) == 1
        assert p == [(('aaa', 'bbb'), (), (),)]
        assert p.isToRunInBackground()

    def test_background8(self):
        p = Parser("aaa bbb |&")
        p.parse()
        assert len(p) == 1
        assert p == [(('aaa', 'bbb'), (), (),)]
        assert p.isToRunInBackground()

    def test_background9(self):
        p = Parser("aaa bbb | ccc&")
        p.parse()
        assert len(p) == 2
        assert p == [(('aaa', 'bbb'), (), (),), (('ccc',), (), (),)]
        assert p.isToRunInBackground()

    def test_background10(self):
        p = Parser("aaa bbb| cdf &")
        p.parse()
        assert len(p) == 2
        assert p == [(('aaa', 'bbb'), (), (),), (('cdf',), (), (),)]
        assert p.isToRunInBackground()

    def test_background11(self):
        p = Parser("aaa bbb | ccc&c")
        p.parse()
        assert len(p) == 2
        assert p == [(('aaa', 'bbb'), (), (),), (('ccc&c',), (), (),)]
        assert not p.isToRunInBackground()

    # ## ESCAPING ## #

    def test_escaping1(self):
        original = "plop"
        s = escapeString(original)
        assert s == "\"plop\""
        p = Parser(s)
        p.parse()
        assert p == [((original,), (), (),)]

    def test_escaping2(self):
        original = "$p\"l$o\\p"
        s = escapeString(original)
        assert s == "\"\\$p\\\"l$o\\\\p\""
        p = Parser(s)
        p.parse()
        assert p == [((original,), (), (),)]

    def test_escaping3(self):
        original = "-a$b | cde\nfg\\hi& "
        s = escapeString(original, False)
        assert s == "\\-a\\$b\\ \\|\\ cde\\\nfg\\\\hi\\&\\ "
        p = Parser(s)
        p.parse()
        assert p == [((original,), (), (),)]
