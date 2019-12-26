#!/usr/bin/env python3

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

import os
import sys
import tvheadend
from tvheadend import __version__ as verstr
import tvheadend.tvh as TVH
import tvheadend.tvhlog
import tvheadend.config as CONF
import tvheadend.fileutils as FUT
import tvheadend.utils as UT
from tvheadend.errors import errorRaise
from tvheadend.errors import errorNotify
from tvheadend.errors import errorExit

log = tvheadend.tvhlog.log


class CurrentPrograms(Gtk.Grid):
    def __init__(self, window):
        super().__init__()
        self.win = window
        self.set_row_spacing(12)
        self.set_column_spacing(10)
        self.set_column_homogeneous(True)
        self.progData()

    def progData(self):
        total, progs = TVH.finishedRecordings()
        self.win.setTitle(f"{total} Current Recordings")
        sprogs = sorted(progs, key=lambda i: (i["start"], i["channelname"]))
        store = Gtk.ListStore(str, str, str, str, str, str, str, str)
        cols = [
            "Channel",
            "Time",
            "Duration",
            "Title",
            "Sub-Title",
            "Description",
            "filename",
            "uuid",
        ]
        for prog in sprogs:
            tstr, durstr = UT.progFullStartAndDur(prog["start"], prog["stop"])
            if prog["disp_subtitle"] == prog["disp_description"]:
                subtitle = ""
            else:
                subtitle = prog["disp_subtitle"]
            treeiter = store.append(
                [
                    prog["channelname"],
                    tstr,
                    durstr,
                    prog["disp_title"],
                    subtitle,
                    prog["disp_description"],
                    prog["filename"],
                    prog["uuid"],
                ]
            )
        tree = Gtk.TreeView(model=store)
        # when a row is selected, it emits a signal
        tree.get_selection().connect("changed", self.on_changed)
        # set the TreeView to expand both horizontally and vertically
        tree.set_hexpand(True)
        tree.set_vexpand(True)
        for i, coltitle in enumerate(cols):
            if i < 5:
                rend = Gtk.CellRendererText()
                col = Gtk.TreeViewColumn(coltitle, rend, text=i)
                tree.append_column(col)
        swin = Gtk.ScrolledWindow()
        swin.add(tree)
        # label for description
        self.label = Gtk.Label()
        self.label.set_text("")
        # self.label.set_property("Wrap", True)
        self.label.set_line_wrap(True)
        self.label.set_line_wrap_mode(Pango.WrapMode.WORD)
        self.attach(swin, 0, 0, 1, 1)
        self.attach(self.label, 0, 1, 1, 1)

    def on_changed(self, selection):
        # get the model and the iterator that points at the data in the model
        (model, iter) = selection.get_selected()
        # set the label to a new value depending on the selection
        self.label.set_text(f"{model[iter][5]}")
        return True


class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="tvhg" + verstr)
        self.set_default_size(800, 600)
        self.set_border_width(10)
        self.page = None

    def setTitle(self, title):
        self.set_title(title + " " + verstr)

    def CurrRecs(self):
        self.page = CurrentPrograms(self)
        self.add(self.page)
        self.show_all()


def main():
    try:
        log.info("tvheadend gui " + tvheadend.__version__)
        config = CONF.readConfig()
        tvheadend.user = config["user"]
        tvheadend.passw = config["pass"]
        tvheadend.ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
        win = MainWindow()
        win.connect("destroy", Gtk.main_quit)
        win.CurrRecs()
        Gtk.main()
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


if __name__ == "__main__":
    main()
