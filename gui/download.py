# -*- coding: UTF-8 -*-
'''
Created on 28.4.2012

@author: marko
'''
import os

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from enigma import loadPNG, RT_HALIGN_RIGHT, RT_VALIGN_TOP, eSize, eListbox, ePoint, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont, getDesktop, ePicLoad, eServiceCenter, iServiceInformation, eServiceReference, iSeekableService, iPlayableService, iPlayableServicePtr
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.MenuList import MenuList
from Components.ScrollLabel import ScrollLabel
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.config import config
from Components.Button import Button
from Components.Label import Label, MultiColorLabel
from Tools.Directories import resolveFilename, pathExists, fileExists

from Plugins.Extensions.archivCZSK import _
from Plugins.Extensions.archivCZSK.resources.tools.items import PVideo
from Plugins.Extensions.archivCZSK.resources.tools.downloader import DownloadManager
from base import BaseArchivCZSKScreen, BaseArchivCZSKMenuListScreen
from common import PanelList

global_session = None

def setGlobalSession(session):
    global global_session
    global_session = session

def PanelListEntry(name, idx, png):
    res = [(name)]
    res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(35, 25), png=loadPNG(png)))
    res.append(MultiContentEntryText(pos=(60, 5), size=(550, 30), font=0, flags=RT_VALIGN_TOP, text=name))
    return res


def PanelListDownloadEntry(name, download):
    res = [(name)]
    res.append(MultiContentEntryText(pos=(0, 5), size=(400, 30), font=0, flags=RT_VALIGN_TOP, text=name))
    if download.downloaded and not download.running:
        res.append(MultiContentEntryText(pos=(420, 5), size=(180, 30), font=0, flags=RT_HALIGN_RIGHT, text=_('finished'), color=0x00FF00))
    elif not download.downloaded and not download.running:
        res.append(MultiContentEntryText(pos=(420, 5), size=(180, 30), font=0, flags=RT_HALIGN_RIGHT, text=_('finished with errors'), color=0xff0000))
    else:
        res.append(MultiContentEntryText(pos=(420, 5), size=(180, 30), font=0, flags=RT_HALIGN_RIGHT, text=_('downloading'))) 
    return res

class DownloadManagerMessages(object):

    @staticmethod
    def finishDownloadCB(download):
        session = global_session
        def updateDownloadList(callback=None):
            if DownloadListScreen.instance is not None:
                DownloadListScreen.instance.updateGUI()
        if download.downloaded:
            session.openWithCallback(updateDownloadList, MessageBox, _("ArchivCZSK - Download:") + ' ' + \
                                      download.name.encode('utf-8') + ' ' + _("successfully finished."), \
                                      type=MessageBox.TYPE_INFO, timeout=5)
        else:
            session.openWithCallback(updateDownloadList, MessageBox, _("ArchivCZSK - Download:") + ' ' + \
                                      download.name.encode('utf-8') + ' ' + _("finished with errors."), \
                                      type=MessageBox.TYPE_ERROR, timeout=5)  
    @staticmethod
    def startDownloadCB(download):
        session = global_session
        session.open(MessageBox, _("ArchivCZSK - Download:") + ' ' + \
                     download.name.encode('utf-8') + ' ' + _("started."), \
                     type=MessageBox.TYPE_INFO, timeout=5)
        
    @staticmethod
    def askOverrideDownloadCB(download):
        session = global_session
        def overrideDownload(callback=None):
            if callback:
                download.remove()
                DownloadManager.getInstance().addDownload(download)
            else:
                pass
        if download is not None:
            session.openWithCallback(DownloadManagerMessages.saveDownload, MessageBox, _("The file")\
                                      + download.name.encode('utf-8') + "already exist. Do you want to override?" , \
                                       type=MessageBox.TYPE_YESNO)  


class DownloadStatusScreen(Screen):
    skin = """
        <screen position="center,center" size="550,400" title="Status..." >
            <widget name="text" position="0,0" size="550,400" font="Console;14" />
        </screen>"""

    def __init__(self, session, download, title=_("Download Status")):
        Screen.__init__(self, session)

        self.download = download
        self.download.outputCB = self.outputCallback

        self["text"] = ScrollLabel("")
        self["actions"] = ActionMap(["WizardActions", "DirectionActions"],
        {
            "ok": self.cancel,
            "back": self.cancel,
            "up": self["text"].pageUp,
            "down": self["text"].pageDown
        }, -1)
        self.newtitle = title

        self.onShown.append(self.updateTitle)

        self.run = 0
        self.onLayoutFinish.append(self.startRun) # dont start before gui is finished

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def outputCallback(self, output):
        self["text"].setText(output)

    def startRun(self):
        self["text"].setText(_("Execution Progress:") + "\n\n")
        self.download.showOutput = True

    def cancel(self):
        self.download.showOutput = False
        self.close()


class DownloadList:
    def __init__(self):
        self["DownloadListActions"] = HelpableActionMap(self, "DownloadActions",
            {
                "showDownloadListView": (self.showDownloadListScreen, _("show download list")),
            })

    def showDownloadListScreen(self):
        self.session.open(DownloadListScreen)

class DownloadListScreen(BaseArchivCZSKMenuListScreen):
    instance = None       
    def __init__(self, session):
        BaseArchivCZSKMenuListScreen.__init__(self, session)
        DownloadListScreen.instance = self
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Play"))
        self["key_yellow"] = Button(_("Remove"))
        self["key_blue"] = Button("")
        
        self.lst_items = []
        self.title = _("Recent downloads")
        self.onClose.append(self.__onClose)

        self["actions"] = NumberActionMap(["archivCZSKActions"],
            {
                "ok": self.ok,
                "cancel": self.cancel,
                "red": self.askCancelDownload,
                "green": self.askPlayDownload,
                "yellow": self.askRemoveDownload,
                "up": self.up,
                "down": self.down,
            }, -2)
            
        self.onLayoutFinish.append(self.updateGUI)
        self.onShown.append(self.setWindowTitle)
        
    def __onClose(self):
        DownloadListScreen.instance = None

    def setWindowTitle(self):
        self.setTitle(self.title)
    
    def updateGUI(self):
        self.lst_items = DownloadManager.getInstance().download_lst
        self.updateMenuList()
        
    def askCancelDownload(self):
        if len(self.lst_items) > 0:
            download = self.getSelectedItem()
            self.session.openWithCallback(self.cancelDownload, MessageBox, _('Do you want to cancel') + ' '\
                                           + download.name.encode('utf-8') + ' ?', type=MessageBox.TYPE_YESNO)    
    
    def cancelDownload(self, callback=None):
        if callback:
            download = self.getSelectedItem()
            DownloadManager.getInstance().cancelDownload(download)
            self.updateGUI()
            
    def askRemoveDownload(self):
        if len(self.lst_items) > 0:
            download = self.getSelectedItem()
            self.session.openWithCallback(self.removeDownload, MessageBox, _('Do you want to remove') + ' '\
                                           + download.name.encode('utf-8') + ' ?', type=MessageBox.TYPE_YESNO)    
    
    def removeDownload(self, callback=None):
        if callback:
            download = self.getSelectedItem()
            DownloadManager.getInstance().removeDownload(download)
            self.updateGUI()
            
    def askPlayDownload(self):
        if len(self.lst_items) > 0:
            self.working = True
            download = self.getSelectedItem()
            if download.downloaded:
                self.playDownload(True)
            else:
                message = '%s %s %s' % (_("The file"), download.name.encode('utf-8'), _('is not downloaded yet. Do you want to play it anyway?'))
                self.session.openWithCallback(self.cancelDownload, MessageBox, message, type=MessageBox.TYPE_YESNO)    
    
            
    def playDownload(self, callback=None):
        if callback:
            download = self.getSelectedItem()
            from Plugins.Extensions.archivCZSK.player.player import Player
            video = Player(self.session)
            video.playDownload(download)

    def updateMenuList(self):
        del self.menu_list[:]
        list = []
        idx = 0
        for x in self.lst_items:
            list.append(PanelListDownloadEntry(x.name.encode('utf-8'), x))
            self.menu_list.append(x)
            idx += 1    
        self["menu"].setList(list)        

    def ok(self):
        if  len(self.lst_items) > 0:
            download = self.getSelectedItem()
            self.session.openWithCallback(self.workingFinished, DownloadStatusScreen, download)
        

class ArchiveDownloadsScreen(BaseArchivCZSKMenuListScreen, DownloadList):
    instance = None        
    def __init__(self, session, archive):
        BaseArchivCZSKMenuListScreen.__init__(self, session)
        DownloadList.__init__(self)
        self.archive = archive
        
        self["key_red"] = Button(_("Remove"))
        self["key_green"] = Button("")
        self["key_yellow"] = Button("")
        self["key_blue"] = Button("")
        
        self.lst_items = self.archive.get_downloads()
        self.title = self.archive.name.encode('utf-8') + ' ' + (_("downloads"))

        self["actions"] = NumberActionMap(["archivCZSKActions"],
            {
                "ok": self.ok,
                "cancel": self.cancel,
                "red": self.askRemoveDownload,
                "up": self.up,
                "down": self.down,
            }, -2)
        
        self.onShown.append(self.setWindowTitle)    
        self.onLayoutFinish.append(self.updateGUI)

    def setWindowTitle(self):
        self.setTitle(self.title)
    
    def updateGUI(self):
        self.lst_items = self.pdownloads.getDownloads()
        self.updateMenuList()
        
    def askRemoveDownload(self):
        if len(self.lst_items) > 0:
            self.working = True
            download = self.getSelectedItem()
            self.session.openWithCallback(self.removeDownload, MessageBox, _('Do you want to remove') \
                                          + ' ' + download.name.encode('utf-8') + ' ?', type=MessageBox.TYPE_YESNO)    
    
    def removeDownload(self, callback=None):
        if callback:
            it = self.getSelectedItem()
            self.pdownloads.removeDownload(it)
            self.updateGUI()

    def updateMenuList(self):
        del self.menu_list[:]
        list = []
        idx = 0
        for x in self.lst_items:
            list.append(PanelListEntry(x.name.encode('utf-8'), idx, x.thumb))
            self.menu_list.append(x)
            idx += 1    
        self["menu"].setList(list)        

    def ok(self):
        if len(self.lst_items) > 0:
            it = self.getSelectedItem()
            from Plugins.Extensions.archivCZSK.player.player import Player
            video = Player(self.session, it)
            video.play()
            
