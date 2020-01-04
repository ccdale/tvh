import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import tvheadend
from tvheadend import __version__ as verstr
import tvheadend.tvh as TVH
import tvheadend.tvhlog

log = tvheadend.tvhlog.log


class TranscodeWindow(Gtk.Grid):
    """ displays the list of programs to move to kodi and to be transcoded
    """

    def __init__(self, window, drama=[], documentary=[], comedy=[], music=[], films=[]):
        log.debug("Transcode Window init")
        super().__init__()
        self.win = window
        self.drama = drama
        self.documentary = documentary
        self.comedy = comedy
        self.music = music
        self.films = films
        self.store = None

    def progTree(self):
        self.store = Gtk.ListStore(str, str, str, str, str, str, str, str)
        cols = [
            "Channel",
            "Time",
            "Duration",
            "Title",
            "Sub-Title",
            "Description",
            "filename",
            "year",
        ]
        self.addListToStore(self.drama, "Drama")
        self.addListToStore(self.documentary, "Documentary")
        self.addListToStore(self.music, "Music")
        self.addListToStore(self.comedy, "Comedy")
        self.addListToStore(self.films, "Films")
        tree = Gtk.TreeView(model=self.store)
        tree.set_hexpand(True)
        tree.set_vexpand(True)
        for i, coltitle in enumerate(cols):
            if i < 5:
                rend = Gtk.CellRendererText()
                col = Gtk.TreeViewColumn(coltitle, rend, text=i)
                tree.append_column(col)
        return tree

    def addListToStore(self, xlist, listname):
        if len(xlist) > 0:
            ti = self.store.append(["", "", "", f"{listname}", "", "", "", ""])
            for prog in xlist:
                tstr, durstr = UT.progFullStartAndDur(prog["start"], prog["stop"])
                if "year" in prog:
                    subtitle = prog["year"]
                    year = prog["year"]
                elif prog["disp_subtitle"] == prog["disp_description"]:
                    subtitle = ""
                    year = ""
                else:
                    subtitle = prog["disp_subtitle"]
                    year = ""
                treeiter = self.store.append(
                    [
                        prog["channelname"],
                        tstr,
                        durstr,
                        prog["disp_title"],
                        subtitle,
                        prog["disp_description"],
                        prog["filename"],
                        year,
                    ]
                )
