#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Automatically detect other plugins dropped into this folder and provide them in
a list.
"""

import os
import glob
import importlib
from src.plugins import pluginbase as pb

_KNOWN_FILES = [
        "_plugin_autodetect.py",
        "pluginbase.py",
        "persist.py",
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
        return os.path.join('src', 'plugins')
    elif 'plugins' in startlist:
        # we're in the src folder
        return 'plugins'
    elif 'pluginbase' in startlist:
        # we're in plugin folder
        return '.'
    elif 'TrashBin' in startlist:
        # we're above the module --- won't something else break here??
        # well, it won't be this function
        return os.path.join('TrashBin', 'src', 'plugins')
    else:
        # ok, no idea where we are, and not much chance of finding out
        raise FileNotFoundError("I can't find the plugin directory!")

def recursive_list_of_files(startdir='.'):
    path = os.path.join(startdir, '**', '*.py')
    files = glob.glob(path, recursive=True)
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

def module_list():
    modules = []
    for plugin in wanted_file_list():
        filename = os.path.splitext(plugin)[0]
        modname = filename.replace('/', '.')
        # maintain windows compat, also replace backslashes with dots
        modname = modname.replace('\\', '.')
        modules.append(importlib.import_module(modname))
    return modules

def _ident_subclasses_of(module, basecls):
    attribs = dir(module)
    children = []
    for attrib in attribs:
        attrib = getattr(module, attrib)
        if not isinstance(attrib, type):
            continue
        if not hasattr(attrib, '__mro__'):
            continue
        if not basecls in attrib.__mro__:
            continue

        children.append(attrib)
    return children

def plugin_list():
    modules = module_list()
    plugins = []
    factories = []
    for module in modules:
        module_plugins = _ident_subclasses_of(module, pb.TrashBinPlugin)
        module_factories = _ident_subclasses_of(module, pb.TBPluginFactory)
        for mp in module_plugins:
            plugins.append(mp)
        for fc in module_factories:
            factories.append(fc)
    return plugins, factories


