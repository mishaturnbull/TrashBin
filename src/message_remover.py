#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Removes selected messages from a DFReader log.
"""

import re

def filter_packet_type(log, msgtypes=[]):
    """
    Given a DFReader (or DFReader derivative) object, filter out all the
    messages of given MAV packet types.

    :param log: DFReader object containing log information
    :param msgtypes: list.  contains case-insensitive strings corresponding to
    message types to remove.  example: ['att', 'gps', 'gpa', 'gps2'].  regex
    matching is applied.
    :return: 2-tuple: (messages-matching, messages-not-matching).  both lists.
    """

    if len(msgtypes) == 0:
        # nothing selected; no work to do
        return ([], log.all_messages)

    matching = []
    not_matching = []
    re_objects = [re.compile(s) for s in msgtypes]

    for msg in log.all_messages:
        if msg is None:
            continue
        mtype = msg.to_dict()['mavpackettype']
        for reo in re_objects:
            if reo.match(mtype):
                matching.append(msg)
                # this only breaks out of the inner loop
                break
        else:
            # reached if the inner for-loop terminates normally, i.e. did not
            # reach the inner break
            not_matching.append(msg)

    return (matching, not_matching)

