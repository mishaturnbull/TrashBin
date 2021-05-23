#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Same file data comparison plugin.
"""

import tkinter as tk
import tkinter.ttk as ttk
import functools
import src.plugins.pluginbase as pluginbase
import src.logutils.DFWriter as dfwriter


class SFDataCompFactory(pluginbase.TBPluginFactory):

    author_name = "Misha Turnbull"
    author_email = "misha@turnbull.link"
    plugin_name = "Same-file data comparison"
    plugin_desc = "This plugin allows for comparing every datapoint of two " \
            "lines in a data file."

    def __init__(self, handler):
        """
        Create an instance of the data comparison plugin factory.
        """
        super().__init__(handler)
        self.lineA = tk.StringVar()
        self.lineA.set('')
        self.lineB = tk.StringVar()
        self.lineB.set('')
        self.do_popup = tk.BooleanVar()
        self.do_popup.set(True)
        self.do_coop = tk.BooleanVar()
        self.do_coop.set(False)
        self.modevar = tk.IntVar()
        self.modevar.set(0)
        self.flags = {
                'mindiff': tk.BooleanVar(),
                'maxdiff': tk.BooleanVar(),
                'avgdiff': tk.BooleanVar(),
                'stddev': tk.BooleanVar(),
                'rmsdiff': tk.BooleanVar(),
                'r2': tk.BooleanVar(),
                'avg-avg': tk.BooleanVar(),
                'rawdiff': tk.BooleanVar(),
            }
        
        # turn all off and only re-enable the usual ones by default
        for val in self.flags.values():
            val.set(False)
        self.flags['mindiff'].set(True)
        self.flags['avgdiff'].set(True)
        self.flags['maxdiff'].set(True)
        self.flags['rawdiff'].set(True)

    @property
    def work_per_file(self):
        return len(self.lines) - 1

    def start_ui(self, frame):
        self.lineframe = tk.Frame(frame)
        tk.Label(self.lineframe, text="A:").grid(row=0, column=0, sticky='nw')
        tk.Label(self.lineframe, text="B:").grid(row=1, column=0, sticky='nw')
        entryA = tk.Entry(self.lineframe, textvariable=self.lineA)
        entryA.grid(row=0, column=1, sticky='new')
        entryB = tk.Entry(self.lineframe, textvariable=self.lineB)
        entryB.grid(row=1, column=1, sticky='new')
        self.lineframe.grid(row=0, column=0, sticky='new')
        frame.grid_columnconfigure(0, weight=1)

        self.oframe = tk.Frame(frame)
        statsframe = tk.LabelFrame(self.oframe, text='Stats', relief=tk.RIDGE)
        ck_mindiff = tk.Checkbutton(statsframe, text='Min diff',
                variable=self.flags['mindiff'], onvalue=True, offvalue=False)
        ck_mindiff.grid(row=0, column=0, sticky='nw')
        ck_maxdiff = tk.Checkbutton(statsframe, text='Max diff',
                variable=self.flags['maxdiff'], onvalue=True, offvalue=False)
        ck_maxdiff.grid(row=1, column=0, sticky='nw')
        ck_avgdiff = tk.Checkbutton(statsframe, text='Avg diff',
                variable=self.flags['avgdiff'], onvalue=True, offvalue=False)
        ck_avgdiff.grid(row=2, column=0, sticky='nw')
        ck_stddev = tk.Checkbutton(statsframe, text="Std. dev",
                variable=self.flags['stddev'], onvalue=True, offvalue=False)
        ck_stddev.grid(row=3, column=0, sticky='nw')
        ck_rmsdiff = tk.Checkbutton(statsframe, text="RMS diff",
                variable=self.flags['rmsdiff'], onvalue=True, offvalue=False)
        ck_rmsdiff.grid(row=4, column=0, sticky='nw')
        ck_r2 = tk.Checkbutton(statsframe, text='R^2',
                variable=self.flags['r2'], onvalue=True, offvalue=False)
        ck_r2.grid(row=5, column=0, sticky='nw')
        ck_avgavg = tk.Checkbutton(statsframe, text="AvgA - AvgB",
                variable=self.flags['avg-avg'], onvalue=True, offvalue=False)
        ck_avgavg.grid(row=6, column=0, sticky='nw')
        ck_rawdiff = tk.Checkbutton(statsframe, text="Raw diff",
                variable=self.flags['rawdiff'], onvalue=True, offvalue=False)
        ck_rawdiff.grid(row=7, column=0, sticky='nw')
        statsframe.grid(row=0, column=0, rowspan=3, sticky='nw')

        outframe = tk.LabelFrame(self.oframe, text="Output", relief=tk.RIDGE)
        popupbox = tk.Checkbutton(outframe, text="Display results",
                variable=self.do_popup, onvalue=True, offvalue=False)
        popupbox.grid(row=0, column=0, sticky='nw')
        coopbox = tk.Checkbutton(outframe, text="Coop mode",
                variable=self.do_coop, onvalue=True, offvalue=False)
        coopbox.grid(row=1, column=0, sticky='nw')
        outframe.grid(row=0, column=1, sticky='nw')

        modeframe = tk.LabelFrame(self.oframe, text="Tsync handling", 
                relief=tk.RIDGE)
        rb_mostrec = tk.Radiobutton(modeframe, text="Most recent",
                variable=self.modevar,
                value=0,
            )
        rb_lininterp = tk.Radiobutton(modeframe, text="Linear interpolation",
                variable=self.modevar,
                value=1,
            )
        rb_nearest = tk.Radiobutton(modeframe, text="Nearest (timewise)",
                variable=self.modevar,
                value=2,
            )
        rb_mostrec.grid(row=0, column=0, sticky='nw')
        rb_lininterp.grid(row=1, column=0, sticky='nw')
        rb_nearest.grid(row=2, column=0, sticky='nw')
        modeframe.grid(row=1, column=1, sticky='nw')
        self.oframe.grid(row=1, column=0, sticky='nw')

    def stop_ui(self, frame):
        self.oframe.destroy()
        self.filterframe.destroy()
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_columnconfigure(0, weight=0)

    def export_savestate(self):
        return {
                "popup": self.do_popup.get(),
                "coop": self.do_coop.get(),
                "lines": [
                    self.lineA.get(),
                    self.lineB.get(),
                ],
                "mode": self.modevar.get(),
                "flags": {k: v.get() for k, v in self.flags.items()}
            }

    def load_savestate(self, state):
        self.do_popup.set(state['popup'])
        self.do_coop.set(state['coop'])
        lines = state['lines']
        self.lineA.set(lines[0])
        self.lineB.set(lines[1])
        self.modevar.set(state['mode'])
        for key, val in state['flags'].items():
            self.flags[key].set(val)

    def cleanup_and_exit(self):
        pass

    def give_plugin(self, processor=None):
        plug = SFDataCompPlugin(
                self,
                processor,
                self.do_popup.get(),
                self.do_coop.get(),
                self.lineA.get(),
                self.lineB.get(),
                self.modevar.get(),
                {k: v.get() for k, v in self.flags.items()},
            )
        return plug


class SFDataCompPlugin(pluginbase.TrashBinPlugin):
    """
    Does the data comparison work.
    """
    
    def __init__(self, handler, processor, popup, coop, A, B, mode, flags):
        super().__init__(handler, proc)
        self.popup = popup
        self.coop = coop
        self.infilename = None
        self.lineA = A.split('.')
        self.lineB = B.split('.')
        self.diffpoints = []
        self.mode = mode
        self.flags = flags
        self.data = {}
        self.same_packet = self.lineA[0] == self.lineB[0]

        for key, val in self.flags.items():
            if val:
                self.data.update({key: None})
        if 'rawdiff' in self.data.keys():
            self.data['rawdiff'] = []

    def run_filename(self, filename):
        self.infilename = filename

    def run_messages(self, messages):
        if self.same_packet:
            self._msgs_same(messages)
        if self.mode == 0:
            self._msgs_mostrecent(messages)
        elif self.mode == 1:
            self._msgs_lininterp(messages)
        elif self.mode == 2:
            self._msgs_nearest(messages)

        if self.coop:
            self._publish_results()
        if self.popup:
            self._disp_results()

    def _rolling_stats(self, newpoint):
        if self.flags['rawdiff']:
            self.data['rawdiff'].append(newpoint)
        if self.flags['mindiff']:
            if newpoint[0] < self.data['mindiff']:
                self.data['mindiff'] = newpoint[0]
        if self.flags['maxdiff']:
            if newpoint[0] > self.data['maxdiff']:
                self.data['maxdiff'] = newpoint[0]

    def _msgs_same(self, messages):
        for message in messages:
            if message['mavpackettype'] != self.lineA[0]:
                continue

            fieldA = message[self.lineA[1]]
            fieldB = message[self.lineB[1]]
            self._rolling_stats(fieldB - fieldA)

    def _msgs_mostrecent(self, messages):
        raise NotImplemented("Doesn't have that yet, sorry")

    def _msgs_lininterp(self, messages):
        raise NotImplemented("Doesn't have that yet, sorry")

    def _msgs_nearest(self, messages):
        raise NotImplemented("Doesn't have that yet, sorry")


