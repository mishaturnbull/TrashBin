#!/usr/bin/python3
# -*- coding: utf-8 -*-

import multiprocessing
import src.logutils.DFReader as dfr
import src.processor.processorbase as pb


class Worker(object):
    """
    Handles actual processing of the plugins.
    """
    def __init__(self, handler):
        self.handler = handler
        self.do_abort = False

    def pipeline_filename(self, filename):
        for plugin in self.handler.plugins:
            plugin.run_filename(filename)
            self.handler.progress.set(self.handler.progress.get() + 1)

    def pipeline_filehandle(self, filehandle):
        for plugin in self.handler.plugins:
            plugin.run_filehandle(filehandle)
            self.handler.progress.set(self.handler.progress.get() + 1)

    def pipeline_parsedlog(self, parsedlog):
        for plugin in self.handler.plugins:
            plugin.run_parsedlog(parsedlog)
            self.handler.progress.set(self.handler.progress.get() + 1)

    def pipeline_messages(self, messages):
        for plugin in self.handler.plugins:
            plugin.run_messages(messages)
            self.handler.progress.set(self.handler.progress.get() + 1)

    def run(self):
        """
        Main callable item for worker thread.
        """
        print("Started main execution loop")
        print("Input files: {}".format(self.handler.input_files))
        print("Plugins: {}".format(self.handler.plugins))
        for filename in self.handler.input_files:
            print("On {}".format(filename))
            if self.do_abort:
                break
            self.pipeline_filename(filename)
            print("Done filename pipeline")
            with open(filename, 'r') as filehandle:
                self.pipeline_filehandle(filehandle)
            print("Done filehandle pipeline")
            parsedlog = dfr.DFReader_auto(filename)
            self.pipeline_parsedlog(parsedlog)
            print("Done parsedlog pipeline")
            
            # process messages into one big list
            # rip RAM :(
            while True:
                m = parsedlog.recv_msg()
                if m is None:
                    break
            self.pipeline_messages(parsedlog.all_messages)
            print("Done messages pipeline")


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
        self.process = multiprocessing.Process(
                target=self.worker.run,
                args=(),
            )
        
    @property
    def max_work(self):
        # the *4 at the end is due to each plugin having 4 stages in its
        # operation pipeline -- filename, handle, parse, and messages
        return len(self.input_files) * len(self.plugins) * 4

    def run(self):
        print("About to hit process.start")
        self.process.start()

    def stop(self):
        self.worker.do_abort = True
        self.process.join()

    def force_stop(self):
        self.worker.do_abort = True
        self.process.terminate()


