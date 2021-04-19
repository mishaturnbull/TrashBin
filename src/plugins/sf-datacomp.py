#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Same file data comparison plugin.
"""

import tkinter as tk
import tkinter.ttk as ttk
import functools
import src.plugins.pluginbase as pluginbase
import src.logutils.DFWriter as dfwriter


class SFDataCompFactory(pluginbase.TBPluginFactory):

    author_name = "Misha Turnbull"
    author_email = "misha@turnbull.link"
    plugin_name = "Same-file data comparison"
    plugin_desc = "This plugin allows for comparing every datapoint of two " \
            "lines in a data file."

    def __init__(self, handler):
        """
        Create an instance of the data comparison plugin factory.
        """
        super().__init__(handler)
        self.lineA = tk.StringVar()
        self.lineA.set('')
        self.lineB = tk.StringVar()
        self.lineB.set('')
        self.do_popup = tk.BooleanVar()
        self.do_popup.set(True)

    @property
    def work_per_file(self):
        return len(self.lines) - 1

    def start_ui(self, frame):
        self.popupbox = tk.Checkbutton(frame, text="Display results",
                variable=self.do_popup, onvalue=True, offvalue=False)
        self.popupbox.grid(row=0, column=0, columnspan=2, sticky='nw')

        self.lineframe = tk.Frame(frame)
        tk.Label(self.lineframe, text="A:").grid(row=0, column=0, sticky='nw')
        tk.Label(self.lineframe, text="B:").grid(row=1, column=0, sticky='nw')
        entryA = tk.Entry(self.lineframe, textvariable=self.lineA)
        entryA.grid(row=0, column=1, sticky='new')
        entryB = tk.Entry(self.lineframe, textvariable=self.lineB)
        entryB.grid(row=1, column=1, sticky='new')

        self.lineframe.grid(row=1, column=0, sticky='nesw')
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.update()

    def stop_ui(self, frame):
        self.popupbox.destroy()
        self.filterframe.destroy()
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_columnconfigure(0, weight=0)

    def export_savestate(self):
        return {
                "popup": self.do_popup.get(),
                "lines": [
                    self.lineA.get(),
                    self.lineB.get(),
                ],
            }

    def load_savestate(self, state):
        self.do_popup.set(state['popup'])
        lines = state['lines']
        self.lineA.set(lines[0])
        self.lineB.set(lines[1])

    def cleanup_and_exit(self):
        pass

    def give_plugin(self, processor=None):
        plug = SFDataCompPlugin(
                self,
                processor,
                self.do_popup.get(),
                self.lineA.get(),
                self.lineB.get(),
            )
        return plug


class SFDataCompPlugin(pluginbase.TrashBinPlugin):
    """
    Does the data comparison work.
    """
    
    def __init__(self, handler, processor, popup, A, B):
        super().__init__(handler, proc)
        self.popup = popup
        self.infilename = None
        self.lineA = A.split('.')
        self.lineB = B.split('.')
        self.diffpoints = []
        self.last_point_a = (None, 0)
        self.last_point_b = (None, 0)

    def run_filename(self, filename):
        self.infilename = filename

    def run_messages(self, messages):
        for msg in messages:
            d = msg.to_dict()
            packettype = d['mavpackettype']
            if packettype == self.lineA[0]:
                self._dispatch(self.last_point_a, d)
            elif packettype == self.lineB[0]:
                self._dispatch(self.last_point_b, d)
            else:
                continue

    def _dispatch(self, tupl, d):
        tupl[0] = d[self.lineA[1]]
        tupl[1] = d['TimeUS']
        

