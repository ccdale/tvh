# vim: set expandtab tabstop=4 shiftwidth=4 softtabstop=4 foldmethod=indent ft=python:

import sqlite3
import time
import tvheadend.tvhlog
import tvheadend.fileutils as FUT
from tvheadend.errors import errorRaise
from tvheadend.errors import errorNotify

log = tvheadend.tvhlog.log


class DBInsertError(Exception):
    pass


class DBUpdateError(Exception):
    pass


class DBLockError(Exception):
    pass


class TVHDb(object):
    def __init__(self, dbfilename):
        log.debug("Db starting")
        self.dbpath = dbfilename
        self.lockfn = dbfilename + ".LOCKED"
        self.locktime = 30

    def get_connection(self):
        try:
            self.aquireLock()
            self.connection = sqlite3.connect(self.dbpath)
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def close_connection(self):
        try:
            self.connection.close()
            self.releaseLock()
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def aquireLock(self):
        try:
            cn = 0
            while FUT.fileExists(self.lockfn):
                time.sleep(1)
                cn += 1
                if cn > self.locktime:
                    raise DBLockError("Timeout waiting for locked DB")
            FUT.fileTouch(self.lockfn)
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def releaseLock(self):
        try:
            FUT.fileDelete(self.lockfn)
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorRaise(fname, e)

    def doSql(self, sql, dictionary=1, one=0):
        self.get_connection()
        with self.connection:
            if dictionary == 1:
                self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            log.debug("SQL: {}".format(sql))
            try:
                cursor.execute(sql)
                if one > 0:
                    rows = cursor.fetchone()
                else:
                    rows = cursor.fetchall()
            except Exception as E:
                log.error("dosql error: {}: {}".format(type(E).__name__, E))
                log.error("dosql sql: {}".format(sql))
                rows = {}
        self.close_connection()
        return rows

    def doUpdateSql(self, sql):
        ret = False
        self.get_connection()
        try:
            with self.connection:
                cursor = self.connection.cursor()
                log.debug("Update SQL: {}".format(sql))
                cursor.execute(sql)
            self.close_connection()
            ret = True
        except Exception as e:
            log.error("update sql error: sql {}".format(sql))
            log.error("update sql error: {}: {}".format(type(e).__name__, e))
        return ret

    def doInsertSql(self, sql):
        ret = False
        self.get_connection()
        try:
            with self.connection:
                cursor = self.connection.cursor()
                log.debug("Insert SQL: {}".format(sql))
                cursor.execute(sql)
            self.close_connection()
            ret = True
        except Exception as e:
            log.error("insert sql error: sql {}".format(sql))
            log.error("insert sql error: {}: {}".format(type(e).__name__, e))
        return ret

    def doReplaceSql(self, sql):
        ret = False
        self.get_connection()
        try:
            with self.connection:
                cursor = self.connection.cursor()
                log.debug("replace SQL: {}".format(sql))
                cursor.execute(sql)
            ret = True
        except Exception as e:
            log.error("replace sql error: sql {}".format(sql))
            log.error("replace sql error: {}: {}".format(type(e).__name__, e))
        return ret

    def sqlStr(self, xstr):
        if type(xstr).__name__ == "int":
            op = str(xstr)
        elif "'" in xstr:
            op = '"' + xstr + '"'
        else:
            op = "'" + xstr + "'"
        return op

    def addToString(self, instr, item, delimeter=","):
        ostr = ""
        if len(instr) == 0:
            ostr += item
        else:
            ostr += instr + delimeter + item
        return ostr

    def makeWhere(self, data):
        where = ""
        for key in data.keys():
            dat = key + "=" + self.sqlStr(data[key])
            where = self.addToString(where, dat, " and ")
        return "where {}".format(where)

    def makeColumns(self, keys, xdict):
        ostr = ""
        for key in keys:
            tstr = self.sqlStr(xdict[key])
            ostr = self.addToString(ostr, tstr)
        return ostr

    def makeCheckSelect(self, keys, xdict, table):
        sql = "select * from {} where ".format(table)
        where = ""
        for key in keys:
            tstr = self.sqlStr(xdict[key])
            where = self.addToString(where, key + "=" + tstr, " and ")
        sql += where
        return sql

    def rowExists(self, table, data):
        sql = "select * from {}".format(table)
        sql += " {}".format(self.makeWhere(data))
        row = self.doSql(sql, one=1)
        if row is not None and len(row) > 0:
            return (True, row)
        else:
            return (False, row)

    def makeInsertSql(self, table, data):
        kstr = vstr = ""
        for key in data.keys():
            kstr = self.addToString(kstr, key)
            vstr = self.addToString(vstr, self.sqlStr(data[key]))
        return "insert into {} ({}) values ({})".format(table, kstr, vstr)

    def makeUpdateStr(self, data):
        setstr = ""
        for key in data.keys():
            setstr = self.addToString(
                setstr, "{}={}".format(key, self.sqlStr(data[key]))
            )
        return setstr

    def makeUpdateSql(self, table, indexdict, data):
        where = self.makeWhere(indexdict)
        setstr = self.makeUpdateStr(data)
        return "update {} set {} {}".format(table, setstr, where)
