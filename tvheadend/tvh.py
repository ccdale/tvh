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
tvheadend module for tvh application
"""
import sys
import requests
import tvheadend
from tvheadend.errors import errorNotify

class TVHError(Exception):
    pass


def sendToTVH(route,  data=None):
    """
    send a request to tvheadend
    """
    try:
        # auth = (xuser, xpass)
        auth = (tvheadend.user, tvheadend.passw)
        url = "http://" + tvheadend.ipaddr + "/api/" + route
        r = requests.post(url, data=data, auth=auth)
        # r = requests.get(url, auth=auth)
        if r.status_code is not 200:
            raise TVHError("error from tvh: {}".format(r))
        return r.json()
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorNotify(fname, e)


def finishedRecordings():
    """
    grid_finished returns a dict
    """
    entries = None
    total = 0
    try:
        data = {"limit": 100}
        j = sendToTVH("dvr/entry/grid_finished", data)
        if "entries" in j:
            entries = j["entries"]
        if "total" in j:
            total = int(j["total"])
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorNotify(fname, e)
    finally:
        return (total, entries)

def deleteRecording(uuid):
    try:
        data = {"uuid": uuid}
        sendToTVH("dvr/entry/remove", data)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorNotify(fname, e)
