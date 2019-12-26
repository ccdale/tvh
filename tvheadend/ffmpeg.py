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
import queue
import tvheadend.utils as UT
import tvheadend.fileutils as FUT
import tvheadend.tvhlog
from tvheadend.errors import errorExit
from tvheadend.errors import errorRaise
from tvheadend.errors import errorNotify

log = tvheadend.tvhlog.log
olines = []
thebin = "/home/chris/Videos/kmedia/thebin/"
gpid = -1


class ConvertFailure(Exception):
    pass


def stopProcessing():
    global gpid
    if gpid > 0:
        os.kill(gpid)


def fileInfo(fqfn):
    try:
        finfo = None
        try:
            if FUT.fileExists(fqfn):
                cmd = [
                    "ffprobe",
                    "-loglevel",
                    "quiet",
                    "-of",
                    "json",
                    "-show_streams",
                    fqfn,
                ]
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
                    ret = 2
        except Exception as e:
            errorNotify("canConvert", e)
        return ret
    except Exception as e:
        errorNotify("canConvert", e)


def fileDuration(finfo):
    try:
        dur = 0
        sdur = ""
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
        if FUT.fileExists(ofn):
            size = FUT.fileSize(ofn)
            if size > 0:
                msg = "Destination file '{}' exists: {}, not converting".format(
                    ofn, FUT.sizeof_fmt(size)
                )
                log.info(msg)
                raise ConvertFailure(msg)
            else:
                msg = "Deleting existing zero length destination file '{}'".format(ofn)
                log.info(msg)
                os.remove(ofn)
    except Exception as e:
        errorNotify("checkRemoveOutputFile", e)


def makeStub(tracks, fqfn):
    try:
        cmdstub = ["nice", "-n", "19", "ffmpeg", "-i", fqfn]
        mapcmd = ["-map", f"0:{tracks[0]}", "-map", f"0:{tracks[1]}"]
        ascmd = ["-acodec", "copy"]
        withsubs = True if tracks[2] > 0 else False
        if withsubs:
            mapcmd += ["-map", f"0:{tracks[2]}"]
            ascmd += ["-scodec", "copy"]
        return (cmdstub, mapcmd, ascmd)
    except Exception as e:
        errorNotify("makeStub", e)


def makeHDCmd(tracks, fqfn, ofn):
    try:
        cmdstub, mapcmd, ascmd = makeStub(tracks, fqfn)
        # convcmd = ["-c:v", "libx265", "-preset", "ultrafast", "-x265-params"]
        # convcmd.append(
        #     "crf=22:qcomp=0.8:aq-mode=1:aq_strength=1.0:qg-size=16:psy-rd=0.7:psy-rdoq=5.0:rdoq-level=1:merange=44"
        # )
        convcmd = ["-vcodec", "copy"]
        cmd = cmdstub + mapcmd + convcmd + ascmd + [ofn]
        msg = "HD Command:"
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
        msg = "SD Command:"
        for thing in cmd:
            msg += " " + thing
        return (cmd, msg)
    except Exception as e:
        errorNotify("makeCmd", e)


def runThreadConvert(cmd, fqfn, ofn, duration, regex):
    global gpid
    try:
        print("")
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        gpid = proc.pid
        outq = queue.Queue()
        t = threading.Thread(target=processProc, args=(proc, regex, duration, outq))
        # wait a bit before processing output
        time.sleep(10)
        # start the thread to read and process output from ffmpeg
        t.start()
        try:
            print("")
            while True:
                try:
                    line = outq.get(block=False)
                    # log.info(line)
                    print(f"\r{line:>56}", end="")
                except queue.Empty:
                    time.sleep(10)
                if proc.poll() is not None:
                    print("")
                    break
        finally:
            rc = proc.returncode
            # wait for ffmpeg to finish producing output
            t.join()
            return rc
    except Exception as e:
        errorNotify("runThreadConvert", e)


def processProc(proc, regex, duration, outq):
    """
    looking for the output lines from ffmpeg that look like

    frame=   71 fps=0.0 q=-0.0 size=       3kB time=00:00:03.43 bitrate=   7.7kbits/s speed=6.86x

    frame=34458 fps= 35 q=-0.0 size= 1031676kB time=00:22:59.64 bitrate=6125.9kbits/s speed= 1.4x

    using the python regex extensions to name the groups
    (see https://docs.python.org/3/howto/regex.html#non-capturing-and-named-groups)

    The regular expression is now in the convert function so that it is
    only compiled once.
    """
    global olines
    try:
        pc = 0
        sthen = stleft = ""
        for line in iter(proc.stdout.readline, ""):
            # print(line)
            # canoutput = False
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
                        tleft = int((duration - tsecs) / float(xdict["speed"]))
                        stleft = UT.hms(tleft)
                        then = now + tleft
                        dtts = datetime.datetime.fromtimestamp(then)
                        sthen = dtts.strftime("%H:%M:%S")
                        # canoutput = True
            else:
                olines.append(line)
            outq.put(f"Complete: {pc}% ETA: {sthen} ({stleft})")
    except Exception as e:
        errorNotify("processProc", e)


def tidy(rc, fqfn, ofn):
    """
    tidies up after ffmpeg.
    rc = ffmpeg returncode
    """
    global olines
    global thebin
    bname = os.path.basename(fqfn)
    olog = thebin + bname + "-tvhf.log"
    if rc == 0:
        log.info("Conversion was successful")
        insize = FUT.fileSize(fqfn)
        sinsize = FUT.sizeof_fmt(insize)
        outsize = FUT.fileSize(ofn)
        soutsize = FUT.sizeof_fmt(outsize)
        log.info("Input size: {}, output size: {}".format(sinsize, soutsize))
        if outsize > insize:
            log.info("input size is smaller than output size, keeping input file")
            obname = os.path.basename(ofn)
            destfn = thebin + bname
            log.info("Deleting '{}' file (to {})".format(ofn, thebin))
            FUT.rename(ofn, destfn)
        else:
            destfn = thebin + bname
            log.info("Deleting '{}' file (to {})".format(fqfn, thebin))
            FUT.rename(fqfn, destfn)
        with open(olog, "w") as olfn:
            olfn.writelines(olines)
        log.info(f"ffmpeg output in {olog}")
        olines = []
    else:
        olog = thebin + bname + "-tvhf.log"
        with open(olog, "w") as olfn:
            olfn.writelines(olines)
        olines = []
        msg = f"Conversion of {fqfn} to {ofn} failed, output in {olog}"
        log.error(msg)
        if FUT.fileExists(ofn):
            os.remove(ofn)
        raise ConvertFailure(msg)


def convert(fqfn):
    rc = 1
    try:
        finfo = fileInfo(fqfn)
        rstr = r"frame=\s*(?P<frame>[0-9]+)\s+"
        rstr += r"fps=\s*(?P<fps>[0-9.]+)\s+.*"
        rstr += r"size=\s*(?P<size>[0-9kmgB]+)\s+"
        rstr += r"time=(?P<time>[0-9:.]+)\s+"
        rstr += r"bitrate=\s*(?P<bitrate>[0-9.]+[km]bits/s)\s+"
        rstr += r"speed=\s*(?P<speed>[0-9.]+)x"
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
                log.info("{}".format(msg))
                xmsg = ", with subtitles," if withsubs else ""
                msg = "Converting{} '{}' to '{}'".format(xmsg, fqfn, ofn)
                log.info(msg)
                dur, sdur = fileDuration(finfo)
                log.info("file duration: {}".format(sdur))
                rc = runThreadConvert(cmd, fqfn, ofn, dur, regex)
                tidy(rc, fqfn, ofn)
        else:
            msg = "Cannot convert {}".format(fqfn)
            log.info(msg)
            raise ConvertFailure(msg)
    except Exception as e:
        errorNotify("convert", e)
    return rc


def main():
    if len(sys.argv) > 1:
        rc = convert(sys.argv[1])
        sys.exit(rc)
    else:
        print("ffmpeg.py <filename>")


if __name__ == "__main__":
    main()
