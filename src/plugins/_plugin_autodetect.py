#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Automatically detect other plugins dropped into this folder and provide them in
a list.
"""

import os
import importlib

_KNOWN_FILES = [
        "_plugin_autodetect.py",
        "pluginbase.py",
        "__init__.py",
        "__pycache__.py",
    ]
# whether to skip modules starting with an '_'
_BLOCK_PRIVATE_MODS = True

def check_if_module_is_import(filename):
    if not filename.endswith(".py"):
        return False, "Must be Python file to import!"
    modname = os.path.splitext(filename)[0]
    try:
        mod = importlib.import_module(modname)
    except ImportError as ie:
        return False, "No module found!"
    except Exception as e:
        return False, e.message

def find_plugins_dir(startdir='.'):
    startlist = os.listdir(startdir)
    if '.git' in startlist:
        # we're in top level folder
        return 'src/plugins'
    elif 'plugins' in startlist:
        # we're in the src folder
        return 'plugins'
    elif 'pluginbase' in startlist:
        # we're in plugin folder
        return '.'
    elif 'TrashBin' in startlist:
        # we're above the module --- won't something else break here??
        # well, it won't be this function
        return 'TrashBin/src/plugins'
    else:
        # ok, no idea where we are, and not much chance of finding out
        raise FileNotFoundError("I can't find the plugin directory!")

def recursive_list_of_files(startdir='.'):
    files = os.listdir(startdir)
    print("Starting recurse {}".format(startdir))
    subdirs = []
    for f in files:
        if os.path.isdir(os.path.join(startdir, f)):
            subdirs.append(f)
            files.remove(f)
    for subdir in subdirs:
        subfiles = recursive_list_of_files(os.path.join(startdir, subdir))
        for subfile in subfiles:
            files.append(os.path.join(subdir, subfile))
    print("Recursed {}: {}".format(startdir, files))
    return files

def list_of_importable_files():
    all_files = wanted_file_list()
    importable = []
    for f in all_files:
        if check_if_module_is_import(f):
            all_files.append(f)
    return importable

def wanted_file_list():
    available = recursive_list_of_files(find_plugins_dir())
    wanted = []
    for f in available:
        fname = os.path.split(f)[-1]
        if not f.endswith('.py'):
            continue
        if _BLOCK_PRIVATE_MODS and fname.startswith('_'):
            continue
        if fname in _KNOWN_FILES:
            continue
        wanted.append(f)
    return wanted

def plugin_list():
    modules = []
    for plugin in wanted_file_list():
        filename = os.path.join(find_plugins_dir(), plugin)[:-3]
        modname = filename.replace('/', '.')
        modules.append(importlib.import_module(modname))
    return modules

