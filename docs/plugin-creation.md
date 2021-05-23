# Creating TrashBin Plugins

This document attempts to guide new users/developers on the creation of new
custom plugins to be used with TrashBin.

## Prerequisites

* General installation prereqs (see README)
* Familiarity with the Python 3 programming language
  * Should be familiar with general object-oriented programming concepts
  * Familiarity with the Tkinter GUI framework is strongly recommended, but...
    I guess you could get by without
* A use case for a plugin

## Plugin installation

Plugins are automatically detected and loaded at runtime by an autodetection
module.  To be detected, a plugin must:

1. Be entirely contained in a single Python file (`.py` file)
2. Have a unique name in that folder
3. Be located in the `TrashBin/src/plugins/` folder
4. Contain exactly one class that is a subclass of `pluginbase.TBPluginFactory`
5. Contain exactly one class that is a subclass of `pluginbase.TrashBinPlugin`

## High-level design

TrashBin's plugin architecture revolves around a factory design pattern.  While
typical in the Java world, and less common in Python, I found this pattern
gives a very flexible setup and provides the most capabilities for plugin
developers.

When a user clicks on the 'load plugin' button to add a plugin to TrashBin,
they actually don't create a plugin but rather a factory.  The factory object
is responsible for populating the third panel with plugin-specific options,
storing those options in save files if requested (and loading them), and does
not actually perform any log analysis of its own.  One factory object of each
plugin type exists for each occurance of the plugin in the plugin list (ex: in
the screenshot in the README, there is exactly one instance of the message
remover factory and of the parameter extracter factory).

When the user clicks the 'run' button, a processor object is created (will be
documented elsewhere... for now, it's a class responsible for the execution of
plugins) and launched.  The processor will interface with the factory objects
instantiated earlier, and ask them to produce plugin objects.  The plugin
objects are where the actual log processing work is done, and do not have to
bear the GUI or savestate processing thanks to the factory and processor passing
any necessary information to the plugin in a usable format.

The plugin may act on various stages of the processing pipeline by overriding
certain methods in the base class.  Each of these methods are called on all
existing plugins by the processor at appropriate times.  In general, plugin
developers should attempt to write multithreading-safe code (multi*threading*,
not multi*processing*) --- but!  Factories are asked for one instance of their
plugin **per file**.  This means that, if the use case requires analyzing data
from multiple files to compare, the factory can simply instantiate a single
plugin and continue to return the same instance for every file, thereby allowing
the plugin to collect data from as many files as needed.

## Base classes

This section describes base classes to override to produce a factory/plugin
pair.

### Factory

The base class for factory objects is `pluginbase.TBPluginFactory`.  The
following methods must be overriden to produce a functional factory object:

1. `work_per_file` (`@property`) object:
  * Defines an integer value, summarizing the amount of steps that must be taken
    to complete processing of one file.  Used to determine the size of the
	progress bar in the UI.
  * Full signature: `@property \n def work_per_file(self):`
2. `export_savestate` method:
  * Returns a dictionary of information to be exported when plugin configuration
    is saved.
  * All keys must be string objects.
  * Keys may not be in this list: `['plugin_name', 'plugin_cls', 'uuid']`
  * All values must be objects that can be directly dumped to JSON.
  * Full signature: `def export_savestate(self):`
3. `load_savestate` method:
  * Takes a dictionary object and sets object attributes as appropriate.  This
    method is invoked when loading a plugin configuration, and as such should
	most commonly be given the dictionary produced by the `export_savestate`
	method.
  * It should be safe to assume this method is called directly after a factory
    is instantiated.
  * There will be three extra key:value pairs in the dictionary not exported by
    the export method (the three forbidden names for keys).  They may be safely
	ignored.
  * Full signature: `def load_savestate(self, state):`  (`state` is a dict)
4. `start_ui` method:
  * This method is responsible for the construction of the GUI elements shown
    in the third panel (plugin configuration elements).
  * The only argument, `frame`, is the Tkinter frame represented in the
    rightmost panel of the UI.  It is a fixed size, and you should not attempt
	to expand it.  I'm not quite sure what would happen.
  * Full signature: `def start_ui(self, frame):` (`frame` is `Tk.Frame` inst)
5. `stop_ui` method:
  * This method should safely undo all of the actions done by `start_ui`.  It is
    called when the GUI wants to empty the panel before handoff to another
	factory's `start_ui` method.
  * Full signature: `def stop_ui(self, frame):` (`frame` is the same `Tk.Frame`
    instance given to `start_ui`)
6. `give_plugin` method:
  * This method is where the plugin object should be instantiated and that
    instance passed to the processor.  Generally, the factory object converts
	any Tkinter-based variables to atomic types, and hands them to the plugin
	instantiator to reduce workload on the plugin itself.
  * If the plugin in question is meant to analyze multiple files, the flow
    of this method should be roughly as follows:
```
def give_plugin(self, processor=None):
    if self._plugin_inst is None:
		self._plugin_inst = ExamplePlugin(self, processor, self.foo, self.bar)
    return self._plugin_inst
```

The following methods/attributes are not technically required, but strongly
suggested to create a better factory:

* `author_name`: string, representing author name
* `author_email`: string, representing author contact email (WARNING: this is
  public!)
* `plugin_name`: A readable name of the plugin
* `plugin_desc`: String (may be multiple lines) describing in detail what the
  plugin does
* `__init__` method: best place to create factory-specific attributes.  Be sure
  to call the superclass `__init__` as well.

### Plugin

The base class for plugin objects is `pluginbase.TrashBinPlugin`.  The following
methods must be overriden to produce a functional plugin object:

1. `cleanup_and_exit` method:
  * This method is responsible for doing any cleanup work necessary before the
    plugin is deleted.  
  * Full signature: `def cleanup_and_exit(self):`

The following methods are not technically required, but should be where the
actual log processing work takes place.  You may safely assume these methods are
called in the order listed below, but may *not* assume that they are not called
simultaneously (from different threads).  You also may not make assumptions
about the current execution state of other plugins' `run_` methods.
(footnote 1)

Unless you are inheriting from a class other than `TrashBinPlugin`, you do *not*
need to call the superclass method in your overrides.

1. `run_filename` method:
  * This method is called with the filename as an argument.  This will be the
    first time the plugin is made aware of the filename of the file it's
	processing.
  * Typical usage here, if producing another file, could be to determine the
    desired output filename.
  * Full signature: `def run_filename(self, filename):`
2. `run_filehandle` method:
  * This method is called after the processor has opened the input file, and
    it passes the file handle object to the plugin.
  * Full signature: `def run_filehandle(self, filehandle):`
3. `run_parsedlog` method:
  * This method is run after the initial log parsing is completed by the
    DFReader class.  In general, for basic message processing, it is less
	efficient to use this method than to use the following; but this method
	would provide access to certain attributes of the log that the pure message
	list would not.
  * The argument to this class is fully compliant with `pymavlink.DFReader`.
  * Full signature: `def run_parsedlog(self, dflog):`
4. `run_messages` method:
  * This method is called by the processor once it has a list of every message
    in the log file.
  * In general, it is suggested to use this over the previous method if only
    message processing is being done; it reduces the amount of work done
    overall.
  * The argument to this method is a list of `logutil.DFReader.DFMessage`
    objects.  They may most easily be processed by calling the `to_dict`
	method to generate a native dictionary.
  * Full signature: `def run_messages(self, messages):`

To allow for cooperation between plugins, the TrashBinPlugin has an attribute
`coopdata`, which returns a dictionary-like object shared between all plugins.
Plugins have arbitrary read-write access to this object, and this is the
suggested method of sharing data cooperatively.

(footnote 1) Technically, these assumptions depend on the processor object being
used.  However, at time of writing, there is only one available, and the others
in the roadmap make a more heavy use of multithreading and thus these assumtions
should remain valid.

