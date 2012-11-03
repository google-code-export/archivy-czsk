# -*- coding: UTF-8 -*-
'''
Created on 28.4.2012

@author: marko
'''
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ScrollLabel import ScrollLabel
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.Button import Button
from Components.Label import Label

from Plugins.Extensions.archivCZSK import _
from Plugins.Extensions.archivCZSK.engine.downloader import DownloadManager

from base import  BaseArchivCZSKMenuListScreen
from common import PanelListEntryHD, PanelListDownloadEntry
PanelListEntry = PanelListEntryHD

global_session = None


def openDownloads(session, name, content_provider, cb):
    session.openWithCallback(cb, DownloadsScreen, name, content_provider)
    
def openAddonDownloads(session, addon, cb):
    openDownloads(session, addon.name, addon.provider, cb)


def setGlobalSession(session):
    global global_session
    global_session = session

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
        self.workingStarted()
        self.session.openWithCallback(self.workingFinished, DownloadListScreen)

class DownloadListScreen(BaseArchivCZSKMenuListScreen):
    instance = None       
    def __init__(self, session):
        BaseArchivCZSKMenuListScreen.__init__(self, session)
        DownloadListScreen.instance = self
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Play"))
        self["key_yellow"] = Button(_("Remove"))
        self["key_blue"] = Button("")
        
        from Plugins.Extensions.archivCZSK.engine.player.player import Player
        self.player = Player(session, self.workingFinished)
        
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
            self.workingStarted()
            download = self.getSelectedItem()
            if download.downloaded or not download.running:
                self.playDownload(True)
            else:
                message = '%s %s %s' % (_("The file"), download.name.encode('utf-8'), _('is not downloaded yet. Do you want to play it anyway?'))
                self.session.openWithCallback(self.playDownload, MessageBox, message, type=MessageBox.TYPE_YESNO)
    
            
    def playDownload(self, callback=None):
        if callback:
            download = self.getSelectedItem()
            self.player.playDownload(download)
        else:
            self.workingFinished()

    def updateMenuList(self):
        menu_list = []
        for idx, x in enumerate(self.lst_items):
            menu_list.append(PanelListDownloadEntry(x.name.encode('utf-8'), x)) 
        self["menu"].setList(menu_list)      

    def ok(self):
        if  len(self.lst_items) > 0:
            download = self.getSelectedItem()
            self.session.openWithCallback(self.workingFinished, DownloadStatusScreen, download)
        

class DownloadsScreen(BaseArchivCZSKMenuListScreen, DownloadList):
    instance = None        
    def __init__(self, session, name, content_provider):
        BaseArchivCZSKMenuListScreen.__init__(self, session)
        DownloadList.__init__(self)
        self.name = name
        self.content_provider = content_provider
        
        from Plugins.Extensions.archivCZSK.engine.player.player import Player
        self.player = Player(session, self.workingFinished)
        
        self["key_red"] = Button(_("Remove"))
        self["key_green"] = Button("")
        self["key_yellow"] = Button("")
        self["key_blue"] = Button("")
        
        self.lst_items = self.content_provider.get_downloads()
        self.title = self.name.encode('utf-8') + ' ' + (_("downloads"))

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
        self.lst_items = self.content_provider.get_downloads()
        self.updateMenuList()
        
    def askRemoveDownload(self):
        if len(self.lst_items) > 0:
            download = self.getSelectedItem()
            self.session.openWithCallback(self.removeDownload, MessageBox, _('Do you want to remove') \
                                          + ' ' + download.name.encode('utf-8') + ' ?', type=MessageBox.TYPE_YESNO)    
    
    def removeDownload(self, callback=None):
        if callback:
            self.addon.provider.remove_download(self.getSelectedItem())
            self.updateGUI()

    def updateMenuList(self):
        menu_list = []
        for idx, x in enumerate(self.lst_items):
            menu_list.append(PanelListEntry(x.name.encode('utf-8'), idx, x.thumb)) 
        self["menu"].setList(menu_list)        

    def ok(self):
        if not self.working and len(self.lst_items) > 0:
            it = self.getSelectedItem()
            download = DownloadManager.getInstance().findDownloadByIt(it)
            if download is not None and download.running:
                self.player.playDownload(download)
            else:
                self.player.setVideoItem(it)
                self.player.play()
            
