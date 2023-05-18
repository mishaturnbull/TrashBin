#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Classes & functions used in the saving and loading of .tbp and .tbpz files for
plugin savestates.
"""

import json
import zipfile
from src.plugins import _plugin_autodetect as _pad
import src.config.config as config

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
        if handler.config['debug']:
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
    cfg = config.Configuration(filename, zipped=False)
    cfg.overridedata({
        "__scope": config.SCOPE_PLUGIN,
        "factories": get_all_savestates(factories),
        })
    cfg.save()

def load_text_file(filename, handler):
    cfg = config.Configuration(filename, zipped=False)
    savestates = cfg.data()
    assert cfg['__scope'] == config.SCOPE_PLUGIN, "Not a plugin config!"
    return load_all_savestates(savestates['factories'], handler)

def write_zip_file(filename, factories):
    cfg = config.Configuration(filename, zipped=True)
    cfg.overridedata(get_all_savestates(factories))
    cfg.save()

def load_zip_file(filename, handler):
    cfg = config.Configuration(filename, zipped=True)
    savestates = cfg.data()
    return load_all_savestates(savestates, handler)


