import sys
import tvheadend
import tvheadend.utils as UT
import tvheadend.fileutils as FUT
import tvheadend.tvhlog
import tvheadend.tvhdb
from tvheadend.errors import errorExit
from tvheadend.errors import errorRaise
from tvheadend.errors import errorNotify

log = tvheadend.tvhlog.log


def main():
    try:
        files = []
        fvals = []
        dbfn = "/home/chris/Videos/kmedia/tvh/tvh.db"
        fffn = "/home/chris/Videos/kmedia/TV/mpeg-todo"
        with open(fffn, "r") as fn:
            lines = fn.readlines()
        for line in lines:
            files.append(line.strip())
        log.info("Found {} files to insert".format(len(files)))
        for fn in files:
            if FUT.fileExists(fn):
                log.info("obtaining details of {}".format(fn))
                fhash, fsize = FUT.getFileHash(fn, blocksize=10485760)
                log.info("{} {}".format(fhash, FUT.sizeof_fmt(fsize)))
                fvals.append((fn, fsize, fhash))
        cn = len(fvals)
        log.info("inserting {} files into DB".format(len(fvals)))
        db = tvheadend.tvhdb.TVHDb(dbfn)
        sql = "insert into files (name,size,hash) values (?, ?, ?)"
        db.doInsertSql(sql, fvals)
        sql = "select count(*) as cn from files"
        row = db.doSql(sql, one=1)
        log.info("there are {} files in the db".format(row["cn"]))
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


if __name__ == "__main__":
    main()
