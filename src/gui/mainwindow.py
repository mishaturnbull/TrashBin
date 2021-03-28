#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Main GUI window.

Responsible for starting and delegating tasks.
"""

import tkinter as tk
import tkinter.filedialog as tkfd
from tkinter import ttk
import os
import src.logutils.DFReader as dfr
import src.plugins._plugin_autodetect as _pad


class PluginLoaderPanel(object):
    """
    Creates the plugin load selector user interface.
    """

    def __init__(self, root, plugins_available):
        self.parent = root
        self.plugins_available = plugins_available
        self.selected = []
        self.spawn_ui()

    def spawn_ui(self):
        """
        Spawns UI components.
        """
        self.root = tk.Toplevel(self.parent)
        self.root.resizable(False, False)

        # plugin listbox and scrollbar
        listframe = tk.Frame(self.root)
        listframe.grid(row=0, column=0)
        self.pluginselbox = tk.Listbox(listframe, height=20, width=40,
                selectmode="multiple")
        self.pluginselbox.pack(side=tk.LEFT, fill=tk.BOTH)
        scrollbar = tk.Scrollbar(listframe)
        scrollbar.grid(side=tk.RIGHT, fill=tk.BOTH)
        self.pluginselbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.pluginselbox.yview)


class MainPanelUI(object):
    """
    Creates the main 3-panel graphical user inyerface (GUI).
    """

    def __init__(self):
        self.plugins = []
        self.children = []
        self.root = tk.Tk()
        self.processor = None
        self.debug = tk.BooleanVar()
        self.debug.set(False)
        self.pbar_var = tk.IntVar()
        self.pbar_var.set(0)

        self.spawn_ui()
        self.root.mainloop()

    @property
    def files(self):
        try:
            return list(self.ui_filelistbox.get(0, tk.END))
        except AttributeError:
            # ui_filelistbox doesn't exist yet
            return []

    def spawn_ui(self):
        self.root.title("TrashBin Log Utility")
        
        self.spawn_ui_menubar()
        self.spawn_ui_frame1()
        self.spawn_ui_frame2()
        self.spawn_ui_frame3()
        self.spawn_ui_frame4()

    def cb_save_plugins(self):
        pass

    def cb_load_plugins(self):
        pass

    def cb_options(self):
        pass

    def cb_add_files(self):
        """
        Callback to add file(s) to our input file list.
        """
        newfiles = tkfd.askopenfilenames(
                parent=self.root, title="Log selection",
                filetypes=(("Binary logs", "*.bin"),("Text logs", "*.log"),
                    ("All files",'*')))
        # add the files to our list and UI listbox
        # eliminate duplicates at the same time
        for newfile in newfiles:
            if newfile in self.files:
                continue
            self.ui_filelistbox.insert(1, newfile)
    
    def cb_rm_files(self):
        """
        Callback to remove file(s) from our input file list
        """
        selected = self.ui_filelistbox.curselection()
        # delete in reverse to prevent over-indexing
        for i in selected[::-1]:
            self.ui_filelistbox.delete(i)

    def cb_add_plugs(self):
        """
        Callback to load plugin(s) from the available plugin list.
        Plugin list is provided by the plugin manager.
        """
        available_plugins = _pad.plugin_list()

    def cb_rm_plugs(self):
        pass

    def cb_go(self):
        pass

    def cb_plugselect(self):
        pass

    def spawn_ui_menubar(self):
        """
        Spawns the menu bar along the top
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
        
        menu_opts.add_checkbutton(label="Debug",
                onvalue=1, offvalue=0,
                variable=self.debug)
        menu_opts.add_command(label="Options",
                command=self.cb_options)

        self.root.config(menu=self.menu)

    def spawn_ui_frame1(self):
        """
        Spawns the left frame for adding files
        """
        self.frame1 = tk.LabelFrame(self.root, text="File selection",
                relief=tk.RIDGE)
        self.frame1.grid(row=0, column=0)

        self.ui_filelistbox = tk.Listbox(self.frame1, height=20, width=40,
                selectmode='multiple')
        self.ui_filelistbox.grid(row=0, column=0)

        # we don't need to save this for anything later on
        addfilebtn = tk.Button(self.frame1, text="Add File(s)",
                command=self.cb_add_files)
        addfilebtn.grid(row=1, column=0, sticky='nesw')

        rmfilebtn = tk.Button(self.frame1, text='Remove File(s)',
                command=self.cb_rm_files)
        rmfilebtn.grid(row=2, column=0, sticky='nesw')
    
    def spawn_ui_frame2(self):
        """
        Spawns the middle frame for adding/listing plugins
        """
        self.frame2 = tk.LabelFrame(self.root, text="Plugin selection",
                relief=tk.RIDGE)
        self.frame2.grid(row=0, column=1)

        self.ui_pluglistbox = tk.Listbox(self.frame2, height=20, width=40)
        self.ui_pluglistbox.grid(row=0, column=0)
        self.ui_pluglistbox.bind("<<ListboxSelect>>", self.cb_plugselect)

        # again, don't need to save these for later, just the callbacks
        addplugbtn = tk.Button(self.frame2, text="Add Plugin(s)",
                command=self.cb_add_plugs)
        addplugbtn.grid(row=1, column=0, sticky='nesw')

        rmplugbtn = tk.Button(self.frame2, text='Remove Plugin(s)',
                command=self.cb_rm_plugs)
        rmplugbtn.grid(row=2, column=0, sticky='nesw')

    def spawn_ui_frame3(self):
        """
        Spawns the right frame for plugin-specific options
        """
        # need to determine the size of frame2 to set this one equal to it
        # first, you have to force an update
        self.frame2.update()
        # then, get the size and parse it
        geo = self.frame2.winfo_geometry()
        width = int(geo.split('x')[0])
        height = int(geo.split('x')[1].split('+')[0])
        # and then set it in the instantiator
        self.frame3 = tk.LabelFrame(self.root, text="Plugin configuration",
                relief=tk.RIDGE, width=width, height=height)
        self.frame3.grid(row=0, column=2, sticky='nesw')

    def spawn_ui_frame4(self):
        """
        Spawns the bottom frame for go button and loading bar.
        """
        self.frame4 = tk.LabelFrame(self.root, text="Progress",
                relief=tk.RIDGE)
        self.frame4.grid(row=1, column=0, columnspan=3, sticky='nesw')
        # we'll force an update now to set the progress bar to the full width
        # shortly
        self.frame4.update()

        self.btn_go = tk.Button(self.frame4, text="Start",
                command=self.cb_go)
        self.btn_go.grid(row=0, column=0, sticky='nesw')

        self.pbar = ttk.Progressbar(self.frame4, orient='horizontal',
                length=self.frame4.winfo_width(), mode='indeterminate',
                variable=self.pbar_var)
        self.pbar.grid(row=1, column=0, sticky='sw')

