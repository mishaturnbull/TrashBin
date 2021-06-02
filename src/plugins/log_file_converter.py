#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
GUI plugin to convert a message to text format.
"""

import os
import tkinter as tk
import src.plugins.pluginbase as pluginbase
import src.logutils.DFWriter as dfwriter

LFMT_BINARY = 0
LFMT_TEXT = 1
LFMT_CSV = 2


class LogFormatConverter(pluginbase.TBPluginFactory):

    author_name = 'Misha Turnbull'
    author_email = 'misha@turnbull.link'
    plugin_name = "Log format converter"
    plugin_desc = "This plugin allows for converting log files between file " \
            "types, such as from binary to text or CSV."

    def __init__(self, handler):
        super().__init__(handler)
        self.output = tk.IntVar()
        self.output.set(LFMT_TEXT)
        self.force = tk.BooleanVar()
        self.force.set(False)

    @property
    def work_per_file(self):
        return 1

    def start_ui(self, frame):
        self.modeframe = tk.LabelFrame(frame, text='Output type',
                relief=tk.RIDGE)
        self.modeframe.grid(row=0, column=0, sticky='new')
        rb_binary = tk.Radiobutton(self.modeframe,
                text='Binary',
                variable=self.output,
                value=LFMT_BINARY,
            )
        rb_text = tk.Radiobutton(self.modeframe,
                text='Text',
                variable=self.output,
                value=LFMT_TEXT,
            )
        rb_csv = tk.Radiobutton(self.modeframe,
                text='CSV',
                variable=self.output,
                value=LFMT_CSV,
            )
        # to remain commented out until facilities exist for exporting files
        # in binary format.  doesn't make much sense to advertise a feature
        # that doesn't work
        #rb_binary.grid(row=0, column=0, sticky='nw')
        rb_text.grid(row=1, column=0, sticky='nw')
        rb_csv.grid(row=2, column=0, sticky='nw')

        self.optsframe = tk.Frame(frame)
        self.optsframe.grid(row=1, column=0, sticky='new')
        forcebox = tk.Checkbutton(self.optsframe, text='Force output',
                variable=self.force, onvalue=True, offvalue=False)
        forcebox.grid(row=0, column=0, sticky='nw')

    def stop_ui(self, frame):
        self.modeframe.destroy()
        self.optsframe.destroy()

    def export_savestate(self):
        return {
                'mode': self.output.get(),
                'force': self.force.get(),
            }

    def load_savestate(self, state):
        self.output.set(state['mode'])
        self.force.set(state['force'])

    def cleanup_and_exit(self):
        pass

    def give_plugin(self, processor=None):
        plug = LogConvPlugin(self,
                processor,
                self.output.get(),
                self.force.get(),
            )
        return plug


class LogConvPlugin(pluginbase.TrashBinPlugin):

    def __init__(self, handler, processor, mode, force):
        super().__init__(handler, processor)
        self.mode = mode
        self.force = force
        self.infilename = None
        self.outfilename = None

    def run_filename(self, filename):
        self.infilename = filename
        infn_noext = os.path.splitext(self.infilename)[0]
        newext = 'unk'
        if self.mode == LFMT_BINARY:
            newext = 'bin'
        elif self.mode == LFMT_TEXT:
            newext = 'log'
        elif self.mode == LFMT_CSV:
            newext = 'csv'
        self.outfilename = '.'.join([infn_noext, newext])

    def run_messages(self, messages):
        self.messages = messages
        if self.mode == LFMT_TEXT:
            self._conv_to_text(self.messages)
        elif self.mode == LFMT_BINARY:
            self._conv_to_binary(self.messages)
        elif self.mode == LFMT_CSV:
            self._conv_to_csv(self.messages)

    def _conv_to_text(self, messages):
        dfw_t = dfwriter.DFWriter_text(messages, self.outfilename)
        self.handler.notify_work_done(1)

    def _conv_to_binary(self, messages):
        raise NotImplemented

    def _conv_to_csv(self, messages):
        # turns out csv files are the same as regular text, but with a
        # different extension!
        self._conv_to_text(messages)

