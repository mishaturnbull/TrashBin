#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Starts the TrashBin program.
"""

import argparse
import sys

MASTER_FILENAME = "~/.trashbin-master.json"

parser = argparse.ArgumentParser(
        description=__doc__,
    )
parser.add_argument(
        '-e',
        type=str,
        help="Running environment -- headless CLI-arg-only, or spawn GUI",
        default="gui",
        dest='opermode',
        choices=['gui', 'headless'],
        required=False
    )
parser.add_argument(
        '-m',
        type=str,
        help="Specify filepath for the master configuration location",
        default=MASTER_FILENAME,
        dest='mastercfg',
        required=False
    )
parser.add_argument(
        '-c', '--config',
        type=str,
        help="Specify filepath for additional config files",
        action='append',
        metavar='extraconfigs',
        dest='extraconfigs',
        default=[]
    )

if __name__ == '__main__':
    args = parser.parse_args()
    # we have to import this and optionally override the tkinter module before
    # importing anything else
    from src.tkstubs import tb_override_tkinter
    tb_override_tkinter(args.opermode)
    import src.processor.main as mainproc
    mainexec = mainproc.MainExecutor(args.mastercfg,
            opermode=args.opermode,
            extraconfigs=args.extraconfigs,
        )

    import code
    code.interact(local=locals())

