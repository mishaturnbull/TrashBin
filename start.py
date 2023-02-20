#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Starts the TrashBin program.
"""

import argparse
import sys
import src.processor.main as mainproc

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

if __name__ == '__main__':
    args = parser.parse_args()
    mainexec = mainproc.MainExecutor(args.mastercfg,
            opermode=args.opermode
        )
    import code
    code.interact(local=locals())

