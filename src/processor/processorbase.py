#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Base class for processor objects.
"""

import src.config.config as config

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
        self.active = False
        self.plugins = []
        self.data = config.Configuration(None)
        self.data['base'] = self
        self.update()

    def update(self):
        self.input_files = self.handler.files
        self.factories = self.handler.factories

    @property
    def max_work(self):
        per_file = sum([f.work_per_file for f in self.factories])
        total = per_file * len(self.input_files)
        return total

    def run(self):
        raise NotImplemented("Method run must be overriden!")

    def stop(self):
        raise NotImplemented("Method stop must be overriden!")

    def force_stop(self):
        raise NotImplemented("Method force_stop must be overriden!")

    def notify_done(self):
        self.handler.notify_done()

