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


USAGE = """
Usage:

    tvhfile "<fqfn1>" "<fqfn2>" ... "<fqfnn>"
"""


def processFile(fn, db):
    try:
        fhash, fsize = FUT.getFileHash(fn)
        sql = "insert into files (name,size,hash) values (?, ?, ?)"
        db.doInsertSql(sql, (fn, fsize, fhash,))
        log.info("added {} to db".format(fn))
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


def doFile():
    try:
        log.info("tvheadend TS file insert utility " + tvheadend.__version__)
        config = CONF.readConfig()
        db = tvheadend.tvhdb.TVHDb(config["tvhdb"])
        if len(sys.argv) > 1:
            for fn in sys.argv[1:]:
                processFile(fn, db)
        else:
            sys.exit(USAGE)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


if __name__ == "__main__":
    doFile()
