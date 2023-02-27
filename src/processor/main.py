#!/usr/env/python3
# -*- coding: utf-8 -*-

"""
Main execution handler for entire TrashBin program.

This class handles main order of operations based on execution environment, and
provides a backend for the GUI if necessary.
"""

import sys
import os
import uuid
import tkinter as tk
import src.config.config as config
import src.plugins.persist as persist
import src.plugins._plugin_autodetect as _pad
import src.gui.mainwindow as mainwindow

# the processor selection isn't as user-importable as plugins, we just import
# them all and then pick
import src.processor.singlethread as singlethread

class MainExecutor(object):

    def __init__(self, mastercfgfile,
            opermode='gui',
            extraconfigs=[],
            ):
        self.mastercfg = config.ConfigManager(mastercfgfile)
        self.work_total = 0
        self.work_done = 0
        self.available_factories = _pad.plugin_list()[1]
        self._extraconfigs = extraconfigs
        self.opermode = opermode
        self.factmap = {}
        if self.mastercfg.plugins:
            self.add_plugin_by_savedata(self.mastercfg.plugins['factories'])

        # we've hard-selected a single thread processor for now, because that's
        # the only one implemented.  for future when there's more
        # processor backends, this should be set to None and specified via
        # master config file (probably)
        self.processor = singlethread.SingleThreadProcessor(self)

        self._start_main_operations()

    def _load_extra_configs(self):
        for extra in self._extraconfigs:
            self.mastercfg.load_new_config_from_file(
                    extra,
                    permanent=False
                )
        if self.mastercfg['factories']:
            self.load_plugins(self.mastercfg.plugins.filename)
        if not self.mastercfg.inputs:
            inp = config.Configuration(None)
            inp['filenames'] = []
            inp['directories'] = []
            inp['rawtext'] = ""
            inp['__uuid'] = str(uuid.uuid4())
            inp['__scope'] = config.SCOPE_INPUTS
            self.mastercfg.slots.append(inp)

    def _start_main_operations(self):
        if self.opermode == 'gui':
            self._start_gui()
        elif self.opermode == 'headless':
            self._start_headless()
        else:
            print("MainExecutor - invalid operation mode {}".format(
                self.opermode))
            sys.exit(1)

    def _start_gui(self):
        self._gui = mainwindow.MainPanelUI(self)
        self._load_extra_configs()
        self._gui.update_inputs_from_mainexec()
        self._gui.start()

    def _start_headless(self):
        # there's no user to click go -- we've already got the master config,
        # let's just get into it!
        self._load_extra_configs()
        self.go()

    def _retotal_total_work(self):
        self.work_total = sum([p.work_total for p in self.processor.plugins])

    def notify_work_done(self, amt=1):
        self.work_done += amt
        self._retotal_total_work()
        if self.gui:
            self._gui.adjust_pbar(self.work_done, self.work_total)

    def notify_done(self):
        self.processor.active = False
        self.work_done = self.work_total
        if self.gui:
            self._gui.adjust_pbar(self.work_done, self.work_total)
            self._gui.notify_done()

    def set_files(self, newfiles):
        self.mastercfg.inputs['filenames'] = list(newfiles)

    def add_file(self, newfile):
        if newfile in self.mastercfg.inputs['filenames']:
            return
        self.mastercfg.inputs['filenames'].append(newfile)

    def add_dir(self, newdir):
        if newdir in self.mastercfg.inputs['directories']:
            return
        self.mastercfg.inputs['directories'].append(newdir)

    def set_dirs(self, dirs):
        self.mastercfg.inputs['directories'] = list(dirs)

    def add_plug_by_idx(self, idx):
        plugin = _pad.plugin_list()[1][idx]
        instance = plugin(self)
        self.factmap.update({instance.uuid: instance})
        return plugin

    def add_plugin_by_savedata(self, data):
        factories = persist.load_all_savestates(data, self)
        for factory in factories:
            self.factmap.update({factory.uuid: factory})

    @property
    def config(self):
        return self.mastercfg

    @property
    def input(self):
        if self.mastercfg.inputs:
            return self.mastercfg.inputs
        return {'filenames': [], 'directories': [], 'rawtext': []}

    @property
    def gui(self):
        return 'gui' in self.opermode

    @property
    def active(self):
        return self.processor.active

    @property
    def factories(self):
        return list(self.factmap.values())

    def go(self):
        if len(self.factories) == 0:
            print("No plugins specified, nothing to do!")
            return
        if self.config['debug']:
            print("Starting processor")
        self.processor.update()
        self.processor.reinit()
        self.processor.active = True
        self.processor.run()

    def stop(self):
        if self.config['debug']:
            print("Stopping processor")
        self.processor.stop()
        self.processor.active = False

    def load_plugins(self, filename):
        if os.path.splitext(filename)[1].endswith("tbz"):
            if self.config['debug']:
                print("Reading zip-wrapped file")
            factories = persist.load_zip_file(filename, self)
        else:
            if self.config['debug']:
                print("Reading JSON file")
            factories = persist.load_text_file(filename, self)
        if self.config['debug']:
            print("Got list of factories: {}".format(factories))
        for factory in factories:
            self.factmap.update({factory.uuid: factory})
            if self.gui:
                self._gui.ui_pluglistbox.insert(tk.END, factory.plugin_name)

    def save_plugins(self, filename):
        if os.path.splitext(filename)[1].endswith('tbz'):
            if self.config['debug']:
                print("Saving to zip-wrapped file")
            persist.write_zip_file(filename, list(self.factmap.values()))
        else:
            if self.config['debug']:
                print("Saving to JSON file")
            persist.write_text_file(filename, list(self.factmap.values()))

