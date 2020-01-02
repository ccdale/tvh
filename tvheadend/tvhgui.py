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
import tvheadend.categories as CATS
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
        self.model = None
        self.iter = None
        self.drama = []
        self.documentary = []
        self.comedy = []
        self.music = []
        self.years = []
        self.applybutton = None
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
        but = Gtk.Button.new_with_mnemonic("_Comedy")
        but.connect("clicked", self.comedyClicked)
        box.pack_start(but, True, True, 0)
        but = Gtk.Button.new_with_mnemonic("_Music")
        but.connect("clicked", self.musicClicked)
        box.pack_start(but, True, True, 0)
        but = Gtk.Button.new_with_mnemonic("_Google")
        but.connect("clicked", self.googleClicked)
        box.pack_start(but, True, True, 0)
        but = Gtk.Button.new_with_mnemonic("_Year")
        but.connect("clicked", self.yearClicked)
        box.pack_start(but, True, True, 0)
        self.applybutton = Gtk.Button.new_with_mnemonic("_Apply")
        self.applybutton.connect("clicked", self.applyClicked)
        self.applybutton.set_sensitive(False)
        box.pack_start(self.applybutton, True, True, 0)
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
        self.label.set_line_wrap(True)
        self.label.set_line_wrap_mode(Pango.WrapMode.WORD)
        self.attach(swin, 0, 0, 1, 1)
        self.attach(self.label, 0, 1, 1, 1)
        bbox = self.progButtons()
        self.attach(bbox, 0, 2, 1, 1)

    def on_changed(self, selection):
        log.debug("CurrentPrograms on_change")
        # get the model and the iterator that points at the data in the model
        (self.model, self.iter) = selection.get_selected()
        # set the label to a new value depending on the selection
        desc = 5
        filename = 6
        uuid = 7
        self.cuuid = f"{self.model[self.iter][uuid]}"
        self.label.set_text(f"{self.model[self.iter][desc]}")
        # self.label.set_text(f"{model[iter][desc]}\n{self.cuuid}")
        # self.label.set_text(f"{model[iter][desc]}\n{model[iter][filename]}")
        return True

    def enableApply(self):
        if (
            len(self.drama)
            or len(self.documentary)
            or len(self.comedy)
            or len(self.music)
            or len(self.years)
        ):
            self.applybutton.set_sensitive(True)
        else:
            self.applybutton.set_sensitive(False)

    def addTo(self, xlist, prog):
        if self.model is not None and self.iter is not None and self.cuuid is not None:
            self.removeFromTree()
            self.removeCurrentProg(prog)
            xlist.append(prog)

    def dramaClicked(self, button):
        log.debug("drama clicked")
        cprog = self.findCurrentProg()
        self.addTo(self.drama, cprog)
        self.enableApply()

    def documentaryClicked(self, button):
        log.debug("documentary clicked")
        cprog = self.findCurrentProg()
        self.addTo(self.documentary, cprog)
        self.enableApply()

    def comedyClicked(self, button):
        log.debug("comedy clicked")
        cprog = self.findCurrentProg()
        self.addTo(self.comedy, cprog)
        self.enableApply()

    def musicClicked(self, button):
        log.debug("music clicked")
        cprog = self.findCurrentProg()
        self.addTo(self.music, cprog)
        self.enableApply()

    def googleClicked(self, button):
        log.debug("google clicked")
        cprog = self.findCurrentProg()
        title = cprog["disp_title"]
        if cprog is not None:
            log.debug(f"finding {title}")
            CATS.movieSearch(title)

    def yearClicked(self, button):
        log.debug("year clicked")
        self.enableApply()

    def applyClicked(self, button):
        log.debug("apply clicked")

    def quitClicked(self, button):
        log.debug("quit clicked")
        self.win.doQuit()

    def findCurrentProg(self):
        cprog = None
        if self.cuuid is not None:
            for prog in self.progs:
                if prog["uuid"] == self.cuuid:
                    cprog = prog
                    break
        return cprog

    def removeFromTree(self):
        self.model.remove(self.iter)

    def removeCurrentProg(self, cprog):
        log.debug(f"attempting to remove {self.cuuid}")
        ret = False
        icn = len(self.progs)
        if cprog is not None:
            self.progs.remove(cprog)
            ocn = len(self.progs)
            if ocn == (icn - 1):
                log.debug("programme removed ok")
                ret = True
            else:
                log.debug("failed to remove programmed")
        return ret


class AppMainWindow(Gtk.ApplicationWindow):
    """ tvhg application main window
    """

    def __init__(self, *args, **kwargs):
        log.debug("AppMainWindow __init__")
        super().__init__(*args, **kwargs)
        self.application = kwargs["application"]
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

    def do_activate(self):
        log.debug("tvhg Application do_activate")
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = AppMainWindow(application=self, title="Main Window")

        self.window.present()
        log.debug(f"{self.window.grid.progs[0]}")


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
