#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test GUI plugin for debug purposes
"""

import random
import time
import tkinter as tk
import tkinter.ttk as ttk
from src.plugins import pluginbase


class PluginTestFactory(pluginbase.TBPluginFactory):

    author_name = "Misha Turnbull"
    author_email = "misha@turnbull.link"
    plugin_name = "Debug plugin test"
    plugin_desc = "This plugin calls as many functions of its handers as it" \
            " can in order to perform debug tests."

    def __init__(self, handler):
        """
        Create an instance of the plugin test factory.
        """
        super().__init__(handler)
        self._work_needed = random.randint(10, 100) * 4

    @property
    def work_per_file(self):
        return self._work_needed

    def start_ui(self, frame):
        self.iframe = tk.Frame(frame)
        self.iframe.grid(row=0, column=0, sticky='nesw')

        tk.Label(self.iframe, text="My work per file is {} units".format(
            self.work_per_file)).grid(row=0, column=0)

    def stop_ui(self, frame):
        self.iframe.delete()

    def export_savestate(self):
        return {
                'work': self.work_per_file,
            }

    def load_savestate(self, state):
        self._work_needed = state['work']

    def cleanup_and_exit(self):
        pass

    def give_plugin(self, processor=None):
        plug = TestPlugin(self, processor, self.work_per_file)
        print("ParamTestFactory: giving new plugin {}".format(plug))
        return plug


class TestPlugin(pluginbase.TrashBinPlugin):
    """
    Does the random test work.
    """
    
    def __init__(self, handler, processor, work_per_file):
        super().__init__(handler, processor)
        self.work_per_file = work_per_file
    
    def run_filename(self, filename):
        print("Plugin test: in run_filename: {}".format(filename))
        self.handler.notify_work_done(self.work_per_file / 4)
        time.sleep(0.5)

    def run_filehandle(self, filehandle):
        print("Plugin test: in run_filehandle: {}".format(filehandle))
        self.handler.notify_work_done(self.work_per_file / 4)
        time.sleep(0.5)

    def run_parsedlog(self, dflog):
        print("Plugin test: in run_parsedlog: {}".format(dflog))
        self.handler.notify_work_done(self.work_per_file / 4)
        time.sleep(0.5)

    def run_messages(self, messages):
        print("Plugin test: in run_messages with len {}".format(len(messages)))
        self.handler.notify_work_done(self.work_per_file / 4)
        time.sleep(0.5)

    def cleanup_and_exit(self):
        # nothing to do here!
        pass


