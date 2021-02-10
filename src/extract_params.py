#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Extract parameters from a log file and write them to a specified .param file.
"""

import os

def get_text_to_write(log):
    """
    Given a log file, return the file contents of the output .param file.
    """
    params = log.params
    lines = []
    for key, val in params.items():
        lines.append("{},{}".format(key, str(val)))
    return '\n'.join(lines)

def write_out_file(text, filename, force=False):
    """
    Write contents to desired filename.  May be absolute or relative.
    """
    if os.path.exists(filename) and not force:
        return False
    

