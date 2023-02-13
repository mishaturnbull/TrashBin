#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Sub-ui specifically for program-wide configuration.
"""

import tkinter as tk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb
from tkinter import ttk
import uuid

import src.config.config as config

DEFAULT_COL_WIDTH = 180  # pixels


class ConfigurationEditorPanel(object):

    def __init__(self, parent):
        self.parent = parent

        self.uifilepath = tk.StringVar()
        self.uifilepath.set(self.parent.config.filename)
        self.spawn_ui()
        self.cb_load()

    def spawn_ui(self):
        self.root = tk.Toplevel(self.parent.root)
        self.root.resizable(True, True)

        topframe = tk.Frame(self.root)
        mainframe = tk.Frame(self.root)

        btnSave = tk.Button(topframe, text="Save",
                command=self.cb_save)
        btnSave.grid(row=0, column=0, sticky='nws')
        btnLoad = tk.Button(topframe, text="Load",
                command=self.cb_load)
        btnLoad.grid(row=0, column=1, sticky='nesw')
        btnPick = tk.Button(topframe, text="Select file",
                command=self.cb_pick)
        btnPick.grid(row=0, column=2, sticky='nes')
        entryFile = tk.Entry(topframe, textvariable=self.uifilepath)
        entryFile.grid(row=1, column=0, columnspan=3, sticky='nesw')

        self.tree = ttk.Treeview(mainframe)
        self.tree.grid(row=0, column=0, sticky='nesw')

        verscrlbar = ttk.Scrollbar(mainframe, orient='vertical',
                command=self.tree.yview)
        verscrlbar.grid(row=0, column=1, sticky='nes')
        self.tree.configure(yscrollcommand=verscrlbar.set)

        self.tree['columns'] = ('item', 'value')
        self.tree['show'] = 'headings'
        self.tree.column('item', width=180, anchor='w')
        self.tree.column('value', width=180, anchor='e')
        self.tree.heading('item', text="Item")
        self.tree.heading('value', text="Value")

        topframe.grid(row=0, column=0, sticky='nesw')
        mainframe.grid(row=1, column=0, sticky='nesw')

    def cb_save(self):
        pass

    def cb_load(self):
        configs = self.parent.config.data()
        self._insert_items('', configs)

    def _insert_items(self, treeparent, data):
        print("enter: treeparent=`{}`, data={}".format(
            treeparent, data))

        for key in data:
            val = data[key]
            uid = uuid.uuid4()
            print("TOL: treeparent=`{}`, key={}, val={}".format(
                treeparent, key, val))

            if isinstance(val, dict):
                self.tree.insert(treeparent, 'end', uid, text=key)
                self._insert_items(uid, val)
            
            elif isinstance(val, list):
                self.tree.insert(treeparent, 'end', uid, text=key+"[]")
                self._insert_items(uid,
                        dict([(i, x) for i, x in enumerate(val)]))

            else:
                if val is None:
                    val = 'None'
                self.tree.insert(treeparent, 'end', uid, text=key, 
                    values=[key, val])

    def cb_pick(self):
        pass

