#!/usr/env/python3
# -*- coding: utf-8 -*-

import sys
import os

def _has_display():
    disp = os.getenv('DISPLAY')
    try:
        return len(disp) > 0
    except TypeError:
        return False

HAS_DISPLAY = _has_display()

def tb_override_tkinter(opermode):
    if (not HAS_DISPLAY) or ('headless' in opermode):
        me = os.path.abspath(os.path.expanduser(__file__))
        fldr = os.path.split(me)[0]
        sys.path.insert(1, fldr)

