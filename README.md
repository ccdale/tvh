# tvh and tvhb Applications

Applications to assist categorising and moving tvheadend recordings into
the Kodi TV Show / Movie file stores.


## User Install

To install for a normal user:

```
make install
```

## Make Targets

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



[modeline]: # ( vim: set ft=markdown tw=74 fenc=utf-8 spell spl=en_gb mousemodel=popup: )
