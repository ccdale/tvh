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

def getStreamType(finfo, stype="video"):
    for stream in finfo["streams"]:
        if "codec_type" in stream and stream["codec_type"] == stype:
            return stream
    return None

def trackIndexes(finfo):
    vtrack = atrack = strack = -1
    try:
        for stream in finfo["streams"]:
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

def hasSubtitles(finfo):
    ret = False
    try:
        stream = getStreamType(finfo, stype="subtitle")
        if stream is not None:
            ret = True
    except Exception as e:
        errorNotify("hasSubtitles", e)
    return ret

def canConvert(finfo):
    ret = False
    try:
        stream = getStreamType(finfo, "video")
        if stream is not None and stream["codec_name"] == "mpeg2video":
            ret = True
    except Exception as e:
        errorNotify("canConvert", e)
    return ret

def fileDuration(finfo):
    dur = 0
    sdur =""
    stream = getStreamType(finfo, "video")
    if stream is not None and "duration" in stream:
        dur = int(stream["duration"])
        sdur = UT.hms(dur)
    return (dur, sdur)

def checkRemoveOutputFile(ofn):
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

def makeCmd(tracks, ofn):
    cmdstub = ["nice", "-n", "19", "ffmpeg", "-i", fqfn]
    mapcmd = ["-map", "0:{}".format(tracks[0]), "-map", "0:{}".format(tracks[1])]
    if withsubs:
        mapcmd.append("-map")
        mapcmd.append("0:{}".format(tracks[2]))
    convcmd = ["-c:v", "libx265", "-crf", "28", "-acodec", "copy"]
    if withsubs:
        convcmd.append("-scodec")
        convcmd.append("copy")
    cmd = cmdstub + mapcmd + convcmd + [ofn]
    msg = ""
    for thing in cmd:
        msg += " " + thing
    return (cmd, msg)

def runConvert(cmd, fqfn, ofn, duration):
    proc = subprocess.run(cmd, capture_output=True)
    stderr = proc.stderr.decode("utf-8")
    stdout = proc.stdout.decode("utf-8")
    if proc.returncode == 0:
        logout("Conversion was successful")
        bname = os.path.basename(fqfn)
        thebin = "/home/chris/Videos/kmedia/thebin/"
        destfn = thebin + bname
        logout("Deleting '{}' file (to {})".format(fqfn, thebin))
        UT.rename(fqfn, destfn)
    else:
        msg = "Conversion of '{}' to '{}' failed".format(fqfn, ofn)
        logout(msg + "\n\n" + stdout + "\n\n" + stderr)
        logout("Removing failed out file '{}'".format(ofn))
        if UT.fileExists(ofn):
            os.remove(ofn)
        raise ConvertFailure(msg)

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
            tracks = trackIndexes(finfo)
            withsubs = True if tracks[2] > 0 else False
            fn, fext = os.path.splitext(fqfn)
            ofn = fn + ".mkv"
            checkRemoveOutputFile(ofn)
            cmd, msg = makeCmd(tracks, ofn)
            logout("command: {}".format(msg))
            xmsg = ", with subtitles," if withsubs else ""
            msg = "Converting{} '{}' to '{}'".format(xmsg, fqfn, ofn)
            logout(msg)
            dur, sdur = fileDuration(finfo)
            logout("file duration: {}".format(sdur))
            runConvert(cmd, fqfn, ofn, dur)
        else:
            msg = "Cannot convert {}".format(fqfn)
            logout(msg)
            raise ConvertFailure(msg)
    except Exception as e:
        errorNotify("convert", e)

def processStdOut(stdout, regex, duration):
    """
    looking for the output lines from ffmpeg that look like

    frame=   71 fps=0.0 q=-0.0 size=       3kB time=00:00:03.43 bitrate=   7.7kbits/s speed=6.86x

    using the python regex extensions to name the groups
    (see https://docs.python.org/3/howto/regex.html#non-capturing-and-named-groups)

    The regular expression is now in the convert function so that it is
    only compiled once.
    """
    m = regex.match(stdout)
    if m is not None:
        xdict = m.groupdict()
        print(xdict)

def main():
    # finfo = fileInfo("/home/hts/Would-I-Lie-To-You_.ts")
    # finfo = fileInfo("/home/hts/The-Protectors.ts")
    # finfo = fileInfo("/home/hts/World-War-Weird-S02E05.ts")
    # print(finfo)
    # if canConvert(finfo):
    #     print("can convert")
    # else:
    #     print("cannot convert")
    # if hasSubtitles(finfo):
    #     print("has subtitles")
    # else:
    #     print("doesn't have subtitles")
    # convert("/home/chris/Videos/kmedia/incoming/Abandoned Engineering - Escobar's Ruin - S04E06.mpg")
    # finfo = fileInfo("/home/chris/Videos/kmedia/incoming/Abandoned Engineering - S04E06.mpg")
    if len(sys.argv) > 1:
        convert(sys.argv[1])
    else:
        print("ffmpeg.py <filename>")

if __name__ == "__main__":
    main()
