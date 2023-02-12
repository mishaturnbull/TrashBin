#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Handle persistent configuration data and make available to the program.
"""

import json
import os
import threading

DEFAULT_FILENAME = "~/.trashbin.cfg"

def create_blank_file(filename):
    with open(filename, 'w') as outfile:
        json.dump({}, outfile, indent=4)

class Configuration(object):

    def __init__(self, filename=DEFAULT_FILENAME, readonly=False):
        self._filename = os.path.abspath(os.path.expanduser(filename))
        self._readonly = readonly

        exist = os.path.exists(self._filename)
        if not exist:
            print("WARNING: No configuration file found at {}.  Creating one!" \
                    .format(self._filename))
            create_blank_file(self._filename)

        self._data = {}
        self._datalock = threading.Lock()
        self._filelock = threading.Lock()
        self._update_data_from_file()

    def change_file(self, newname):
        newname = os.path.abspath(os.path.expanduser(newname))
        self._filename = newname
        self._flush_data_to_file()

    def _update_data_from_file(self):
        self._datalock.acquire()
        self._filelock.acquire()
        with open(self._filename, 'r') as datafile:
            string = datafile.read()
        self._data = json.loads(string)
        self._filelock.release()
        self._datalock.release()

    def _flush_data_to_file(self):
        self._datalock.acquire()
        self._filelock.acquire()
        with open(self._filename, 'w') as datafile:
            json.dump(self._data, datafile, indent=4)
        self._filelock.release()
        self._datalock.release()

    def __getitem__(self, item):
        self._datalock.acquire()
        value = self._data[item]
        self._datalock.release()
        return value

    def __setitem__(self, item, value):
        self._datalock.acquire()
        self._data[item] = value
        self._datalock.release()

    def __delitem__(self, key):
        self._datalock.acquire()
        del self._data[key]
        self._datalock.release()

    def __contains__(self, item):
        self._datalock.acquire()
        cont = item in self._data
        self._datalock.release()
        return cont

    def save(self):
        self._flush_data_to_file()

    def load(self):
        self._update_data_from_file()


