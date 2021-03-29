#!/usr/bin/python3
# -*- coding: utf-8

"""
GUI plugin for log message sanitization.
"""

import src.plugins.pluginbase as pluginbase
import src.logutils.message_remover as message_remover


class MessageRemoverPlugin(pluginbase.TrashBinPlugin):

    author_name = "Misha Turnbull"
    author_email = "misha@turnbull.link"
    plugin_name = "MessageRemover"
    plugin_desc = "This plugin allows for selective removal of MAVLink log " \
            "messages in a log file."
    
    def __init__(self, handler):
        """
        Create an instance of the message remover plugin for TrashBin UI.
        """
        super().__init__(self, handler)
        self.filter = []
        self.keeping = False

    def run_filename(self, filename):
        pass

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

