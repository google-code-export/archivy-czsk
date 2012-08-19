# -*- coding: UTF-8 -*-
'''
Created on 28.2.2012

@author: marko
'''

from Plugins.Extensions.archivCZSK import _
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Components.Button import Button
from Components.Label import Label
from Components.MenuList import MenuList
from Components.ScrollLabel import ScrollLabel
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.config import config
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, pathExists, fileExists

from enigma import loadPNG, RT_HALIGN_RIGHT, RT_VALIGN_TOP, eSize, eListbox, ePoint, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont, getDesktop, ePicLoad, eServiceCenter, iServiceInformation, eServiceReference, iSeekableService, iPlayableService, iPlayableServicePtr
import os, urllib2
from menu import ArchiveCZSKConfigScreen, ArchiveConfigScreen
from content import ContentScreen
from common import *
from download import DownloadList, DownloadListView
from Plugins.Extensions.archivCZSK.resources.exceptions.archiveException import *
from Plugins.Extensions.archivCZSK.resources.tools.util import PItem, PArchive

pluginPath = "/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/"


class ArchiveScreen(Screen, DownloadList):
    skin = """
            <screen position="center,center" size="720,576" title="Main Menu" >
                <widget name="key_red" position="8,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="186,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="364,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="542,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="menu" position="0,55" size="330,485" transparent="1" scrollbarMode="showOnDemand" />
                <widget name="image" position="407,90" zPosition="2" size="256,256" alphatest="on" />
                <widget name="title" position="350,55" size="370,25" halign="left" font="Regular;22" transparent="1" foregroundColor="yellow" />
                <widget name="author" position="350,355" size="370,25" halign="left" font="Regular;20" transparent="1" foregroundColor="yellow" />
                <widget name="version" position="350,390" size="370,25" halign="left" font="Regular;20" transparent="1" foregroundColor="yellow" />
                <widget name="about" position="350,425" size="370,100" halign="left" font="Regular;20" transparent="1" foregroundColor="white" />
                <ePixmap position="0,545" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon/key_info.png"  zPosition="3" transparent="1" alphatest="on" />
                <widget name="menu_text" position="45,545" size="370,25" halign="left" font="Regular;20" transparent="1" foregroundColor="white" />
            </screen>"""

    def __init__(self, session, tv_archives, video_archives, archive_dict):
        Screen.__init__(self, session)
        DownloadList.__init__(self)
        self.list = []
        self.menu = []
        self.working = True
        self.video_archives = video_archives
        self.tv_archives = tv_archives
        self.archive_dict = archive_dict

        self["image"] = Pixmap()
        self["title"] = Label("")
        self["author"] = Label("")
        self["version"] = Label("")
        self["about"] = Label("")
        self["menu"] = PanelList([])
        self["menu_text"] = Label(_("Show recent downloads"))
        self["key_red"] = Button(_("TV archives"))
        self["key_green"] = Button(_("Video archives"))
        self["key_yellow"] = Button(_("Live streams"))
        self["key_blue"] = Button(_("Settings"))
        self["actions"] = NumberActionMap(["archivCZSKActions"],
            {
                "ok": self.okClicked,
                "cancel": self.closePlugin,
                "blue": self.openSettings,
                "red": self.listTVArch,
                "green": self.listVideoArch,
                "yellow": self.listStreams,
                "up": self.up,
                "down": self.down,
                "info": self.activeDownloads
            }, -2)
        self.onShown.append(self.setWindowTitle)
        self.onLayoutFinish.append(self.updateMenuList)

    def activeDownloads(self):
        self.session.openWithCallback(self.workingFinished, DownloadListView)

    def setWindowTitle(self):
        self.setTitle(_("Archiv CZSK"))

    def listTVArch(self):
        self.updateMenuList(self.tv_archives)

    def listVideoArch(self):
        self.updateMenuList(self.video_archives)

    def listStreams(self):
        stream = self.archive_dict['streamy']
        stream.modul.loadList()
        def open(params):
            it = params['it']
            return stream.modul.getContent(it, None)
        stream.open = open
        params = {}
        (params['lst_items'], command), params['date'] = stream.modul.getContent(None, None)
        self.session.openWithCallback(self.workingFinished2, ContentScreen, stream, params) 

    def openSettings(self):
        self.working = True
        self.session.openWithCallback(self.workingFinished, ArchiveCZSKConfigScreen)

    def updateGUI(self):
        idx = self["menu"].getSelectedIndex()
        sel = self.menu_main[idx]

        if self.archive_dict.has_key(sel.id):
            archive = self.archive_dict[sel.id]
            self["image"].instance.setPixmap(archive.image)
            self["title"].setText(archive.name.encode('utf-8'))
            self["author"].setText(_("Author: ") + archive.author.encode('utf-8'))
            self["version"].setText(_("Version: ") + archive.version.encode('utf-8'))
            self["about"].setText(archive.about.encode('utf-8'))
        else:
            self["image"].instance.setPixmap(None)
            self["title"].setText("")
            self["author"].setText("")
            self["version"].setText("")
            self["about"].setText("")

    def updateMenuList(self, lst=None):
        if not lst:
            lst = self.tv_archives
        self.working = True
        self.menu_main = []
        for x in self.menu_main:
            del self.menu_main[0]
        list = []
        idx = 0
        for x in lst:
            list.append(PanelListEntry(x.id.encode('utf-8'), idx))
            self.menu_main.append(x)
            idx += 1
        self["menu"].setList(list)
        self.updateGUI()
        self.working = False

    def workingFinished2(self, xmlBackup=None, xml_scBackup=None):
        """Called when exiting archive, writes automatic xml (xmlBackup) if its allowed and xml shortcuts (xml_scBackup)"""
        if xmlBackup is not None:
            xmlBackup.writeArchiveFile()
        if xml_scBackup is not None:
            xml_scBackup.writeArchiveFile()
        self.working = False

    def workingFinished(self, callback=None):
        self.working = False

    def keyNumberGlobal(self, idx):
        if (self.working) == False and (idx < len(self.menu_main)):
            self.working = True
            sel = self.menu_main[idx]
            params = {}
            if self.archive_dict.has_key(sel.id):
                    archive = self.archive_dict[sel.id]
                    try:
                        (params['lst_items'], command), params['date'] = archive.open(params)

                    except CustomInfoError as er:
                        self.showInfo(er.value)

                    except CustomError as er:
                        self.showError(er.value)

                    except urllib2.HTTPError:
                        self.showError(_("In this moment, archive is not available, try later"))    

                    except urllib2.URLError:    
                        self.showError(_("In this moment, archive is not available, try later"))

                    else:
                        #archive.reloadXMLSetting()
                        self.session.openWithCallback(self.workingFinished2, ContentScreen, archive, params)                        

    def okClicked(self):
        self.keyNumberGlobal(self["menu"].getSelectedIndex())

    def up(self):
        if not self.working:
            self.working = True
            self["menu"].up()
            self.updateGUI()
            self.working = False

    def down(self):
        if not self.working:
            self.working = True
            self["menu"].down()
            self.updateGUI()
            self.working = False

    def freeMemory(self):
        os.system("echo 1 > /proc/sys/vm/drop_caches")

    def closePlugin(self):
        self.session.openWithCallback(self.exit, MessageBox, _('Do you want to exit ArchivCZSK?'), type=MessageBox.TYPE_YESNO)

    def exit(self, callback=None):
        if callback:
            if config.plugins.archivCZSK.clearMemory.value:
                self.freeMemory()
            self.close()

    def showError(self, error):
        self.session.openWithCallback(self.workingFinished, MessageBox, _(error), type=MessageBox.TYPE_ERROR, timeout=5)

    def showInfo(self, info):
        self.session.openWithCallback(self.workingFinished, MessageBox, _(info), type=MessageBox.TYPE_INFO, timeout=5)

