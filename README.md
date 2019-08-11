# tvh and tvhb Applications

Applications to assist categorising and moving tvheadend recordings into
the Kodi TV Show / Movie file stores.

<a name='contents'></a>
* [User Install](#uinstall)
* [Configuration](#config)
* [Make Targets](#maketargets)
* [Commands](#commands)
    * [tvh](#tvh)
    * [tvhb](#tvhb)
    * [tvhl](#tvhl)
    * [tvhnfo](#tvhnfo)
    * [tvhd](#tvhd)

<a name='unistall'></a>
## User Install

To install for a normal user:

```
make install
```

<a name='config'></a>
## [Configuration](#contents)

Copy the default config file `tvh.yaml` to your `~/.config` directory.
Edit the copy, setting `videohome` and `filmhome` appropriately.  The
categories will be the top-level directories under `videohome`.


<a name='maketargets'></a>
## [Make Targets](#contents)

### dev
Checks that you are in virtual environment, bumps the build number,
commits back to git and uses pip to install an editable version.

### install
Normal user install

### uninstall
Normal user uninstall

### sdist

Builds the source distribution

### bdist

Builds the source distribution then builds the distribution wheel

### upload

Runs `bdist` then does a test upload to `testpypi`

### pypi

Runs `bdist` then uploads to pypi


<a name='commands'></a>
## [Commands](#contents)

<a name='tvh'></a>
### [tvh](#contents)

The main, interactive, utility.  This allows you to mark recordings for
moving to the Kodi file stores.

Using the config file it will 'remember' your choices and not display them
in the future.  Recordings can be categorised, ignored or left alone.

Ignored recordings are not displayed and not moved (they stay in your
tvheadend list).

Categorised recordings are displayed at the top of the output, and removed
from the current list.  Recordings with the same title are categorised
together.

Giving a recording a 4-digit date will mark it as a movie and it will be
moved into Kodi's movie file store, rather than the tv file store.

<a name='tvhb'></a>
### [tvhb](#contents)

Batch utility that reads the config file and moves any categorised
recordings to the appropriate places in the Kodi file stores.  The
recordings are removed from tvheadend.

This utility is designed to be run from cron.

<a name='tvhl'></a>
### [tvhl](#contents)

Utility to list all recordings and their filenames.


<a name='tvhnfo'></a>
### [tvhnfo](#contents)

Utility to write a Kodi compatible nfo file with the recording
information.  Takes a list of filenames and writes out the nfo files into
the current directory.


<a name='tvhd'></a>
### [tvhd](#contents)

Utility to delete recordings from tvheadend without moving them to Kodi.
Takes a list of filenames to delete and asks tvheadend to delete them.

[modeline]: # ( vim: set ft=markdown tw=74 fenc=utf-8 spell spl=en_gb mousemodel=popup: )
