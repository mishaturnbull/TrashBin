#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Main GUI window.

Responsible for starting and delegating tasks.
"""

import tkinter as tk
import tkinter.filedialog as tkfd
import tkinter.messagebox as tkmb
from tkinter import ttk
import os
import src.logutils.DFReader as dfr
import src.plugins._plugin_autodetect as _pad


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


class MainPanelUI(object):
    """
    Creates the main 3-panel graphical user inyerface (GUI).
    """

    def __init__(self):
        self.available_plugins = []
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

    @property
    def plugins(self):
        try:
            l = list(self.ui_pluglistbox.get(0, tk.END))
        except AttributeError:
            # it doesn't exist yet, or is empty...
            return []
        # the box only stores the string name, not the actual plugin.  we have
        # to correlate that back to the actual plugin object here
        plugins = []
        for pname in l:
            for availplug in self.available_plugins:
                if availplug.plugin_name == pname:
                    plugins.append(availplug)
        return plugins

    def spawn_ui(self):
        self.root.title("TrashBin Log Utility")
        
        self.spawn_ui_menubar()
        self.spawn_ui_frame1()
        self.spawn_ui_frame2()
        self.spawn_ui_frame3()
        self.spawn_ui_frame4()

        self.root.resizable(False, False)

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

    def cb_rm_all_files(self):
        """
        Callback to remove all files from the input file list
        """
        # if we have more than 5 files, check with the user
        if len(self.files) >= 5:
            res = tkmb.askyesno("Remove All", "Are you sure you want to " \
                    "remove all input files?")
            if not res:
                # they said no
                return
        for i in range(len(self.files))[::-1]:
            self.ui_filelistbox.delete(i)

    def cb_add_plugs(self):
        """
        Callback to load plugin(s) from the available plugin list.
        Plugin list is provided by the plugin manager.
        """
        self.available_plugins = _pad.plugin_list()
        plp = PluginLoaderPanel(self, self.available_plugins)

    def cb_rm_plugs(self):
        """
        Callback to remove selected plugin(s) from the input list.
        """
        selected = self.ui_pluglistbox.curselection()
        for i in selected[::-1]:
            self.ui_pluglistbox.delete(i)

    def cb_rm_all_plugs(self):
        """
        Callback to remove all currently listed plugins.
        """
        if len(self.plugins) >= 5:
            res = tkmb.askyesno("Remove All", "Are you sure you want to " \
                    "unload all plugins?")
            if not res:
                # they said no
                return
        for i in range(len(self.plugins))[::-1]:
            self.ui_pluglistbox.delete(i)

    def cb_plug_up(self):
        pass

    def cb_plug_dn(self):
        pass

    def cb_go(self):
        pass

    def cb_plugselect(self, event):
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
        self.frame1.grid_columnconfigure(0, weight=1, uniform='a')
        self.frame1.grid_columnconfigure(1, weight=1, uniform='a')

        self.ui_filelistbox = tk.Listbox(self.frame1, height=20, width=40,
                selectmode='multiple')
        self.ui_filelistbox.grid(row=0, column=0, columnspan=2)

        # we don't need to save this for anything later on
        addfilebtn = tk.Button(self.frame1, text="Add File(s)",
                command=self.cb_add_files)
        addfilebtn.grid(row=1, column=0, columnspan=2, sticky='nesw')

        rmfilebtn = tk.Button(self.frame1, text='Remove Selected',
                command=self.cb_rm_files)
        rmfilebtn.grid(row=2, column=0, sticky='nesw')
        rmallbtn = tk.Button(self.frame1, text='Remove All',
                command=self.cb_rm_all_files)
        rmallbtn.grid(row=2, column=1, sticky='nesw')
    
    def spawn_ui_frame2(self):
        """
        Spawns the middle frame for adding/listing plugins
        """
        # we want this frame to be the same size as the first one, so 
        # force an update then use its width and height in the instantiator
        self.frame1.update()
        self.frame2 = tk.LabelFrame(self.root, text="Plugin selection",
                relief=tk.RIDGE, width=self.frame1.winfo_width(),
                height=self.frame1.winfo_height())
        self.frame2.grid(row=0, column=1, sticky='nesw')
        self.frame2.grid_propagate(0)
        self.frame2.grid_columnconfigure(0, weight=1, uniform='a')
        self.frame2.grid_columnconfigure(1, weight=1, uniform='a')
        self.frame2.grid_rowconfigure(0, weight=1)

        self.ui_pluglistbox = tk.Listbox(self.frame2)
        self.ui_pluglistbox.grid(row=0, column=0, columnspan=2, sticky='nesw')
        self.ui_pluglistbox.grid_rowconfigure(0, weight=1)
        self.ui_pluglistbox.grid_columnconfigure(0, weight=1)
        self.ui_pluglistbox.bind("<<ListboxSelect>>", self.cb_plugselect)

        plugupbtn = tk.Button(self.frame2, text="Move plugin up",
                command=self.cb_plug_up)
        plugupbtn.grid(row=1, column=0, columnspan=2, sticky='esw')
        
        plugdnbtn = tk.Button(self.frame2, text="Move plugin down",
                command=self.cb_plug_dn)
        plugdnbtn.grid(row=2, column=0, columnspan=2, sticky='esw')

        addplugbtn = tk.Button(self.frame2, text="Add Plugin(s)",
                command=self.cb_add_plugs)
        addplugbtn.grid(row=3, column=0, columnspan=2, sticky='esw')

        rmplugbtn = tk.Button(self.frame2, text='Remove Selected',
                command=self.cb_rm_plugs)
        rmplugbtn.grid(row=4, column=0, sticky='esw')
        rmallbtn = tk.Button(self.frame2, text='Remove All',
                command=self.cb_rm_all_plugs)
        rmallbtn.grid(row=4, column=1, sticky='esw')

    def spawn_ui_frame3(self):
        """
        Spawns the right frame for plugin-specific options
        """
        self.frame3 = tk.LabelFrame(self.root, text="Plugin configuration",
                relief=tk.RIDGE, width=self.frame1.winfo_width(),
                height=self.frame1.winfo_height())
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

