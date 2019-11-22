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
watch module for tvh application
"""

import sys
import os
import time
import tvheadend
import tvheadend.tvhlog
import tvheadend.tvhdb
import tvheadend.config as CONF
import tvheadend.fileutils as FUT
import tvheadend.ffmpeg as FF

log = tvheadend.tvhlog.log
stopnext = "/home/chris/Videos/kmedia/tvh/stopnext"


def deleteFirstFile(db, name, xhash):
    try:
        vals = (1, name, xhash)
        sql = "delete from files where status=? and name=? and hash=?"
        db.doDeleteSql(sql, vals)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def getFirstFile(db):
    try:
        sql = "select * from files where status=0 limit 1"
        row = db.doSql(sql, one=1)
        vals = (row["name"], row["hash"])
        sql = "update files set status=1 where name=? and hash=?"
        db.doUpdateSql(sql, vals)
        return row
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def filesWaiting(db):
    try:
        sql = "select count(*) as cn from files where status=0"
        rows = db.doSql(sql)
        return int(rows[0][0])
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def processFiles(db):
    try:
        ret = True if FUT.fileExists(stopnext) else False
        cn = filesWaiting(db)
        log.info("{} files to process.".format(cn))
        while cn > 0:
            frow = getFirstFile(db)
            if FUT.fileExists(frow["name"]):
                log.info(
                    "Converting {}: {}".format(
                        os.path.basename(frow["name"]), FUT.sizeof_fmt(frow["size"])
                    )
                )
                FF.convert(frow["name"])
            log.info("updating DB, deleting {}".format(os.path.basename(frow["name"])))
            deleteFirstFile(db, frow["name"], frow["hash"])
            if FUT.fileExists(stopnext):
                ret = True
                break
            cn = filesWaiting(db)
            log.info("{} files to process.".format(cn))
        return ret
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def tvhwatch():
    try:
        log.info("tvheadend watch utility " + tvheadend.__version__)
        config = CONF.readConfig()
        db = tvheadend.tvhdb.TVHDb(config["tvhdb"])
        while True:
            stopnow = processFiles(db)
            if stopnow:
                FUT.fileDelete(stopnext)
                log.info("Stop file found, stopping now")
                break
            time.sleep(300)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


if __name__ == "__main__":
    tvhwatch()
