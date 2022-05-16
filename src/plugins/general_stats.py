#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
This plugin provides general statistics about the log, including messate types,
counts of each,
"""

import os
import tkinter as tk
import src.plugins.pluginbase as pluginbase

class GeneralStatsFactory(pluginbase.TBPluginFactory):

    author_name = "Misha Turnbull"
    author_email = "misha@turnbull.link"
    plugin_name = "General statistics"
    plugin_desc = "This plugin performs general analysis on the provided log" \
            " file, such as log duration (time), message types and counts, " \
            " and other related info."

    def __init__(self, handler):
        """
        Create an instance of the general stats plugin factory.
        """
        super().__init__(handler)

    @property
    def work_per_file(self):
        return 100

    def start_ui(self, frame):
        pass

    def stop_ui(self, frame):
        pass

    def export_savestate(self):
        return {}

    def load_savestate(self, state):
        pass

    def cleanup_and_exit(self):
        pass

    def give_plugin(self, processor=None):
        return None


class GeneralStatsPlugin(pluginbase.TrashBinPlugin):
    """
    Does the general statistics analysis.
    """

    def __init__(self):
        pass

    def run_filename(self, filename):
        pass

    def run_filehandle(self, handle):
        pass

    def run_parsedlog(self, dflog):
        pass

    def run_messages(self, messages):
        pass

    def cleanup_and_exit(self):
        pass

