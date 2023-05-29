#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file provides the main, flow-esque panel for the user interface.
"""

import tkinter as tk
import tkinter.filedialog as tkfd
from tkinter import ttk
from src.gui import configui
from src.plugins import _plugin_autodetect as _pad

DEFAULT_MODULE_WIDTH = 250
DEFAULT_PLUGIN_WIDTH = 250

class FlowPanelUI(object):
    """
    Class wrapper around the flow panel user interface.

    This is **not** a direct subclass of tk.Tk; instead, it *contains* a
    tk.Tk!
    """

    def __init__(self, mainexec):
        self.mainexec = mainexec
        self.root = tk.Tk()

        # state variable init
        self.pbar_var = tk.IntVar()
        self.pbar_var.set(0)
        self.status_var = tk.StringVar()
        self.status_var.set("Waiting for start")
        self.stage_var = tk.StringVar()
        self.stage_var.set("Not running")
        self.status_plug = tk.StringVar()
        self.status_plug.set("Not running")

    @property
    def config(self):
        """Shortcut to the main exec's master configuration object."""
        return self.mainexec.mastercfg

    def start(self):
        """
        Control to start the GUI.
        """
        self.spawn_ui()
        self.root.mainloop()

    def spawn_ui(self):
        """
        Rev up that graphics card, baby!

        +----------------------------------------------------------------+
        | File | Options | About |                                 - o x |
        |                                                                |
        | +--------------+ +-------------------------+ +---------------+ |
        | | > builtin    | |                         | | |cfg|adv|doc| | |
        | | v developer  | |                         | |-+   +---------| |
        | |   dummy_load | |                         | | plugin config | |
        | |   user_pause | |         canvas          | |               | |
        | |              | |                         | |               | |
        | |              | |                         | |               | |
        | |              | |                         | |               | |
        | +--------------+ +-------------------------+ +---------------+ |
        |                                                                |
        | +------------------------------------------------------------+ |
        | | 123/456 (27%) [=============                             ] | |
        | | (Start) (Stop) __ status text goes here __                 | |
        | +------------------------------------------------------------+ |
        +----------------------------------------------------------------+
        """
        self.root.title("TrashBin Log Utility")
        self.root.resizable(True, True)
        # prevent making it too small, to the point of unrecoverability
        self.root.minsize(600, 250)

        self.root.grid_columnconfigure(0, weight=0, minsize=200)
        self.root.grid_columnconfigure(1, weight=1, minsize=400)
        self.root.grid_columnconfigure(2, weight=0, minsize=200)
        self.root.grid_rowconfigure(0, weight=1, minsize=200)
        self.root.grid_rowconfigure(1, weight=0, minsize=50)

        self.spawn_ui_menubar()
        self.spawn_ui_canvas()
        self.spawn_ui_plugtree()
        self.spawn_ui_plugopts()
        self.spawn_ui_status()

        self.update_plugin_list()

    def cb_save_plugins(self):
        filename = tkfd.asksaveasfilename(
                parent=self.root,
                title="Save TrashBin Plugin Config",
                filetypes=(
                    ("JSON text dump", "*.tbp"),
                    ("ZIP compressed dump", "*.tbz"),
                    ("all files", "*.*"),
                ),
            )
        self.mainexec.save_plugins(filename)

    def cb_load_plugins(self):
        filename = tkfd.askopenfilename(
                parent=self.root,
                title="Load TrashBin Plugin Config",
                filetypes=(
                    ("TrashBin Plugin File", ".tbp .tbz"),
                    ("JSON text dump", "*.tbp"),
                    ("ZIP compressed dump", "*.tbz"),
                    ("all files", "*.*"),
                ),
            )
        self.mainexec.load_plugins(filename)

    def cb_procoptions(self):
        pass

    def cb_open_config(self):
        """
        Callback to open configuration sub-UI.
        Actual UI is provided by the configui module.
        """
        configui.ConfigurationEditorPanel(self)

    def spawn_ui_menubar(self):
        """
        Menu bar (along the top).
        """
        self.menu = menu = tk.Menu(self.root)

        menu_file = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='File', menu=menu_file)
        menu_opts = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Options', menu=menu_opts)

        menu_file.add_command(label="Save plugin configuration",
                command=self.cb_save_plugins)
        menu_file.add_command(label="Load plugin configuration",
                command=self.cb_load_plugins)

        menu_opts.add_command(label="Processing options",
                command=self.cb_procoptions)
        menu_opts.add_command(label="Configuration",
                command=self.cb_open_config)

        self.root.config(menu=self.menu)

    def spawn_ui_canvas(self):
        """
        Big white area for drag-and-drop stuff.
        """
        cframe = tk.Frame(self.root)
        cframe.grid(row=0, column=1, sticky='nesw')
        self.canvas = tk.Canvas(cframe, bg='white')
        self.canvas.pack(fill='both', expand=True)

    def spawn_ui_plugtree(self):
        """
        Plugin tree running down the side.
        """
        pframe = tk.Frame(self.root)
        pframe.grid(row=0, column=0, sticky='nesw')

        self.tree = ttk.Treeview(pframe)
        self.tree.grid(row=0, column=0, sticky='nesw')

        verscrlbar = ttk.Scrollbar(pframe, orient='vertical',
                command=self.tree.yview)
        verscrlbar.grid(row=0, column=1, sticky='nes')
        self.tree.configure(yscrollcommand=verscrlbar.set)

        #self.tree['columns'] = ('plugin',)
        self.tree['show'] = 'tree'
        self.tree['selectmode'] = 'browse'
        self.tree.bind('<<TreeviewSelect>>', self.cb_describe)
        self.tree.bind("<Double-1>", self.cb_loadsel)
        self.tree.column('#0', width=DEFAULT_MODULE_WIDTH, anchor='w')
        #self.tree.column('plugin', width=DEFAULT_PLUGIN_WIDTH)
        #self.tree.heading('#0', text="Module")
        #self.tree.heading('plugin', text="Plugin")

    def cb_describe(self, arg):
        pass

    def cb_loadsel(self, arg):
        selected = self.tree.item(self.tree.focus())
        print(selected)
        if len(selected['tags']) == 0:
            # selected a parent module, not a plugin.  nothing else to do here.
            return

        factory_name = selected['tags'][0]
        plugin_names = [p.__name__ for p in self.plugins_available]
        plugin_idx = plugin_names.index(factory_name)

        plugin = self.mainexec.add_plug_by_idx(plugin_idx)

    def update_plugin_list(self):
        """
        Queries the available plugins, then generates the tree of them displayed
        in the GUI plugin loader panel.
        """
        self.plugins_available = _pad.plugin_list()[1]

        # build the tree first as a dictionary
        # {'developer': {
        #   'submodule': {
        #       'file': {plugin}
        # }}}
        tree = {}
        for plugin in self.plugins_available:
            # import name, with src.plugins removed.  ex., "developer.debugger"
            modpath = plugin.__module__.split('.')[2:]

            # dive to the bottom of the tree for this module, and add the plugin
            # to it
            elem = tree
            for mod in modpath:
                try:
                    elem = elem[mod]
                except KeyError:
                    # not present, add it
                    elem[mod] = {}
                    elem = elem[mod]

            elem[plugin.__name__] = plugin

        # recursively add the dictionary-based tree structure to the GUI
        def rcr_addtree(root, tree):
            for key, item in tree.items():
                if isinstance(item, dict):
                    # subtree.  add an element, then recurse on it
                    self.tree.insert(root, 'end', key, text=key)
                    rcr_addtree(key, item)
                else:
                    # plugin.  add the element, but don't recurse
                    self.tree.insert(root, 'end', key, text=item.plugin_name,
                            tags=[item.__name__])

        rcr_addtree('', tree)

    def spawn_ui_plugopts(self):
        """
        Plugin options running down the (other) side.
        """
        pframe = tk.Frame(self.root)
        pframe.grid(row=0, column=2, sticky='nesw')

        tk.Label(pframe, text="Options frame!").grid(row=0, column=0, sticky='nesw')

    def spawn_ui_status(self):
        """
        Status information along the bottom.
        """
        sframe = tk.Frame(self.root)
        sframe.grid(row=1, column=0, columnspan=3, sticky='nesw')

        tk.Label(sframe, text="----- Status frame! -----").grid(row=0,
                column=0, sticky='nesw')

if __name__ == '__main__':
    panel = FlowPanelUI(None)
    panel.start()

