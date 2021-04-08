#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Sub-ui specifically for plugin import and loading.
"""

import tkinter as tk

class PluginLoaderPanel(object):
    """
    Creates the plugin load selector user interface.
    """

    def __init__(self, parent, plugins_available):
        self.parent = parent
        self.plugins_available = plugins_available
        self.spawn_ui()

    def cb_loadsel(self):
        selected = self.pluginselbox.curselection()
        for i in selected:
            plugin = self.plugins_available[i]
            instance = plugin(self.parent)
            self.parent.factmap.update({instance.uuid: instance})
            self.parent.ui_pluglistbox.insert(tk.END, plugin.plugin_name)

    def cb_describe(self, event):
        selected = self.pluginselbox.curselection()
        plugin = self.plugins_available[selected[0]]
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
        listframe = tk.Frame(self.root)
        listframe.grid(row=0, column=0)
        self.pluginselbox = tk.Listbox(listframe, height=20, width=40)
        self.pluginselbox.pack(side=tk.LEFT, fill=tk.BOTH)
        scrollbar = tk.Scrollbar(listframe)
        scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.pluginselbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.pluginselbox.yview)

        addbtn = tk.Button(self.root, text="Load plugin",
                command=self.cb_loadsel)
        addbtn.grid(row=1, column=0, columnspan=2, sticky='nesw')
        self.pluginselbox.bind("<<ListboxSelect>>", self.cb_describe)

        # populate the plugin list
        print(self.plugins_available)
        for plugin in self.plugins_available:
            print(plugin)
            self.pluginselbox.insert(tk.END, plugin.plugin_name)

        # plugin details box
        listframe.update()
        rightframe = tk.Frame(self.root, width=listframe.winfo_width(),
                height=listframe.winfo_height())
        rightframe.grid(row=0, column=1)
        self.detailsbox = tk.Text(rightframe, height=21, width=40)
        self.detailsbox.grid(row=0, column=0, sticky='nesw')

