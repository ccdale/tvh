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
DB list module for tvh application
"""

import tvheadend
import tvheadend.tvhlog
import tvheadend.tvhdb
import tvheadend.config as CONF
from tvheadend.ffmpeg import fileInfo
from tvheadend.ffmpeg import canConvert
from tvheadend.errors import errorRaise
from tvheadend.errors import errorNotify
from tvheadend.errors import errorExit

log = tvheadend.tvhlog.log

def listFilesWaiting(db):
    try:
        sql = "select * from files where status=0"
        rows = db.doSql(sql)
        sd = hd = 0
        for row in rows:
            finfo = fileInfo(row["name"])
            cconv = canConvert(finfo)
            ftype = "HD" if cconv == 2 else "SD"
            if cconv == 2:
                ftype = "HD"
                hd += 1
            else:
                ftype = "SD"
                sd += 1
            print(f"""{ftype}: {row["name"]}""")
        print(f"\n{sd} SD files, {hd} HD files")
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def tvhwatchlist():
    try:
        log.info("tvheadend watch utility " + tvheadend.__version__)
        config = CONF.readConfig()
        db = tvheadend.tvhdb.TVHDb(config["tvhdb"])
        listFilesWaiting(db)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)

if __name__ == "__main__":
    tvhwatchlist()
