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
import json
import os

import src.config.config as config

DEFAULT_ITEM_WIDTH = 150
DEFAULT_TYPE_WIDTH = 90
DEFAULT_VALUE_WIDTH = 350
DEFAULT_ENTRY_WIDTH = 50  # chars

_TYPE_NULL = 0
_TYPE_STR = 1
_TYPE_NUM = 2
_TYPE_OBJ = 3
_TYPE_ARR = 4
_TYPE_BOOL = 5

def conv_num(x):
    try:
        return int(x)
    except ValueError:
        return float(x)

_TYPE_CONVS = [
        lambda x: None,
        str,
        conv_num,
        json.loads,
        lambda x: [x],
        lambda x: False if (x == 'False') else bool(x)
    ]

class ConfigurationEditorPanel(object):

    def __init__(self, parent):
        self.parent = parent
        self.trmap = {}

        self.slotsel = tk.StringVar()
        self.slotsel.set("Select config...")
        self.slotsel.trace('w', self.cb_slotsel_changed)
        self.activeslot = None
        self.uifilepath = tk.StringVar()
        self.edittype = tk.IntVar()
        self.edittype.set(_TYPE_NULL)
        self.editkey = tk.StringVar()
        self.editval = tk.StringVar()
        self.spawn_ui()
        self.cb_load()

    def spawn_ui(self):
        self.root = tk.Toplevel(self.parent.root)
        self.root.wait_visibility()
        self.root.grab_set()
        self.root.resizable(True, True)

        topframe = tk.Frame(self.root)
        treeframe = tk.Frame(self.root)
        editframe = tk.Frame(self.root)

        self.cbSlot = ttk.Combobox(topframe, textvariable=self.slotsel,
                values=self.parent.config.slotfilenames)
        self.cbSlot.grid(row=0, column=0, sticky='news')
        btnAddSlot = tk.Button(topframe, text="Add to slots",
                command=self.cb_addslot)
        btnAddSlot.grid(row=0, column=1, sticky='news')
        btnRemSlot = tk.Button(topframe, text="Remove slot",
                command=self.cb_rmslot)
        btnRemSlot.grid(row=0, column=2, sticky='news')
        btnSave = tk.Button(topframe, text="Save",
                command=self.cb_save)
        btnSave.grid(row=1, column=0, sticky='news')
        btnLoad = tk.Button(topframe, text="Load / New",
                command=self.cb_load)
        btnLoad.grid(row=1, column=1, sticky='news')
        btnPick = tk.Button(topframe, text="Select file",
                command=self.cb_pick)
        btnPick.grid(row=1, column=2, sticky='nwes')
        entryFile = tk.Entry(topframe, textvariable=self.uifilepath)
        entryFile.grid(row=2, column=0, columnspan=4, sticky='nesw')

        self.tree = ttk.Treeview(treeframe)
        self.tree.grid(row=0, column=0, sticky='nesw')

        verscrlbar = ttk.Scrollbar(treeframe, orient='vertical',
                command=self.tree.yview)
        verscrlbar.grid(row=0, column=1, sticky='nes')
        self.tree.configure(yscrollcommand=verscrlbar.set)

        self.tree['columns'] = ('type', 'value')
        self.tree['show'] = 'tree headings'
        self.tree['selectmode'] = 'browse'
        self.tree.bind('<<TreeviewSelect>>', self.cb_selected)
        self.tree.column('#0', width=DEFAULT_ITEM_WIDTH, anchor='w')
        self.tree.column('type', width=DEFAULT_TYPE_WIDTH)
        self.tree.column('value', width=DEFAULT_VALUE_WIDTH, anchor='e')
        self.tree.heading('#0', text="Item")
        self.tree.heading('type', text="Type")
        self.tree.heading('value', text="Value")

        addBtn = tk.Button(editframe, text='New', command=self.edit_new)
        addBtn.grid(row=0, column=0, sticky='nesw')
        delBtn = tk.Button(editframe, text='Delete', command=self.edit_del)
        delBtn.grid(row=1, column=0, sticky='nesw')
        updBtn = tk.Button(editframe, text='Apply', command=self.edit_apply)
        updBtn.grid(row=2, column=0, sticky='nesw')

        typeframe = tk.LabelFrame(editframe, text='Type', relief=tk.RIDGE)
        rbtnNull = tk.Radiobutton(typeframe, text='NULL',
                variable=self.edittype, value=_TYPE_NULL)
        rbtnStr = tk.Radiobutton(typeframe, text='String',
                variable=self.edittype, value=_TYPE_STR)
        rbtnNum = tk.Radiobutton(typeframe, text='Number',
                variable=self.edittype, value=_TYPE_NUM)
        rbtnObj = tk.Radiobutton(typeframe, text='Dict',
                variable=self.edittype, value=_TYPE_OBJ)
        rbtnBool = tk.Radiobutton(typeframe, text='Bool',
                variable=self.edittype, value=_TYPE_BOOL)
        rbtnArr = tk.Radiobutton(typeframe, text='Array',
                variable=self.edittype, value=_TYPE_ARR)
        rbtnStr.grid(row=0, column=1, sticky='nw')
        rbtnNum.grid(row=1, column=1, sticky='nw')
        rbtnBool.grid(row=2, column=1, sticky='nw')
        rbtnObj.grid(row=0, column=2, sticky='nw')
        rbtnArr.grid(row=1, column=2, sticky='nw')
        rbtnNull.grid(row=2, column=2, sticky='nw')
        typeframe.grid(row=0, column=1, rowspan=3, sticky='nesw')

        tk.Label(editframe, text="Key:").grid(row=3, column=0, sticky='nesw')
        tk.Label(editframe, text="Val:").grid(row=4, column=0, sticky='nesw')
        keyEntry = tk.Entry(editframe, textvariable=self.editkey)
        keyEntry.grid(row=3, column=1, sticky='nesw')
        valEntry = tk.Entry(editframe, textvariable=self.editval)
        valEntry.grid(row=4, column=1, sticky='nesw')

        insFileBtn = tk.Button(editframe, text="Pick file(s) into val",
                command=self.cb_ins_file)
        insFileBtn.grid(row=5, column=0, columnspan=2, sticky='new')
        insDirBtn = tk.Button(editframe, text="Pick folder into val",
                command=self.cb_ins_dir)
        insDirBtn.grid(row=6, column=0, columnspan=2, sticky='new')

        if self.parent.config['debug']:
            self.pathlbl = tk.Label(editframe)
            self.pathlbl.grid(row=7, column=0, columnspan=2, sticky='esw')

        topframe.grid_columnconfigure(0, weight=1, uniform='b')
        topframe.grid_columnconfigure(1, weight=1, uniform='b')
        topframe.grid_columnconfigure(2, weight=1, uniform='b')

        topframe.grid(row=0, column=0, sticky='nesw')
        treeframe.grid(row=1, column=0, sticky='nesw')
        editframe.grid(row=0, column=1, sticky='nesw', rowspan=2)

    def cb_ins_file(self):
        # get a filename from GUI picker and pass it off to the value
        filename = tkfd.askopenfilenames()
        self.editval.set(filename)

    def cb_ins_dir(self):
        # just like cb_ins_file but with directory
        dirname = tkfd.askdirectory()
        self.editval.set(dirname)

    def cb_slotsel_changed(self, *args):
        newname = self.slotsel.get()
        allfiles = self.parent.config.slotfilenames
        try:
            idx = allfiles.index(newname)
        except ValueError:
            # no such file
            self._clear_tree()
            return
        self.activeslot = self.parent.config.slots[idx]
        self.uifilepath.set(self.activeslot.filename)
        self._reload_after_edit()

    def cb_addslot(self):
        self.parent.config.load_new_config_from_file(self.uifilepath.get(),
                readonly=False, permanent=True)
        self.cbSlot['values'] = self.parent.config.slotfilenames
        self.slotsel.set(os.path.split(self.uifilepath.get())[1])
        self._reload_after_edit()

    def cb_rmslot(self):
        self.parent.config.remove_config_from_slots(self.activeslot)
        self.cbSlot['values'] = self.parent.config.slotfilenames
        self.slotsel.set("")
        self.uifilepath.set("")
        self._clear_tree()

    def cb_selected(self, event):
        try:
            sel = self.tree.selection()[0]
        except IndexError:
            # no selection was made
            # happens after some of the apply/edit callbacks
            return

        # resolve the path to the key
        path = []
        item = sel
        while True:
            path.append(self.trmap[item])
            item = self.tree.parent(item)

            #if (item != '') and (self.tree.item(item)['values'][0] == 'Dict'):

            # if we're in a list, convert the index to integer instead of str
            if self.tree.item(item)['text'].endswith('[]') and \
                    not (path[-1].endswith('[]')):
                path[-1] = int(path[-1])

            if item == '':
                break

        value = self.activeslot.data()
        for key in path[::-1]:
            value = value[key]

        self._path = path

        if self.parent.config['debug']:
            self.pathlbl.config(text=repr(path))

        self.update_editor_fields(path, value)

    def update_editor_fields(self, path, value):
        self.editkey.set(path[0])
        self.editval.set(str(value))
        tipe = type(value)
        if tipe in [int, float]:
            self.edittype.set(_TYPE_NUM)
        elif tipe in [str]:
            self.edittype.set(_TYPE_STR)
        elif tipe in [dict]:
            self.edittype.set(_TYPE_OBJ)
        elif tipe in [list, tuple]:
            self.edittype.set(_TYPE_ARR)
        elif tipe in [bool]:
            self.edittype.set(_TYPE_BOOL)
        elif value is None:
            self.edittype.set(_TYPE_NULL)
        else:
            self.edittype.set(-1)

    def edit_new(self):
        sel = self.tree.selection()
        dic = self.activeslot.data()
        if len(sel) > 0:
            # something is selected
            # if it's an array or dictionary, add new element under it
            # otherwise, add it adjacent to it
            if self.edittype.get() not in [_TYPE_OBJ, _TYPE_ARR]:
                self._path.remove(self._path[0])

            for key in self._path[::-1]:
                if not (isinstance(dic[key], dict) or \
                        isinstance(dic[key], list)):
                    break
                dic = dic[key]

            if len(self._path) == 0:
                dic = self.activeslot.data()

        newkey = self.editkey.get()
        newval = self.editval.get()
        typefunc = _TYPE_CONVS[self.edittype.get()]
        # sanity checking
        if isinstance(dic, list):
            try:
                newkey = int(newkey)
                if newkey > (len(dic) + 1):
                    tkmb.showwarning(title="Warning", message="Index is " \
                            "beyond the length of the list!  I'm shortening " \
                            "it to the end of the list for you.")
                    newkey = len(dic)
            except ValueError:
                tkmb.showerror(title="Error", message="Key must be an integer" \
                        " when inserting in an array!")
                return
        else:
            if newkey in dic.keys():
                tkmb.showerror("Error", message="Element already present in" \
                        " the object!")
                return

        # and finally, add the new item
        if isinstance(dic, list):
            dic.insert(newkey, typefunc(newval))
        else:
            # dictionary
            dic[newkey] = typefunc(newval)

        self._reload_after_edit()

    def edit_del(self):
        key = self.editkey.get()
        dic = self.activeslot.data()
        for key in self._path[::-1]:
            if not (isinstance(dic[key], dict) or \
                    isinstance(dic[key], list)):
                break
            dic = dic[key]
        del dic[key]

        self._reload_after_edit()

    def edit_apply(self):
        val = self.editval.get()
        newkey = self.editkey.get()
        typefunc = _TYPE_CONVS[self.edittype.get()]

        dic = self.activeslot.data()
        for key in self._path[::-1]:
            if not (isinstance(dic[key], dict) or \
                    isinstance(dic[key], list)):
                dic = dic[key]
                continue
            else:
                break
        
        dic[newkey] = typefunc(val)
        if newkey != key:
            del dic[key]

        self._reload_after_edit()

    def _reload_after_edit(self):
        self._path = []
        for sel in self.tree.selection():
            self.tree.selection_remove(sel)
        self._clear_tree()
        self._insert_items('', self.activeslot.data())

    def cb_save(self):
        self.activeslot.save()

    def cb_load(self):
        self._clear_tree()
        if len(self.uifilepath.get()) == 0:
            return
        self.activeslot = config.Configuration(filename=self.uifilepath.get(),
                readonly=False)
        configs = self.activeslot.data()
        self._insert_items('', configs)

    def _clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.trmap = {}

    def _insert_items(self, treeparent, data):
        for key in data:
            val = data[key]
            uid = uuid.uuid4()
            self.trmap[str(uid)] = key

            if isinstance(val, dict):
                self.tree.insert(treeparent, 'end', uid, text=key,
                        values=['Dict', ''])
                self._insert_items(uid, val)
            
            elif isinstance(val, list):
                self.tree.insert(treeparent, 'end', uid, text=key,
                        values=['Array', ''])
                self._insert_items(uid,
                        dict([(i, x) for i, x in enumerate(val)]))

            else:
                typeof = type(val).__name__
                if val is None:
                    val = 'None'
                    typeof = 'null'
                self.tree.insert(treeparent, 'end', uid, text=key, 
                        values=[typeof, val])

    def cb_pick(self):
        newfile = tkfd.askopenfilename(
                title="Select TrashBin configuration file",
                initialfile=self.uifilepath.get(),
                filetypes=[('JSON', '*.json'), ('All', '*')],
                multiple=False
            )
        self.uifilepath.set(newfile)

