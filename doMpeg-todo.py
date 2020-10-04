#!/usr/bin/env python3

import sys
import tvheadend
import tvheadend.tvhlog
import tvheadend.tvhdb
import tvheadend.config as CONF
import tvheadend.fileutils as FUT
import tvheadend.ffmpeg as FF
from tvheadend.errors import errorRaise
from tvheadend.errors import errorNotify
from tvheadend.errors import errorExit

log = tvheadend.tvhlog.log


def processFile(fn, db):
    try:
        fhash, fsize = FUT.getFileHash(fn)
        sql = "insert into files (name,size,hash) values (?, ?, ?)"
        db.doInsertSql(sql, (fn, fsize, fhash,))
        log.info("added {} to db".format(fn))
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


def main():
    try:
        log.info("tvheadend db insert utility " + tvheadend.__version__)
        config = CONF.readConfig()
        db = tvheadend.tvhdb.TVHDb(config["tvhdb"])
        with open("/home/chris/Videos/kmedia/TV/mpeg-todo", "r") as ifn:
            lines = ifn.readlines()
        for line in lines:
            fqfn = line.strip()
            log.info("processing {}".format(fqfn))
            processFile(fqfn, db)
        log.info("done")
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


if __name__ == "__main__":
    main()
