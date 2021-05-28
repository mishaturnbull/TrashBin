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
        return 100
    
    def check_rms_reqs(self):
        if self.flags['rmsdiff'].get():
            self.flags['stddev'].set(True)
            self.flags['avgdiff'].set(True)
            self.ck_avgdiff.config(state=tk.DISABLED)
            self.ck_stddev.config(state=tk.DISABLED)
        else:
            self.ck_avgdiff.config(state=tk.NORMAL)
            self.ck_stddev.config(state=tk.NORMAL)

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
        self.ck_avgdiff = ck_avgdiff
        ck_stddev = tk.Checkbutton(statsframe, text="Std. dev",
                variable=self.flags['stddev'], onvalue=True, offvalue=False)
        ck_stddev.grid(row=3, column=0, sticky='nw')
        self.ck_stddev = ck_stddev
        ck_rmsdiff = tk.Checkbutton(statsframe, text="RMS diff",
                variable=self.flags['rmsdiff'], onvalue=True, offvalue=False,
                command=self.check_rms_reqs)
        ck_rmsdiff.grid(row=4, column=0, sticky='nw')
        ck_r2 = tk.Checkbutton(statsframe, text='R^2',
                variable=self.flags['r2'], onvalue=True, offvalue=False)
        # will leave this commented out until it's implemented
        #ck_r2.grid(row=5, column=0, sticky='nw')
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
        super().__init__(handler, processor)
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
        self._n_points = 0
        self.percent_scale = 100

        for key, val in self.flags.items():
            if val:
                self.data.update({key: None})

        # do special-case inits
        if self.flags['rawdiff']:
            self.data['rawdiff'] = []
        if self.flags['stddev']:
            self.S = 0
            self.M = 0
        if self.flags['avg-avg']:
            self._rolling_avgA = 0
            self._rolling_avgB = 0
            self.data['avg-avg'] = []

    def run_filename(self, filename):
        self.infilename = filename

    def run_messages(self, messages):
        # work out the scale factor for percentage first
        self.percent_scale = 100 // len(messages)

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

    def _rolling_stats(self, fieldB, fieldA):
        self._n_points += 1
        newpoint = fieldB - fieldA

        # keep track of raw differences
        # this one is special-cased as a list rather than a single value
        if self.flags['rawdiff']:
            self.data['rawdiff'].append(newpoint)

        # see if this point is less than the previous minimum
        if self.flags['mindiff']:
            if newpoint[0] < self.data['mindiff']:
                self.data['mindiff'] = newpoint[0]

        # see if this point is more than the previous maximum
        if self.flags['maxdiff']:
            if newpoint[0] > self.data['maxdiff']:
                self.data['maxdiff'] = newpoint[0]

        # update a rolling average
        if self.flags['avgdiff']:
            new_avg = (self._n_points * self.data['avgdiff'] + newpoint) / \
                    (self._n_points + 1)
            self.data['avgdiff'] = new_avg

        # update a rolling standard deviation
        if self.flags['stddev']:
            # https://jonisalonen.com/2013/deriving-welfords-method-for-\
            # computing-variance/
            oldM = self.M
            self.M = self.M + (newpoint - self.M) / self._n_points
            self.S = self.S + (newpoint - self.M ) * (newpoint - oldM)
            # have to check if _n_points is above 1 here, otherwise will get
            # divide-by-zero on the first point
            # setting the stddev early is fine, it'll just get overridden as
            # more data comes in
            if self._n_points <= 2:
                self.data['stddev'] = math.sqrt(self.S / (self._n_points - 1))

        # update a rolling root-mean-square of the differences
        # if rmsdiff is enabled, it is safe to assume that avgdiff and stddev
        # are also enabled due to a UI feature that prevents users disabling
        # those two if rmsdiff is checked
        # yeah, yeah, assume user breaks everything, but it's too much math
        # to actually follow through on that.  maybe some day i'll come back
        # and do this properly.
        if self.flags['rmsdiff']:
            self.data['rmsdiff'] = math.sqrt(
                    self.data['avgdiff']**2 + self.data['stddev']**2
                )

        # update a rolling difference of averages
        # this is avg(A) - avg(B)
        # this one is also a list
        if self.flags['avg-avg']:
            newA = (self._n_points * self._rolling_avgA + fieldA) / \
                    (self._n_points + 1)
            newB = (self._n_points * self._rolling_avgB + fieldB) / \
                    (self._n_points + 1)
            self._rolling_avgA = newA
            self._rolling_avgB = newB
            self.data['avg-avg'].append(newB - newA)


    def _msgs_same(self, messages):
        for message in messages:
            if message['mavpackettype'] != self.lineA[0]:
                continue

            fieldA = message[self.lineA[1]]
            fieldB = message[self.lineB[1]]
            self._rolling_stats(fieldB, fieldA)

            self.handler.notify_work_done(self.percent_scale)

    def _msgs_mostrecent(self, messages):
        # set up some initial values
        time_since_last_other = 0
        last_val_A = None
        last_val_B = None
        last_time_A = None
        last_time_B = None
        # presetting these saves a few cycles on accesses during the loop
        key_A = self.lineA[1]
        key_B = self.lineB[1]
        packet_A = self.lineA[0]
        packet_B = self.lineB[0]
        # this should always be false, but sanity-check just in case
        assert packet_A != packet_B, "Should be using _msgs_same!"

        for message in messages:
            # first, figure out which message we have
            have_lineA = message['mavpackettype'] == packet_A
            have_lineB = message['mavpackettype'] == packet_B

            # update the most-recent values and make skip first packet to make
            # sure we don't deal with values that don't make sense
            if have_lineA:
                last_val_A = message[key_A]
                last_time_A = message['TimeUS']
                if last_val_B is None:
                    continue
            if have_lineB:
                last_val_B = message[key_B]
                last_time_B = message['TimeUS']
                if last_val_A is None:
                    continue
            
            # invoke the stats counter!
            self._rolling_stats(last_val_B, last_val_A)
            
            # update progress bar
            self.handler.notify_work_done(self.percent_scale)

    def _msgs_lininterp(self, messages):
        raise NotImplemented("Doesn't have that yet, sorry")

    def _msgs_nearest(self, messages):
        raise NotImplemented("Doesn't have that yet, sorry")


