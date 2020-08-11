#!/usr/bin/env python3

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

import sys
import tvheadend
from tvheadend import __version__ as verstr
import tvheadend.tvhlog

log = tvheadend.tvhlog.log
tvheadend.tvhlog.setDebug()


class fcDialog(Gtk.Dialog):
    """Displays the file copying dialog."""

    def __init__(self, parent, src, dest):
        Gtk.Dialog.__init__(
            self,
            "Copying Files",
            parent,
            0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,),
        )

        self.set_modal(True)
        self.set_default_size(150, 100)

        msg = f"{src}\n->\n{dest}"
        label = Gtk.Label(msg)
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_fraction(0.9)

        box = self.get_content_area()
        box.add(label)
        box.add(self.progressbar)
        self.show_all()


class AppMainWindow(Gtk.ApplicationWindow):
    """Filecopy application window."""

    def __init__(self, *args, **kwargs):
        log.debug("AppMainWindow __init__")
        super().__init__(*args, **kwargs)
        src = "/home/chris/Downloads/torrents/The Expendables (2010) [1080p]/The.Expendables.2010.1080p.BrRip.x264.YIFY.mp4"
        dest = "/home/chris/Videos/kmedia/thebin/the.expendables.mp4"
        dialog = fcDialog(self, src, dest)
        dialog.set_default_response(Gtk.ResponseType.CANCEL)
        resp = dialog.run()
        dialog.destroy()


class tvhfc(Gtk.Application):
    """tvhfc application."""

    def __init__(self, *args, **kwargs):
        log.debug("tvhfc Application __init__")
        super().__init__(*args, application_id="org.cca.tvhg", **kwargs)
        self.window = None
        log.debug(f"tvhfc init: args: {args}")
        log.debug(f"tvhfc init: kwargs: {kwargs}")

    def do_startup(self):
        log.debug("tvhfc Application do_startup")
        Gtk.Application.do_startup(self)

    def do_activate(self):
        log.debug("tvhfc Application do_activate")
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = AppMainWindow(application=self, title="Main Window")
        self.window.present()


def main():
    try:
        log.info("tvheadend filecopy gui " + tvheadend.__version__)
        app = tvhfc()
        app.run(sys.argv)
    except Exception as e:
        fname = sys._getframe().f_code.co_name
        errorExit(fname, e)


if __name__ == "__main__":
    main()
