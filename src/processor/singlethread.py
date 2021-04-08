#!/usr/bin/python3
# -*- coding: utf-8 -*-

import threading
import src.logutils.DFReader as dfr
import src.processor.processorbase as pb


class Worker(object):
    """
    This class does the actual heavy lifting in another thread.

    Due to the GIL, and using threading instead of multiprocessing, it's not
    all that much of a huge speedup, but it does keep the GUI from freezing.
    """
    def __init__(self, handler):
        self.handler = handler

    def stage_filename(self, filename, plugins):
        for plugin in plugins:
            print("filename: {}, {}".format(plugin, filename))
            plugin.run_filename(filename)

    def stage_filehandle(self, handle, plugins):
        for plugin in plugins:
            print("filehandle: {}, {}".format(plugin, handle))
            plugin.run_filehandle(handle)

    def stage_parsedlog(self, dfl, plugins):
        for plugin in plugins:
            print("parsedlog: {}, {}".format(plugin, dfl))
            plugin.run_parsedlog(dfl)

    def stage_messages(self, msgs, plugins):
        for plugin in plugins:
            print("messages: {}".format(plugin))
            plugin.run_messages(msgs)

    def process_one_log(self, filename):
        print("in child.proc_one_log({})".format(filename))
        # first, spawn new plugins for it all
        plugs = []
        for factory in self.factories:
            plugs.append(factory.give_plugin())

        # now, run through the processing pipeline
        self.stage_filename(filename, plugs)

        with open(filename, 'r') as filehandle:
            self.stage_filehandle(filehandle, plugs)

        dfl = dfr.DFReader_auto(filename)
        self.stage_parsedlog(dfl, plugs)

        # have to process all the messages now
        while True:
            m = dfl.recv_msg()
            if m is None:
                break
        self.stage_messages(dfl.all_messages, plugs)
        print("Done with that file")

    def run(self):
        self.filenames = self.handler.input_files
        self.factories = self.handler.factories
        print("In child.run")
        for filename in self.filenames:
            self.process_one_log(filename)

class SingleThreadProcessor(pb.ProcessorBase):
    """
    Single-threaded, sequential implementation of log processing.
    
    Basically:
    for file in files:
        for plugin in plugins:
            plugin(file)
    """

    def __init__(self, handler):
        super().__init__(handler)
        self.worker = Worker(self)
        self.process = threading.Thread(
                target=self.worker.run,
                args=(),
            )

    def run(self):
        print("About to hit process.start")
        self.process.start()

    def stop(self):
        self.worker.do_abort = True
        self.process.join()

    def force_stop(self):
        self.worker.do_abort = True
        self.process.terminate()


