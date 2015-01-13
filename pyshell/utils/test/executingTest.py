#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.utils.executing import Parser

class ParserTest(unittest.TestCase):
    def setUp(self):
        pass
        
    def test_simple(self):
        p = Parser("abc def ghi")
        p.parse()
        self.assertEqual(p.commandList,[['abc', 'def', 'ghi']])
        
    def test_simplePipe(self):
        p = Parser("abc def ghi | jkl mno pqr")
        p.parse()
        self.assertEqual(p.commandList,[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr']])
        
    #TODO more test
        
if __name__ == '__main__':
    unittest.main()
