#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Handle persistent configuration data and make available to the program.
"""

import json
import os
import threading
import uuid
import zipfile
import traceback

ZIP_INTERNAL_FILENAME = "data.json"

SCOPE_GLOBAL = 1
SCOPE_PLUGIN = 2
SCOPE_INPUTS = 3
_SCOPE_AUTO = -1

def create_blank_file(filename, zipped=False):
    data = {'__uuid': str(uuid.uuid4()),
            '__scope': SCOPE_GLOBAL}
    if zipped:
        with zipfile.ZipFile(filename, 'w') as ziph:
            ziph.writestr(ZIP_INTERNAL_FILENAME,
                    json.dumps(data))
    else:
        with open(filename, 'w') as datafile:
            json.dump(data, datafile, indent=4)


class ConfigManager(object):

    __instance = None

    def __new__(cls, master):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)

        return cls.__instance

    def __init__(self, master):
        if hasattr(self, "_init_called"):
            # __init__ has already been called on this instance
            return
        # __init__ has not been called here, flag it for the next time
        self._init_called = True

        self._master_config = Configuration(master, False, False)
        self.slots = []

        if 'slots' not in self._master_config:
            self._master_config['slots'] = []
            self._master_config.save()

        for slot in self._master_config['slots']:
            self.load_new_config_from_file(slot['filename'], slot['readonly'])

    def load_new_config_from_file(self, filename, readonly=False,
            permanent=True, scope=_SCOPE_AUTO):
        newfilename = os.path.abspath(os.path.expanduser(filename))
        config = Configuration(filename=newfilename, readonly=readonly)

        # make sure it's not a duplicate
        for slot in self.slots:
           if slot['__uuid'] == config['__uuid']:
               print("WARNING: Trying to load config already present as new." \
                       "  Not re-adding, and triggering config reload " \
                       "instead!")
               slot.load()
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
            if config.filename:
                files.append(os.path.split(config.filename)[1])
        return files

    def get_configs_in_scope(self, scope):
        outs = []
        for config in self.slots:
            if config['__scope'] == scope:
                outs.append(config)
        return outs

    @property
    def plugins(self):
        confs = self.get_configs_in_scope(SCOPE_PLUGIN)
        assert len(confs) <= 1, "Cannot have more than one plugin " \
                "configuration loaded, got {}".format(len(confs))
        if len(confs) > 0:
            return confs[0]
        return None

    @property
    def inputs(self):
        confs = self.get_configs_in_scope(SCOPE_INPUTS)
        assert len(confs) <= 1, "Cannot have more than one input " \
                "configuration loaded, got {}".format(len(confs))
        if len(confs) > 0:
            return confs[0]
        return None

class Configuration(object):

    def __init__(self, filename, readonly=False, uid=None, zipped=False):
        if not (filename is None):
            self._filename = os.path.abspath(os.path.expanduser(filename))
        else:
            print("WARNING: Anonymous config created!")
            traceback.print_stack()
            print("="*40)
            self._filename = None
        self._readonly = readonly
        self.zipped = zipped
        self.uuid = uid
        if self.uuid is None:
            self.uuid = str(uuid.uuid4())
        self._data = {}
        self._datalock = threading.Lock()
        self._filelock = threading.Lock()

        if self._filename is None:
            return

        exist = os.path.exists(self._filename)
        if not exist:
            print("WARNING: No configuration file found at {}.  Creating one!" \
                    .format(self._filename))
            create_blank_file(self._filename, self.zipped)
        else:
            # make sure the zipped argument matches the file
            iszip = zipfile.is_zipfile(self._filename)
            if iszip != self.zipped:
                print("WARNING: Incorrect `zipped` specified for {}." \
                        "Updating it to match!".format(self._filename))
                self.zipped = iszip

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
        if self._filename is None:
            raise FileNotFoundError("No file backend for this configuration!")

        self._datalock.acquire()
        self._filelock.acquire()

        self._data = {}
        if self.zipped:
            with zipfile.ZipFile(self._filename, 'r') as ziph:
                strdata = ziph.read(ZIP_INTERNAL_FILENAME)
        else:
            with open(self._filename, 'r') as datafile:
                strdata = datafile.read()
        self._data = json.loads(strdata)

        self._filelock.release()
        self._datalock.release()

    def _flush_data_to_file(self):
        if self._filename is None:
            raise FileNotFoundError("No file backend for this configuration!")
        if self._readonly:
            raise AttributeError("Attempted to flush to file on a readonly" \
                    "configuration object!")

        self._datalock.acquire()
        self._filelock.acquire()

        if self.zipped:
            with zipfile.ZipFile(self._filename, 'w') as ziph:
                ziph.writestr(ZIP_INTERNAL_FILENAME,
                        json.dumps(self._data))
        else:
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

    def overridedata(self, newdata):
        self._datalock.acquire()
        newdata['__uuid'] = self._data['__uuid']
        self._data = newdata
        self._datalock.release()

    def save(self):
        self._flush_data_to_file()

    def load(self):
        self._update_data_from_file()

if __name__ == '__main__':
    import code
    code.interact(local=locals())

