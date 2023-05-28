#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file provides the main, flow-esque panel for the user interface.
"""

import tkinter as tk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb
from tkinter import ttk
import src.gui.pluginloader as pluginloader
import src.config.config as config
import src.gui.configui as configui


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
        | +------------------------------------------+  +--------------+ |
        | |                                          |  | > builtin    | |
        | |                                          |  | v developer  | |
        | |                                          |  |   dummy_load | |
        | |                 canvas                   |  |   user_pause | |
        | |                                          |  |              | |
        | |                                          |  |              | |
        | |                                          |  |              | |
        | +------------------------------------------+  +--------------+ |
        |                                                                |
        | +------------------------------------------------------------+ |
        | | 123/456 (27%) [=============                             ] | |
        | | [Stage: files]  [Plugin: whatever] [Status: computing pi]  | |
        | +------------------------------------------------------------+ |
        +----------------------------------------------------------------+
        """
        self.root.title("TrashBin Log Utility")
        self.root.resizable(True, True)

        self.spawn_ui_menubar()
        self.spawn_ui_canvas()
        self.spawn_ui_plugins()
        self.spawn_ui_status()

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
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        cframe.grid(row=0, column=0, sticky='nesw')
        self.canvas = tk.Canvas(cframe, bg='white')
        self.canvas.pack(fill='both', expand=True)

    def spawn_ui_plugins(self):
        """
        Plugin tree running down the side.
        """
        pframe = tk.Frame(self.root)
        pframe.grid(row=0, column=1, sticky='nesw')

        tk.Label(pframe, text="    Plugin frame!    ").grid(row=0, column=0,
                sticky='nesw')

    def spawn_ui_status(self):
        """
        Status information along the bottom.
        """
        sframe = tk.Frame(self.root)
        sframe.grid(row=1, column=0, columnspan=2, sticky='nesw')

        tk.Label(sframe, text="----- Status frame! -----").grid(row=0,
                column=0, sticky='nesw')

if __name__ == '__main__':
    panel = FlowPanelUI(None)
    panel.start()

