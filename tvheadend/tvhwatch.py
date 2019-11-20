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
import tvheadend
import tvheadend.tvhlog
import tvheadend.tvhdb
import tvheadend.config as CONF

log = tvheadend.tvhlog.log


def tvhwatch():
    try:
        log.info("tvheadend watch utility " + tvheadend.__version__)
        config = CONF.readConfig()
        db = tvheadend.tvhdb.TVHDb(config["tvhdb"])
        sql = "select count(*) as cn from files"
        rows = db.doSql(sql)
        for row in rows:
            print(row)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


if __name__ == "__main__":
    tvhwatch()
