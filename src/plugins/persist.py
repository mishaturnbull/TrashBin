#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Classes & functions used in the saving and loading of .tbp and .tbpz files for
plugin savestates.
"""

import json
import zipfile
import src.plugins._plugin_autodetect as _pad

ZIP_INTERNAL_FILENAME = "data.tbp"

def get_all_savestates(factories):
    states = []
    for factory in factories:
        states.append(factory._export_savestate())
    return states

def _auto_find_fact_cls(state):
    available_facts = _pad.plugin_list()[1]
    for factory in available_facts:
        if factory.__name__ == state['plugin_cls']:
            return factory

def load_all_savestates(states, handler):
    factories = []
    for state in states:
        if handler.debug.get():
            print("Loading {}".format(state['plugin_cls']))
        cls = _auto_find_fact_cls(state)
        if cls is None:
            print("Could not find plugin {}".format(state['plugin_name']))
            continue
        inst = cls(handler)
        inst._load_savestate(state, handler)
        factories.append(inst)
    return factories

def write_text_file(filename, factories):
    with open(filename, 'w') as outfile:
        json.dump(get_all_savestates(factories), outfile, indent=4)

def load_text_file(filename, handler):
    with open(filename, 'r') as infile:
        string = infile.read()
    savestates = json.loads(string)
    return load_all_savestates(savestates, handler)

def write_zip_file(filename, factories):
    with zipfile.ZipFile(filename, 'w') as ziph:
        ziph.writestr(ZIP_INTERNAL_FILENAME,
            json.dumps(get_all_savestates(factories)))

def load_zip_file(filename, handler):
    with zipfile.ZipFile(filename, 'r') as ziph:
        data = ziph.read(ZIP_INTERNAL_FILENAME)
    savestates = json.loads(data)
    return load_all_savestates(savestates, handler)


