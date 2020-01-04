import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import tvheadend
from tvheadend import __version__ as verstr
import tvheadend.tvh as TVH
import tvheadend.utils as UT
import tvheadend.fileutils as FUT
import tvheadend.nfo as NFO
import tvheadend.tvhlog
import tvheadend.tvhdb
import time
import shutil

log = tvheadend.tvhlog.log


class CopyFailure(Exception):
    pass


class TranscodeWindow(Gtk.Grid):
    """ displays the list of programs to move to kodi and to be transcoded
    """

    def __init__(self, window, xlists):
        log.debug("Transcode Window init")
        super().__init__()
        self.win = window
        self.xlists = xlists
        self.store = None
        self.progressbar = None
        self.makePage()

    def makePage(self):
        log.debug("TranscodeWindow makePage")
        tree = self.progTree()
        swin = Gtk.ScrolledWindow()
        swin.add(tree)
        self.progressbar = Gtk.ProgressBar()
        bbox = self.transButtons()
        self.attach(swin, 0, 0, 1, 1)
        self.attach(self.progressbar, 0, 1, 1, 1)
        self.attach(bbox, 0, 2, 1, 1)

    def transButtons(self):
        box = Gtk.Box(spacing=6)
        but = Gtk.Button.new_with_mnemonic("_Current Recordings")
        but.connect("clicked", self.doButtonClicked)
        box.pack_start(but, True, True, 0)
        but = Gtk.Button.new_with_mnemonic("_Run")
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
                    if "opbase" not in prog:
                        UT.addBaseFn(prog)
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
        tmp = blab.split("_")
        tblab = "".join(tmp).lower()
        log.debug(f"{tblab} clicked")
        if tblab == "current recordings":
            self.win.destroyPage()
            self.win.doCurrentRecordings(existinglists=self.xlists)
        elif tblab == "run":
            log.debug("running transcode")
            self.runTranscode()
        else:
            log.info(f"Unhandled button {tblab} clicked")

    def moveShow(self, show):
        try:
            then = time.time()
            tvhstat = os.stat(show["filename"])
            log.info("{}: {}".format(show["opbase"], FUT.sizeof_fmt(tvhstat.st_size)))
            if "year" in show:
                if show["title"].startswith("The "):
                    letter = show["title"][4:5].upper()
                else:
                    letter = show["title"][0:1].upper()
                opdir = "/".join([tvheadend.filmhome, letter, show["opbase"]])
                snfo = NFO.makeFilmNfo(show)
            else:
                opdir = "/".join([tvheadend.videohome, show["category"], show["title"]])
                snfo = NFO.makeProgNfo(show)
            basefn = "/".join([opdir, show["opbase"]])
            opfn = basefn + ".mpg"
            mkopfn = basefn + ".mkv"
            existingfile = None
            if FUT.fileExists(opfn):
                existingfile = opfn
            elif FUT.fileExists(mkopfn):
                existingfile = mkopfn
            if existingfile is not None:
                log.info(
                    "kodi file already exists, not copying {}".format(existingfile)
                )
                log.info("deleting from tvheadend")
                TVH.deleteRecording(show["uuid"])
            else:
                log.info("making directory {}".format(opdir))
                FUT.makePath(opdir)
                nfofn = basefn + ".nfo"
                log.info("writing nfo to {}".format(nfofn))
                with open(nfofn, "w") as nfn:
                    nfn.write(snfo)
                log.info("copying {} to {}".format(show["filename"], opfn))
                shutil.copy2(show["filename"], opfn)
                if FUT.fileExists(opfn):
                    cstat = os.stat(opfn)
                    if cstat.st_size == tvhstat.st_size:
                        log.info(
                            "copying {} took: {}".format(
                                FUT.sizeof_fmt(cstat.st_size),
                                NFO.hmsDisplay(int(time.time() - then)),
                            )
                        )
                        log.info("show copied to {} OK.".format(opfn))
                        fhash, fsize = FUT.getFileHash(show["filename"])
                        log.info("deleting from tvheadend")
                        TVH.deleteRecording(show["uuid"])
                        log.info("updating DB")
                        db = tvheadend.tvhdb.TVHDb(dbfn)
                        sql = "insert into files (name,size,hash) values (?, ?, ?)"
                        return db.doInsertSql(sql, (opfn, fsize, fhash,))
                else:
                    raise (
                        CopyFailure(
                            "Failed to copy {} to {}".format(show["filename"], opfn)
                        )
                    )
            return False
        except Exception as e:
            fname = sys._getframe().f_code.co_name
            errorExit(fname, e)

    def countLists(self):
        cn = 0
        for xl in self.xlists:
            for prog in self.xlists:
                cn += 1
        return cn

    def runTranscode(self):
        todo = self.countLists()
        progress = 0
        for xl in self.xlists:
            for prog in self.xlists[xl]:
                if self.moveShow(prog):
                    progress += 1
                    pc = progress / todo
                    self.progressbar.set_fraction(pc)
        self.win.destroyPage()
        self.win.doCurrentRecordings()
