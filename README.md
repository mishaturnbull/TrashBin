# TrashBin

TrashBin is a log editor for ArduPilot log files (.BIN), allowing selective
deletes of parts of the log.  In effect, an advanced and much more configurable
brother of Mission Planner's log anonymizer feature.  This was written with
the goal of being able to delete certain log packets entirely to comply with
privacy policies - e.g. GPS.\*, GPA.\*, PARAM messages, and others.

## What does it look like?

<div style="text-align-center">
    <!-- if you're reading this file offline, sorry about the html... -->
    <img src="https://github.com/mishaturnbull/TrashBin/raw/feature/docs/docs/scrnshot-mainpg.png"/>
</div>

## Built-in plugins

A few plugins are available immediately for use on download.  These plugins
are:

* Parameter extractor:
  * Given a log file, create a .param file with all of the parameters that are
    in the log file.  Allows intelligent handling of duplicate entries and
	regex-based filtering.
* Message remover:
  * Given a log file, create another log file keeping only selected data from
    the first (in whitelist mode) or cloning the first file without selected
	data from the first (in blacklist mode).  Currently only supports writing
	*.log (plain-text) format; maybe a .bin writer coming in the future if I
	can figure out the spec.
* Plugin factory test:
  * A simple debug plugin meant to test the UI.

### Plugin extensibility

This program was written with the primary goal being ease of extension by end
users, hence the plugin architecture.  It uses a plugin factory object to spawn
a plugin object for each file, allowing for both easy multiple-file processing
and save/load of plugin configuration.  This also provides the capability for
a factory object to store and always return the same instance of a plugin,
which means that a plugin can support reading multiple files (and all of the
capabilites that come with that, such as data correlation between flights).

As long as the individual plugins are written with the intent, TrashBin fully
supports cooperative plugins, allowing easy cross-plugin data exchange via a
shared read/write namespace.

Documentation is... not really there yet.  But it's coming, I promise!  Check
the `feature/docs` branch!

## Prerequisites

* Python 3
  * Tcl/Tk libraries

That's it!  To run the GUI at least.  Select parts of pymavlink are built in
to allow for frequent tasks (such as reading log files) without having to
install the entire pymavlink library.

*However*, certain plugins may require additional modules.  If that is the
case, the plugin author should specify what additional work is needed to get
that particular plugin functioning correctly.  All of the modules that ship
with TrashBin out-of-the-box will function without additional installs.

## Acknowledgements

This code makes use of the DFReader.py file found in `pymavlink`.  `pymavlink`
is licensed under the LGPL v3.  DFReader.py can be found under the src/ folder,
and has been modified slightly (see commit history).  Thanks to all who
contributed to it!

