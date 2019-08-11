tvh and tvhb Applications
=========================

Applications to assist categorising and moving tvheadend recordings into
the Kodi TV Show / Movie file stores.

 \* `User Install <#uinstall>`__ \* `Make Targets <#maketargets>`__ \*
`Commands <#commands>`__ \* `tvh <#tvh>`__ \* `tvhb <#tvhb>`__ \*
`tvhl <#tvhl>`__ \* `tvhnfo <#tvhnfo>`__ \* `tvhd <#tvhd>`__

 ## User Install

To install for a normal user:

::

   make install

 ## Make Targets

dev
~~~

Checks that you are in virtual environment, bumps the build number,
commits back to git and uses pip to install an editable version.

install
~~~~~~~

Normal user install

uninstall
~~~~~~~~~

Normal user uninstall

sdist
~~~~~

Builds the source distribution

bdist
~~~~~

Builds the source distribution then builds the distribution wheel

upload
~~~~~~

Runs ``bdist`` then does a test upload to ``testpypi``

pypi
~~~~

Runs ``bdist`` then uploads to pypi

 ## `Commands <#contents>`__

 ### `tvh <#contents>`__

The main, interactive, utility. This allows you to mark recordings for
moving to the Kodi file stores.

Using the config file it will ‘remember’ your choices and not display
them in the future. Recordings can be categorised, ignored or left
alone.

Ignored recordings are not displayed and not moved (they stay in your
tvheadend list).

Categorised recordings are displayed at the top of the output, and
removed from the current list. Recordings with the same title are
categorised together.

 ### `tvhb <#contents>`__

Batch utility that reads the config file and moves any categorised
recordings to the appropriate places in the Kodi file stores. The
recordings are removed from tvheadend.

This utility is designed to be run from cron.

 ### `tvhl <#contents>`__

Utility to list all recordings and their filenames.

 ### `tvhnfo <#contents>`__

Utility to write a Kodi compatible nfo file with the recording
information. Takes a list of filenames and writes out the nfo files into
the current directory.

 ### `tvhd <#contents>`__

Utility to delete recordings from tvheadend without moving them to Kodi.
Takes a filename (only one) as it’s input.
