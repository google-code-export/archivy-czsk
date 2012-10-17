# -*- coding: UTF-8 -*-
'''
Created on 28.2.2012

@author: marko
'''
import copy, urllib2, os, traceback

from enigma import eTimer
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.Button import Button
from Components.Label import Label
from Components.ActionMap import ActionMap, NumberActionMap
from Components.config import config
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap

from Plugins.Extensions.archivCZSK import _
from Plugins.Extensions.archivCZSK.resources.exceptions.archiveException import CustomError, CustomInfoError, ArchiveThreadException
from Plugins.Extensions.archivCZSK.resources.tools.items import PItem, PFolder, PExit, PVideo, PSearch, PDownloads
from Plugins.Extensions.archivCZSK.resources.tools.task import Task
from Plugins.Extensions.archivCZSK.gui.common import PanelList, PanelList, PanelListEntryHD, PanelListEntrySD, LoadingScreen , TipBar
from Plugins.Extensions.archivCZSK.gui.captcha import Captcha
from Plugins.Extensions.archivCZSK.gui.shortcuts import ShortcutsScreen
from Plugins.Extensions.archivCZSK.gui.context import ContextMenuScreen
from Plugins.Extensions.archivCZSK.gui.info import Info
from Plugins.Extensions.archivCZSK.gui.download import ArchiveDownloadsScreen, DownloadList
from Plugins.Extensions.archivCZSK.player.player import Player
from menu import  ArchiveConfigScreen
from base import BaseArchivCZSKScreen, BaseArchivCZSKMenuListScreen

PanelListEntry = PanelListEntryHD

KEY_MENU_IMG = LoadPixmap(cached=True, path=os.path.join(BaseArchivCZSKScreen.ICON_PATH, 'key_menu.png'))
KEY_INFO_IMG = LoadPixmap(cached=True, path=os.path.join(BaseArchivCZSKScreen.ICON_PATH, 'key_info.png'))
KEY_5_IMG = LoadPixmap(cached=True, path=os.path.join(BaseArchivCZSKScreen.ICON_PATH, 'key_5.png'))

def debug(data):
    if config.plugins.archivCZSK.debug.getValue():
        print '[ArchivCZSK] ContentScreen:', data.encode('utf-8')
 
 
class BaseContentScreen(BaseArchivCZSKMenuListScreen):
    """Base Content Screen for archive Items"""
    def __init__(self, session, archive, params):
        BaseArchivCZSKMenuListScreen.__init__(self, session)
        
        self.archive = archive
        
        # root item
        root_it = PFolder()
        root_it.name = "root"
        root_it.root = True
        
        self.parent_it = root_it
        
        self.refresh = False #to refresh screen
        self.refreshing = False #when screen is refreshing
        self.searching = False #when searching
        self.loading = False #when 
        
        if params.has_key('lst_items'):
            self.lst_items = params["lst_items"][:]
        
        self["status_label"] = Label("")
        self.loadingScreen = session.instantiateDialog(LoadingScreen)
        

        # stack to save loaded content of screens
        self.stack = []
        
        #called by workingFinished
        self.onStopWork.append(self.resetState)
        self.onStopWork.append(self.stopLoading)
        self.onStopWork.append(self.updateGUI)
        
        #called by loadingList
        # list of functions which will be executed before Loading list
        self.onLoadList = [self.workingStarted, self.startLoading, self.updateGUI]
        
        #called by showingList
        # list of functions which will be executed before showing list
        self.onShowList = [self.updateMenuList, self.workingFinished]
        

    
    def loadingList(self):
        for f in self.onLoadList:
            f()
    
    def showingList(self):
        for f in self.onShowList:
            f()
    
    def resetState(self):
        self.searching = False
        self.refreshing = False
        
    def startLoading(self):
        self.loadingScreen.start()
        self.loading = True
        
    def stopLoading(self):
        self.loading = False
        self.loadingScreen.stop()
    
    
    
    def resolveCommand(self, command, arg):
        print arg
        debug("resolving %s command " % command)
        
        if command is None:
            self.workingFinished()
            return
        
        if command == 'refreshnow':
            self.refreshList()
            
        elif command == 'refreshafter':
            self.refresh = True
            self.workingFinished()
            
        elif command == 'openitem':
            self.openItem(arg['it'])
            
        elif command == 'play':
            self.playItem((arg['it']), False)
            
        elif command == 'playndownload':
            self.playItem((arg['it']), True)
            
        else:
            self.workingFinished()
            debug("unknown command %s" % command)
    
    
    def openArchiveDownloads(self):
        if not self.working:
            debug("opening archiveDownloads")
            self.workingStarted()
            self.session.openWithCallback(self.workingFinished, ArchiveDownloadsScreen, self.archive)
            
    def openArchiveSettings(self):
        if not self.working:
            self.workingStarted()
            debug("opening archiveSettings")
            self.session.openWithCallback(self.workingFinished, ArchiveConfigScreen, self.archive)
        
        
    def showCaptcha(self, arg):
        Captcha(self.session, arg['captchaCB'], self.captchaCB, self.workingFinished(), arg['prmLD'])
        
    def captchaCB(self, prmLD):
        self.save()
        self.refresh = False
        self.input = None
        self.load(prmLD)
     
    def playItem(self, it):
        pass
       
    def search(self):
        self.session.openWithCallback(self.searchCB, VirtualKeyBoard, title=_("Please enter search expression"))

    def searchCB(self, word):
        if word is not None and len(word) > 0:
            self.input = word
            self.searching = True
            self.openItem(self.getSelectedItem())
        else:
            self.workingFinished()

    def updateMenuList(self):
        debug("updateMenuList")
        
        #clear menu_list
        del self.menu_list[:]
        
        gui_list = []

        #first item is always exit item
        exit_it = PExit()
        gui_list.append(PanelListEntry(exit_it.name.encode('utf-8'), 0, exit_it.thumb))
        self.menu_list.append(exit_it)
        
        #adding next items from loaded lst_items
        idx = 1
        for x in self.lst_items:
            gui_list.append(PanelListEntry(x.name.encode('utf-8'), idx, x.thumb))
            self.menu_list.append(x)
            idx += 1
            
        self["menu"].setList(gui_list)
        self["menu"].moveToIndex(0)
        
    def updateGUI(self):
        debug("updateGUI")
        
        if self.loading:
            self["status_label"].setText(_("Loading"))
            self["menu"].hide()
            self.loadingScreen.start()
            
        else:
            if self.loadingScreen.isShown():
                self.loadingScreen.stop()
                
            if not self["menu"].visible:
                self["menu"].show()
                
            self["status_label"].setText("")
    
 
    def ok(self):
        if not self.working and len(self.lst_items) > 0:
            self.openItem(self.getSelectedItem())
            
    
    def openContextMenu(self):
        if not self.working and len(self.lst_items) > 0:
            self.workingStarted()
            it = self.getSelectedItem()
            debug("opening context menu for %s" % it.name)
            self.session.openWithCallback(self.openContextMenuCB, ContextMenuScreen, self.archive, it)
        
    def openContextMenuCB(self, command=None, arg=None):
        debug("ContextMenuCB %s command" % str(command))
        self.resolveCommand(command, arg)
                  
    def openItem(self, it):
        
        ## nested function called when loading was successful
        def successItemCB(content_cb):
            debug("succes opening of item")
            
            items = content_cb[0][:]
            command = content_cb[1]
            arg = content_cb[2].copy()
                
            if len(items) == 0 and command is not None:
                debug("received only screen command")
                self.resolveCommand(command, arg)
                    
            elif len(items) > 0 and command is not None:
                debug("received item list and screen command")
                self.workingFinished()
            
            elif len(items) > 0 and command is None:
                debug("received only item list")
                prmLD['lst_items'] = items
                
                if self.searching:
                    self.refresh = True
                    
                #save current screen
                if not self.refreshing:
                    self.save()
                    
                self.load(prmLD)
                
            elif len(items) == 0 and command is None:
                debug("received nothing")
                self.input = None
                if self.searching:
                    self.stopLoading()
                    self.updateGUI()
                    self.refreshList()
                else:
                    self.stopLoading()
                    self.updateGUI()
                    self.showInfo(_("Loaded list is empty"))
                
            else:
                debug("Unknown situation")
                self.input = None
                self.workingFinished()
         
        ## nested function called when loading was unsuccessful
        @self.exception_dec        
        def errorItemCB(failure):
            self.stopLoading()
            self.updateGUI()
            failure.raiseException()
                
        if isinstance(it, PExit): 
            self.cancel()

        elif isinstance(it, PFolder): 
            # parameters for opening item
            # parameters for screen
            prmLD = {'parent_it': it, 'refresh' :False}

            
            # set callbacks for success/error which will be called when deffered fired
            
            self.loadingList()
            
            #start opening items
            d = self.archive.openItem(self.session, it)
            d.addCallbacks(successItemCB, errorItemCB)
                            

        elif isinstance(it, PVideo):
            if it.url == '':
                pass
            else:
                self.playItem(it, False)   
        else:
            debug("cannot open unknown item %s" % it.__class__.__name__)
            
            
    
    def load(self, params):
        """loads content of screen from screen parameters"""
        debug("loading screen")
        #set defaults for new "screen" (list+parameters)
        self.refresh = False
        self.input = None
        
        #set items for new screen
        self.lst_items = params["lst_items"]
        
        #set parent item, for refresh purpose
        self.parent_it = params["parent_it"]
        
        debug("loading screen of %s item" % self.parent_it.name)
        
        if params['refresh']:
            self.refreshList()
        else:
            self.showingList()
            
    def save(self):
        """saves current content of screen to stack"""
        debug("saving current screen to stack")
        lst_items = self.lst_items[:]
        
        #saving screen parameters to stack
        self.stack.append({'lst_items':lst_items, 'parent_it':copy.copy(self.parent_it), 'refresh':copy.copy(self.refresh)})
        
    def refreshList(self):
        """refreshes current screen"""
        debug("refreshing screen for %s item" % self.parent_it.name)
        self.refreshing = True
        self.openItem(self.parent_it)
        
        
    def toggleCancelLoading(self):
        if Task.getInstance() is not None and not Task.getInstance().isCancelling():
            self["status_label"].setText("Canceling...")
            Task.getInstance().setCancel()
            
        elif Task.getInstance() is not None and Task.getInstance().isCancelling():
            self["status_label"].setText("Loading...")
            Task.getInstance().setResume()
        else:
            debug("Task is not running")
                
    def exitContentScreen(self):
        self.close(self.archive.xml_sc)
        
    def exitItem(self):
        if len(self.stack) == 0:
            self.exitContentScreen()
        else:
            self.load(self.stack.pop()) 
        
    def cancel(self):
        if self.working:
            self.toggleCancelLoading()
        else:
            self.exitItem()     


 
class ContentScreen(BaseContentScreen, DownloadList, TipBar):
    
    CSFD_TIP = (KEY_5_IMG, _("show info in CSFD"))
    INFO_TIP = (KEY_INFO_IMG, _("show additional info"))
    CONTEXT_TIP = (KEY_MENU_IMG, _("show menu of current item"))
       
    def __init__(self, session, archive, params):
        
        BaseContentScreen.__init__(self, session, archive, params)
        
        #include DownloadList
        DownloadList.__init__(self)
        
        #include TipList
        TipBar.__init__(self, [self.CSFD_TIP, self.CONTEXT_TIP, self.INFO_TIP], startOnShown=True)
        
        debug('initializing')
         
        self["key_red"] = Button("")
        self["key_green"] = Button(_("Downloads"))
        self["key_yellow"] = Button(_("Shortcuts"))
        self["key_blue"] = Button(_("Settings"))
        self["actions"] = NumberActionMap(["archivCZSKActions"],
            {
                "ok": self.ok,
                "up": self.up,
                "down": self.down,
                "cancel": self.cancel,
                "green" : self.openArchiveDownloads,
                "blue": self.openArchiveSettings,
                "yellow": self.openArchiveShortcuts,
                "info": self.openArchiveInfo,
                "menu": self.openContextMenu,
                "csfd": self.openCSFD
            }, -2)

        self.onShown.append(self.setWindowTitle)
        
    def setWindowTitle(self):
        self.setTitle(self.archive.name.encode('utf-8'))
        
    def openArchiveShortcuts(self):
        if not self.working:
            self.workingStarted()
            debug("opening archiveShortcuts")
            self.session.openWithCallback(self.openArchiveShortcutsCB, ShortcutsScreen, self.archive)
            
    def openArchiveShortcutsCB(self, it_sc):
        if it_sc is not None:
            self.openItem(it_sc)
        else:
            self.workingFinished()
                       
    def archiveInfo(self, it):
        return not isinstance(it, PExit)
        
    def openArchiveInfo(self):
        if not self.working and len(self.lst_items) > 0:
            self.workingStarted()
            it = self.getSelectedItem()
            if self.archiveInfo(it):
                Info(self.session, it, self.workingFinished)
     
    def CSFDInfo(self, it):
        return config.plugins.archivCZSK.csfd.getValue() and not (isinstance(it, PExit))
               
    def openCSFD(self):
        if not self.working and len(self.lst_items) > 0:
            it = self.getSelectedItem()
            if self.CSFDInfo(it):
                self.workingStarted()
                try:
                    from Plugins.Extensions.CSFD.plugin import CSFD
                    movieName = it.name
                    if isinstance(it, PVideo):
                        movieName = it.name.replace('.', ' ').replace('_', ' ').replace('-', ' ')
                    self.session.openWithCallback(self.workingFinished, CSFD, movieName, False)
                except ImportError:
                    self.showInfo(_("Plugin CSFD is not installed."))


    def playItem(self, it, playAndDownload=False):
        if isinstance(it, PVideo):
            player = Player(self.session, it, self.archive, self.workingFinished, config.plugins.archivCZSK.useVideoController)
            if playAndDownload:
                player.playAndDownload()
            else:
                player.play()
        else:
            self.workingFinished()
            
