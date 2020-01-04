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
import tvheadend.categories as CATS
import tvheadend.fileutils as FUT
import tvheadend.utils as UT
from tvheadend.recordedprograms import CurrentPrograms
from tvheadend.transcode import TranscodeWindow
from tvheadend.errors import errorRaise
from tvheadend.errors import errorNotify
from tvheadend.errors import errorExit

log = tvheadend.tvhlog.log
tvheadend.tvhlog.setDebug()

dir_path = os.path.dirname(os.path.realpath(__file__))
menufn = "/".join([dir_path, "menu.xml"])


class AppMainWindow(Gtk.ApplicationWindow):
    """ tvhg application main window
    """

    def __init__(self, *args, **kwargs):
        log.debug("AppMainWindow __init__")
        super().__init__(*args, **kwargs)
        self.application = kwargs["application"]
        self.set_default_size(1024, 800)
        self.set_border_width(10)
        self.page = None
        self.doCurrentRecordings()

    def destroyPage(self):
        self.page.destroy()
        self.page = None

    def doCurrentRecordings(self, existinglists=None):
        if self.page is None:
            log.debug("getting current recordings page")
            self.page = CurrentPrograms(self, currlists=existinglists)
            log.debug("adding current recordings page to window")
            self.add(self.page)
            log.debug("showing current recordings page")
            self.page.show_all()
        else:
            log.error("Showing current recordings page failed as self.page is not none")

    def doTranscodeWindow(self, xlists):
        if self.page is None:
            log.debug("Getting transcode window page")
            self.page = TranscodeWindow(self, xlists)
            log.debug("adding transcode window page to window")
            self.add(self.page)
            log.debug("showing transcode window page")
            self.page.show_all()
        else:
            log.error("Showing transcode window page failed as self.page is not none")

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
        # log.debug(f"{self.window.grid.progs[0]}")


def main():
    try:
        log.info("tvheadend gui " + tvheadend.__version__)
        config = CONF.readConfig()
        tvheadend.user = config["user"]
        tvheadend.passw = config["pass"]
        tvheadend.ipaddr = str(config["tvhipaddr"]) + ":" + str(config["tvhport"])
        tvheadend.videohome = config["videohome"]
        tvheadend.filmhome = config["filmhome"]
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
