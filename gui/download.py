# -*- coding: UTF-8 -*-
'''
Created on 28.4.2012

@author: marko
'''
import os
from Plugins.Extensions.archivCZSK import _
from Screens.Screen import Screen
from Components.Button import Button
from Components.Label import Label, MultiColorLabel
from Screens.MessageBox import MessageBox
from enigma import loadPNG, RT_HALIGN_RIGHT, RT_VALIGN_TOP, eSize, eListbox, ePoint, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont, getDesktop, ePicLoad, eServiceCenter, iServiceInformation, eServiceReference, iSeekableService, iPlayableService, iPlayableServicePtr
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.MenuList import MenuList
from Components.ScrollLabel import ScrollLabel
from Tools.Directories import resolveFilename, pathExists, fileExists
from Components.ActionMap import ActionMap, HelpableActionMap
from Plugins.Extensions.archivCZSK.resources.tools.util import PVideo, PDownloads
from Plugins.Extensions.archivCZSK.resources.tools.downloader import DownloadManager
from Components.config import config
global_session = None

def setGlobalSession(session):
    global global_session
    global_session = session


class PanelList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setItemHeight(35)
        self.l.setFont(0, gFont("Regular", 22))


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

class DownloadManagerGUI(object):
    @staticmethod
    def askSaveDownloadCB(it):
        session = global_session
        download = DownloadManager.getInstance().findDownloadByIT(it)
        
        def saveDownload(callback=None):
            if callback:
                pass
            else:              
                DownloadManager.getInstance().removeDownload(download)

        if download is not None:
            if download.downloaded:
                session.openWithCallback(saveDownload, MessageBox, _("Do you want to save") + ' ' + download.name.encode('utf-8') + ' ' + _("to disk?"), type=MessageBox.TYPE_YESNO)  
            else:
                session.openWithCallback(saveDownload, MessageBox, _("Do you want to continue downloading") + ' ' + download.name.encode('utf-8') + ' ' + _("to disk?"), type=MessageBox.TYPE_YESNO)  

    @staticmethod
    def playDownloadCB(download):
        session = global_session
        it = PVideo()
        it.name = download.name
        it.url = download.local
        #it.subs = os.path.join(download.local,os.path.splitext(download.local.split('/')[-1])[0] + '.srt')
        #from Plugins.Extensions.archivCZSK.player.player import Player
        #video = Player(session, it, DownloadManagerGUI.askSaveDownloadCB)
        from content import ContentScreen
        
        def playVideo(cb=None):
            ContentScreen.instance.playVideo(it, True)
        
        def showPlayDownloadInfo():
            ContentScreen.instance.onShow.remove(showPlayDownloadInfo)
            session.openWithCallback(playVideo, MessageBox, _('Video starts playing in few seconds...'), type=MessageBox.TYPE_INFO, timeout=int(config.plugins.archivCZSK.playDelay.value), enable_input=False)
        
        
        while ContentScreen.instance is None:
            pass
        ContentScreen.instance.onShow.append(showPlayDownloadInfo)
            
        
        #timer = eTimer()
        #timer.callback.append(video.play, DownloadManagerGUI.askSaveDownloadCB)
        #timer.start(int(config.plugins.archivCZSK.playDelay.value) * 1000, False)
    
        #Wait for x seconds to start playing
        #from twisted.internet import reactor
        #reactor.callLater(int(config.plugins.archivCZSK.playDelay.value), video.play, askSaveDownloadCB)

    @staticmethod
    def finishDownloadCB(download):
        session = global_session
        def updateDownloadList(callback=None):
            if DownloadListView.instance is not None:
                DownloadListView.instance.updateGUI()
        if download.downloaded:
            session.openWithCallback(updateDownloadList, MessageBox, _("ArchivCZSK - Download:") + ' ' + download.name.encode('utf-8') + ' ' + _("successfully finished."), type=MessageBox.TYPE_INFO, timeout=5)
        else:
            session.openWithCallback(updateDownloadList, MessageBox, _("ArchivCZSK - Download:") + ' ' + download.name.encode('utf-8') + ' ' + _("finished with errors."), type=MessageBox.TYPE_ERROR, timeout=5)  

    @staticmethod
    def startDownloadCB(download):
        session = global_session
        session.open(MessageBox, _("ArchivCZSK - Download:") + ' ' + download.name.encode('utf-8') + ' ' + _("started."), type=MessageBox.TYPE_INFO, timeout=5)
        
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
                session.openWithCallback(DownloadManagerGUI.saveDownload, MessageBox, _("The file ") + download.name.encode('utf-8') + "already exist. Do you want to override?" , type=MessageBox.TYPE_YESNO)  


class DownloadStatus(Screen):
    skin = """
        <screen position="center,center" size="550,400" title="Status..." >
            <widget name="text" position="0,0" size="550,400" font="Console;14" />
        </screen>"""

    def __init__(self, session, download, title="Download Status"):
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
                "showDownloadListView": (self.showDownloadListView, _("show download list")),
            })

    def showDownloadListView(self):
            self.session.open(DownloadListView)

class DownloadListView(Screen):
    instance = None
    skin = """
            <screen position="center,center" size="610,435" title="Main Menu" >
                <widget name="key_red" position="10,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="160,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="310,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="460,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="menu" position="0,55" size="610,350" scrollbarMode="showOnDemand" />
            </screen>"""
            
    def __init__(self, session):
        DownloadListView.instance = self
        Screen.__init__(self, session)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Play"))
        self["key_yellow"] = Button(_("Remove"))
        self["key_blue"] = Button("")
        self["menu"] = PanelList([])
        self.onShown.append(self.setWindowTitle)
        self.working = True
        self.lst_items = None
        self.title = _("Recent downloads")
        self.onClose.append(self.__onClose)

        self["actions"] = NumberActionMap(["archivCZSKActions"],
            {
                "ok": self.okClicked,
                "cancel": self.exit,
                "red": self.askCancelDownload,
                "green": self.playDownload,
                "yellow": self.askRemoveDownload,
                "up": self.up,
                "down": self.down,
            }, -2)
            
        self.onLayoutFinish.append(self.updateGUI)
        
    def __onClose(self):
        DownloadListView.instance = None

    def setWindowTitle(self):
        self.setTitle(self.title)
    
    def updateGUI(self):
        self.working = True
        self.lst_items = DownloadManager.getInstance().download_lst
        self.updateMenuList()
        self.working = False
        
    def askCancelDownload(self):
        if not self.working and len(self.lst_items) > 0:
            self.working = True
            idx = self["menu"].getSelectedIndex()
            download = self.menu_dir[idx]
            self.session.openWithCallback(self.cancelDownload, MessageBox, _('Do you want to cancel') + ' ' + download.name.encode('utf-8') + ' ?', type=MessageBox.TYPE_YESNO)    
    
    def cancelDownload(self, callback=None):
        if callback:
            idx = self["menu"].getSelectedIndex()
            download = self.menu_dir[idx]
            DownloadManager.getInstance().cancelDownload(download)
            self.updateGUI()
        else:
            self.working = False
            
    def askRemoveDownload(self):
        if not self.working and len(self.lst_items) > 0:
            self.working = True
            idx = self["menu"].getSelectedIndex()
            download = self.menu_dir[idx]
            self.session.openWithCallback(self.removeDownload, MessageBox, _('Do you want to remove') + ' ' + download.name.encode('utf-8') + ' ?', type=MessageBox.TYPE_YESNO)    
    
    def removeDownload(self, callback=None):
        if callback:
            idx = self["menu"].getSelectedIndex()
            download = self.menu_dir[idx]
            DownloadManager.getInstance().removeDownload(download)
            self.updateGUI()
        else:
            self.working = False
            
    def playDownload(self):
        if not self.working and len(self.lst_items) > 0:
            self.working = True
            idx = self["menu"].getSelectedIndex()
            download = self.menu_dir[idx]
            it = PVideo()
            it.name = download.name
            it.url = download.local
            #it.subs = os.path.join(download.local,os.path.splitext(download.local.split('/')[-1])[0] + '.srt')
            from Plugins.Extensions.archivCZSK.player.player import Player
            video = Player(self.session, it, self.workingFinished)
            video.play()

    def updateMenuList(self):
        self.menu_dir = []
        for x in self.menu_dir:
            del self.menu_dir[0]
        list = []
        idx = 0
        for x in self.lst_items:
            list.append(PanelListDownloadEntry(x.name.encode('utf-8'), x))
            self.menu_dir.append(x)
            idx += 1    
        self["menu"].setList(list)        

    def keyNumberGlobal(self):
        pass
    
    def exit(self):
        self.close(None)

    def okClicked(self):
        if not self.working and len(self.lst_items) > 0:
            self.working = True
            idx = self["menu"].getSelectedIndex()
            download = self.menu_dir[idx]
            self.session.openWithCallback(self.workingFinished, DownloadStatus, download)
            
    def up(self):
        if not self.working:
            self["menu"].up()

    def down(self):
        if not self.working:
            self["menu"].down()
    

    def workingFinished(self, callback=None):
        self.working = False
    
    def showError(self, error):
        self.session.openWithCallback(self.workingFinished, MessageBox, _(error), type=MessageBox.TYPE_ERROR, timeout=5)
        
    def showInfo(self, info):
        self.session.openWithCallback(self.workingFinished, MessageBox, _(info), type=MessageBox.TYPE_INFO, timeout=5)  
        

class ArchiveDownloads(Screen):
    instance = None
    skin = """
            <screen position="center,center" size="610,435" title="Main Menu" >
                <widget name="key_red" position="10,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="160,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="310,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="460,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="menu" position="0,55" size="610,350" scrollbarMode="showOnDemand" />
            </screen>"""
            
    def __init__(self, session, archive):
        Screen.__init__(self, session)
        self.archive = archive
        self["key_red"] = Button(_("Remove"))
        self["key_green"] = Button("")
        self["key_yellow"] = Button("")
        self["key_blue"] = Button("")
        self["menu"] = PanelList([])
        self.onShown.append(self.setWindowTitle)
        self.working = True
        self.pdownloads = PDownloads(archive)
        self.lst_items = None
        self.title = self.archive.name.encode('utf-8') + ' ' + (_("downloads"))

        self["actions"] = NumberActionMap(["archivCZSKActions"],
            {
                "ok": self.okClicked,
                "cancel": self.exit,
                "red": self.askRemoveDownload,
                "up": self.up,
                "down": self.down,
            }, -2)
            
        self.onLayoutFinish.append(self.updateGUI)

    def setWindowTitle(self):
        self.setTitle(self.title)
    
    def updateGUI(self):
        self.working = True
        self.lst_items = self.pdownloads.getDownloads()
        self.updateMenuList()
        self.working = False
        
    def askRemoveDownload(self):
        if not self.working and len(self.lst_items) > 0:
            self.working = True
            idx = self["menu"].getSelectedIndex()
            download = self.menu_dir[idx]
            self.session.openWithCallback(self.removeDownload, MessageBox, _('Do you want to remove') + ' ' + download.name.encode('utf-8') + ' ?', type=MessageBox.TYPE_YESNO)    
    
    def removeDownload(self, callback=None):
        if callback:
            idx = self["menu"].getSelectedIndex()
            it = self.menu_dir[idx]
            self.pdownloads.removeDownload(it)
            self.updateGUI()
        else:
            self.working = False
            
    def playDownload(self):
        if not self.working and len(self.lst_items) > 0:
            self.working = True
            idx = self["menu"].getSelectedIndex()
            download = self.menu_dir[idx]
            it = PVideo()
            it.name = download.name
            it.url = download.local
            #it.subs = os.path.join(download.local,os.path.splitext(download.local.split('/')[-1])[0] + '.srt')
            from Plugins.Extensions.archivCZSK.player.player import Player
            video = Player(self.session, it, self.workingFinished)
            video.play()

    def updateMenuList(self):
        self.menu_dir = []
        for x in self.menu_dir:
            del self.menu_dir[0]
        list = []
        idx = 0
        for x in self.lst_items:
            list.append(PanelListEntry(x.name.encode('utf-8'), idx, x.thumb))
            self.menu_dir.append(x)
            idx += 1    
        self["menu"].setList(list)        

    def keyNumberGlobal(self):
        pass
    
    def exit(self):
        self.close(None)

    def okClicked(self):
        if not self.working and len(self.lst_items) > 0:
            self.working = True
            idx = self["menu"].getSelectedIndex()
            it = self.menu_dir[idx]
            from Plugins.Extensions.archivCZSK.player.player import Player
            video = Player(self.session, it, self.workingFinished)
            video.play()
            
    def up(self):
        if not self.working:
            self["menu"].up()

    def down(self):
        if not self.working:
            self["menu"].down()

    def workingFinished(self, callback=None):
        self.working = False

    def showError(self, error):
        self.session.openWithCallback(self.workingFinished, MessageBox, _(error), type=MessageBox.TYPE_ERROR, timeout=5)

    def showInfo(self, info):
        self.session.openWithCallback(self.workingFinished, MessageBox, _(info), type=MessageBox.TYPE_INFO, timeout=5)        

