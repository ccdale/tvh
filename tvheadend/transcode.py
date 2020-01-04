import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import tvheadend
from tvheadend import __version__ as verstr
import tvheadend.tvh as TVH
import tvheadend.utils as UT
import tvheadend.tvhlog

log = tvheadend.tvhlog.log


class TranscodeWindow(Gtk.Grid):
    """ displays the list of programs to move to kodi and to be transcoded
    """

    def __init__(self, window, xlists):
        log.debug("Transcode Window init")
        super().__init__()
        self.win = window
        self.xlists = xlists
        self.store = None
        self.makePage()

    def makePage(self):
        log.debug("TranscodeWindow makePage")
        tree = self.progTree()
        swin = Gtk.ScrolledWindow()
        swin.add(tree)
        bbox = self.transButtons()
        self.attach(swin, 0, 0, 1, 1)
        self.attach(bbox, 0, 1, 1, 1)

    def transButtons(self):
        box = Gtk.Box(spacing=6)
        but = Gtk.Button.new_with_mnemonic("Current Recordings")
        but.connect("clicked", self.doButtonClicked)
        box.pack_start(but, True, True, 0)
        return box

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
        self.addListsToStore()
        tree = Gtk.TreeView(model=self.store)
        tree.set_hexpand(True)
        tree.set_vexpand(True)
        for i, coltitle in enumerate(cols):
            if i < 5:
                rend = Gtk.CellRendererText()
                col = Gtk.TreeViewColumn(coltitle, rend, text=i)
                tree.append_column(col)
        return tree

    def addListsToStore(self):
        for xl in self.xlists:
            if len(self.xlists[xl]) > 0:
                tlab = xl[0].upper() + xl[1:]
                ti = self.store.append(["", "", "", f"{tlab}", "", "", "", ""])
                for prog in self.xlists[xl]:
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

    def doButtonClicked(self, button):
        blab = button.get_label()
        log.debug(f"doButtonClicked: button: {blab}")
