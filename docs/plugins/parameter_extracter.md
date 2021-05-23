# Parameter Extracter

This plugin parses a log file for `PARAM` messages, and generates parameter
files compatible with ArduPilot from the logs.  It offers distinction on how
duplicate parameters should be handled, and an option to filter parameters
extracted.

At time of writing, parameter files are generated alongside the log file(s)
and have the same name as the log file with the extension changed to `.param`.

