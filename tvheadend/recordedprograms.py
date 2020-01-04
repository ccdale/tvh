import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

import tvheadend
from tvheadend import __version__ as verstr
import tvheadend.tvh as TVH
import tvheadend.tvhlog
import tvheadend.categories as CATS
import tvheadend.utils as UT
from tvheadend.errors import errorRaise
from tvheadend.errors import errorNotify
from tvheadend.errors import errorExit

log = tvheadend.tvhlog.log


class YearDialog(Gtk.Dialog):
    """ displays the year request dialog box
    """

    def __init__(self, parent, title):
        Gtk.Dialog.__init__(
            self,
            "Enter Year",
            parent,
            0,
            (
                Gtk.STOCK_CANCEL,
                Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OK,
                Gtk.ResponseType.OK,
            ),
        )

        self.set_modal(True)
        self.set_default_size(150, 100)

        label = Gtk.Label(title)
        self.txt = Gtk.Entry()

        box = self.get_content_area()
        box.add(label)
        box.add(self.txt)
        self.show_all()


class CurrentPrograms(Gtk.Grid):
    """ displays the current list of programs in a grid
    """

    def __init__(self, window, currlists=None):
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
        if currlists is None:
            self.xlists = {
                "drama": [],
                "documentary": [],
                "comedy": [],
                "music": [],
                "films": [],
            }
            removeexisting = False
        else:
            self.xlists = currlists
            removeexisting = True
        # self.drama = []
        # self.documentary = []
        # self.comedy = []
        # self.music = []
        # self.years = []
        self.applybutton = None
        self.makePage(removeexisting)
        self.doTitle()
        self.xenableApply()

    def findExisting(self, prog):
        for xl in self.xlists:
            for xp in self.xlists[xl]:
                if xp["uuid"] == prog["uuid"]:
                    return True
        return False

    def progTree(self, removeexisting=True):
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
            if removeexisting and self.findExisting(prog):
                continue
            else:
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
        box = Gtk.Box(spacing=6)
        labels = [
            "_Drama",
            "D_ocumentary",
            "_Comedy",
            "_Music",
            "_Google",
            "_Year",
            "_Apply",
            "_Quit",
        ]
        for lab in labels:
            but = Gtk.Button.new_with_mnemonic(lab)
            but.connect("clicked", self.doButtonClicked)
            box.pack_start(but, True, True, 0)
            if lab == "_Apply":
                self.applybutton = but
                self.applybutton.set_sensitive(False)
        # but = Gtk.Button.new_with_mnemonic("_Drama")
        # but.connect("clicked", self.dramaClicked)
        # box.pack_start(but, True, True, 0)
        # but = Gtk.Button.new_with_mnemonic("D_ocumentary")
        # but.connect("clicked", self.documentaryClicked)
        # box.pack_start(but, True, True, 0)
        # but = Gtk.Button.new_with_mnemonic("_Comedy")
        # but.connect("clicked", self.comedyClicked)
        # box.pack_start(but, True, True, 0)
        # but = Gtk.Button.new_with_mnemonic("_Music")
        # but.connect("clicked", self.musicClicked)
        # box.pack_start(but, True, True, 0)
        # but = Gtk.Button.new_with_mnemonic("_Google")
        # but.connect("clicked", self.googleClicked)
        # box.pack_start(but, True, True, 0)
        # but = Gtk.Button.new_with_mnemonic("_Year")
        # but.connect("clicked", self.yearClicked)
        # box.pack_start(but, True, True, 0)
        # self.applybutton = Gtk.Button.new_with_mnemonic("_Apply")
        # self.applybutton.connect("clicked", self.applyClicked)
        # self.applybutton.set_sensitive(False)
        # box.pack_start(self.applybutton, True, True, 0)
        # but = Gtk.Button.new_with_mnemonic("_Quit")
        # but.connect("clicked", self.quitClicked)
        # box.pack_start(but, True, True, 0)
        return box

    def makePage(self, removeexisting=True):
        log.debug("CurrentRecordings makePage")
        self.progData(removeexisting)

    def progData(self, removeexisting=True):
        log.debug("progData")
        total, self.progs = TVH.finishedRecordings()
        self.win.set_title(f"{total} Current Recordings")
        tree = self.progTree(removeexisting)
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

    def xenableApply(self):
        xenable = False
        for lab in self.xlists:
            if len(self.xlists[lab]) > 0:
                xenable = True
                break
        self.applybutton.set_sensitive(xenable)

    def addTo(self, xlist, prog):
        if self.model is not None and self.iter is not None and self.cuuid is not None:
            xlist.append(prog)
            self.removeProgFromDisplay(prog)

    def doButtonClicked(self, button):
        blab = button.get_label()
        tmp = blab.split("_")
        tblab = "".join(tmp).lower()
        log.debug(f"{tblab} clicked")
        if tblab == "quit":
            self.win.doQuit()
        else:
            cprog = self.findCurrentProg()
            if cprog is not None:
                if tblab in self.xlists:
                    self.addTo(self.xlists[tblab], cprog)
                    log.debug(f"{tblab}: {len(self.xlists[tblab])}")
                    self.xenableApply()
                elif tblab == "google":
                    title = cprog["disp_title"]
                    log.debug(f"finding {title}")
                    CATS.movieSearch(title)
                    self.doYearDialog(cprog)
                elif tblab == "year":
                    self.doYearDialog(cprog)
                elif tblab == "apply":
                    self.win.destroyPage()
                    self.win.doTranscodeWindow(self.xlists)
            else:
                log.error(f"{tblab} Button clicked but cprog is none")

    # def dramaClicked(self, button):
    #     log.debug("drama clicked")
    #     cprog = self.findCurrentProg()
    #     self.addTo(self.drama, cprog)
    #     log.debug(f"{len(self.drama)}")
    #     self.enableApply()

    # def documentaryClicked(self, button):
    #     log.debug("documentary clicked")
    #     cprog = self.findCurrentProg()
    #     self.addTo(self.documentary, cprog)
    #     log.debug(f"{len(self.documentary)}")
    #     self.enableApply()

    # def comedyClicked(self, button):
    #     log.debug("comedy clicked")
    #     cprog = self.findCurrentProg()
    #     self.addTo(self.comedy, cprog)
    #     log.debug(f"{len(self.comedy)}")
    #     self.enableApply()

    # def musicClicked(self, button):
    #     log.debug("music clicked")
    #     cprog = self.findCurrentProg()
    #     self.addTo(self.music, cprog)
    #     log.debug(f"{len(self.music)}")
    #     self.enableApply()

    def doYearDialog(self, prog):
        title = prog["disp_title"]
        dialog = YearDialog(self.win, title)
        resp = dialog.run()
        if resp == Gtk.ResponseType.OK:
            year = dialog.txt.get_text().strip()
            log.debug(f"{title}: {year}")
            prog["year"] = year
            self.addTo(self.xlists["films"], prog)
            label = "films"
            log.debug(f"films: {len(self.xlists[label])}")
            self.xenableApply()
        dialog.destroy()

    # def googleClicked(self, button):
    #     log.debug("google clicked")
    #     cprog = self.findCurrentProg()
    #     if cprog is not None:
    #         title = cprog["disp_title"]
    #         log.debug(f"finding {title}")
    #         CATS.movieSearch(title)
    #         self.doYearDialog(cprog)

    # def yearClicked(self, button):
    #     log.debug("year clicked")
    #     cprog = self.findCurrentProg()
    #     if cprog is not None:
    #         self.doYearDialog(cprog)

    # def applyClicked(self, button):
    #     log.debug("apply clicked")
    #     self.win.destroyPage()
    #     kwargs = {
    #         "drama": self.drama,
    #         "documentary": self.documentary,
    #         "music": self.music,
    #         "comedy": self.comedy,
    #         "films": self.years,
    #     }
    #     self.win.doTranscodeWindow(**kwargs)

    # def quitClicked(self, button):
    #     log.debug("quit clicked")
    #     self.win.doQuit()

    def findCurrentProg(self):
        cprog = None
        if self.cuuid is not None:
            for prog in self.progs:
                if prog["uuid"] == self.cuuid:
                    cprog = prog
                    break
        return cprog

    def removeProgFromDisplay(self, cprog):
        self.removeFromTree()
        self.removeCurrentProg(cprog)
        self.doTitle()

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

    def doTitle(self):
        cn = len(self.progs)
        scn = 0
        for xl in self.xlists:
            scn += len(self.xlists[xl])
        smsg = f" ({scn}) " if scn > 0 else ""
        msg = f"{cn}{smsg} Current Recordings"
        self.win.set_title(msg)
