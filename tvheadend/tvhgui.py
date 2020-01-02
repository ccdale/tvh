#!/usr/bin/env python3

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk, Pango

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
tvheadend.tvhlog.setDebug()

dir_path = os.path.dirname(os.path.realpath(__file__))
menufn = "/".join([dir_path, "menu.xml"])


class CurrentPrograms(Gtk.Grid):
    """ displays the current list of programs in a grid
    """

    def __init__(self, window):
        log.debug("CurrentPrograms __init__")
        super().__init__()
        self.win = window
        self.set_row_spacing(12)
        self.set_column_spacing(10)
        self.set_column_homogeneous(True)
        self.progs = None
        self.cuuid = None
        self.progData()

    def progTree(self):
        sprogs = sorted(self.progs, key=lambda i: (i["start"], i["channelname"]))
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
        return tree

    def progButtons(self):
        labels = ["_Drama", "D_ocumentary", "_Music", "_Google", "_Quit"]
        box = Gtk.Box()
        but = Gtk.Button.new_with_mnemonic("_Drama")
        but.connect("clicked", self.dramaClicked)
        box.pack_start(but, True, True, 0)
        but = Gtk.Button.new_with_mnemonic("D_ocumentary")
        but.connect("clicked", self.documentaryClicked)
        box.pack_start(but, True, True, 0)
        but = Gtk.Button.new_with_mnemonic("_Music")
        but.connect("clicked", self.musicClicked)
        box.pack_start(but, True, True, 0)
        but = Gtk.Button.new_with_mnemonic("_Google")
        but.connect("clicked", self.googleClicked)
        box.pack_start(but, True, True, 0)
        but = Gtk.Button.new_with_mnemonic("_Quit")
        but.connect("clicked", self.quitClicked)
        box.pack_start(but, True, True, 0)
        return box

    def progData(self):
        log.debug("progData")
        global menufn
        total, self.progs = TVH.finishedRecordings()
        self.win.set_title(f"{total} Current Recordings")
        tree = self.progTree()
        swin = Gtk.ScrolledWindow()
        swin.add(tree)
        # label for description
        self.label = Gtk.Label()
        self.label.set_text("")
        # self.label.set_property("Wrap", True)
        self.label.set_line_wrap(True)
        self.label.set_line_wrap_mode(Pango.WrapMode.WORD)
        self.attach(swin, 0, 0, 1, 1)
        # swin.show()
        self.attach(self.label, 0, 1, 1, 1)
        # self.label.show()
        # builder = Gtk.Builder.new_from_file(menufn)
        # menu = builder.get_object("app-menu")
        # button = Gtk.MenuButton.new()
        # popover = Gtk.Popover.new_from_model(button, menu)
        # button.set_popover(popover)
        # self.attach(button, 0, 2, 1, 1)
        # button.show()
        # self.show_all()
        bbox = self.progButtons()
        self.attach(bbox, 0, 2, 1, 1)

    def on_changed(self, selection):
        log.debug("CurrentPrograms on_change")
        # get the model and the iterator that points at the data in the model
        (model, iter) = selection.get_selected()
        # set the label to a new value depending on the selection
        desc = 5
        filename = 6
        uuid = 7
        self.cuuid = f"{model[iter][uuid]}"
        self.label.set_text(f"{model[iter][desc]}\n{self.cuuid}")
        # self.label.set_text(f"{model[iter][desc]}\n{model[iter][filename]}")
        return True

    def dramaClicked(self, button):
        log.debug("drama clicked")

    def documentaryClicked(self, button):
        log.debug("documentary clicked")

    def musicClicked(self, button):
        log.debug("music clicked")

    def googleClicked(self, button):
        log.debug("google clicked")

    def quitClicked(self, button):
        log.debug("quit clicked")
        self.win.doQuit()


class AppMainWindow(Gtk.ApplicationWindow):
    """ tvhg application main window
    """

    def __init__(self, *args, **kwargs):
        log.debug("AppMainWindow __init__")
        super().__init__(*args, **kwargs)
        self.set_default_size(1024, 800)
        self.set_border_width(10)
        log.debug("getting grid")
        self.grid = CurrentPrograms(self)
        log.debug("adding grid to window")
        self.add(self.grid)
        log.debug("showing grid")
        self.grid.show_all()

    def doQuit(self):
        log.debug("AppMainWindow.doQuit()")
        self.application.quit()


class tvhg(Gtk.Application):
    """ tvhg application
    """

    def __init__(self, *args, **kwargs):
        log.debug("tvhg Application __init__")
        super().__init__(*args, application_id="org.cca.tvhg", **kwargs)
        self.window = None

    def do_startup(self):
        log.debug("tvhg Application do_startup")
        Gtk.Application.do_startup(self)
        action = Gio.SimpleAction.new("tvhgdrama", None)
        action.connect("activate", self.on_tvhgdrama)
        self.add_action(action)
        action = Gio.SimpleAction.new("tvhgdocumentary", None)
        action.connect("activate", self.on_tvhgdocumentary)
        self.add_action(action)
        action = Gio.SimpleAction.new("tvhgmusic", None)
        action.connect("activate", self.on_tvhgmusic)
        self.add_action(action)
        self.applyaction = Gio.SimpleAction.new("tvhgapply", None)
        self.applyaction.connect("activate", self.on_tvhgapply)
        self.applyaction.set_enabled(False)
        self.add_action(self.applyaction)
        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        action.set_enabled(True)
        self.add_action(action)

    def do_activate(self):
        log.debug("tvhg Application do_activate")
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = AppMainWindow(application=self, title="Main Window")

        self.window.present()
        log.debug(f"{self.window.grid.progs[0]}")

    def on_quit(self, action, param):
        log.debug("tvhg Application on_quit")
        self.quit()

    def on_tvhgdrama(self, action, param):
        log.debug("tvhg Application on_tvhgdrama")
        self.applyaction.set_enabled(True)

    def on_tvhgdocumentary(self, action, param):
        log.debug("tvhg Application on_tvhgdocumentary")
        self.applyaction.set_enabled(True)

    def on_tvhgmusic(self, action, param):
        log.debug("tvhg Application on_tvhgmusic")
        self.applyaction.set_enabled(True)

    def on_tvhgapply(self, action, param):
        log.debug("tvhg Application on_tvhgapply")


def main():
    try:
        log.info("tvheadend gui " + tvheadend.__version__)
        config = CONF.readConfig()
        tvheadend.user = config["user"]
        tvheadend.passw = config["pass"]
        tvheadend.ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
        app = tvhg()
        app.run(sys.argv)
        # win = MainWindow()
        # win.connect("destroy", Gtk.main_quit)
        # win.CurrRecs()
        # Gtk.main()
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


if __name__ == "__main__":
    main()
