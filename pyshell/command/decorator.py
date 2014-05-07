#!/usr/bin/python
# -*- coding: utf-8 -*-

#use to mark a command that is allowed to return None
def allowToReturnNone(enable=True):
    def decorator(fun):
        fun.allowToReturnNone = enable
        return fun
    return decorator
