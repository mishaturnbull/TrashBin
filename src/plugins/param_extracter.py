#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
GUI plugin for parameter file generation
"""

import src.plugins.pluginbase as pluginbase
import src.logutils.extract_params as extract_params


class ParamExtractPlugin(pluginbase.TrashBinPlugin):

    author_name = "Misha Turnbull"
    author_email = "misha@turnbull.link"
    plugin_name = "Parameter Extracter"
    plugin_desc = "This plugin generates .param files containing parameters " \
            "described in a MAVLink log file.  It can handle de-duplication " \
            " of parameters by keeping only the first, only the last, or " \
            "refuting duplicate parameters altogether."

    def __init__(self, handler):
        """
        Create an instance of the param extracter plugin.
        """
        super().__init__(self, handler)
        self.infilename = None
        self.outfilename = None
    
    def run_filename(self, filename):
        self.infilename = filename

    def run_filehandle(self, filehandle):
        pass

    def run_messages(self, messages):
        pass

    def start_ui(self):
        pass

    def stop_ui(self):
        pass

    def cleanup_and_exit(self):
        pass

