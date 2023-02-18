#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Handle persistent configuration data and make available to the program.
"""

import json
import os
import threading
import uuid

MASTER_FILENAME = "~/.trashbin-master.json"

def create_blank_file(filename):
    with open(filename, 'w') as outfile:
        json.dump({'__uuid': str(uuid.uuid4())}, outfile, indent=4)


class ConfigManager(object):

    def __init__(self, master=MASTER_FILENAME):
        self._master_config = Configuration(master, False, False)
        self.slots = []

        assert 'slots' in self._master_config, "Master config file contains " \
                "no slot information!"

        for slot in self._master_config['slots']:
            self.load_new_config_from_file(slot['filename'], slot['readonly'])

    def load_new_config_from_file(self, filename, readonly=False,
            permanent=True):
        newfilename = os.path.abspath(os.path.expanduser(filename))
        config = Configuration(filename=newfilename, readonly=readonly)

        # make sure it's not a duplicate
        for slot in self.slots:
           if slot['__uuid'] == config['__uuid']:
               print("HIT")
               return

        self.slots.append(config)
        if permanent:
            # we've made sure it's not a duplicate in self.slots, but now we
            # also need to make sure it's not a duplicate in the master config
            # backend
            for slot in self._master_config['slots']:
                if slot['uuid'] == config['__uuid']:
                    return
            self._master_config['slots'].append({
                'uuid': config['__uuid'],
                'filename': newfilename,
                'readonly': readonly})
            self._master_config.save()

    def remove_config_from_slots(self, cfg, permanent=True):
        if not (cfg in self.slots):
            print("WARNING: Attempting to remove a config item not in a slot.")
            return

        idx = self.slots.index(cfg)
        self.slots.pop(idx)

        if permanent:
            self._master_config['slots'].pop(idx)
            self._master_config.save()

    def __contains__(self, item):
        for config in self.slots:
            if item in config:
                return True
        return False

    def __getitem__(self, item):
        for config in self.slots:
            if item in config:
                return config[item]
        return None

    def __setitem__(self, item, val):
        nset = 0
        for config in self.slots:
            if item in config:
                nset += 1
                config[item] = val
        if nset == 0:
            raise ValueError("{} not present in any slot, cannot set!".format(
                item))

    def __delitem__(self, item):
        for config in self.slots:
            if item in config:
                del config[item]

    @property
    def slotfilenames(self):
        files = []
        for config in self.slots:
            files.append(os.path.split(config.filename)[1])
        return files


class Configuration(object):

    def __init__(self, filename, readonly=False, uid=None):
        self._filename = os.path.abspath(os.path.expanduser(filename))
        self._readonly = readonly
        self.uuid = uid
        if self.uuid is None:
            self.uuid = str(uuid.uuid4())

        exist = os.path.exists(self._filename)
        if not exist:
            print("WARNING: No configuration file found at {}.  Creating one!" \
                    .format(self._filename))
            create_blank_file(self._filename)

        self._data = {}
        self._datalock = threading.Lock()
        self._filelock = threading.Lock()
        self._update_data_from_file()

        if 'debug' in self and self['debug']:
            print("Configuration file has been read")

    @property
    def filename(self):
        return self._filename

    def change_file(self, newname):
        if self._readonly:
            raise AttributeError("Attempted to change filepath to a readonly" \
                    "configuration object!")
        newname = os.path.abspath(os.path.expanduser(newname))
        self._filename = newname
        self._flush_data_to_file()

    def _update_data_from_file(self):
        self._datalock.acquire()
        self._filelock.acquire()
        self._data = {}
        with open(self._filename, 'r') as datafile:
            string = datafile.read()
        self._data = json.loads(string)
        self._filelock.release()
        self._datalock.release()

    def _flush_data_to_file(self):
        if self._readonly:
            raise AttributeError("Attempted to flush to file on a readonly" \
                    "configuration object!")
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
        if self._readonly:
            raise AttributeError("Attempted to assign value to a readonly" \
                    "configuration object!")
        self._datalock.acquire()
        self._data[item] = value
        self._datalock.release()

    def __delitem__(self, key):
        if self._readonly:
            raise AttributeError("Attempted to delete a value from readonly" \
                    "configuration object!")
        self._datalock.acquire()
        del self._data[key]
        self._datalock.release()

    def __contains__(self, item):
        self._datalock.acquire()
        cont = item in self._data
        self._datalock.release()
        return cont

    def items(self):
        return list(self._data.items())

    def data(self):
        return self._data

    def save(self):
        self._flush_data_to_file()

    def load(self):
        self._update_data_from_file()


