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
import time
import src.logutils.DFReader as dfr
import src.plugins._plugin_autodetect as _pad
import src.plugins.persist as persist
import src.gui.pluginloader as pluginloader

# the processor selection isn't as user-importable as plugins, we just import
# them all and then pick
import src.processor.singlethread as singlethread


class MainPanelUI(object):
    """
    Creates the main 3-panel graphical user inyerface (GUI).
    """

    def __init__(self):
        self.available_factories = []
        self.root = tk.Tk()
        self.debug = tk.BooleanVar()
        self.debug.set(False)
        self.pbar_var = tk.IntVar()
        self.pbar_var.set(0)
        self._plugui = None
        self.factmap = {}

        self.spawn_ui()
        self.processor = singlethread.SingleThreadProcessor(self)
        self.root.mainloop()

    @property
    def files(self):
        try:
            return list(self.ui_filelistbox.get(0, tk.END))
        except AttributeError:
            # ui_filelistbox doesn't exist yet
            raise
            return []

    @property
    def factory_classes(self):
        try:
            l = list(self.ui_pluglistbox.get(0, tk.END))
        except AttributeError:
            # it doesn't exist yet, or is empty...
            return []
        # the box only stores the string name, not the actual factory.  we have
        # to correlate that back to the actual factory object here
        factories = []
        for pname in l:
            for availplug in self.available_factories:
                if availplug.plugin_name == pname:
                    factories.append(availplug)
        return factories

    @property
    def factories(self):
        return self.factmap.values()

    def spawn_ui(self):
        self.root.title("TrashBin Log Utility")
        
        self.spawn_ui_menubar()
        self.spawn_ui_frame1()
        self.spawn_ui_frame2()
        self.spawn_ui_frame3()
        self.spawn_ui_frame4()

        self.root.resizable(False, False)

        if self.debug.get():
            print("UI setup complete")

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
        if os.path.splitext(filename)[1].endswith('tbz'):
            if self.debug.get():
                print("Saving to zip-wrapped file")
            persist.write_zip_file(filename, list(self.factmap.values()))
        else:
            if self.debug.get():
                print("Saving to JSON file")
            persist.write_text_file(filename, list(self.factmap.values()))

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
        if os.path.splitext(filename)[1].endswith("tbz"):
            if self.debug.get():
                print("Reading zip-wrapped file")
            factories = persist.load_zip_file(filename, self)
        else:
            if self.debug.get():
                print("Reading JSON file")
            factories = persist.load_text_file(filename, self)
        if self.debug.get():
            print("Got list of factories: {}".format(factories))
        for factory in factories:
            self.factmap.update({factory.uuid: factory})
            self.ui_pluglistbox.insert(tk.END, factory.plugin_name)

    def cb_procoptions(self):
        pass

    def cb_add_files(self):
        """
        Callback to add file(s) to our input file list.
        """
        for a, b in self.factmap.items():
            print(a, b.__dict__)
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
        Callback to load factory(s) from the available plugin list.
        Plugin list is provided by the factory manager.
        """
        self.available_factories = _pad.plugin_list()[1]
        plp = pluginloader.PluginLoaderPanel(self, self.available_factories)

    def cb_rm_plugs(self):
        """
        Callback to remove selected factory(s) from the input list.
        """
        selected = self.ui_pluglistbox.curselection()
        for i in selected[::-1]:
            self.ui_pluglistbox.delete(i)
        self.ui_pluglistbox.selection_clear(0, tk.END)
        # now that selection has been cleared, invoke the selected cb to
        # remove UI elements and cleanup the factory
        self.cb_plugselect(None)
        # now we need to find and remove that one from the factory map
        targ = list(self.factmap.keys())[i]
        self.factmap = {k:v for k, v in self.factmap.items() if k != targ}

    def cb_rm_all_plugs(self):
        """
        Callback to remove all currently listed factories.
        """
        if len(self.factories) >= 5:
            res = tkmb.askyesno("Remove All", "Are you sure you want to " \
                    "unload all plugins?")
            if not res:
                # they said no
                return
        self.ui_pluglistbox.selection_clear(0, tk.END)
        for i in range(len(self.factories))[::-1]:
            self.ui_pluglistbox.delete(i)
            self.cb_plugselect(None)
        self.factmap = {}

    def cb_plug_up(self):
        """
        Callback to move a factory up the chain.
        """
        idx = self.ui_pluglistbox.curselection()[0]
        # check if we're at the top (or the only one)
        if idx == 0:
            # nothing to do!
            return
        item = self.ui_pluglistbox.get(idx)
        self.ui_pluglistbox.delete(idx)
        self.ui_pluglistbox.insert(idx - 1, item)
        self.ui_pluglistbox.selection_set(idx - 1)

    def cb_plug_dn(self):
        """
        Callback to move a factory down the chain.
        """
        idx = self.ui_pluglistbox.curselection()[0]
        # are we at the bottom
        if idx == len(self.factories) - 1:
            return
        item = self.ui_pluglistbox.get(idx)
        self.ui_pluglistbox.delete(idx)
        self.ui_pluglistbox.insert(idx + 1, item)
        self.ui_pluglistbox.selection_set(idx + 1)

    def cb_go(self):
        """
        Callback to handle the start(/stop) button press.
        """
        if self.debug.get():
            print("Handling go button")
        if not self.processor.active:
            # start
            if self.debug.get():
                print("Starting processor")
            self.processor.update()
            self.processor.reinit()
            self.pbar['maximum'] = self.processor.max_work
            self.pbar_var.set(0)
            self.btn_go.config(text="Stop")
            self.processor.active = True
            self.processor.run()
        else:
            # inactive
            self.processor.stop()
            self.btn_go.config(text="Start")
            self.processor.active = False
            self.pbar_var.set(0)

    def cb_plugselect(self, event):
        """
        Callback for what do when a factory is selected.
        """
        try:
            idx = self.ui_pluglistbox.curselection()[0]
        except IndexError:
            # no selection
            idx = None
        # first thing to do is destroy the old ui if it's still up
        if not (self._plugui is None):
            if self.debug.get():
                print("Removing old plugin UI")
            try:
                self._plugui.stop_ui(self.frame3)
            except Exception as e:
                if self.debug.get():
                    raise
                else:
                    pass
            finally:
                self._plugui.is_active = False
        self._plugui = None
        # ok, old factory ui is out of the way now
        # check if anything is actually selected
        if idx is None:
            # nope, get outta here
            return
        plugname = self.ui_pluglistbox.get(idx)
        # load the real factory - have to search through our .factmap dict
        for key, val in self.factmap.items():
            if val.plugin_name == plugname:
                self._plugui = val
                break
        # mark as active & setup new factory UI!
        if self.debug.get():
            print("Starting new plugin UI")
        try:
            self._plugui.start_ui(self.frame3)
        except:
            if self.debug.get():
                raise
            else:
                pass
        finally:
            self._plugui.is_active = True

    def notify_work_done(self, amt=1):
        self.pbar_var.set(self.pbar_var.get() + amt)

    def notify_done(self):
        self.btn_go.config(text="Done! (Click to restart)")
        self.processor.active = False

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
        menu_opts.add_command(label="Processing options",
                command=self.cb_procoptions)

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
        self.frame3.grid_propagate(0)
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
                length=self.frame4.winfo_width(), mode='determinate',
                variable=self.pbar_var, maximum=100)
        self.pbar.grid(row=1, column=0, sticky='sw')

