#!/usr/bin/env python -t
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
from pyshell.utils.flushable import Flushable

#README these tests could look stupid but it is very important for the whole application that these four class respect drasticaly this structure

class FlushableTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_flushable(self):
        f = Flushable()
        self.assertTrue(hasattr(f,"flush"))
        self.assertTrue(hasattr(f.flush,"__call__"))
        self.assertEqual(f.flush(),None)
    
if __name__ == '__main__':
    unittest.main()
    
    
