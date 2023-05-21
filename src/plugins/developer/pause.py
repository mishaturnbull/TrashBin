#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Test GUI plugin for debug purposes
"""

import code
import tkinter as tk
from tkinter import ttk, messagebox as tkmb
from src.plugins import pluginbase

_PHASES = [
        "Filename",
        "Filehandle",
        "Parsed log",
        "Messages",
    ]

def pause_popup(phase):
    msg = f"I have paused execution as requested in the {phase} phase.  " \
            "Click OK when ready to continue!"
    tkmb.showinfo(title="User pause", message=msg)

def pause_repl(phase, plug):
    print(f"\n\nI have paused execution as requested in the {phase} phase, "\
            "and invoked an interactive console session.  Send an EOF to "\
            "exit (ctrl-D at the prompt) and continue execution.\n")
    self = plug
    code.interact(local=locals())

def handle_phase(plug, idx):
    var = plug.enables[idx]
    if var == 1:
        pause_popup(_PHASES[idx])
    elif var == 2:
        pause_repl(_PHASES[idx], plug)

class PauseFactory(pluginbase.TBPluginFactory):

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

        self._enables = [tk.IntVar() for ph in _PHASES]

    @property
    def work_per_file(self):
        return 1

    def start_ui(self, frame):
        self.iframe = tk.Frame(frame)
        self.iframe.grid(row=0, column=0, sticky='nesw')
        self.iframe.grid_columnconfigure(0, weight=1)

        for i in range(len(self._enables)):
            frame = tk.LabelFrame(self.iframe, relief=tk.RIDGE,
                    text=_PHASES[i])
            frame.grid(row=i, column=0, sticky='nesw')
            frame.grid_columnconfigure(0, weight=1)

            tk.Radiobutton(frame, text="No pause", variable=self._enables[i],
                    value=0).grid(row=0, column=0, sticky='nw')
            tk.Radiobutton(frame, text="Popup", variable=self._enables[i],
                    value=1).grid(row=0, column=1, sticky='nw')
            tk.Radiobutton(frame, text="REPL", variable=self._enables[i],
                    value=2).grid(row=0, column=2, sticky='nw')

    def stop_ui(self, frame):
        self.iframe.destroy()

    def export_savestate(self):
        return {"pause": {i: var.get() for i, var in enumerate(self._enables)}}

    def load_savestate(self, state):
        print(f"LOAD: {state}")
        for i, val in state["pause"].items():
            self._enables[int(i)].set(val)

    def cleanup_and_exit(self):
        pass

    def give_plugin(self, processor=None):
        print("asked to give plugin")
        return PausePlugin(self, processor, [v.get() for v in self._enables])


class PausePlugin(pluginbase.TrashBinPlugin):
    """
    Does the random test work.
    """

    def __init__(self, handler, processor, enables):
        super().__init__(handler, processor)
        print(f"enables: {enables}")
        self.enables = enables

    def run_filename(self, filename):
        handle_phase(self, 0)

    def run_filehandle(self, filehandle):
        handle_phase(self, 1)

    def run_parsedlog(self, dflog):
        handle_phase(self, 2)

    def run_messages(self, messages):
        handle_phase(self, 3)

