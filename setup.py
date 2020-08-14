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
setup module for tvh application
"""
# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path
from tvheadend import __version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tvh",
    version=__version__,
    description="tvheadend file management utility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ccdale/tvh",
    author="Christopher Allison",
    author_email="chris.charles.allison+tvh@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Archiving",
        "Topic :: System :: Archiving :: Backup",
        "Topic :: System :: Archiving :: Compression",
        "Topic :: System :: Archiving :: Mirroring",
        "Topic :: Utilities",
    ],
    keywords="tvheadend",
    packages=["tvheadend"],
    project_urls={
        "Source": "https://github.com/ccdale/tvh",
        "Bug Reports": "https://github.com/ccdale/tvh/issues",
    },
    python_requires=">=3",
    install_requires=["requests", "pyyaml", "PyGObject"],
    entry_points={
        "console_scripts": [
            "tvh = tvheadend.tvhcmd:tvh",
            "tvhb = tvheadend.tvhbatch:tvhbatch",
            "tvhnfo = tvheadend.tvhnfo:tvhnfo",
            "tvhd = tvheadend.tvhdelete:tvhdelete",
            "tvhl = tvheadend.tvhlist:tvhlist",
            "tvhc = tvheadend.tvhchannels:tvhc",
            "tvhf = tvheadend.ffmpeg:main",
            "tvhw = tvheadend.tvhwatch:tvhwatch",
            "tvhwl = tvheadend.tvhwlist:tvhwatchlist",
            "tvhfile = tvheadend.doTSfile:doFile",
            "tvhg = tvheadend.tvhgui:main",
            "tvhfc = tvheadend.filecopy:main",
        ]
    },
)
