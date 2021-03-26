#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Extract parameters from a log file and write them to a specified .param file.
"""

import os
import re
import sys
import argparse

from . import message_remover

MULTIVAL_FIRST = 0x01
MULTIVAL_LAST = 0x02
MULTIVAL_FAIL = 0x04
MULTIVAL_WARN = 0x08

parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter,
)
parser.add_argument(
        'infilename',
        type=str,
        #        action='store_const',
        help="Filename of the log for processing (.bin file)",
)
parser.add_argument(
        '-o', '--output',
        type=str,
        #        action='store_const',
        dest='outfilename',
        help="Filename of the output parameter file.",
)
parser.add_argument(
        '-d',
        choices=['first', 'last', 'fail'],
        dest='duplication',
        default='last',
        help='Handling of duplicate parameter values.',
)
parser.add_argument(
        '-w', '--warn',
        action='store_true',
        dest='warn',
        help='Emit warnings and info on duplicate parameter values',
)
parser.add_argument(
        '-m', '--match',
        type=str,
        dest='paramfilter',
        help="Regex to match parameter names by",
        default='.*',
)


def params_to_filecontents(params):
    """
    Given a dictionary of parameters, mangle it into a string that can be
    written to a file.

    (Don't use .writelines() on this -- file.write(...)!)
    """
    lines = []
    for key, val in params.items():
        lines.append("{},{}".format(key, str(val)))
    return '\n'.join(lines)

def grab_params_simple(log):
    """
    Given a log file, return the file contents of the output .param file.
    Always returns the last occuring value of a parameter.
    """
    # sometimes the dfreader fails to completely parse the file for some reason
    # ensure it's done before continuing
    while True:
        m = log.recv_msg()
        if m is None:
            break
    return log.params

def grab_params_complex(log, multivalhandle=None, paramfilter=None):
    """
    Grab parameters in a more advanced manner allowing for better handling of
    non-unique parameter responses and filtering.

    Multivalhandle may be set to None (default), MULTIVAL_FIRST, MULTIVAL_LAST,
    or MULTIVAL_FAIL.  _FIRST will record the first instance of the parameter
    being set; _last will record the last instance; and _FAIL will cause a
    ValueError to be raised on a duplicate parameter.  Any of those options
    may also be combined (via addition) with MULTIVAL_WARN, which
    will cause a printed warning to be emmitted to stdout on each duplicate
    value.  Default behavior is MULTIVAL_LAST.

    Filtering is accomplished with a list of strings.  Each string is compiled
    to a regex object, A parameter name matching any of the objects will be
    recorded; non-matching parameter names are ommitted from the output.
    Default behavior matches everything.
    """

    if paramfilter is None:
        paramfilter = ['.*']
    paramfilter = [re.compile(f) for f in paramfilter]

    # check for illegal parameters
    sets = [MULTIVAL_FIRST & multivalhandle,
            MULTIVAL_LAST & multivalhandle,
            MULTIVAL_FAIL & multivalhandle]
    n = 0
    for i in range(len(sets)):
        if sets[i]:
            n += 1
    if n > 1:
        raise AttributeError("Invalid arguments supplied!")
    if n == 0:
        multivalhandle = MULTIVAL_LAST

    # process!  we're actually going to use the message filter here to grab
    # all the PARM messages, since those contain the parameters.  The rest
    # will be discarded
    parm, _ = message_remover.filter_packet_type(log, ['PARM'])
    del _

    params = {}
    for msg in parm:
        key, val = msg.Name, msg.Value
        # first, does it match the filter?
        matching = False
        for reo in paramfilter:
            if reo.match(key):
                matching = True
                break
        if not matching:
            continue

        # now, check for duplicates
        if key in params.keys():
            # uh-oh!  duplicate!
            if multivalhandle & MULTIVAL_WARN:
                # let the user know
                old = params[key]
                new = val
                print("Duplicate parameter: {}; was {}, now {}".format(
                    key, old, new
                ))
            if multivalhandle & MULTIVAL_FIRST:
                # if only want the first parameter, skip. messages are sorted
                # by arrival time, so anything after the first one comes later
                continue
            elif multivalhandle & MULTIVAL_LAST:
                # if only want the last value, overwrite it with this occurance
                params[key] = val
            elif multivalhandle & MULTIVAL_FAIL:
                # commit honorable seppuku
                raise ValueError("Duplicate parameters detected!")
            else:
                # no behavior specified... hrmph.
                pass
        else:
            # no duplication, good to continue processing normally
            params.update({key: val})
    return params
    

def write_out_file(text, filename, force=False):
    """
    Write contents to desired filename.  May be absolute or relative.
    """
    if os.path.exists(filename) and not force:
        return False
    with open(filename, 'w') as pfile:
        pfile.write(text)


if __name__ == '__main__':
    import src.logutils.DFReader as dfr
    args = parser.parse_args()

    infilename = args.infilename
    if os.path.splitext(infilename)[1].lower() == '.bin':
        cls = dfr.DFReader_binary
    elif os.path.splitext(infilename)[1].lower() == '.log':
        cls = dfr.DFReader_text
    else:
        print("I don't know how to open that!")
        sys.exit(1)
    if args.outfilename is None:
        outfilename = os.path.splitext(infilename)[0] + '.param'
    else:
        outfilename = args.outfilename
    
    if args.duplication == 'first':
        handling = MULTIVAL_FIRST
    elif args.duplication == 'last':
        handling = MULTIVAL_LAST
    elif args.duplication == 'fail':
        handling = MULTIVAL_FAIL
    if args.warn:
        handling += MULTIVAL_WARN


    log = cls(infilename)
    params = grab_params_complex(log, handling, [args.paramfilter])
    lines = params_to_filecontents(params)
    write_out_file(lines, outfilename)

    print("Done!")
