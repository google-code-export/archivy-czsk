# -*- coding: UTF-8 -*-
'''
Created on 28.4.2012

@author: marko
'''
from enigma import loadPNG, RT_HALIGN_RIGHT, RT_VALIGN_TOP, eSize, eListbox, ePoint, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont, getDesktop, ePicLoad, eServiceCenter, iServiceInformation, eServiceReference, iSeekableService, iPlayableService, iPlayableServicePtr
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Label import Label
from Components.MenuList import MenuList

from download import DownloadManagerMessages
from base import  BaseArchivCZSKMenuListScreen
from common import PanelList, PanelListEntryHD
from Plugins.Extensions.archivCZSK import _
from Plugins.Extensions.archivCZSK.resources.tools.items import PItem, PFolder, PVideo
from Plugins.Extensions.archivCZSK.resources.exceptions.archiveException import CustomError, CustomInfoError

PanelListEntry = PanelListEntryHD    


class ContextMenuScreen(BaseArchivCZSKMenuListScreen):  
        def __init__(self, session, archive, it):
            BaseArchivCZSKMenuListScreen.__init__(self, session)
    
            self.archive = archive
            self.it = it
            self.input = None
        
            self["menu"] = PanelList([])
            self["actions"] = NumberActionMap(["archivCZSKActions"],
                {
                "ok": self.ok,
                "cancel": self.cancel,
                "up": self.up,
                "down": self.down,
                }, -2)
            
            self.onShown.append(self.setWindowTitle)

        def setWindowTitle(self):
            self.setTitle('Menu')
                
        def updateMenuList(self):
            self.menu_list[:]
            idx = 0
            list = []
            # video menu
            if isinstance(self.it, PFolder):
                list.append(PanelListEntry(_('Open item'), 0))
                self.menu_list.append(self.it)
                list.append(PanelListEntry(_('Add shortcut'), 1))
                self.menu_list.append(self.it)
                idx += 2
                
            # folder menu        
            elif isinstance(self.it, PVideo):
                list.append(PanelListEntry(_('Play'), 0))
                self.menu_list.append(self.it)
                list.append(PanelListEntry(_('Play and download'), 1))
                self.menu_list.append(self.it)
                list.append(PanelListEntry(_('Download'), 2))
                self.menu_list.append(self.it)
                idx += 3
                
            # archive menu items        
            for key, value in self.it.menu.iteritems():
                x = PItem()
                x.url = value
                list.append(PanelListEntry(key.encode('utf-8'), idx))
                self.menu_list.append(x)
                idx += 1
                            
            self["menu"].setList(list)      
                
        def addShortcut(self, callback=None):
            if callback:
                if self.archive.create_shortcut(self.it):
                    self.showInfo(_('Shortcut was successfully added'))
                self.cancel()
            else:
                self.working = False
                self.cancel()
                
        def askCreateShortcut(self):
            self.session.openWithCallback(self.addShortcut, MessageBox, _('Add shortcut') + ' '\
                                           + self.it.name.encode('utf-8') + '?', type=MessageBox.TYPE_YESNO)           
        
        def doMenuAction(self, idx):
            executed = False
            if isinstance(self.it, PFolder) and not executed:
                # open item
                if idx == 0:
                    executed = True
                    command = 'openitem'
                    arg = {}
                    arg['it'] = self.it
                    self.cancel(command, arg)
                # create shortcut
                elif idx == 1:
                    executed = True
                    self.askCreateShortcut()
                                
            if isinstance(self.it, PVideo) and not executed:
                command = {}
                # play video
                if idx == 0:
                    executed = True
                    command = 'play'
                    arg = {}
                    arg['it'] = self.it
                # play and download video
                elif idx == 1:
                    executed = True
                    command = 'playndownload'
                    arg = {}
                    arg['it'] = self.it
                # download video
                elif idx == 2:
                    executed = True
                    command = None
                    self.archive.download(self.it, DownloadManagerMessages.startDownloadCB, \
                                          DownloadManagerMessages.finishDownloadCB, playDownload=False)
                self.cancel(command, arg)
                
            # custom archive actions        
            if not executed:
                executed = True
                command = self.archive.menuAction(self.menu_list[idx], self.input)
                self.input = None
                if command == 'addtag':
                    self.session.openWithCallback(self.searchCB, VirtualKeyBoard, title=_("Please enter tag name"))
                else:
                    self.cancel(command, None)
                        
        def searchCB(self, word):
            if word is not None and len(word) > 0:
                self.input = word
                self.working = False
                self.ok()
            else:
                self.working = False
                
        def ok(self):
            if not self.working:
                self.working = True
                idx = self["menu"].getSelectedIndex()
                self.doMenuAction(idx)
                
        def cancel(self, command=None, arg={}):
            self.close(command, arg)
    
