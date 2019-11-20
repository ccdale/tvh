#!/usr/bin/env python3
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
batch module for tvh application
"""

import sys
import os
import shutil
import time
import subprocess
import requests
import datetime
from requests.exceptions import ConnectionError
import tvheadend
import tvheadend.tvh as TVH
import tvheadend.utils as UT
import tvheadend.fileutils as FUT
import tvheadend.config as CONF
import tvheadend.categories as CATS
import tvheadend.nfo as NFO
import tvheadend.ffmpeg as FFMPEG
import tvheadend.tvhlog
import tvheadend.tvhdb
from tvheadend.errors import errorExit

log = tvheadend.tvhlog.log
dbfn = "/home/chris/Videos/kmedia/tvh/tvh.db"


class CopyFailure(Exception):
    pass


def logout(msg):
    xtime = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
    print("{} {}".format(xtime, msg))


def removeFromYear(show, config):
    try:
        if "year" in show:
            if config["Year"] is not None:
                syear = str(show["year"])
                years = config["Year"]
                changed = False
                for xyear in years:
                    for yearname in xyear:
                        if yearname == syear:
                            if show["title"] in xyear[yearname]:
                                xyear[yearname].remove(show["title"])
                                changed = True
                                break
                    if changed:
                        break
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


def cleanYears(config):
    try:
        txy = []
        xy = config["Year"]
        if xy is not None:
            while len(xy) > 0:
                ty = xy.pop()
                for key in ty.keys():
                    if len(ty[key]) == 0:
                        log.info("Remove empty year: {}".format(key))
                    else:
                        txy.append(ty)
        config["Year"] = txy
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


def moveShow(show, config):
    try:
        then = time.time()
        tvhstat = os.stat(show["filename"])
        log.info("{}: {}".format(show["opbase"], FUT.sizeof_fmt(tvhstat.st_size)))
        if "year" in show:
            opdir = "/".join(
                [config["filmhome"], show["title"][0:1].upper(), show["opbase"]]
            )
            snfo = NFO.makeFilmNfo(show)
        else:
            opdir = "/".join([config["videohome"], show["category"], show["title"]])
            snfo = NFO.makeProgNfo(show)
        basefn = "/".join([opdir, show["opbase"]])
        opfn = basefn + ".mpg"
        mkopfn = basefn + ".mkv"
        existingfile = None
        if FUT.fileExists(opfn):
            existingfile = opfn
        elif FUT.fileExists(mkopfn):
            existingfile = mkopfn
        if existingfile is not None:
            log.info("kodi file already exists, not copying {}".format(existingfile))
            log.info("deleting from tvheadend")
            TVH.deleteRecording(show["uuid"])
        else:
            log.info("making directory {}".format(opdir))
            FUT.makePath(opdir)
            nfofn = basefn + ".nfo"
            log.info("writing nfo to {}".format(nfofn))
            with open(nfofn, "w") as nfn:
                nfn.write(snfo)
            log.info("copying {} to {}".format(show["filename"], opfn))
            shutil.copy2(show["filename"], opfn)
            if FUT.fileExists(opfn):
                cstat = os.stat(opfn)
                if cstat.st_size == tvhstat.st_size:
                    log.info(
                        "copying {} took: {}".format(
                            FUT.sizeof_fmt(cstat.st_size),
                            NFO.hmsDisplay(int(time.time() - then)),
                        )
                    )
                    log.info("show copied to {} OK.".format(opfn))
                    fhash, fsize = FUT.getFileHash(show["filename"])
                    log.info("deleting from tvheadend")
                    TVH.deleteRecording(show["uuid"])
                    log.info("updating DB")
                    db = tvheadend.tvhdb.TVHDb(dbfn)
                    # sql = "insert into files (name,size,hash) values ("
                    # sql += "'{}',{},'{}')".format(opfn, fsize, fhash)
                    # db.doSql(sql)
                    sql = "insert into files (name,size,hash) values (?, ?, ?)"
                    db.doInsertSql(sql, (opfn, fsize, fhash,))
                    # it is safe to run removeFromYear for all shows
                    # as it tests whether this is a movie or not
                    removeFromYear(show, config)
                    # log.info("\n")
                    # if show["channelname"].endswith("HD"):
                    #     log.info("Not converting HD programme {}".format(show["title"]))
                    # else:
                    # log.info("converting {} to mkv".format(show["title"]))
                    # convertToMkv(opfn)
                    # FFMPEG.convert(opfn)
            else:
                raise (
                    CopyFailure(
                        "Failed to copy {} to {}".format(show["filename"], opfn)
                    )
                )
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


def convertToMkv(fqfn):
    if FUT.fileExists(fqfn):
        cmd = ["/home/chris/bin/convert-ts-to-mkv.sh", "{}".format(fqfn)]
        proc = subprocess.run(cmd)
        if proc.returncode == 0:
            log.info("Converted {} to mkv".format(fqfn))
        else:
            log.info("Error muxing {}".format(fqfn))


def updateKodi():
    try:
        data = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan"}
        headers = {"content-type": "application/json"}
        url = "http://127.0.0.1:8080/jsonrpc"
        resp = requests.post(url, data=data, headers=headers, timeout=10)
        if resp.status_code < 399:
            log.info("Kodi update starting")
            log.info("response: {}".format(resp))
            log.info("response text: {}".format(resp.text))
        else:
            log.info("Failed to update Kodi")
            log.info("response: {}".format(resp))
            log.info("response text: {}".format(resp.text))
    except ConnectionError as ce:
        log.info("Kodi isn't running")
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


def tvhbatch():
    try:
        log.info("tvheadend batch utility " + tvheadend.__version__)
        config = CONF.readConfig()
        tvheadend.user = config["user"]
        tvheadend.passw = config["pass"]
        tvheadend.ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
        # ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
        # tvhauth = {"ip": ipaddr, "xuser": config["user"], "xpass": config["pass"]}
        tot, ents = TVH.finishedRecordings()
        shows = CATS.setCategories(ents, config)
        cn = 0
        for show in shows["shows"]:
            UT.addBaseFn(show)
            moveShow(show, config)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)
    finally:
        cleanYears(config)
        CONF.writeConfig(config)
        updateKodi()


if __name__ == "__main__":
    tvhbatch()
