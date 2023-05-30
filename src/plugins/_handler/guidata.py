#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Provides the GUI data & math to deal with drawing plugins on a canvas object.
"""

IO_BOXHEIGHT = 20
IO_SPACING = 20
CHAR_WIDTH = 8
TXT_OFFSET_X = 6
TXT_OFFSET_Y = 3


class _UIDataContainer(object):
    """
    Container class for some user interface-specific data about this plugin
    (e.g., where it is on the canvas, inlinks, outlinks, display data, etc).

    In tkinter, XY (0, 0) is the top-left corner of the canvas.  This object's
    .x and .y mark the top-left corner of the "no IO box":

    +-----------------------------------------------------
    | * (0, 0) for the canvas
    |
    |       V (.x, .y) for this object
    |       +-------------------+
    |       |    Boolean AND    |
    |   | i1                    |
    |       |                    o1 |
    |   | i2                    |
    |       |                   |
    |       +-------------------+
    |
    |
    """

    def __init__(self, factory):
        self.factory = factory
        self.x = None
        self.y = None
        self.w = None
        self.h = None
        self.autosize()

        self._elements = {}

    def autosize(self):
        """
        Guess the size of the box necessary to show this plugin.
        """
        textlen = max([10, len(self.factory.plugin_name)+2])
        n_inputs = len(self.factory.inputs)
        n_outputs = len(self.factory.outputs)
        # never let the boxes get *too* short
        io_height = max([n_inputs, n_outputs])

        self.w = CHAR_WIDTH * textlen
        self.h = IO_SPACING + (IO_BOXHEIGHT + IO_SPACING) * io_height

    def autoposition(self, canvas):
        """
        Place the box in the center of the canvas.
        """
        center_x = canvas.winfo_width() / 2
        center_y = canvas.winfo_height() / 2
        self.x = center_x - (self.w / 2)
        self.y = center_y - (self.h / 2)

    def determine_io_box_width(self, mode):
        """
        Determines the needed box width for either the inputs or the outputs,
        so that they are all drawn the same.

        :param mode: must be either "input" or "output".
        """
        if mode == 'input':
            args = self.factory.inputs
        elif mode == 'output':
            args = self.factory.outputs
        else:
            raise ValueError(f"I don't know what {mode} means!")

        if len(args) == 0:
            return 0
        return max(len(name) for name in args) * CHAR_WIDTH

    def draw(self, canvas):
        """
        Draws this thing on the specified canvas.
        """

        rect_id = canvas.create_rectangle(
                self.x,
                self.y,
                self.x + self.w,
                self.y + self.h,
            )
        self._elements['base'] = rect_id
        name_id = canvas.create_text(
                self.x + TXT_OFFSET_X,
                self.y + TXT_OFFSET_Y,
                text=self.factory.plugin_name,
                anchor='nw',
                font='TkMenuFont',
                fill='black',
            )
        self._elements['name'] = name_id

        down = IO_SPACING
        self._elements['inputs'] = []
        inpwidth = self.determine_io_box_width('input')
        for inp in self.factory.inputs:
            inp_box = canvas.create_rectangle(
                    self.x - inpwidth - (TXT_OFFSET_X * 2),
                    self.y + down,
                    self.x,
                    self.y + down + IO_BOXHEIGHT + (TXT_OFFSET_Y * 2),
                )
            inp_txt = canvas.create_text(
                    self.x - inpwidth + TXT_OFFSET_X,
                    self.y + down + TXT_OFFSET_Y,
                    text=inp,
                    anchor='nw',
                    font='TkMenuFont',
                )
            self._elements['inputs'].append([inp_box, inp_txt])
            down += IO_BOXHEIGHT + IO_SPACING

        down = IO_SPACING
        self._elements['outputs'] = []
        outwidth = self.determine_io_box_width('output')
        for out in self.factory.outputs:
            out_box = canvas.create_rectangle(
                    self.x + self.w,
                    self.y + down,
                    self.x + self.w + outwidth + (TXT_OFFSET_X * 2),
                    self.y + down + IO_BOXHEIGHT + (TXT_OFFSET_Y * 2),
                )
            out_txt = canvas.create_text(
                    self.x + self.w + TXT_OFFSET_X,
                    self.y + down + TXT_OFFSET_Y,
                    text=out,
                    anchor='nw',
                    font='TkMenuFont',
                )
            self._elements['outputs'].append([out_box, out_txt])
            down += IO_BOXHEIGHT + IO_SPACING



