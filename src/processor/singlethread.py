#!/usr/bin/python3
# -*- coding: utf-8 -*-

import threading
import ctypes
import tkinter as tk
from tkinter import messagebox as tkmb
import src.logutils.DFReader as dfr
import src.processor.processorbase as pb

def license_to_kill(root=None):
    if not root:
        myroot = tk.Tk()
        myroot.withdraw()
    # https://catb.org/jargon/html/os-and-jedgar
    res = tkmb.askyesno(title="JEDGAR",
            message="Worker thread is not responding to stop request!  May I " \
                    "have a license to kill it?",
            icon=tkmb.WARNING)
    if not root:
        myroot.destroy()

    return res

def estop(tid):
    exc = ctypes.py_object(KeyboardInterrupt)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, exc)

    if res == 0:
        raise ValueError("Invalid thread ID")
    elif res != 1:
        # if this returns >1, that is a "big problem" and you should put it
        # to the way it was by raising None exception
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PTS_SAE failed: {}".format(res))


class Worker(object):
    """
    This class does the actual heavy lifting in another thread.

    Due to the GIL, and using threading instead of multiprocessing, it's not
    all that much of a huge speedup, but it does keep the GUI from freezing.
    """
    def __init__(self, handler):
        self.handler = handler

    @property
    def data(self):
        return self.handler.data

    def stage_filename(self, filename, plugins):
        self.handler.put_stage_str("Filename")
        for plugin in plugins:
            self.handler.put_plugin_str(type(plugin.handler).plugin_name)
            plugin.run_filename(filename)

    def stage_filehandle(self, handle, plugins):
        self.handler.put_stage_str("Filehandle")
        for plugin in plugins:
            self.handler.put_plugin_str(type(plugin.handler).plugin_name)
            plugin.run_filehandle(handle)

    def stage_parsedlog(self, dfl, plugins):
        self.handler.put_stage_str("Parsedlog")
        for plugin in plugins:
            self.handler.put_plugin_str(type(plugin.handler).plugin_name)
            plugin.run_parsedlog(dfl)

    def stage_messages(self, msgs, plugins):
        self.handler.put_stage_str("Messages")
        for plugin in plugins:
            self.handler.put_plugin_str(type(plugin.handler).plugin_name)
            plugin.run_messages(msgs)

    def process_one_log(self, filename):
        # first, spawn new plugins for it all
        plugs = []
        for factory in self.factories:
            plugs.append(factory.give_plugin(self))
        self.plugins = plugs

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

    def run(self):
        self.filenames = self.handler.input_files
        self.factories = self.handler.factories
        for filename in self.filenames:
            self.process_one_log(filename)
        self.handler.notify_done()

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

    def reinit(self):
        self.process = threading.Thread(
                target=self.worker.run,
                args=()
            )

    @property
    def _tid(self):
        if hasattr(self.process, '_thread_id'):
            return ctypes.c_long(self.process._thread_id)

        for tid, tobj in threading._active.items():
            if tobj is self.process:
                self.process._thread_id = tid
                return ctypes.c_long(tid)

    def run(self):
        self.process.start()
        super().run()

    def stop(self):
        self.worker.do_abort = True
        self.process.join(timeout=5)
        if self.process.is_alive():
            if self.handler.gui:
                do_kill = license_to_kill(self.handler._gui.root)
                if not do_kill:
                    return
                print("WARNING: Thread did not rejoin normally, invoking JEDGAR")
                self.force_stop()
        else:
            super().stop()

    def force_stop(self):
        estop(self._tid)
        super().force_stop()


