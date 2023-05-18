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
from src.plugins import _plugin_autodetect as _pad
import src.gui.pluginloader as pluginloader
import src.config.config as config
import src.gui.configui as configui


class MainPanelUI(object):
    """
    Creates the main 3-panel graphical user inyerface (GUI).
    """

    def __init__(self, mainexec):
        self.mainexec = mainexec
        self.available_factories = []
        self.root = tk.Tk()
        self.pbar_var = tk.IntVar()
        self.pbar_var.set(0)
        self.status_var = tk.StringVar()
        self.status_var.set("Waiting for start")
        self.stage_var = tk.StringVar()
        self.stage_var.set("Not running")
        self.status_plug = tk.StringVar()
        self.status_plug.set("Not running")
        self._plugui = None

    def start(self):
        self.spawn_ui()
        self.root.mainloop()

    @property
    def config(self):
        return self.mainexec.mastercfg

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
        return self.mainexec.factmap.values()

    def spawn_ui(self):
        self.root.title("TrashBin Log Utility")
        
        self.spawn_ui_menubar()
        self.spawn_ui_frame1()
        self.spawn_ui_frame2()
        self.spawn_ui_frame3()
        self.spawn_ui_frame4()

        self.root.resizable(False, False)

        if self.config['debug']:
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
        self.mainexec.set_files(self.ui_filelistbox.get(0, tk.END))

    def cb_rm_files(self):
        """
        Callback to remove file(s) from our input file list
        """
        selected = self.ui_filelistbox.curselection()
        # delete in reverse to prevent over-indexing
        for i in selected[::-1]:
            self.ui_filelistbox.delete(i)
        self.mainexec.set_files(self.ui_filelistbox.get(0, tk.END))

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
        self.mainexec.set_files(self.ui_filelistbox.get(0, tk.END))

    def cb_add_dirs(self):
        newdir = tkfd.askdirectory(
                parent=self.root, title="Folder selection",
                )
        self.ui_dirlistbox.insert(1, newdir)
        self.mainexec.set_dirs(self.ui_dirlistbox.get(0, tk.END))

    def cb_rm_dirs(self):
        selected = self.ui_dirlistbox.curselection()
        for i in selected[::-1]:
            self.ui_dirlistbox.delete(i)
        self.mainexec.set_dirs(self.ui_dirlistbox.get(0, tk.END))

    def cb_rm_all_dirs(self):
        for i in range(len(self.config.inputs['directories']))[::-1]:
            self.ui_dirlistbox.delete(i)
        self.mainexec.set_dirs([])

    def cb_rawtextvar_changed(self, *args):
        self.config.inputs['rawtext'] = self.rawtextentry.get('1.0', tk.END)

    def cb_add_plugs(self):
        """
        Callback to load factory(s) from the available plugin list.
        Plugin list is provided by the factory manager.
        """
        self.available_factories = _pad.plugin_list()[1]
        plp = pluginloader.PluginLoaderPanel(self, self.available_factories)

    def cb_open_config(self):
        """
        Callback to open configuration sub-UI.
        Actual UI is provided by the configui module.
        """
        configui.ConfigurationEditorPanel(self)

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
        targ = list(self.mainexec.factmap.keys())[i]
        self.mainexec.factmap = {k:v for k, v in self.mainexec.factmap.items() if k != targ}

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
        self.mainexec.factmap = {}

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
        if self.config['debug']:
            print("Handling go button")
        # start
        if self.config['debug']:
            print("Starting processor")
        self.pbar['maximum'] = self.mainexec.processor.max_work
        self.pbar_var.set(0)
        self.btn_go.config(text="Stop")
        self.mainexec.go()
        self.update_startstop_btns()

    def cb_stop(self):
        """
        Callback to handle the stop button press.
        """
        if self.config['debug']:
            print("Handing stop button")
        self.mainexec.stop()
        self.update_startstop_btns()
        #self.pbar_var.set(0)
        self.update_startstop_btns()

    def update_startstop_btns(self):
        """
        Fix enable/disable state.
        """
        if self.mainexec.active:
            self.btn_go.config(state='disabled')
            self.btn_stop.config(state='normal')
        else:
            self.btn_go.config(state='normal')
            self.btn_stop.config(state='disabled')

    def cb_plugselect(self, event):
        """
        Callback for what do when a factory is selected.
        """
        try:
            idx = self.ui_pluglistbox.curselection()[0]
        except IndexError:
            # no selection
            idx = None
            # happens when user tabs or interacts with something out of focus
            # we usually don't want to clear the plugUI in this case, as the
            # focus may have gone over there -- and we shouldn't destroy that
            # UI from under the user
            return

        # first thing to do is destroy the old ui if it's still up
        if not (self._plugui is None):
            if self.config['debug']:
                print("Removing old plugin UI")
            try:
                self._plugui.stop_ui(self.frame3)
            except Exception as e:
                if self.config['debug']:
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
        for key, val in self.mainexec.factmap.items():
            if val.plugin_name == plugname:
                self._plugui = val
                break
        # mark as active & setup new factory UI!
        if self.config['debug']:
            print("Starting new plugin UI")
        try:
            # clean up frame3 before handing it off
            self.frame3.destroy()
            del self.frame3
            self.spawn_ui_frame3()
            self._plugui.start_ui(self.frame3)
        except:
            if self.config['debug']:
                raise
            else:
                pass
        finally:
            self._plugui.is_active = True

    def notify_work_done(self, amt=1):
        self.pbar_var.set(self.pbar_var.get() + amt)

    def notify_done(self):
        self.btn_go.config(text="Done! (Click to restart)")

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
        
        menu_opts.add_command(label="Processing options",
                command=self.cb_procoptions)
        menu_opts.add_command(label="Configuration",
                command=self.cb_open_config)

        self.root.config(menu=self.menu)

    def spawn_ui_frame1(self):
        """
        Spawns the left frame for adding files
        """
        self.frame1 = tk.LabelFrame(self.root, text="Inputs", relief=tk.RIDGE)
        notebook = ttk.Notebook(self.frame1)
        notebook.grid(row=0, column=0, sticky='nsew')



        self.frame1.grid(row=0, column=0)

        fileframe = tk.Frame(notebook)
        notebook.add(fileframe, text="Files")
        fileframe.grid_columnconfigure(0, weight=1, uniform='a')
        fileframe.grid_columnconfigure(1, weight=1, uniform='a')

        self.ui_filelistbox = tk.Listbox(fileframe, height=20, width=40,
                selectmode='multiple')
        self.ui_filelistbox.grid(row=0, column=0, columnspan=2)

        # we don't need to save this for anything later on
        addfilebtn = tk.Button(fileframe, text="Add File(s)",
                command=self.cb_add_files)
        addfilebtn.grid(row=1, column=0, columnspan=2, sticky='nesw')

        rmfilebtn = tk.Button(fileframe, text='Remove Selected',
                command=self.cb_rm_files)
        rmfilebtn.grid(row=2, column=0, sticky='nesw')
        rmallbtn = tk.Button(fileframe, text='Remove All',
                command=self.cb_rm_all_files)
        rmallbtn.grid(row=2, column=1, sticky='nesw')

        dirframe = tk.Frame(notebook)
        notebook.add(dirframe, text="Folders")
        dirframe.grid_columnconfigure(0, weight=1, uniform='a')
        dirframe.grid_columnconfigure(1, weight=1, uniform='a')

        self.ui_dirlistbox = tk.Listbox(dirframe, height=20, width=40,
                selectmode='multiple')
        self.ui_dirlistbox.grid(row=0, column=0, columnspan=2)

        # we don't need to save this for anything later on
        adddirbtn = tk.Button(dirframe, text="Add Folder(s)",
                command=self.cb_add_dirs)
        adddirbtn.grid(row=1, column=0, columnspan=2, sticky='nesw')

        rmdirbtn = tk.Button(dirframe, text='Remove Selected',
                command=self.cb_rm_dirs)
        rmdirbtn.grid(row=2, column=0, sticky='nesw')
        rmalldirbtn = tk.Button(dirframe, text='Remove All',
                command=self.cb_rm_all_dirs)
        rmalldirbtn.grid(row=2, column=1, sticky='nesw')


        textframe = tk.Frame(notebook)
        notebook.add(textframe, text="Raw text")

        self.rawtextentry = tk.Text(textframe, height=1, width=1)
        textframe.grid_columnconfigure(0, weight=1)
        textframe.grid_rowconfigure(0, weight=1)
        self.rawtextentry.grid(row=0, column=0, sticky='nesw')
        textappbtn = tk.Button(textframe, text="Apply",
                command=self.cb_rawtextvar_changed)
        textappbtn.grid(row=1, column=0, sticky='news')


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

        self.btn_stop = tk.Button(self.frame4, text="Stop",
                command=self.cb_stop)
        self.btn_stop.grid(row=0, column=1, sticky='nesw')

        els = [
            tk.Label(self.frame4, text="Stage:"),
            tk.Label(self.frame4, textvariable=self.stage_var),
            tk.Label(self.frame4, text="Plugin:"),
            tk.Label(self.frame4, textvariable=self.status_plug),
            tk.Label(self.frame4, text="Status:"),
            tk.Label(self.frame4, textvariable=self.status_var)
            ]
        i = 2
        for el in els:
            el.grid(row=0, column=i, sticky='nsw')
            i += 1

        self.update_startstop_btns()

        self.pbar = ttk.Progressbar(self.frame4, orient='horizontal',
                length=self.frame4.winfo_width(), mode='determinate',
                variable=self.pbar_var, maximum=100)
        self.pbar.grid(row=1, column=0, columnspan=i, sticky='sw')

