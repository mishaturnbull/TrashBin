# Parameter Extracter

This plugin parses a log file for `PARAM` messages, and generates parameter
files compatible with ArduPilot from the logs.  It offers distinction on how
duplicate parameters should be handled, and an option to filter parameters
extracted.

At time of writing, parameter files are generated alongside the log file(s)
and have the same name as the log file with the extension changed to `.param`.

## Options

### Param duplication

These options handle how duplicate parameter occurences are handled:

* `First occurance` will retain only the first time a parameter is entered.
* `Last occurance` will retain only the last time a parameter is entered.
* `Abort` will cause the program to abort creating the parameter file if
  duplicate parameters are detected.
  *NOTE: ArduPilot dataflash logs nearly always contain duplicate parameters.
  It is generally not advisable to set this option to abort.*

### Output options

`Force output`: if enabled, the program will overwrite existing parameter files
with the same name.  This generally should be left off, unless a previous run
was aborted partway through.

### Parameter filter

This text box allows specification of which parameters to output.  Note that it
only affects output - all parameters are still detected.  The syntax is that of
a general Python regular expression.  Backslashes must be used to escape
special characters.  Keep in mind regex is case-sensitive, and all ArduPilot
parameters are uppercase.  Some examples:

```
# this group will record all rangefinder parameters
RNGFND.*
```

```
# this group will record all parameters
.*
```

```
# this group will record all parameters without an underscore in their name
[^_]*
```

