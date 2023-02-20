#!/usr/env/python3
# -*- coding: utf-8 -*-

import os
import sys

def _has_display():
    if 'headless' in os.getenv('_TRASHBIN_OPERMODE'):
        return False
    disp = os.getenv('DISPLAY')
    try:
        return len(disp) > 0
    except TypeError:
        return False

HAS_DISPLAY = _has_display()

def tb_override_tkinter():
    if not HAS_DISPLAY:
        me = os.path.abspath(os.path.expanduser(__file__))
        fldr = os.path.split(me)[0]
        print(fldr)
        sys.path.insert(1, fldr)

