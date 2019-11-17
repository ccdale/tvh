#
# Copyright (c) 2018, Christopher Allison
#
#     This file is part of tvh.
#
#     tvh is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     tvh is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with tvh.  If not, see <http://www.gnu.org/licenses/>.
"""
utils module for tvh application
"""
import os
import sys
import hashlib
from pathlib import Path
from tvheadend.errors import errorRaise


class FileDoesNotExist(Exception):
    pass


def fileExists(fn):
    try:
        return Path(fn).is_file()
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def dirExists(dn):
    try:
        return Path(dn).is_dir()
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def dfExists(dfn):
    try:
        ret = Path(dfn).is_file()
        if not ret:
            ret = Path(dfn).is_dir()
        return ret
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def makePath(pn):
    try:
        if not dirExists(pn):
            p = Path(pn)
            ret = False
            p.mkdir(mode=0o755, parents=True, exist_ok=True)
            ret = True
        else:
            ret = True
        return ret
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def makeFilePath(fn):
    try:
        pfn = os.path.basename(fn)
        ret = makePath(pfn)
        return ret
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def absPath(fn):
    try:
        return os.path.abspath(os.path.expanduser(fn))
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def rename(src, dest):
    try:
        if dfExists(src):
            p = Path(src)
            p.rename(dest)
        else:
            raise FileDoesNotExist("src file does not exist: {}".format(src))
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def fileDelete(fqfn):
    try:
        os.unlink(fqfn)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def fileSize(fqfn):
    try:
        if fileExists(fqfn):
            return os.stat(fqfn).st_size
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def sizeof_fmt(num, suffix="B"):
    """
    from article by Fred Cirera:
    https://web.archive.org/web/20111010015624/http://blogmag.net/blog/read/38/Print_human_readable_file_size
    and stackoverflow:
    https://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(num) < 1024.0:
            return "{:3.1f}{}{}".format(num, unit, suffix)
        num /= 1024.0
    return "{:3.1f}{}{}".format(num, "Y", suffix)


def getFileHash(fqfn, blocksize=65536):
    """
    returns the sha256 hash of the named file

    uses fileSize (above) to test that the file exists
    """
    try:
        fnsize = fileSize(fqfn)
        sha = hashlib.sha256()
        with open(fqfn, "rb") as ifn:
            fbuf = ifn.read(blocksize)
            while len(fbuf) > 0:
                sha.update(fbuf)
                fbuf = ifn.read(blocksize)
        return (sha.hexdigest(), fnsize)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def fileTouch(fqfn, exists=True):
    try:
        junk = open(fqfn, "w").close()
        # pth = Path.touch(fqfn, exist_ok=exists)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
