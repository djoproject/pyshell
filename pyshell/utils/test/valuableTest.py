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
from pyshell.utils.valuable import Valuable, SelectableValuable, DefaultValuable, SimpleValuable

#README these tests could look stupid but it is very important for the whole application that these four class respect drasticaly this structure

class ValuableTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_valuable(self):
        v = Valuable()
        self.assertTrue(hasattr(v,"getValue"))
        self.assertTrue(hasattr(v.getValue, "__call__"))
        self.assertEqual(v.getValue(), None)
        
    def test_selectableValuable(self):
        sv = SelectableValuable()
        
        self.assertTrue(hasattr(sv,"getValue"))
        self.assertTrue(hasattr(sv.getValue, "__call__"))
        self.assertEqual(sv.getValue(), None)
        
        self.assertTrue(hasattr(sv,"getSelectedValue"))
        self.assertTrue(hasattr(sv.getSelectedValue, "__call__"))
        self.assertEqual(sv.getSelectedValue(), None)
        
    def test_defaultValuable(self):
        d = DefaultValuable("plop")
        
        self.assertTrue(hasattr(d,"getValue"))
        self.assertTrue(hasattr(d.getValue, "__call__"))
        self.assertEqual(d.getValue(), "plop")
        
        self.assertTrue(hasattr(d,"getSelectedValue"))
        self.assertTrue(hasattr(d.getSelectedValue, "__call__"))
        self.assertEqual(d.getSelectedValue(), "plop")
        
    def test_simpleValuable(self):
        sv = SimpleValuable(42)
        
        self.assertTrue(hasattr(sv,"getValue"))
        self.assertTrue(hasattr(sv.getValue, "__call__"))
        self.assertEqual(sv.getValue(), 42)
        
        self.assertTrue(hasattr(sv,"getSelectedValue"))
        self.assertTrue(hasattr(sv.getSelectedValue, "__call__"))
        self.assertEqual(sv.getSelectedValue(), 42)
        
        self.assertEqual(sv.setValue(23),23)
        self.assertEqual(sv.getValue(), 23)
        self.assertEqual(sv.getSelectedValue(), 23)
        
if __name__ == '__main__':
    unittest.main()
