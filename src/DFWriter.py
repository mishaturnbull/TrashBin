#!/usr/bin/env python3

"""
APM DataFlash log file writer.

Mean to to precisely undo the actions of DFReader.py.

Heavily based on DFReader.py - thanks to all who contributed to it!
"""

import array
import math
import sys
import struct
import os

from . import mavutil
from . import DFReader


class DFWriter(object):
    """
    Write a generic log file
    """
    def __init__(self, messages, filename):
        self.all_messages = messages
        self._msg_idx = 0
        self.filehandle = None
        self.filename = filename
        self.is_done = False

        self.open_file()
        self.write_all_log()
        self.close_file()

    def write_all_log(self):
        while not self.is_done:
            self.write_next_message()
            self.check_done()

    def check_done(self):
        self.is_done = (self._msg_idx >= len(self.all_messages)) or \
                (self.is_done) or \
                (self.all_messages[self._msg_idx] is None)
        return self.is_done

    def write_next_message(self):
        self.filehandle.write(self._gen_contents(self._msg_idx))
        self._msg_idx += 1

    def _gen_contents(self, message_idx):
        raise NotImplemented("Can't use generic DFWriter to actually write")

    def open_file(self):
        if os.path.exists(self.filename):
            raise FileExistsError("File exists")
        self._open_file()

    def _open_file(self):
        raise NotImplemented("Can't use generic DFWriter to actually write")

    def close_file(self):
        assert self.filehandle != None, "Never opened file!"
        self.filehandle.close()

class DFWriter_text(DFWriter):
    """
    Write a text
    """
    def _gen_contents(self, message_idx):
        msg = self.all_messages[message_idx]
        parts = [msg.get_type()]
        d = msg.to_dict()
        for col in msg.fmt.columns:
            parts.append(str(d[col]))
        s = ','.join(parts) + '\n'
        return s

    def _open_file(self):
        self.filehandle = open(self.filename, 'w')

if __name__ == '__main__':
    import src.DFReader as dfr
    infile = sys.argv[1]
    assert infile.endswith(".bin"), "File input needs to be binary!"
    inlog = dfr.DFReader_binary(infile)
    while True:
        _ = inlog.recv_msg()
        if _ is None:
            break
    DFWriter_text(inlog.all_messages, infile + '.log')

