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
ffmpeg module for tvh application
"""

import sys
import os
import datetime
import subprocess
import threading
import time
import datetime
import re
import json
import tvheadend.utils as UT
from tvheadend.errors import errorExit
from tvheadend.errors import errorRaise
from tvheadend.errors import errorNotify

class ConvertFailure(Exception):
    pass

def logout(msg):
    xtime = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
    print("{} {}".format(xtime, msg))

def fileInfo(fqfn):
    try:
        finfo = None
        try:
            if UT.fileExists(fqfn):
                cmd = ["ffprobe", "-loglevel", "quiet", "-of", "json", "-show_streams", fqfn]
                proc = subprocess.run(cmd, capture_output=True)
                if proc.returncode == 0:
                    xstr = proc.stdout.decode("utf-8")
                    # print(xstr)
                    finfo = json.loads(xstr)
        except Exception as e:
            errorNotify("fileInfo", e)
        return finfo
    except Exception as e:
        errorNotify("fileInfo", e)

def getStreamType(finfo, stype="video"):
    try:
        for stream in finfo["streams"]:
            if "codec_type" in stream and stream["codec_type"] == stype:
                return stream
        return None
    except Exception as e:
        errorNotify("getStreamType", e)

def trackIndexes(finfo):
    try:
        vtrack = atrack = strack = -1
        try:
            for stream in finfo["streams"]:
                if "codec_type" in stream:
                    if stream["codec_type"] == "video":
                        vtrack = stream["index"]
                    elif stream["codec_type"] == "audio":
                        if int(stream["channels"]) > 1:
                            atrack = stream["index"]
                    elif stream["codec_type"] == "subtitle":
                        strack = stream["index"]
        except Exception as e:
            errorNotify("trackIndexes", e)
        return (vtrack, atrack, strack)
    except Exception as e:
        errorNotify("trackIndexes", e)

def hasSubtitles(finfo):
    try:
        ret = False
        try:
            stream = getStreamType(finfo, stype="subtitle")
            if stream is not None:
                ret = True
        except Exception as e:
            errorNotify("hasSubtitles", e)
        return ret
    except Exception as e:
        errorNotify("hasSubtitles", e)

def canConvert(finfo):
    try:
        ret = False
        try:
            stream = getStreamType(finfo, "video")
            if stream is not None:
                if stream["codec_name"] == "mpeg2video":
                    ret = 1
                elif stream["codec_name"] == "h264":
                    ret =2
        except Exception as e:
            errorNotify("canConvert", e)
        return ret
    except Exception as e:
        errorNotify("canConvert", e)

def fileDuration(finfo):
    try:
        dur = 0
        sdur =""
        stream = getStreamType(finfo, "video")
        if stream is not None and "duration" in stream:
            xtmp = stream["duration"].split(".")
            dur = int(xtmp[0])
            sdur = UT.hms(dur)
        return (dur, sdur)
    except Exception as e:
        errorNotify("fileDuration", e)

def checkRemoveOutputFile(ofn):
    try:
        if UT.fileExists(ofn):
            size = UT.fileSize(ofn)
            if size > 0:
                msg = "Destination file '{}' exists: {}, not converting".format(ofn, UT.sizeof_fmt(size))
                logout(msg)
                raise ConvertFailure(msg)
            else:
                msg = "Deleting existing zero length destination file '{}'".format(ofn)
                logout(msg)
                os.remove(ofn)
    except Exception as e:
        errorNotify("checkRemoveOutputFile", e)

def makeStub(tracks, fqfn):
    try:
        cmdstub = ["nice", "-n", "19", "ffmpeg", "-i", fqfn]
        mapcmd = ["-map", "0:{}".format(tracks[0]), "-map", "0:{}".format(tracks[1])]
        ascmd = ["-acodec", "copy"]
        withsubs = True if tracks[2] > 0 else False
        if withsubs:
            mapcmd.append("-map")
            mapcmd.append("0:{}".format(tracks[2]))
            ascmd.append("-scodec")
            ascmd.append("copy")
        return (cmdstub, mapcmd, ascmd)
    except Exception as e:
        errorNotify("makeStub", e)

def makeHDCmd(tracks, fqfn, ofn):
    try:
        cmdstub, mapcmd, ascmd = makeStub(tracks, fqfn)
        convcmd = ["-c:v", "libx265", "-preset", "ultrafast", "-x265-params"]
        convcmd.append("crf=22:qcomp=0.8:aq-mode=1:aq_strength=1.0:qg-size=16:psy-rd=0.7:psy-rdoq=5.0:rdoq-level=1:merange=44")
        cmd = cmdstub + mapcmd + convcmd + ascmd + [ofn]
        msg = ""
        for thing in cmd:
            msg += " " + thing
        return (cmd, msg)
    except Exception as e:
        errorNotify("makeHDCmd", e)

def makeCmd(tracks, fqfn, ofn):
    try:
        cmdstub, mapcmd, ascmd = makeStub(tracks, fqfn)
        convcmd = ["-c:v", "libx265", "-crf", "28"]
        cmd = cmdstub + mapcmd + convcmd + ascmd + [ofn]
        msg = ""
        for thing in cmd:
            msg += " " + thing
        return (cmd, msg)
    except Exception as e:
        errorNotify("makeCmd", e)

def runConvert(cmd, fqfn, ofn):
    bname = os.path.basename(fqfn)
    thebin = "/home/chris/Videos/kmedia/thebin/"
    outfn = thebin + "tvhf.out"
    out = open(outfn, "wb")
    status=["/home/chris/bin/statusconvert.sh"]
    logout("starting status command")
    pstatus = subprocess.Popen(status)
    logout("starting ffmpeg")
    proc = subprocess.run(cmd, stderr=subprocess.STDOUT, stdout=out)
    logout("wait for status command to finish")
    pstatus.wait()
    if proc.returncode == 0:
        out.close()
        logout("Conversion was successful")
        insize = UT.fileSize(fqfn)
        sinsize = UT.sizeof_fmt(insize)
        outsize = UT.fileSize(ofn)
        soutsize = UT.sizeof_fmt(outsize)
        logout("Input size: {}, output size: {}".format(sinsize, soutsize))
        if outsize > insize:
            logout("input size is smaller than output size, keeping input file")
            obname = os.path.basename(ofn)
            destfn = thebin + bname
            logout("Deleting '{}' file (to {})".format(ofn, thebin))
            UT.rename(ofn, destfn)
        else:
            destfn = thebin + bname
            logout("Deleting '{}' file (to {})".format(fqfn, thebin))
            UT.rename(fqfn, destfn)
    else:
        out.close()
        outlog = thebin + bname + "-tvhf.log"
        UT.rename(outfn, outlog)
        msg = "Conversion of '{}' to '{}' failed, output in {}".format(fqfn, ofn, outlog)
        logout(msg)
        logout("Removing failed out file '{}'".format(ofn))
        if UT.fileExists(ofn):
            os.remove(ofn)
        raise ConvertFailure(msg)

def runThreadConvert(cmd, fqfn, ofn, duration, regex):
    try:
        print("")
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, )
        t = threading.Thread(target=processProc, args=(proc, regex, duration))
        # wait a bit before processing output
        time.sleep(10)
        # start the thread to read and process output from ffmpeg
        t.start()
        # wait for ffmpeg to finish producing output
        t.join()
        print("")
    except Exception as e:
        errorNotify("runThreadConvert", e)

def processProc(proc, regex, duration):
    """
    looking for the output lines from ffmpeg that look like

    frame=   71 fps=0.0 q=-0.0 size=       3kB time=00:00:03.43 bitrate=   7.7kbits/s speed=6.86x

    using the python regex extensions to name the groups
    (see https://docs.python.org/3/howto/regex.html#non-capturing-and-named-groups)

    The regular expression is now in the convert function so that it is
    only compiled once.
    """
    try:
        for line in iter(proc.stdout.readline, ''):
            # print(line)
            m = regex.match(line)
            if m is not None:
                xdict = m.groupdict()
                if "time" in xdict:
                    now = int(time.time())
                    # print("getting tsecs")
                    tsecs = UT.secondsFromHMS(xdict["time"])
                    # print("getting pc")
                    pc = int((tsecs * 100) / duration)
                    if "speed" in xdict:
                        # print("getting tleft")
                        tleft = int((duration - tsecs) / float(xdict["speed"]))
                        # print("getting stleft")
                        stleft = UT.hms(tleft)
                        # print("calc then")
                        then = now + tleft
                        # print("getting dtts")
                        dtts = datetime.datetime.fromtimestamp(then)
                        # print("getting sthen")
                        sthen = dtts.strftime("%H:%M:%S")
                        # print("outputting")
                        print("\rComplete: {}% ETA: {} ({})".format(pc, sthen, stleft), end='')
            # print("\nsleeping")
            time.sleep(10)
            # print("flushing")
            proc.stdout.flush()
    except Exception as e:
        errorNotify("processProc", e)

def convert(fqfn):
    try:
        finfo = fileInfo(fqfn)
        rstr = r'frame=\s*(?P<frame>[0-9]+)\s+'
        rstr += r'fps=(?P<fps>[0-9.]+)\s+.*'
        rstr += r'size=\s*(?P<size>[0-9kmgB]+)\s+'
        rstr += r'time=(?P<time>[0-9:.]+)\s+'
        rstr += r'bitrate=\s*(?P<bitrate>[0-9.]+[km]bits/s)\s+'
        rstr += r'speed=(?P<speed>[0-9.]+)x'
        regex = re.compile(rstr)
        if finfo is not None and canConvert(finfo):
            cconv = canConvert(finfo)
            if cconv:
                tracks = trackIndexes(finfo)
                withsubs = True if tracks[2] > 0 else False
                fn, fext = os.path.splitext(fqfn)
                ofn = fn + ".mkv"
                checkRemoveOutputFile(ofn)
                if cconv == 1:
                    cmd, msg = makeCmd(tracks, fqfn, ofn)
                else:
                    cmd, msg = makeHDCmd(tracks, fqfn, ofn)
                logout("command: {}".format(msg))
                xmsg = ", with subtitles," if withsubs else ""
                msg = "Converting{} '{}' to '{}'".format(xmsg, fqfn, ofn)
                logout(msg)
                dur, sdur = fileDuration(finfo)
                logout("file duration: {}".format(sdur))
                runConvert(cmd, fqfn, ofn)
                # runThreadConvert(cmd, fqfn, ofn, dur, regex)
        else:
            msg = "Cannot convert {}".format(fqfn)
            logout(msg)
            raise ConvertFailure(msg)
    except Exception as e:
        errorNotify("convert", e)

def main():
    if len(sys.argv) > 1:
        convert(sys.argv[1])
    else:
        print("ffmpeg.py <filename>")

if __name__ == "__main__":
    main()
