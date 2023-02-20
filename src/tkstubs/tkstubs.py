#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Provides stubs for Tkinter variables if running in a non-graphical environment.
"""

import os

def has_display():
    disp = os.getenv('DISPLAY')
    try:
        return len(disp) > 0
    except TypeError:
        return False


class Variable(object):

    def __init__(self, val=None, *args):
        self.val = val
        self.args = args

    def get(self):
        return self.val

    def set(self, val):
        self.val = val

def _classbuilder(typ):
    class TypeStrictVar(Variable):
        def set(self, val):
            assert isinstance(val, typ), "Tried to assign wrong type to " \
                    "variable expecting {}: {}".format(typ, val)
            super().set(val)
    return TypeStrictVar

IntVar = _classbuilder(int)
StringVar = _classbuilder(str)
BooleanVar = _classbuilder(bool)



