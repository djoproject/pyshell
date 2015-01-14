#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from pyshell.utils.executing import Parser

class ParserTest(unittest.TestCase):
    def setUp(self):
        pass
    
    ####### ONE COMMAND ######

    def test_singleCommand1(self):
        p = Parser("abc def ghi")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi']])

    def test_singleCommand2(self):
        p = Parser("abc def ghi | ")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi']])

    def test_singleCommand3(self):
        p = Parser("abc def ghi | |")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi']])

    def test_singleCommand4(self):
        p = Parser("abc def ghi | ||")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi']])

    def test_singleCommand5(self):
        p = Parser("|abc def ghi")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi']])

    def test_singleCommand6(self):
        p = Parser("| |abc def ghi")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi']])

    def test_singleCommand7(self):
        p = Parser("||| abc def ghi ")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi']])

    #### TWO COMMAND ####
        
    def test_multipleCommand1(self):
        p = Parser("abc def ghi | jkl mno pqr")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr']])

    def test_multipleCommand2(self):
        p = Parser("| |abc def ghi | jkl mno pqr|")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr']])

    def test_multipleCommand3(self):
        p = Parser("abc def ghi | jkl mno pqr|")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr']])

    def test_multipleCommand4(self):
        p = Parser("abc def ghi | jkl mno pqr| |")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr']])

    def test_multipleCommand5(self):
        p = Parser("abc def ghi || jkl mno pqr")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr']])

    def test_multipleCommand6(self):
        p = Parser("abc def ghi | | | jkl mno pqr")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr']])

    def test_multipleCommand7(self):
        p = Parser("| abc def ghi | jkl mno pqr|")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr']])

    def test_multipleCommand8(self):
        p = Parser("||abc def ghi | jkl mno pqr| |")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr']])
        
    ##### THREE COMMAND ######
    def test_multipleCommand9(self):
        p = Parser("abc def ghi | jkl mno pqr | stu vwx yz")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr'], ["stu","vwx","yz"]])

    def test_multipleCommand10(self):
        p = Parser("|||abc def ghi |||| jkl mno pqr |||| stu vwx yz|||")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr'], ["stu","vwx","yz"]])

    def test_multipleCommand11(self):
        p = Parser("abc def ghi ||| jkl mno pqr ||| stu vwx yz")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr'], ["stu","vwx","yz"]])

    def test_multipleCommand12(self):
        p = Parser("||||abc def ghi | jkl mno pqr | stu vwx yz")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr'], ["stu","vwx","yz"]])

    def test_multipleCommand13(self):
        p = Parser("abc def ghi | jkl mno pqr | stu vwx yz|||")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr'], ["stu","vwx","yz"]])

    def test_multipleCommand14(self):
        p = Parser("abc def ghi | jkl mno pqr |||| stu vwx yz")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr'], ["stu","vwx","yz"]])

    def test_multipleCommand15(self):
        p = Parser("abc def ghi |||| jkl mno pqr | stu vwx yz")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr'], ["stu","vwx","yz"]])

    def test_multipleCommand16(self):
        p = Parser("|||abc def ghi | jkl mno pqr | stu vwx yz|")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr'], ["stu","vwx","yz"]])

    def test_multipleCommand17(self):
        p = Parser("|abc def ghi | jkl mno pqr | stu vwx yz|")
        p.parse()
        self.assertEqual(p.getCommandList(),[['abc', 'def', 'ghi'], ['jkl', 'mno', 'pqr'], ["stu","vwx","yz"]])


    ##### ESCAPE CHAR ########

    ##### WRAPPED AREA #######
        
if __name__ == '__main__':
    unittest.main()
