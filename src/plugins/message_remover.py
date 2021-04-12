#!/usr/bin/python3
# -*- coding: utf-8

"""
GUI plugin for log message sanitization.
"""

import os
import tkinter as tk
import tkinter.ttk as ttk
import src.plugins.pluginbase as pluginbase
import src.logutils.message_remover as message_remover
import src.logutils.DFWriter as dfwriter


class MessageRemoverFactory(pluginbase.TBPluginFactory):

    author_name = "Misha Turnbull"
    author_email = "misha@turnbull.link"
    plugin_name = "Message Remover"
    plugin_desc = "This plugin allows for selective removal of MAVLink log " \
            "messages in a log file."
    
    def __init__(self, handler):
        """
        Create an instance of the message remover plugin for TrashBin UI.
        """
        super().__init__(handler)
        self.filter = tk.StringVar()
        self.filter.set('.*')
        self.whitelist = tk.BooleanVar()
        self.whitelist.set(True)
        self.nukemode = tk.BooleanVar()
        self.nukemode.set(True)
        self.replace = tk.StringVar()
        self.replace.set('Zero')

    @property
    def replace_val(self):
        ui = self.replace.get()
        if ui == 'Zero':
            return 0
        elif ui == 'None/NaN':
            return float('nan')
        elif ui == 'One':
            return 1
        else:
            return None

    @property
    def work_per_file(self):
        return MessageRemoverPlugin.total_work

    def start_ui(self, frame):
        self.modeframe = tk.LabelFrame(frame, text='Specificity',
                relief=tk.RIDGE)
        self.modeframe.grid(row=0, column=0, sticky='nw')
        cb_replace = ttk.Combobox(self.modeframe,
                textvariable=self.replace,
                values=('Zero', 'None/NaN', 'One',),
            )
        rb_nuke = tk.Radiobutton(self.modeframe,
                text='Delete entire packet',
                variable=self.nukemode,
                value=True,
                command=lambda: cb_replace.config(state="disabled"),
            )
        rb_razor = tk.Radiobutton(self.modeframe,
                text='Overwrite selected parts of packet',
                variable=self.nukemode,
                value=False,
                command=lambda: cb_replace.config(state="readonly"),
            )
        tk.Label(self.modeframe, text='Replace with:').grid(
                row=2, column=0, sticky='nw')
        rb_nuke.grid(row=0, column=0, columnspan=2, sticky='nw')
        rb_razor.grid(row=1, column=0, columnspan=2, sticky='nw')
        cb_replace.grid(row=2, column=1, sticky='nw')
        # set the default state
        if self.nukemode.get():
            cb_replace.config(state='disabled')
        else:
            cb_replace.config(state='readonly')

        self.colorframe = tk.LabelFrame(frame, text='Filter mode',
                relief=tk.RIDGE)
        self.colorframe.grid(row=1, column=0, sticky='nw')
        rb_white = tk.Radiobutton(self.colorframe,
                text='Keep only selected data (whitelist)',
                variable=self.whitelist,
                value=True,
            )
        rb_black = tk.Radiobutton(self.colorframe,
                text='Keep all BUT selected data (blacklist)',
                variable=self.whitelist,
                value=False,
            )
        rb_white.grid(row=0, column=0, sticky='nw')
        rb_black.grid(row=1, column=0, sticky='nw')

        filterframe = tk.Frame(frame)
        tk.Label(filterframe, text='Message data filter').grid(
                row=0, column=0, sticky='nw')
        tk.Label(filterframe, text='Enter as a multi-line regex').grid(
                row=1, column=0, sticky='nw')
        filterbox = tk.Entry(filterframe, textvariable=self.filter)
        filterbox.grid(row=2, column=0, sticky='nesw')
        filterframe.grid_rowconfigure(2, weight=1)
        filterframe.grid_columnconfigure(0, weight=1)
        filterframe.grid(row=2, column=0, sticky='nesw')
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        frame.update()

    def stop_ui(self, frame):
        for child in frame.winfo_children():
            child.destroy()
        frame.grid_rowconfigure(2, weight=0)
        frame.grid_columnconfigure(0, weight=0)
        frame.update()

    def cleanup_and_exit(self):
        pass

    def give_plugin(self):
        plug = MessageRemoverPlugin(
                self,
                whitelist=self.whitelist.get(),
                nukemode=self.nukemode.get(),
                replace=self.replace.get(),
                msgfilter=self.filter.get(),
                forceoutput=False,
            )
        return plug

class MessageRemoverPlugin(pluginbase.TrashBinPlugin):
    """
    Does the actual work of parameter filtering.
    """

    total_work = 10

    def __init__(self, handler, whitelist, nukemode, replace, msgfilter, 
            forceoutput):
        super().__init__(handler)
        self.whitelist = whitelist
        self.nukemode = nukemode
        self.replace = replace
        self.msgfilter = msgfilter
        self.forceoutput = forceoutput
        self.infilename = None
        self.outfilename = None

    def run_filename(self, filename):
        self.infilename = filename
        if self.outfilename is None:
            self.outfilename = os.path.splitext(filename)[0] + '.tb.log'
        self.handler.notify_work_done(1)

    def run_messages(self, messages):
        # parsing the messages is a decent task in itself
        self.handler.notify_work_done(1)
        if self.nukemode:
            new = self._nukemode(messages)
        else:
            new = self._razor(messages)
        # only one part left
        self.handler.notify_work_done(7)
        self.output(new)
        self.handler.notify_work_done(1)

    def _nukemode(self, messages):
        matching, nonmatching = message_remover.filter_packet_type(
                messages,
                msgtypes=[self.msgfilter]
            )
        if self.whitelist:
            res = matching
        else:
            res = nonmatching
        return res

    def _razor(self, messages):
        new_msgs = message_remover.filter_data_type(
                messages,
                msgfilter=self.msgfilter,
                replace=self.replace,
                reverse=self.whitelist,
            )
        self.new = new_msgs

    def output(self, new):
        dfw = dfwriter.DFWriter_text(new, self.outfilename)


