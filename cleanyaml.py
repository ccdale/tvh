#!/usr/bin/env python3

"""
script to cleanup the yaml format config file
"""

import tvheadend
import tvheadend.tvh as TVH
import tvheadend.config as CONF
import tvheadend.categories as CATS
from tvheadend.errors import errorExit


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


def cleanYaml():
    try:
        config = CONF.readConfig()
        tvheadend.user = config["user"]
        tvheadend.passw = config["pass"]
        tvheadend.ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
        tot, ents = TVH.finishedRecordings()
        titles = set()
        for entry in ents:
            if "disp_title" in entry:
                titles.add(entry["disp_title"])
        if config["Year"] is not None:
            ycn = ocn = 0
            txy = []
            while len(config["Year"]) > 0:
                ty = config["Year"].pop()
                # ty.keys() returns a 1 element list, this turns it into a string
                (year,) = ty.keys()
                tmpyear = []
                for title in ty[year]:
                    ycn += 1
                    if title in titles:
                        ocn += 1
                        tmpyear.append(title)
                if len(tmpyear) > 0:
                    txy.append({year: tmpyear})
            config["Year"] = txy
        print("searched {} titles, found {}".format(ycn, ocn))
        CONF.writeConfig(config)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


if __name__ == "__main__":
    cleanYaml()
