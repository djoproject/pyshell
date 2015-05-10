#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from pyshell.utils.synchronized import synchronous
from threading import Lock

class SynchronizedTester(object):
    def __init__(self):
        self._internalLock = Lock()

    @synchronous()
    def tester(self):
        return 42

class SynchronizedTest(unittest.TestCase):
    def test_Synchronized1(self):#test synchronized, simple execution test without other thread
        st = SynchronizedTester()
        self.assertEqual(st.tester(), 42)

if __name__ == '__main__':
    unittest.main()