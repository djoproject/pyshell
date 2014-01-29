#!/usr/bin/python
# -*- coding: utf-8 -*-

import inspect

def dec():
    #define decorator method
    def decorator(fun):
        frames = inspect.stack()
        #print frames
        defined_in_class = False
        if len(frames) > 2:
            maybe_class_frame = frames[2]
            #print maybe_class_frame
            statement_list = maybe_class_frame[4]
            #print statement_list
            first_statment = statement_list[0]
            #print first_statment
            if first_statment.strip().startswith('class '):
                defined_in_class = True
        
        print "A",type(fun), (len(frames) > 2 and frames[2][4][0].strip().startswith('class '))
        
        return fun
        
    return decorator

class a(object):
    #default preProcess
    
    @dec()
    @staticmethod
    def b(self,args):
        return args

    print "B",type(b)
    
@dec()
def toto():
    pass

print "C",type(a.b)

def toto(self):
    print self


toto("ttt")
