# TrashBin Usage 101

I assume if you're reading this far that you've already decided to use TrashBin
for something, so we'll skip the background and go straight into how to use it.

At a high level, there are a few steps to using TrashBin:

1. Select the log files you want to process.
2. Select the plugins to run on the log files.
3. Configure the plugins as applicable.
4. Click start.

You may also save and load plugin configuration using the `File` menu
in the top left.

## Step 1 - Log File Selection

Selecting log files is done with the `Add File(s)` button near the bottom left
of the window.  When clicked, a popup will open allowing browsing the file
system and selection of multiple files.

Note that by default only `.bin` files are shown.  This can be changed with the
drop down selector at the bottom of the popup, to include `.log` files or any
file at all.

If you want to remove a file, you may select a file (or multiple files) by
clicking on them in the list.  Then, click `Remove Selected` near the bottom
left of the screen to remove the selected files.  If 5 or more files are
selected, you will be asked to confirm removing the files.

You may also click `Remove All` to completely clear the list of input files.

## Step 2 - Plugin Selection

Plugins are selected via a popup window opened with the `Add Plugin(s)` button
near the bottom middle of the window.  The popup will have two main portions,
with the left side displaying a list of available plugins and the right side
displaying information about the selected plugin.

Adding a plugin is done via first selecting the plugin, then clicking the
`Load plugin` button at the bottom of the popup.  This process may be repeated
for multiple plugins.

Once a plugin (or multiple plugins) are added, they can be selected individually
by clicking on the plugin name.  A selected plugin may be moved up or down the
list of active plugins with the `Move Plugin Up` and `Move Plugin Down` button -
although the order of plugins may or may not matter depending on the plugins
used and processor selected.  Plugins should document if they requrie a specific
order.

Plugins may be removed from the plugin list in the same manner as input files.

## Step 3 - Plugin Configuration

Once a plugin is selected (as described above), it will automatically populate
plugin-relevant options in the right side of the window.  The options shown
will depend on the plugin and should be documented in the plugins documentation
folder.  Changes to plugin options take effect immediately, but do not change
the actions performed if processing is already taking place.

## Step 4 - Running

Once steps 1 through 3 are done, log processing is begun by the `Start` button
near the bottom of the window.  Once clicked, it will allow you to click again
to abort the process.  A progress bar will show approximate completion of the
entire process.

Output will be generated or displayed according to the selected plugins.

