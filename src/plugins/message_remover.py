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

    @property
    def work_per_file(self):
        return MessageRemoverPlugin.total_work

    def start_ui(self, frame):
        self.iframe = tk.Frame(frame)

        rb_white = tk.Radiobutton(self.iframe,
                text='Keep only selected data (whitelist)',
                variable=self.whitelist,
                value=True,
            )
        rb_black = tk.Radiobutton(self.iframe,
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
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        filterframe.grid(row=1, column=0, sticky='nesw')
        filterframe.grid_columnconfigure(0, weight=1)
        filterframe.grid_rowconfigure(2, weight=1)
        filterframe.grid_propagate(0)
        self.filterframe = filterframe

        self.iframe.grid(row=0, column=0, sticky='nesw')
        frame.update()

    def stop_ui(self, frame):
        self.iframe.destroy()
        self.filterframe.destroy()
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_columnconfigure(0, weight=0)
        frame.update()

    def cleanup_and_exit(self):
        pass

    def give_plugin(self):
        pass

