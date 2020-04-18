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


class AppMainWindow(Gtk.ApplicationWindow):
    """Filecopy application window."""

    def __init__(self, *args, **kwargs):
        log.debug("AppMainWindow __init__")
        super().__init__(*args, **kwargs)


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
