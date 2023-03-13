#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Base class for processor objects.
"""

import src.config.config as config

STATE_STOPPED = 0
STATE_RUNNING = 1

class ProcessorBase(object):
    """
    Base class for a processor object.
    """

    def __init__(self, handler):
        """
        Instantiate a processor object.
        Does NOT run the processor (yet).
        """
        self.handler = handler
        self.state = STATE_STOPPED
        self.active = False
        self.status = "Waiting for user start"
        self.curr_plug_name = ""
        self.curr_plug_num = 0
        self.plugins = []
        self.data = config.Configuration(None)
        self.data['base'] = self
        self.update()

    def update(self):
        self.input_files = self.handler.input['filenames']
        self.input_dirs = self.handler.input['directories']
        self.input_rawtext = self.handler.input['rawtext']
        self.factories = self.handler.factories

    @property
    def max_work(self):
        per_file = sum([f.work_per_file for f in self.factories])
        total = per_file * len(self.input_files)
        return total

    def run(self):
        self.update()
        self.state = STATE_RUNNING

    def stop(self):
        self.state = STATE_STOPPED

    def force_stop(self):
        self.state = STATE_STOPPED

    def notify_done(self):
        self.handler.notify_done()

    def put_status_str(self, status):
        self.status = status
        self.handler.notify_status_update(self.status)

    def put_stage_str(self, stage):
        self.stage = stage
        self.handler.notify_stage_update(self.stage)

    def put_plugin_str(self, plugname):
        self.plugname = plugname
        self.handler.notify_plugname_update(self.plugname)

