#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Provides the base class for all TrashBin plugin modules.

All plugin classes must inherit this class and override the reqired fields
before use.
"""

import uuid

def _mark_for_override_detection(method):
    method._is_original = True
    return method

def _check_overriden(method):
    if hasattr(method, '_is_original'):
        return not bool(method._is_original)
    return False


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

        self._check_necessary_overrides()

    def _check_necessary_overrides(self):
        for function in self._must_be_overriden:
            assert _check_overriden(function), \
                    "Method {} must be overriden!".format(function.__name__)

    @_mark_for_override_detection
    def start_ui(self, frame):
        pass
    _must_be_overriden.append(start_ui)

    @_mark_for_override_detection
    def stop_ui(self, frame):
        pass
    _must_be_overriden.append(stop_ui)

    @_mark_for_override_detection
    def cleanup_and_exit(self):
        pass
    _must_be_overriden.append(cleanup_and_exit)

    @_mark_for_override_detection
    def run_filename(self, filename):
        pass

    @_mark_for_override_detection
    def run_filehandle(self, filehandle):
        pass

    @_mark_for_override_detection
    def run_parsedlog(self, dflog):
        pass

    @_mark_for_override_detection
    def run_messages(self, messages):
        pass

