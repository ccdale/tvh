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
