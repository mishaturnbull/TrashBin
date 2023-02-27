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
        self.data = config.Configuration(None)
        self.data['base'] = self
        self.update()

    def update(self):
        self.input_files = self.handler.input['filenames']
        self.input_dirs = self.handler.input['directories']
        self.input_rawtext = self.handler.input['rawtext']
        self.factories = self.handler.factories

    def run(self):
        raise NotImplementedError("Method run must be overriden!")

    def stop(self):
        raise NotImplementedError("Method stop must be overriden!")

    def force_stop(self):
        raise NotImplementedError("Method force_stop must be overriden!")

    def notify_done(self):
        self.handler.notify_done()

