#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Provides the base class for all TrashBin plugin modules.

All plugin classes must inherit this class and override the reqired fields
before use.
"""

import uuid
import copy

class TBPluginFactory(object):
    """
    A class that generates file-specific (or not) instances of a plugin class.
    """

    author_name = "Firstname Lastname"
    author_email = "example@example.com"
    plugin_name = "Plugin template"
    plugin_desc = "This plugin does nothing, but serves as a template others."

    def __init__(self, handler):
        """
        Creates a TrashBin plugin factory object.

        This class is used to spawn new instances of its respective plugin
        class for each file.  This class is responsible for handling of GUI
        elements.
        """
        self.uuid = str(uuid.uuid4())
        self.handler = handler
        self.is_active = False
        self.debug = self.handler.config['debug']

    @property
    def work_per_file(self):
        raise NotImplemented("Property work_per_file must be overriden!")

    def _export_savestate(self):
        d = {'plugin_name': type(self).plugin_name,
                'plugin_cls': type(self).__name__,
                'uuid': self.uuid,
            }
        d.update(self.export_savestate())
        return d

    def export_savestate(self):
        raise NotImplemented("Method export_savestate must be overriden!")

    def _load_savestate(self, state, handler):
        assert state['plugin_cls'] == type(self).__name__, \
                "Something has gone horrendously wrong.  I am {}, and you " \
                "think that I am {}".format(type(self), state['plugin_cls'])
        self.handler = handler
        self.uuid = state['uuid']
        self.load_savestate(state)

    def load_savestate(self, state):
        raise NotImplemented("Method load_savestate must be overriden!")
    
    def start_ui(self, frame):
        raise NotImplemented("Method start_ui must be overriden!")

    def stop_ui(self, frame):
        raise NotImplemented("Method stop_ui must be overriden!")

    def cleanup_and_exit(self):
        raise NotImplemented("Method cleanup_and_exit must be overriden!")

    def give_plugin(self, processor=None):
        raise NotImplemented("Method give_plugin must be overriden!")

    def notify_work_done(self, amt=1):
        """
        Notifies the factory of an amount of work done.  It will then relay
        this to its handler, and it will be reflected in the progress bar.
        """
        self.handler.notify_work_done(amt)


class TrashBinPlugin(object):
    """
    Base class for a TrashBin plugin.
    """
    total_work = 0

    def __init__(self, handler, processor=None):
        """
        Create an instance of a TrashBin plugin object.

        This class can make calls to other functions/classes as desired, but
        it must exist to provide a base API for the main program to use.
        """
        self._uuid = uuid.uuid4()
        self.handler = handler
        self.processor = processor
        self.debug = self.handler.debug

    @property
    def uuid(self):
        return str(self._uuid)

    @property
    def coopdata(self):
        return self.processor.data

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

