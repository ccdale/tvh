import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import os
import sys
import time

import tvheadend
from tvheadend import __version__ as verstr
import tvheadend.tvh as TVH
import tvheadend.config as CONF
from tvheadend.errors import errorRaise
from tvheadend.errors import errorNotify
from tvheadend.errors import errorExit

log = tvheadend.tvhlog.log


def getStartLength():
    cn = len(sys.argv)
    if cn == 3:
        start = int(sys.argv[1])
        length = int(sys.argv[2])
    elif cn == 2:
        start = int(sys.argv[1])
        length = 2
    elif cn == 1 or cn > 3:
        start = int(time.time())
        length = 2
    return (start, length)


def gobabe():
    try:
        config = CONF.readConfig()
        tvheadend.user = config["user"]
        tvheadend.passw = config["pass"]
        tvheadend.ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
        start, length = getStartLength()
        TVH.timeSlotPrograms(start, length)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


if __name__ == "__main__":
    gobabe()
