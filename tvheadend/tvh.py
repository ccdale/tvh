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
import json
import time
import tvheadend
from operator import itemgetter
import tvheadend.utils as UT
from tvheadend.errors import errorNotify
from tvheadend.errors import errorRaise


class TVHError(Exception):
    pass


class TVHNoEPG(Exception):
    pass


def sendToTVH(route, data=None):
    """
    send a request to tvheadend
    """
    try:
        # auth = (xuser, xpass)
        auth = (tvheadend.user, tvheadend.passw)
        url = "http://" + tvheadend.ipaddr + "/api/" + route
        r = requests.post(url, data=data, auth=auth)
        # r = requests.get(url, auth=auth)
        if r.status_code != 200:
            raise TVHError("error from tvh: {}".format(r))
        return r.json()
    except Exception:
        try:
            print("Exception, trying again")
            txt = r.text.replace(chr(25), " ")
            return json.loads(txt)
        except Exception as xe:
            print("2nd exception")
            print("{}".format(xe))
    # except json.decoder.JSONDecodeError as je:
    #     # output needs cleaning up
    #     # tvh sometimes has character 25 in place of an apostrophe
    #     txt = r.text.replace(chr(25), " ")
    #     fname = sys._getframe().f_code.co_name
    #     errorNotify(fname, je)
    #     return json.loads(txt)
    # except Exception as e:
    #     print("{}".format(e))
    #     print("text: {}".format(r.text))
    #     fname = sys._getframe().f_code.co_name
    #     errorNotify(fname, e)


def finishedRecordings():
    """
    grid_finished returns a dict

    single program looks like:
    {
        'uuid': 'a64b50c335f01c0df1a49f11a0f8d3f4',
        'enabled': True,
        'start': 1576749600,
        'start_extra': 0,
        'start_real': 1576749570,
        'stop': 1576751400,
        'stop_extra': 0,
        'stop_real': 1576752300,
        'duration': 2700,
        'channel': 'c5827940c7ae3d76ea80df053112dc9c',
        'channel_icon': '',
        'channelname': 'BBC ONE HD',
        'title': {'eng': 'Homes Under the Hammer'},
        'disp_title': 'Homes Under the Hammer',
        'subtitle': {'eng': 'A house with a stream but close to a railway line in Handsacre in Staffordshire and a large three-storey property in Plymouth are sold under the hammer. [S] [HD]'},
        'disp_subtitle': 'A house with a stream but close to a railway line in Handsacre in Staffordshire and a large three-storey property in Plymouth are sold under the hammer. [S] [HD]',
        'description': {'eng': 'A house with a stream but close to a railway line in Handsacre in Staffordshire and a large three-storey property in Plymouth are sold under the hammer. [S] [HD]'},
        'disp_description': 'A house with a stream but close to a railway line in Handsacre in Staffordshire and a large three-storey property in Plymouth are sold under the hammer. [S] [HD]',
        'pri': 2,
        'retention': 0,
        'removal': 0,
        'playposition': 0,
        'playcount': 0,
        'config_name': 'ee86fd19903e87679e5fdfe243966ad0',
        'owner': 'chris',
        'creator': 'chris',
        'filename': '/home/hts/Railway/Homes-Under-the-Hammer.ts',
        'directory': 'Railway',
        'errorcode': 0,
        'errors': 0,
        'data_errors': 0,
        'dvb_eid': 0,
        'noresched': True,
        'norerecord': False,
        'fileremoved': 0,
        'autorec': '0dee37cd9707da051618045a73c9aa43',
        'autorec_caption': 'railway',
        'timerec': '',
        'timerec_caption': '',
        'parent': '',
        'child': '',
        'content_type': 2,
        'broadcast': 0,
        'url': 'dvrfile/a64b50c335f01c0df1a49f11a0f8d3f4',
        'filesize': 1045284324,
        'status': 'Completed OK',
        'sched_status': 'completed',
        'duplicate': 0,
        'comment': 'Auto recording: railway'
    }
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


def channels():
    """
    return a sorted list of enabled channels
    """
    try:
        sents = None
        data = {"limit": 200}
        j = sendToTVH("channel/grid", data)
        if "entries" in j:
            sents = sorted(j["entries"], key=itemgetter("number"), reverse=False)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorNotify(fname, e)
    finally:
        return sents


def channelPrograms(channel="BBC Four HD"):
    """
    return a time sorted dict of programs for the named channel

    each event looks like:
    {
      'eventId': 5050806,
      'episodeId': 5050807,
      'serieslinkId': 91157,
      'serieslinkUri': 'ddprogid:///usr/bin/tv_grab_zz_sdjson/SH000191120000',
      'channelName': 'BBC Four HD',
      'channelUuid': '2f6501b00ef0982c8fc3aa67b0229ecc',
      'channelNumber': '106',
      'channelIcon': 'https://s3.amazonaws.com/schedulesdirect/assets/stationLogos/s83282_h3_aa.png',
      'start': 1567936800,
      'stop': 1567965480,
      'title': 'SIGN OFF',
      'description': 'Sign off.',
      'summary': 'Sign off.', # optional
      'nextEventId': 5050808,
    }
    """
    try:
        # chans = channels()
        # now = int(time.time())
        # xfilter = [ { "field": "name", "type": "string", "value": channel, "comparison": "eq", } ]
        # xfilter = [
        #     {"field": "stop", "type": "numeric", "value": str(now), "comparison": "gt"},
        #     {
        #         "field": "start",
        #         "type": "numeric",
        #         "value": str(now + (3600 * 24)),
        #         "comparison": "lt",
        #     },
        # ]
        # if chans is not None:
        # for chan in chans:
        # if chan["name"] == channel:
        # data = {"filter": xfilter}
        data = {"limit": "999"}
        j = sendToTVH("epg/events/grid", data)
        print(str(j["totalCount"]) + " programs")
        mindur, minprog = UT.displayProgramList(j["entries"], 24, channel)
        print("min duration: {}".format(mindur))
        print("{}".format(minprog))
        # break
        # else:
        # print("chans is none")
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorNotify(fname, e)


def timeSlotPrograms(start=0, length=2):
    try:
        # now = int(time.time())
        if start == 0:
            start = int(time.time())
        xfilter = [
            {
                "field": "stop",
                "type": "numeric",
                "value": str(start),
                "comparison": "gt",
            },
            {
                "field": "start",
                "type": "numeric",
                "value": str(start + (3600 * length)),
                "comparison": "lt",
            },
        ]
        data = {"filter": xfilter}
        data = {"limit": "999"}
        j = sendToTVH("epg/events/grid", data)
        if "entries" in j:
            mindur, minprog = UT.displayProgramList(j["entries"], length)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def channelFilter(epg, channel):
    try:
        cevents = []
        for event in epg:
            if event["channelName"] == channel:
                cevents.append(event)
        return cevents
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def timeFilter(epg, start, length):
    try:
        print(f"start: {start}, length: {length}")
        fevents = []
        if length is None:
            length = 2
        print(f"start: {start}, length: {length}")
        stop = start + (3600 * length)
        print(f"start: {start}, length: {length}, stop: {stop}")
        for event in epg:
            if int(event["stop"]) > start and int(event["start"]) < stop:
                fevents.append(event)
        return fevents
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def filterPrograms(channel=None, start=None, length=None):
    try:
        total, entries = getEpg()
        if channel is not None and start is not None:
            epg = channelFilter(entries, channel)
            return timeFilter(epg, start, length)
        if channel is not None:
            return channelFilter(entries, channel)
        if start is not None:
            return timeFilter(entries, start, length)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)


def getEpg():
    """obtain the epg from tvheadend

    returns as much data as it can (as tvheadend filtering
    doesn't seem to work to well)

    [
        {
            'eventId': 6008447,
            'episodeId': 6059918,
            'episodeUri': 'ddprogid:///usr/bin/tv_grab_zz_sdjson/EP013053180396',
            'channelName': 'BBC Two HD',
            'channelUuid': 'b5ae8b7cd3c1653d66ccfe89710ec067',
            'channelNumber': '102',
            'channelIcon': 'https://s3.amazonaws.com/schedulesdirect/assets/stationLogos/s50059_h3_aa.png',
            'start': 1579428000,
            'stop': 1579433400,
            'title': 'Saturday Kitchen Best Bites',
            'description': 'Matt Tebbutt takes a look back at some of his favourite recipes and best moments from "Saturday Kitchen".',
            'new': 1,
            'repeat': 1,
            'genre': [165],
            'nextEventId': 6008459
        }
    ]
    """
    try:
        total = entries = None
        data = {"limit": "9999"}
        j = sendToTVH("epg/events/grid", data=data)
        if "totalCount" in j:
            total = j["totalCount"]
        if "entries" in j:
            entries = j["entries"]
        else:
            raise TVHNoEPG("Failed to retrieve data from TVHeadend")
        return (total, entries)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorRaise(fname, e)
