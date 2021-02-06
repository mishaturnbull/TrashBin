# TrashBin

TrashBin is a log editor for ArduPilot log files (.BIN), allowing selective
deletes of parts of the log.  In effect, an advanced and much more configurable
brother of Mission Planner's log anonymizer feature.  This was written with
the goal of being able to delete certain log packets entirely to comply with
privacy policies - e.g. GPS.\*, GPA.\*, PARAM messages, and others.

## Prerequisites

* Python 3
  * Tcl/Tk libraries

## Acknowledgements

This code makes use of the DFReader.py file found in `pymavlink`.  `pymavlink`
is licensed under the LGPL v3.  Thanks to all who contributed to it!

