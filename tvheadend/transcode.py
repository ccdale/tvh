import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

import tvheadend
from tvheadend import __version__ as verstr
import tvheadend.tvh as TVH
import tvheadend.tvhlog

log = tvheadend.tvhlog.log


class TranscodeWindow:
    pass
