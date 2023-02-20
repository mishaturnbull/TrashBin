#!/usr/env/python3
# -*- coding: utf-8 -*-

"""
Main execution handler for entire TrashBin program.

This class handles main order of operations based on execution environment, and
provides a backend for the GUI if necessary.
"""

import sys
import os
import time
import src.config.config as config
import src.plugins.persist as persist
import src.gui.mainwindow as mainwindow
import src.tkstubs as tkstubs

if tkstubs.HAS_DISPLAY:
    import tkinter as tk
else:
    import src.tkstubs.tkstubs as tk

# the processor selection isn't as user-importable as plugins, we just import
# them all and then pick
import src.processor.singlethread as singlethread

class MainExecutor(object):

    def __init__(self, mastercfgfile,
            opermode='gui',
            ):
        self.mastercfg = config.ConfigManager(mastercfgfile)
        self.opermode = opermode
        self.factmap = {}
        self.files = []

        # we've hard-selected a single thread processor for now, because that's
        # the only one implemented.  for future when there's more
        # processor backends, this should be set to None and specified via
        # master config file (probably)
        self.processor = singlethread.SingleThreadProcessor(self)

        self._start_main_operations()

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
        self._gui.start()

    def _start_headless(self):
        # there's no user to click go -- we've already got the master config,
        # let's just get into it!
        self.go()

    @property
    def config(self):
        return self.mastercfg

    @property
    def gui(self):
        return 'gui' in self.opermode

    @property
    def active(self):
        return self.processor.active

    @property
    def factories(self):
        return self.factmap.values()

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
        

