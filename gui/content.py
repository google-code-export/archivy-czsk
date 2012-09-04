# -*- coding: UTF-8 -*-
'''
Created on 28.2.2012

@author: marko
'''
import copy, urllib2, os, traceback

from Plugins.Extensions.archivCZSK import _
from Screens.Screen import Screen
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Components.Button import Button
from Components.Label import Label
from Components.ActionMap import ActionMap, NumberActionMap
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
from Components.config import config
from Tools.Directories import resolveFilename, pathExists, fileExists
from enigma import gFont, getDesktop

from Plugins.Extensions.archivCZSK.resources.exceptions.archiveException import *
from menu import ArchiveCZSKConfigScreen, ArchiveConfigScreen
from Plugins.Extensions.archivCZSK.resources.tools.util import PArchive, PItem, PFolder, PExit, PVideo, PSearch, PDownloads
from Plugins.Extensions.archivCZSK.gui.common import *
from Plugins.Extensions.archivCZSK.gui.captcha import Captcha
from Plugins.Extensions.archivCZSK.gui.shortcuts import ShortcutsScreen
from Plugins.Extensions.archivCZSK.gui.context import CtxMenu
from Plugins.Extensions.archivCZSK.gui.info import Info
from Plugins.Extensions.archivCZSK.player.player import Player
from Plugins.Extensions.archivCZSK.gui.download import ArchiveDownloads
from download import DownloadList

_iconPath = "/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon"
ctxMenuImg = LoadPixmap(cached=True, path=os.path.join(_iconPath, 'key_menu.png'))
infoImg = LoadPixmap(cached=True, path=os.path.join(_iconPath, 'key_info.png'))


class ContentScreen(Screen, DownloadList):
    instance = None
    skin = """
        <screen position="center,center" size="720,576" title="Main Menu" >
            <widget name="key_red" position="8,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
            <widget name="key_green" position="186,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
            <widget name="key_yellow" position="364,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
            <widget name="key_blue" position="542,5" zPosition="1" size="170,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
            <widget name="menu" position="0,55" size="720,445" transparent="1" scrollbarMode="showOnDemand" />
            <widget name="ctxmenu_img" position="0,515" size="35,25" zPosition="2" alphatest="on" />
            <widget name="ctxmenu_text" position="40,515" size="535,25" valign="center" halign="left" zPosition="2" font="Regular;18" transparent="1" foregroundColor="white" />
            <widget name="info_img" position="0,545" size="35,25" zPosition="2" alphatest="on" />
            <widget name="info_text" position="40,545" size="535,25" valign="center" halign="left" zPosition="2" font="Regular;18" transparent="1" foregroundColor="white" />
        </screen>
        """
    def __init__(self, session, archive, params):
        ContentScreen.instance = self
        Screen.__init__(self, session)
        DownloadList.__init__(self)
        self["key_red"] = Button("")
        self["key_green"] = Button("")
        self["key_yellow"] = Button("")
        self["key_blue"] = Button("")
        self["menu"] = PanelList([])
        self["ctxmenu_img"] = Pixmap()
        self["ctxmenu_text"] = Label("")
        self["info_img"] = Pixmap()
        self["info_text"] = Label("")
        
        self.title = archive.name.encode('utf-8')
        self.onShown.append(self.setWindowTitle)
        self.onClose.append(self.__onClose)
            
        self.date = None
        self.input = None
        self.parent_it = None
        self.parent_it_commands = None
        
        if params.has_key('lst_items'):
            self.lst_items = params["lst_items"]
        if params.has_key('date'):
            self.date = params["date"]
        if params.has_key('it'):
            self.parent_it = params["it"]
         
        self.xml = None   
        self.archive = archive
        self.stack = []    
                    
        self.working = False #pre blokovanie tlacidiel pri vykonavani funkcie
        self.refresh = False #pre refresh po vyhladavani
        self.loading = False #nacitavame item
    
        
        self.getMode()

        self["actions"] = NumberActionMap(["archivCZSKActions"],
            {
                "ok": self.okClicked,
                "cancel": self.exit,
                "green" : self.downloads,
                #"red": self.updateContent,self.archiveSettings
                "blue": self.archiveSettings,
                "yellow": self.listShortcuts,
                "up": self.up,
                "down": self.down,
                "info": self.info,
                "menu": self.ctxmenu
            }, -2)

        self.onLayoutFinish.append(self.updateGUI)
        
    def __onClose(self):
        ContentScreen.instance = None

    def setWindowTitle(self):
        self.setTitle(self.title)

    def downloads(self):
        self.session.openWithCallback(self.workingFinished, ArchiveDownloads, self.archive)

    def searchDialog(self):
        self.session.openWithCallback(self.searchCB, VirtualKeyBoard, title=_("Please enter search expression"))

    def searchCB(self, word):
        if word is not None and len(word) > 0:
            self.input = word
            self.refresh = True
            self.working = False
            self.okClicked()
        else:
            self.searching = False
            self.working = False
        
    def getMode(self):
        if self.lst_items is not None:
            if len(self.lst_items) > 0:
                if self.lst_items[0].folder and self.date is not None:
                    print "MOD: adresar +xml"
                    self.mode = 0 #adresar +xml
                elif self.lst_items[0].folder and self.date is None and self.archive.name != 'streamy':
                    print "MOD: adresar -xml"
                    self.mode = 1 #adresar -xml
                elif not self.lst_items[0].folder and self.archive.name == 'streamy':
                    print "MOD: streamy-subory"
                    self.mode = 2 #streamy-subory
                elif self.lst_items[0].folder and self.archive.name == 'streamy':
                    print 'MOD: streamy-adresare'
                    self.mode = 5 #streamy-adresare
                elif not self.lst_items[0].folder and not self.archive.name == 'streamy':
                    print 'MOD: subory'
                    self.mode = 3 # subory
                else:
                    print "MOD: chyba- lstitems-existuje"
                    self.mode = 4 #chyba
        else:
            print "MOD: chyba- lstitems-neexistuje "    
            self.mode = 4 #chyba

    def updateGUI(self):
        self.working = True

        if self.mode == 2 or self.mode == 4 or self.mode == 5:
            self["key_red"].setText("")
            self["key_blue"].setText("")
            self["key_yellow"].setText("")

        elif self.mode == 3:
            self["key_red"].setText("")
            self["key_green"].setText(_("Downloads"))
            self["key_blue"].setText(_("Settings"))
            self["key_yellow"].setText(_("Shortcuts"))

        elif self.mode == 1:
            self["key_red"].setText("")
            self["key_green"].setText(_("Downloads"))
            self["key_blue"].setText(_("Settings"))
            self["key_yellow"].setText(_("Shortcuts"))

        elif self.mode == 0:
            print 'date is not None:' + str(self.date)
            self["key_red"].setText(_("Update"))
            self["key_blue"].setText(_("Settings"))
            self["key_yellow"].setText(_("Shortcuts"))
        else:
            self["key_red"].setText("")
            self["key_green"].setText("")
            self["key_blue"].setText("")
            self["key_yellow"].setText("")

        self.updateMenuList()
        self.updateMenuInfoGUI()
        self.working = False


    def updateMenuList(self):
        self.menu_dir = []
        for x in self.menu_dir:
            del self.menu_dir[0]
            
        list = []
        idx = 1
        if self.lst_items is None:
            self.lst_items = []
        exit_it = PExit()
        list.append(PanelListEntry(exit_it.name.encode('utf-8'), 0, exit_it.thumb))
        self.menu_dir.append(exit_it)
        
        for x in self.lst_items:
            list.append(PanelListEntry(x.name.encode('utf-8'), idx, x.thumb))
            self.menu_dir.append(x)
            idx += 1
        self["menu"].setList(list)
        self["menu"].moveToIndex(0)



    def load(self, dir_dict):
            print '[DirectoryScreen] load'
            self.lst_items = dir_dict["lst_items"]
            #self.resolveCommand(dir_dict['lst_items'][1])
            self.date = dir_dict["date"]
            self.parent_it = dir_dict["parent_it"]
            if self.parent_it:
                print self.parent_it.name
            if dir_dict['refresh']:
                self.refreshList()
            else:
                self.getMode()
                self.updateGUI()


    def resolveCommand(self, command):
        if command is None:
            return
        if command['text'] == 'refreshnow':
            self.refreshList()
        elif command['text'] == 'refreshafter':
            self.refresh = True
        elif command['text'] == 'openitem':
            self.openItem(command['it'])
        elif command['text'] == 'captcha':
            Captcha(self.session, command['captchaCB'], self.captchaS, self.workingFinished, command['prmLD'])
        elif command['text'] == 'play':
            self.openItem((command['it']))
        elif command['text'] == 'search':
            self.session.openWithCallback(self.searchCB, VirtualKeyBoard, title=_("Please enter search expression"))
        else:
            print '[resolveCommand] unknown command', command

    def captchaS(self, prmLD):
        self.save()
        self.refresh = False
        self.input = None
        self.load(prmLD)        

    def save(self):
        print 'saving items'
        lst_items = self.lst_items[:]
        self.stack.append({'lst_items':lst_items, 'parent_it':copy.copy(self.parent_it), 'date':copy.copy(self.date), 'refresh':copy.copy(self.refresh)})

    def refreshList(self):
        params = {}
        if self.parent_it is not None:
            params['parent_id'] = self.parent_it.url_text + self.parent_it.mode_text
        params['it'] = self.parent_it
        try:
            (self.lst_items, command), self.date = self.archive.open(params)
        except:
            self.showError(_('Error in updating list'))
        else:
            self.getMode()
            self.updateGUI()

    def okClicked(self):
        print 'okclicked', self.working, len(self.lst_items)
        if not self.working and len(self.lst_items) > 0:
            self.working = True
            idx = self["menu"].getSelectedIndex()
            it = self.menu_dir[idx]
            self.openItem(it) 

    def playVideo(self, it, download=False):
        self.working = True
        if download:
            from download import DownloadManagerGUI
            player = Player(self.session, it, self.workingFinished, DownloadManagerGUI.askSaveDownloadCB)
        else:
            player = Player(self.session, it, self.workingFinished)
        player.play()

    def openItem(self, it):
            print it.name, it.url
            if isinstance(it, PExit): 
                self.working = False
                self.exit()

            elif isinstance(it, PDownloads):
                items = it.getDownloads()
                date = None
                prmLD = {'parent_it': it, 'refresh' :False}
                prmLD['lst_items'] = items
                prmLD['date'] = date
                self.save()
                self.refresh = False
                self.input = None
                self.load(prmLD)

            elif isinstance(it, PFolder) or isinstance(it, PSearch): 
                    id_id = it.url_text + it.mode_text
                    prmOA = {'parent_id':id_id, 'update':False, 'it':it, 'input':self.input}    
                    prmLD = {'parent_it': it, 'refresh' :False}

                    try:
                        (items, command), date = self.archive.open(prmOA)
                    except CustomInfoError as er:
                        self.showInfo(er.value)
                    except CustomError as er:
                        self.showError(er.value)
                    except urllib2.HTTPError:
                        self.showError(_("Error loading: Not accessible/supported show"))
                    except urllib2.URLError:
                        self.showError(_("Error loading: Not accessible/supported show"))
                    except Exception:
                        if not config.plugins.archivCZSK.debug.value:
                            self.showError(_("Unknown error: Not supported show"))
                        else:
                            self.showError(_("Unknown error: Not supported show"))
                            fh = open("/tmp/archivCZSKException.log", "w")
                            traceback.print_exc(file=fh)
                    else:
                        if len(items) == 0 and len(command) > 0:
                            if command['text'] == 'captcha':
                                command['prmLD'] = prmLD
                            self.resolveCommand(command)

                        elif len(items) > 0 and len(command) == 0:
                            prmLD['lst_items'] = items
                            prmLD['date'] = date
                            self.save()
                            self.refresh = False
                            self.input = None
                            self.load(prmLD)

                        elif len(items) == 0 and len(command) == 0:
                            self.input = None
                            self.showInfo(_("Loaded list is empty"))

                        else:
                            self.input = None
                            self.working = False

            elif isinstance(it, PVideo):
               # def askToPlayVideo(callback=None):
                    #if callback:
                        #self.playVideo(it, False)
                    #self.working = False
                if it.url == '':
                    self.working = False
                #else:
                   # if isinstance(it, PNotSupportedVideoFormat):
                        #self.session.openWithCallback(askToPlayVideo, MessageBox, _("You are trying to play maybe not supported video format. Do you want to continue?"), type=MessageBox.TYPE_YESNO)
                else:
                    self.playVideo(it, False)   
            else:
                print '[ContentScreen] - openItem: unknown item'
                
                
    def archiveInfo(self, it):
        return not config.plugins.archivCZSK.csfd.getValue() and (len(it.info) > 0 or it.image is not None)
    
    def CSFDInfo(self, it):
        return config.plugins.archivCZSK.csfd.getValue() and not (isinstance(it, PExit) or isinstance(it, PVideo) or isinstance(it, PSearch))
        
    
    def updateMenuInfoGUI(self):
        idx = self["menu"].getSelectedIndex()
        if len(self.lst_items) > 0:
            it = self.menu_dir[idx]
            if self.CSFDInfo(it):
                self["info_text"].setText(_("Show info from name of item in CSFD plugin"))
                self['info_img'].instance.setPixmap(infoImg)
                      
            elif self.archiveInfo(it):
                self["info_text"].setText(_("Additional informations are available"))
                self['info_img'].instance.setPixmap(infoImg)      
            else:
                self["info_text"].setText("")
                self['info_img'].instance.setPixmap(None)

            if isinstance(it, PExit):
                self['ctxmenu_img'].instance.setPixmap(None)
                self["ctxmenu_text"].setText("")
            else:
                self['ctxmenu_img'].instance.setPixmap(ctxMenuImg)
                self["ctxmenu_text"].setText(_("show posibilities of current item"))
        
    def up(self):
        if not self.working:
            self.working = True
            self["menu"].up()
            self.updateMenuInfoGUI()
            self.working = False            

    def down(self):
        if not self.working:
            self.working = True
            self["menu"].down()
            self.updateMenuInfoGUI()
            self.working = False
            
    def shortcutCallback(self, it_sc):
        if it_sc is not None:
            self.openItem(it_sc)
        else:
            self.workingFinished()    
            
    def listShortcuts(self):
        if not self.working and not (self.mode == 5 or self.mode == 2):
            self.working = True
            self.session.openWithCallback(self.shortcutCallback, ShortcutsScreen, self.archive)    
            
            
    def info(self):
        if not self.working and len(self.lst_items) > 0:
            self.working = True
            idx = self["menu"].getSelectedIndex()
            it = self.menu_dir[idx]
            if self.archiveInfo(it):
                Info(self.session, it, self.workingFinished)
            elif self.CSFDInfo(it):
                try:
                    from Plugins.Extensions.CSFD.plugin import CSFD
                    self.session.open(CSFD, it.name.encode('utf-8'), False)
                except ImportError:
                    self.working = False
            else:
                self.working = False
    
    def ctxmenu(self):
        if not self.working and len(self.lst_items) > 0:
            self.working = True
            idx = self["menu"].getSelectedIndex()
            it = self.menu_dir[idx]
            self.session.openWithCallback(self.contextMenuCB, CtxMenu, self.archive, it, self.refreshList)
    
    def archiveSettings(self):
        if not self.working and not self.mode == 2 and not self.mode == 5:
            self.session.openWithCallback(self.workingFinished, ArchiveConfigScreen, self.archive)
        
    def contextMenuCB(self, command=None):
        self.resolveCommand(command)
        self.working = False
            
    def keyNumberGlobal(self):
        pass

    def workingFinished(self, callback=None, callback2=None):
        self.working = False
    
    def showError(self, error):
        self.session.openWithCallback(self.workingFinished, MessageBox, _(error), type=MessageBox.TYPE_ERROR, timeout=5)
        
    def showInfo(self, info):
        self.session.openWithCallback(self.workingFinished, MessageBox, _(info), type=MessageBox.TYPE_INFO, timeout=5)
        
    def exit(self):
        if not self.working:
            self.working = True
            if len(self.stack) == 0:
                self.close(self.archive.xml_sc, self.archive.xml)
            else:
                self.load(self.stack.pop())
