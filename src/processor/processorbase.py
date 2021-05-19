#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Base class for processor objects.
"""

class Namespace(dict):

    def __init__(self, dct={}):
        super().__init__(dct)

    def __setattr__(self, name, value):
        self[name] = value

    def __getattr__(self, name):
        try:
            return self[name]
        # if not found, hand back an AttributeError instead of a KeyError
        # that's what really should come from this, and makes more sense to
        # whomever's using this class
        except KeyError as e:
            raise AttributeError(e.args[0])

    def __delattr__(self, name):
        del self[name]


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
        self.data = Namespace({'base': self})
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

