#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Removes selected messages from a DFReader log.
"""

import re

def filter_packet_type(messages, msgtypes=[]):
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

    for msg in messages:
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

def filter_data_type(messages, msgfilter='.*', replace=0, reverse=True):
    """
    Given a list of messages (i.e. DFReader_auto.all_messages), and a
    filters to apply, if data matches the filter, then it is replaced with the
    'replace' value.  Dictionaries are joined together case-sensitive with a .

    If the filter matches, the data is replaced.  A list of altered MAVLink
    message objects is returned.

    **WARNING**:  This function operates in-place!  A copy of the messages list
    is returned, but it's the same one that you give as an argument.
    """

    new_msgs = []
    reobj = re.compile(msgfilter)

    for msg in messages:
        if msg is None:
            break  # at the end
        d = msg.to_dict()
        prefix = d.pop('mavpackettype')
        for key in list(d.keys()):
            checkstr = '.'.join([prefix, key])
            if reobj.match(checkstr) and (not reverse):
                d[key] = replace
            elif (not reobj.match(checkstr)) and (reverse):
                d[key] = replace
            msg.__setattr__(key, d[key])
    return messages

