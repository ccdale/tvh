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
        dbfn = "/home/chris/Videos/kmedia/tvh/tvh.db"
        fffn = "/home/chris/Videos/kmedia/TV/mpeg-todo"
        db = tvheadend.tvhdb.TVHDb(dbfn)
        sql = "insert into files (name,size,hash) values (?, ?, ?)"
        with open(fffn, "r") as fn:
            lines = fn.readlines()
        for line in lines:
            files.append(line.strip())
        log.info("Found {} files to insert".format(len(files)))
        cn = 0
        for fn in files:
            if FUT.fileExists(fn):
                log.info("obtaining details of {}".format(fn))
                fhash, fsize = FUT.getFileHash(fn, blocksize=10485760)
                log.info("{} {}".format(fhash, FUT.sizeof_fmt(fsize)))
                log.info("inserting into db")
                db.doInsertSql(sql, [fn, fsize, fhash])
                cn += 1
        log.info("inserted {} files into DB".format(cn))
        db.doInsertSql(sql, fvals)
        sql = "select count(*) as cn from files"
        row = db.doSql(sql, one=1)
        log.info("there are {} files currently in the db".format(row["cn"]))
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


if __name__ == "__main__":
    main()
