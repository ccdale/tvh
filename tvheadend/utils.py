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
import sys
import os
import re
from pathlib import Path
from tvheadend.errors import errorRaise
import tvheadend.categories as CATS


class FileDoesNotExist(Exception):
    pass


def askMe(q, default):
    try:
        ret = default
        val = input("{} ({}) > ".format(q, default))
        if len(val) > 0:
            ret = val
        return ret
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def padStr(xstr, xlen=2, pad=" ", padleft=True):
    try:
        zstr = xstr
        while len(zstr) < xlen:
            if padleft:
                zstr = pad + zstr
            else:
                zstr += pad
        return zstr
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


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
            raise(FileDoesNotExist("src file does not exist: {}".format(src)))
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def seriesId(show):
    show["series"] = None
    try:
        m = re.match(".*([sS][0-9]{1,2}[eE][0-9]{1,3}).*", show["filename"])
        if m is not None and len(m.groups()) > 0:
            show["series"] = m.groups()[0]
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def showParts(show):
    try:
        show["title"] = show["disp_title"]
        if "disp_subtitle" in show:
            show["subtitle"] = show["disp_subtitle"]
            if show["subtitle"].startswith(" - "):
                show["subtitle"] = show["subtitle"][3:]
        else:
            show["subtitle"] = None
        seriesId(show)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def addBaseFn(show):
    try:
        show["opbase"] = None
        showParts(show)
        if "year" in show and show["year"] is not None:
            bfn = delimitString(show["title"], str(show["year"]), " (")
            bfn += ")"
        else:
            bfn = show["title"]
            bfn = delimitString(bfn, show["subtitle"])
            bfn = delimitString(bfn, show["series"])
        show["opbase"] = bfn
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def titleAndSubTitle(show):
    msg = None
    try:
        if "opbase" not in show:
            addBaseFn(show)
            print("had to re-evaluate the show")
        msg = show["opbase"]
        # showParts(show)
        # msg = show["title"]
        # if dparts is not None:
        #     if "year" in show:
        #         msg += " (" + show["year"] + ")"
        #     else:
        #         sub = dparts["subtitle"] if dparts["subtitle"] is not None else ""
        #         series = dparts["series"] if dparts["series"] is not None else ""
        #         filler = "" if len(sub) == 0 else " - "
        #         msg += filler + sub
        #         filler = "" if len(series) == 0 else " - "
        #         msg += filler + series
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return msg


def displayNumberedShows(xdict):
    try:
        cn = 1
        for entry in xdict:
            sn = padStr(str(cn))
            msg = sn + ". "
            addBaseFn(entry)
            # dts = titleAndSubTitle(entry)
            if entry["opbase"] is not None:
                msg += entry["opbase"]
                print(msg)
            cn += 1
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def mainMenu(shows, config):
    ret = False
    try:
        displayNumberedShows(shows["uncatshows"])
        menu = "Select a programme or (E)xit"
        res = askMe(menu, "1")
        prog = 1
        rlow = res.lower()
        if rlow == "e" or rlow == "x" or rlow == "q":
            ret = True
        elif int(res) > 0:
            prog = int(res)
            CATS.setCategory(prog, shows, config)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return ret

def delimitString(xstr, addstr, delimeter=" - "):
    ret = xstr
    try:
        if addstr is not None:
            if len(addstr) > 0:
                ret += delimeter + addstr
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
    finally:
        return ret
