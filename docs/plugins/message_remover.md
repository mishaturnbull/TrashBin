# Message Remover

This plugin creates a second copy of the input log file with select messages
removed.  It can remove entire log packets, or overwrite specific fields within
the packets to allow for more control over the removal.

## Options

### Specificity

Replace/overwrite options:

* `Delete entire packet` will remove the entire packet from the log.  The
  cleaned output log will be missing that packet entirely -- for example, if
  `GPS` is entered below, then the output log will simply not have the `GPS`
  packet.
* `Overwrite selected parts of packet` will alter the specified parts of the
  packet as entered below.  Due to a limitation of the plugin, individual
  datapoints within the packets cannot be removed altogether, but they can be
  overwritten.  Entering `GPS.Lat` below will cause the `GPS.Lat` data point to
  be set entirely to the value selected next.
* `Replace with` controls what replaces data points when
  `Overwrite selected parts of packet` is active.  In general, it is best to
  leave this set to zero.

### Filter mode

The filter mode allows for easy inversion of the remover.  If the whitelist
option is selected, then the output log will contain *only* the messages
specified below.  If the blacklist option is selected, the output log will have
the below entered packets removed.

### Message data filter

This text box allows specification of which messages are being removed or
altered in the logs.  The syntax is that of a general Python multi-line regular
expression.  Backslashes must be used to escape special characters.  Some
examples:

```
# this group matches all GPS, GPS2, GPA, GPA2 packets
GPS|GPS2|GPA|GPA2
```

```
# this group only matches GPS.Lat and GPS.Lon
GPS\.Lat|GPS\.Lon
```

```
# this group matches MAG1 and MAG2 packets, but not MAG3
MAG[12]
```

