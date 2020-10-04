#!/usr/bin/env python3

import re
import tvheadend
import tvheadend.fileutils as FUT

samplestr = """
ffmpeg version n4.2.1 Copyright (c) 2000-2019 the FFmpeg developers
  built with gcc 9.2.0 (GCC)
  configuration: --prefix=/usr --disable-debug --disable-static --disable-stripping --enable-fontconfig --enable-gmp --enable-gnutls --enable-gpl --enable-ladspa --enable-libaom --enable-libass --enable-libbluray --enable-libdav1d --enable-libdrm --enable-libfreetype --enable-libfribidi --enable-libgsm --enable-libiec61883 --enable-libjack --enable-libmodplug --enable-libmp3lame --enable-libopencore_amrnb --enable-libopencore_amrwb --enable-libopenjpeg --enable-libopus --enable-libpulse --enable-libsoxr --enable-libspeex --enable-libssh --enable-libtheora --enable-libv4l2 --enable-libvidstab --enable-libvorbis --enable-libvpx --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxcb --enable-libxml2 --enable-libxvid --enable-nvdec --enable-nvenc --enable-omx --enable-shared --enable-version3
  libavutil      56. 31.100 / 56. 31.100
  libavcodec     58. 54.100 / 58. 54.100
  libavformat    58. 29.100 / 58. 29.100
  libavdevice    58.  8.100 / 58.  8.100
  libavfilter     7. 57.100 /  7. 57.100
  libswscale      5.  5.100 /  5.  5.100
  libswresample   3.  5.100 /  3.  5.100
  libpostproc    55.  5.100 / 55.  5.100
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] SPS unavailable in decode_picture_timing
[h264 @ 0x55e9292df640] non-existing PPS 0 referenced
[h264 @ 0x55e9292df640] decode_slice_header error
[h264 @ 0x55e9292df640] no frame!
[h264 @ 0x55e9292df640] mmco: unref short failure
    Last message repeated 1 times
[mpegts @ 0x55e9292da480] start time for stream 3 is not set in estimate_timings_from_pts
[mpegts @ 0x55e9292da480] PES packet size mismatch
[mpegts @ 0x55e9292da480] Could not find codec parameters for stream 2 (Unknown: none ([17][0][0][0] / 0x0011)): unknown codec
Consider increasing the value for the 'analyzeduration' and 'probesize' options
Input #0, mpegts, from '/home/chris/Videos/kmedia/Films/D/Death on the Nile (1978)/Death on the Nile (1978).mpg':
  Duration: 02:30:00.92, start: 66851.832000, bitrate: 5638 kb/s
  Program 17472
    Metadata:
      service_name    : BBC TWO HD
      service_provider:
    Stream #0:0[0x65]: Video: h264 (High) ([27][0][0][0] / 0x001B), yuv420p(tv, bt709, progressive), 1920x1080 [SAR 1:1 DAR 16:9], 25 fps, 25 tbr, 90k tbn, 50 tbc
    Stream #0:1[0x66](eng): Audio: aac_latm (LC) ([17][0][0][0] / 0x0011), 48000 Hz, stereo, fltp
    Stream #0:2[0x6a](eng): Unknown: none ([17][0][0][0] / 0x0011) (visual impaired) (descriptions) (dependent)
    Stream #0:3[0x69](eng): Subtitle: dvb_subtitle ([6][0][0][0] / 0x0006)
Stream mapping:
  Stream #0:0 -> #0:0 (h264 (native) -> hevc (libx265))
  Stream #0:1 -> #0:1 (copy)
  Stream #0:3 -> #0:2 (copy)
Press [q] to stop, [?] for help
[h264 @ 0x55e929719380] co located POCs unavailable
[h264 @ 0x55e929425680] co located POCs unavailable
[h264 @ 0x55e929331ac0] reference picture missing during reorder
[h264 @ 0x55e929331ac0] Missing reference picture, default is 65758
[h264 @ 0x55e9294ae580] mmco: unref short failure
[h264 @ 0x55e929719380] reference picture missing during reorder
[h264 @ 0x55e929719380] Missing reference picture, default is 65766
[h264 @ 0x55e929425680] mmco: unref short failure
x265 [info]: HEVC encoder version 3.2.1
x265 [info]: build info [Linux][GCC 9.2.0][64 bit] 8bit+10bit+12bit
x265 [info]: using cpu capabilities: MMX2 SSE2Fast LZCNT SSSE3 SSE4.2 AVX FMA3 BMI2 AVX2
x265 [info]: Main profile, Level-4 (Main tier)
x265 [info]: Thread pool created using 4 threads
x265 [info]: Slices                              : 1
x265 [info]: frame threads / pool features       : 2 / wpp(34 rows)
x265 [info]: Coding QT: max CU size, min CU size : 32 / 16
x265 [info]: Residual QT: max TU size, max depth : 32 / 1 inter / 1 intra
x265 [info]: ME / range / subpel / merge         : dia / 44 / 0 / 2
x265 [info]: Keyframe min / max / scenecut / bias: 25 / 250 / 0 / 5.00
x265 [info]: Lookahead / bframes / badapt        : 5 / 3 / 0
x265 [info]: b-pyramid / weightp / weightb       : 1 / 0 / 0
x265 [info]: References / ref-limit  cu / depth  : 1 / off / off
x265 [info]: AQ: mode / str / qg-size / cu-tree  : 1 / 1.0 / 16 / 1
x265 [info]: Rate Control / qCompress            : CRF-22.0 / 0.80
x265 [info]: tools: rd=2 psy-rd=0.70 rdoq=1 psy-rdoq=5.00 early-skip rskip tmvp
x265 [info]: tools: fast-intra strong-intra-smoothing lslices=6 deblock
Output #0, matroska, to '/home/chris/Videos/kmedia/Films/D/Death on the Nile (1978)/Death on the Nile (1978).mkv':
  Metadata:
    encoder         : Lavf58.29.100
    Stream #0:0: Video: hevc (libx265), yuv420p, 1920x1080 [SAR 1:1 DAR 16:9], q=2-31, 25 fps, 1k tbn, 25 tbc
    Metadata:
      encoder         : Lavc58.54.100 libx265
    Side data:
      cpb: bitrate max/min/avg: 0/0/0 buffer size: 0 vbv_delay: -1
    Stream #0:1(eng): Audio: aac_latm (LC) ([2][22][0][0] / 0x1602), 48000 Hz, stereo, fltp
    Stream #0:2(eng): Subtitle: dvb_subtitle ([255][255][255][255] / 0xFFFFFFFF)
frame=   36 fps= 35 q=-0.0 size=       3kB time=00:00:02.76 bitrate=   9.1kbits/s speed=2.65x
frame=   54 fps= 34 q=-0.0 size=       3kB time=00:00:03.48 bitrate=   7.2kbits/s speed=2.19x
frame=   71 fps= 34 q=-0.0 size=       3kB time=00:00:04.16 bitrate=   6.0kbits/s speed=1.97x
frame=   88 fps= 34 q=-0.0 size=       3kB time=00:00:04.84 bitrate=   5.2kbits/s speed=1.85x
frame=  105 fps= 33 q=-0.0 size=       3kB time=00:00:05.52 bitrate=   4.5kbits/s speed=1.75x
frame=  123 fps= 33 q=-0.0 size=       3kB time=00:00:06.24 bitrate=   4.0kbits/s speed=1.68x
frame=  141 fps= 33 q=-0.0 size=       3kB time=00:00:06.96 bitrate=   3.6kbits/s speed=1.64x
frame=  157 fps= 33 q=-0.0 size=       3kB time=00:00:07.60 bitrate=   3.3kbits/s speed= 1.6x
frame=  172 fps= 33 q=-0.0 size=       3kB time=00:00:08.20 bitrate=   3.1kbits/s speed=1.56x
frame=  188 fps= 33 q=-0.0 size=    5157kB time=00:00:11.03 bitrate=3829.1kbits/s speed=1.92x
frame=34247 fps= 35 q=-0.0 size= 1026225kB time=00:22:52.56 bitrate=6124.9kbits/s speed= 1.4x
frame=34264 fps= 35 q=-0.0 size= 1028255kB time=00:22:52.56 bitrate=6137.0kbits/s speed= 1.4x
frame=34286 fps= 35 q=-0.0 size= 1028255kB time=00:22:52.82 bitrate=6135.9kbits/s speed= 1.4x
frame=34308 fps= 35 q=-0.0 size= 1028255kB time=00:22:53.71 bitrate=6131.9kbits/s speed= 1.4x
frame=34329 fps= 35 q=-0.0 size= 1028255kB time=00:22:56.99 bitrate=6117.3kbits/s speed= 1.4x
frame=34349 fps= 35 q=-0.0 size= 1028255kB time=00:22:56.99 bitrate=6117.3kbits/s speed= 1.4x
frame=34370 fps= 35 q=-0.0 size= 1028255kB time=00:22:56.99 bitrate=6117.3kbits/s speed= 1.4x
frame=34389 fps= 35 q=-0.0 size= 1031676kB time=00:22:58.79 bitrate=6129.6kbits/s speed= 1.4x
frame=34412 fps= 35 q=-0.0 size= 1031676kB time=00:22:58.79 bitrate=6129.6kbits/s speed= 1.4x
frame=34436 fps= 35 q=-0.0 size= 1031676kB time=00:22:58.79 bitrate=6129.6kbits/s speed= 1.4x
frame=34458 fps= 35 q=-0.0 size= 1031676kB time=00:22:59.64 bitrate=6125.9kbits/s speed= 1.4x
frame=34470 fps= 35 q=-0.0 Lsize= 1033342kB time=00:23:00.60 bitrate=6131.5kbits/s speed= 1.4x
video:1009230kB audio:21565kB subtitle:1824kB other streams:0kB global headers:2kB muxing overhead: 0.070091%
x265 [info]: frame I:    138, Avg QP:19.82  kb/s: 22456.79
x265 [info]: frame P:   8614, Avg QP:21.79  kb/s: 13701.52
x265 [info]: frame B:  25718, Avg QP:24.81  kb/s: 3326.02
x265 [info]: consecutive B-frames: 1.0% 1.3% 0.7% 97.1%

encoded 34470 frames in 984.38s (35.02 fps), 5995.44 kb/s, Avg QP:24.04
Exiting normally, received signal 2.

22 lines for regex testing
209 lines in total
"""

rstr = r"frame=\s*(?P<frame>[0-9]+)\s+"
rstr += r"fps=\s*(?P<fps>[0-9.]+)\s+.*"
rstr += r"size=\s*(?P<size>[0-9kmgB]+)\s+"
rstr += r"time=(?P<time>[0-9:.]+)\s+"
rstr += r"bitrate=\s*(?P<bitrate>[0-9.]+[km]bits/s)\s+"
rstr += r"speed=\s*(?P<speed>[0-9.]+)x"
regex = re.compile(rstr)

sample = samplestr.split("\n")
ulines = []
mlines = []
for line in sample:
    m = regex.match(line)
    if m is None:
        ulines.append(line)
    else:
        xd = m.groupdict()
        if "size" in xd:
            if xd["size"].endswith("kB"):
                tsz = xd["size"].split("k")
                sz = int(int(tsz[0]) * 1000)
                ssz = FUT.sizeof_fmt(sz)
                print(ssz)
        mlines.append(line)
print(f"lines: {len(sample)}, unmatched: {len(ulines)}, matched: {len(mlines)}")
