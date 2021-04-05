#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
GUI plugin for parameter file generation
"""

import os
import tkinter as tk
import tkinter.ttk as ttk
import src.plugins.pluginbase as pluginbase
import src.logutils.extract_params as extract_params


class ParamExtractPlugin(pluginbase.TrashBinPlugin):

    author_name = "Misha Turnbull"
    author_email = "misha@turnbull.link"
    plugin_name = "Parameter Extracter"
    plugin_desc = "This plugin generates .param files containing parameters " \
            "described in a MAVLink log file.  It can handle de-duplication " \
            " of parameters by keeping only the first, only the last, or " \
            "refuting duplicate parameters altogether."

    def __init__(self, handler):
        """
        Create an instance of the param extracter plugin.
        """
        super().__init__(handler)
        self.infilename = None
        self.outfilename = None
        self.multivalhandle = tk.IntVar()
        self.multivalhandle.set(extract_params.MULTIVAL_FIRST)
        self.paramfilter = tk.StringVar()
        self.paramfilter.set('.*')
        self.force_output = tk.BooleanVar()
        self.force_output.set(False)
    
    def run_filename(self, filename):
        self.infilename = filename
        if self.outfilename is None:
            self.outfilename = os.path.splitext(filename)[0] + '.param'

    def run_parsedlog(self, dflog):
        self.params = extract_params.grab_params_complex(
                dflog,
                multivalhandle=self.multivalhandle.get(),
                paramfilter=[self.paramfilter.get()]
            )
        extract_params.write_out_file(
                extract_params.params_to_filecontents(self.params),
                self.outfilename,
                force=self.force_output.get()
            )

    def start_ui(self, frame):
        self.mvselframe = tk.LabelFrame(frame, text="Param Duplication",
                relief=tk.RIDGE)
        rb_first = tk.Radiobutton(self.mvselframe, text="First occurance",
                variable=self.multivalhandle,
                value=extract_params.MULTIVAL_FIRST,
            )
        rb_last = tk.Radiobutton(self.mvselframe, text="Last occurance",
                variable=self.multivalhandle,
                value=extract_params.MULTIVAL_LAST,
            )
        rb_fail = tk.Radiobutton(self.mvselframe, text="Abort",
                variable=self.multivalhandle,
                value=extract_params.MULTIVAL_FAIL,
            )
        rb_first.grid(row=0, column=0, sticky='nw')
        rb_last.grid(row=1, column=0, sticky='nw')
        rb_fail.grid(row=2, column=0, sticky='nw')
        self.mvselframe.grid(row=0, column=0, sticky='nw')
        frame.update()
        print("Done start_ui")

    def stop_ui(self, frame):
        self.mvselframe.destroy()

    def cleanup_and_exit(self):
        pass

