#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Sub-ui specifically for plugin import and loading.
"""

import tkinter as tk
from tkinter import ttk

DEFAULT_MODULE_WIDTH = 250
DEFAULT_PLUGIN_WIDTH = 250

class PluginLoaderPanel(object):
    """
    Creates the plugin load selector user interface.
    """

    def __init__(self, parent, plugins_available):
        self.parent = parent
        self.plugins_available = plugins_available
        self.spawn_ui()

    def cb_loadsel(self):
        selected = self.tree.item(self.tree.focus())
        print(selected)
        if len(selected['tags']) == 0:
            # selected a parent module, not a plugin.  nothing else to do here.
            return

        factory_name = selected['tags'][0]
        plugin_names = [p.__name__ for p in self.plugins_available]
        plugin_idx = plugin_names.index(factory_name)

        plugin = self.parent.mainexec.add_plug_by_idx(plugin_idx)
        self.parent.ui_pluglistbox.insert(tk.END, plugin.plugin_name)

    def cb_describe(self, event):
        selected = self.tree.item(self.tree.focus())
        print(selected)
        if len(selected['tags']) == 0:
            # selected a parent module, not a plugin
            text = "This is a module container.  Select the drop-down option" \
                    " on the far left of this dialog to see this module's" \
                    " plugins."

        else:
            # an actual plugin
            factory_name = selected['tags'][0]
            plugin_names = [p.__name__ for p in self.plugins_available]
            plugin_idx = plugin_names.index(factory_name)
            plugin = self.plugins_available[plugin_idx]

            text = "Author: {}\n{}\n\n{}".format(
                    plugin.author_name, plugin.author_email, plugin.plugin_desc)

        # now that we have the text, first delete anything currently in the
        # description box to clear it out
        self.detailsbox.delete('1.0', tk.END)
        # now put our text in!
        self.detailsbox.insert('1.0', text)

    def spawn_ui(self):
        """
        Spawns UI components.
        """
        self.root = tk.Toplevel(self.parent.root)
        self.root.resizable(False, False)

        # plugin listbox and scrollbar
        treeframe = tk.Frame(self.root)
        treeframe.grid(row=0, column=0, sticky='nesw')
        treeframe.grid_rowconfigure(0, weight=1)
        treeframe.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(treeframe)
        self.tree.grid(row=0, column=0, sticky='nesw')

        verscrlbar = ttk.Scrollbar(treeframe, orient='vertical',
                command=self.tree.yview)
        verscrlbar.grid(row=0, column=1, sticky='nes')
        self.tree.configure(yscrollcommand=verscrlbar.set)

        self.tree['columns'] = ('plugin',)
        self.tree['show'] = 'tree headings'
        self.tree['selectmode'] = 'browse'
        self.tree.bind('<<TreeviewSelect>>', self.cb_describe)
        self.tree.column('#0', width=DEFAULT_MODULE_WIDTH, anchor='w')
        self.tree.column('plugin', width=DEFAULT_PLUGIN_WIDTH)
        self.tree.heading('#0', text="Module")
        self.tree.heading('plugin', text="Plugin")

        addbtn = tk.Button(self.root, text="Load plugin",
                command=self.cb_loadsel)
        addbtn.grid(row=1, column=0, columnspan=2, sticky='nesw')

        # plugin details box
        treeframe.update()
        rightframe = tk.Frame(self.root, width=treeframe.winfo_width(),
                height=treeframe.winfo_height())
        rightframe.grid(row=0, column=1)
        self.detailsbox = tk.Text(rightframe, height=21, width=40)
        self.detailsbox.grid(row=0, column=0, sticky='nesw')
        self.detailsbox.insert('1.0', "Select a plugin to see more info")

        # populate the plugin list
        self.update_plugin_list()

    def update_plugin_list(self):
        partials = []
        for plugin in self.plugins_available:
            modpath = plugin.__module__.split('.')
            modfile = modpath[-1]
            modpath = modpath[2:-1]
            if len(modpath) == 0:
                modname = ''
            else:
                modname = modpath[-1]
                if modname not in partials:
                    parent = '' if len(modpath) == 1 else modpath[-2]
                    print(f"mod insert {parent}/{modpath}")
                    self.tree.insert(parent, 'end', modname, text=modname,
                            values=[], tags=[])
                    partials.append(modname)

            print(f"plug insert {modname}/{plugin}")
            self.tree.insert(modname, 'end', plugin.__name__, text=modfile,
                    values=[plugin.plugin_name], tags=[plugin.__name__])

