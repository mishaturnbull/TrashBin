#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test GUI plugin for debug purposes
"""

import random
import time
import tkinter as tk
from tkinter import ttk, messagebox as tkmb
from src.plugins import pluginbase

_PHASES = [
        "Filename",
        "Filehandle",
        "Parsed log",
        "Messages",
    ]

def exec_load(plug, data):
    """
    Execute a dummy workload.
    """
    count = data[0]
    time_per = data[1]
    if data[0] <= 0:
        return
    if time_per <= 0:
        return

    for _ in range(count):
        time.sleep(time_per)
        plug.handler.notify_work_done(1)

class DummyLoadFactory(pluginbase.TBPluginFactory):
    """
    Factory class for Pause plugin.
    """

    author_name = "Misha Turnbull"
    author_email = "misha@turnbull.link"
    plugin_name = "Dummy workload"
    plugin_desc = "Pretends to perform (a configurable amount of) work at the" \
            " given stages."

    def __init__(self, handler):
        """
        Create an instance of the plugin test factory.
        """
        super().__init__(handler)

        self.loads = [[tk.IntVar(), tk.DoubleVar()] for ph in _PHASES]
        self._statuslbl = None

    @property
    def work_per_file(self):
        return sum([l[0].get() for l in self.loads])

    def start_ui(self, frame):
        self.iframe = tk.Frame(frame)
        frame.grid_columnconfigure(0, weight=1)
        self.iframe.grid(row=0, column=0, sticky='nesw')
        self.iframe.grid_columnconfigure(0, weight=1)
        self.iframe.grid_columnconfigure(1, weight=1)

        tk.Label(self.iframe, text="Steps").grid(row=0, column=0, sticky='nw')
        tk.Label(self.iframe, text="Time per").grid(row=0, column=1, sticky='nw')

        for i in range(len(self.loads)):
            frame = tk.LabelFrame(self.iframe, relief=tk.RIDGE,
                    text=_PHASES[i])
            frame.grid(row=i+1, column=0, columnspan=2, sticky='nesw')
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_columnconfigure(1, weight=1)

            ttk.Spinbox(frame, from_=0, to=99999, command=self.cb_upd, width=4,
                    textvariable=self.loads[i][0]).grid(
                            row=0, column=0, sticky='nsew')
            ttk.Spinbox(frame, from_=0, to=999, command=self.cb_upd, width=4,
                    textvariable=self.loads[i][1]).grid(
                            row=0, column=1, sticky='nsew')

        self._statuslbl = tk.Label(self.iframe, text="Total time taken: UNCALC")
        self._statuslbl.grid(row=i+2, column=0, columnspan=2, sticky='nesw')

        self.cb_upd()

    def cb_upd(self):
        totaltime = 0
        for load in self.loads:
            totaltime += load[0].get() * load[1].get()
        self._statuslbl.config(text=f"Total time taken: {totaltime} (sec)")

    def stop_ui(self, frame):
        self.iframe.destroy()

    def export_savestate(self):
        out = {}
        for i, load in enumerate(self.loads):
            out.update({i: [load[0].get(), load[1].get()]})
        return {"load": out}

    def load_savestate(self, state):
        for i, load in state['load'].items():
            i = int(i)
            self.loads[i][0].set(load[0])
            self.loads[i][1].set(load[1])

    def cleanup_and_exit(self):
        pass

    def give_plugin(self, processor=None):
        data = [[l[0].get(), l[1].get()] for l in self.loads]
        return DummyWorkloadPlugin(self, processor, data)


class DummyWorkloadPlugin(pluginbase.TrashBinPlugin):
    """
    Does the random test work.
    """

    def __init__(self, handler, processor, loads):
        super().__init__(handler, processor)
        self.loads = loads

    def run_filename(self, filename):
        exec_load(self, self.loads[0])

    def run_filehandle(self, filehandle):
        exec_load(self, self.loads[1])

    def run_parsedlog(self, dflog):
        exec_load(self, self.loads[2])

    def run_messages(self, messages):
        exec_load(self, self.loads[3])

