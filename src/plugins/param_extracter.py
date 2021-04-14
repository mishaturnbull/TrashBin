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


class ParamExtractFactory(pluginbase.TBPluginFactory):

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
        self.multivalhandle = tk.IntVar()
        self.multivalhandle.set(extract_params.MULTIVAL_FIRST)
        self.paramfilter = tk.StringVar()
        self.paramfilter.set('.*')
        self.force_output = tk.BooleanVar()
        self.force_output.set(False)

    @property
    def work_per_file(self):
        return ParamExtractPlugin.total_work

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

        self.forcebox = tk.Checkbutton(frame, text='Force output',
                variable=self.force_output, onvalue=True, offvalue=False)
        self.forcebox.grid(row=0, column=1, sticky='nw')

        self.filterframe = tk.Frame(frame)
        tk.Label(self.filterframe, text="Parameter name filter").grid(
                row=0, column=0, sticky='nw')
        tk.Label(self.filterframe, text="Enter as a multi-line regex").grid(
                row=1, column=0, sticky='nw')
        filterbox = tk.Entry(self.filterframe, 
                textvariable=self.paramfilter)
        filterbox.grid(row=2, column=0, sticky='nesw')
        self.filterframe.grid(row=3, column=0, columnspan=2, sticky='nesw')
        self.filterframe.grid_rowconfigure(2, weight=1)
        self.filterframe.grid_columnconfigure(0, weight=1)
        self.filterframe.grid_propagate(0)
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        frame.update()
        print("Done start_ui")

    def stop_ui(self, frame):
        self.mvselframe.destroy()
        self.forcebox.destroy()
        self.filterframe.destroy()
        frame.grid_rowconfigure(3, weight=0)
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=0)

    def export_savestate(self):
        return {
                'multivalhandle': self.multivalhandle.get(),
                'paramfilter': self.paramfilter.get(),
                'forceout': self.force_output.get(),
            }

    def load_savestate(self, state):
        self.multivalhandle.set(state['multivalhandle'])
        self.paramfilter.set(state['paramfilter'])
        self.force_output.set(state['forceout'])

    def cleanup_and_exit(self):
        pass
    
    def give_plugin(self, processor=None):
        plug = ParamExtractPlugin(self,
                self.multivalhandle.get(),
                [self.paramfilter.get()],
                self.force_output.get()
            )
        print('pef giving plugin {}'.format(plug))
        return plug

class ParamExtractPlugin(pluginbase.TrashBinPlugin):
    """
    Does the work of extracting the parameters from a log.
    """
    total_work = 3

    def __init__(self, handler, multivalhandle, paramfilter, forceoutput):
        self.handler = handler
        self.multivalhandle = multivalhandle
        self.paramfilter = paramfilter
        self.forceoutput = forceoutput
        self.outfilename = None
    
    def run_filename(self, filename):
        print("entering pep.run_filename")
        self.infilename = filename
        if self.outfilename is None:
            self.outfilename = os.path.splitext(filename)[0] + '.param'
        self.handler.notify_work_done()
        print('exited')

    def run_parsedlog(self, dflog):
        print("entering pep.run_parsedlog")
        self.params = extract_params.grab_params_complex(
                dflog,
                multivalhandle=self.multivalhandle,
                paramfilter=self.paramfilter,
            )
        self.handler.notify_work_done()
        extract_params.write_out_file(
                extract_params.params_to_filecontents(self.params),
                self.outfilename,
                force=self.forceoutput,
            )
        self.handler.notify_work_done()
        print('exited')

    def cleanup_and_exit(self):
        # self.params can have over a thousand doubles, this could free up some
        # space for someone else.  gc should get it automatically, but we'll
        # make sure it happens faster
        del self.params

