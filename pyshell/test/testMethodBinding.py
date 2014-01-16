#!/usr/bin/python
# -*- coding: utf-8 -*-

class a(object):
    def plop(self,a):
        return a
        
    def execute_a(self,a):
        return self.plop(a)
        
class b(object):
    def k(self,b):
        return b*5
        
ib = b()
ia = a()
ia.plop = ib.k
print ia.execute_a(5)
