#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Provides the base class for all TrashBin plugin modules.

All plugin classes must inherit this class and override the reqired fields
before use.
"""

import uuid

class TrashBinPlugin(object):
    """
    Base class for a TrashBin plugin.
    """

    author_name = "Firstname Lastname"
    author_email = "example@example.com"
    plugin_name = "Plugin template"
    plugin_desc = "This plugin does nothing, but serves as a template others."

    _must_be_overriden = []

    def __init__(self, handler):
        """
        Create an instance of a TrashBin plugin object.

        This class can make calls to other functions/classes as desired, but
        it must exist to provide a base API for the main program to use.
        """
        self._uuid = uuid.uuid4()
        self.is_active = False
        self.handler = handler

    @property
    def uuid(self):
        return str(self._uuid)

    def start_ui(self, frame):
        raise NotImplemented("Method start_ui must be overriden!")

    def stop_ui(self, frame):
        raise NotImplemented("Method stop_ui must be overriden!")

    def cleanup_and_exit(self):
        raise NotImplemented("Method cleanup_and_exit must be overriden!")

    def run_filename(self, filename):
        pass

    def run_filehandle(self, filehandle):
        pass

    def run_parsedlog(self, dflog):
        pass

    def run_messages(self, messages):
        pass

