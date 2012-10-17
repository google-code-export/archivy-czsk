# -*- coding: UTF-8 -*-
'''
Created on 28.2.2012

@author: marko
'''

import os, urllib2
import twisted.internet.defer as defer

from Screens.MessageBox import MessageBox
from Tools.LoadPixmap import LoadPixmap
from Components.Button import Button
from Components.Label import Label
from Components.MenuList import MenuList
from Components.ScrollLabel import ScrollLabel
from Components.ActionMap import ActionMap, NumberActionMap
from Components.config import config
from Components.Pixmap import Pixmap

from Plugins.Extensions.archivCZSK import _
from Plugins.Extensions.archivCZSK.resources.exceptions.archiveException import CustomError, CustomInfoError, ArchiveThreadException
from Plugins.Extensions.archivCZSK.resources.tools.task import Task
from base import BaseArchivCZSKMenuListScreen
from menu import ArchiveCZSKConfigScreen
from content import ContentScreen
from stream import StreamContentScreen
from download import DownloadListScreen, DownloadList
from common import PanelList, PanelListEntryHD, PanelListEntrySD, LoadingScreen
PanelListEntry = PanelListEntryHD

class ArchiveScreen(BaseArchivCZSKMenuListScreen, DownloadList):
    def __init__(self, session, tv_archives, video_archives, archive_dict):
        BaseArchivCZSKMenuListScreen.__init__(self, session)
        DownloadList.__init__(self)
        
        # first screen to open when starting plugin, so we start ThreadPool where we can run our tasks(ie. loading archives)
        Task.startWorkerThread()
        
        self.video_archives = video_archives
        self.tv_archives = tv_archives
        self.archive_dict = archive_dict
        self.loading_screen = self.session.instantiateDialog(LoadingScreen)
        
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
                "ok": self.ok,
                "cancel": self.cancel,
                "up": self.up,
                "down": self.down,
                "blue": self.openSettings,
                "red": self.showTVArchives,
                "green": self.showVideoArchives,
                "yellow": self.showStreams,
                "info": self.openDownloadsList
            }, -2)
        
        self.onLayoutFinish.append(self.updateGUI)
        
    def openDownloadsList(self):
        if not self.working:
            self.session.open(DownloadListScreen)
        
    def openSettings(self):
        if not self.working:
            self.session.open(ArchiveCZSKConfigScreen)

    def showTVArchives(self):
        if not self.working:
            self.updateMenuList(self.tv_archives)
    
    def showVideoArchives(self):
        if not self.working:
            self.updateMenuList(self.video_archives)

    def showStreams(self):
        def openItem(session,it):
            d = defer.Deferred()
            lst_streams = stream.modul.getContent(it, None)
            lst_itemscp = [[], None, {}]
            lst_itemscp[0] = lst_streams[0][:]
            lst_itemscp[1] = lst_streams[1]
            lst_itemscp[2] = lst_streams[2].copy()
            print 'created stream deferred'
            d.callback(lst_itemscp)
            return d
            
        if not self.working:
            stream = self.archive_dict['streamy']
            stream.modul.loadList()
            stream.openItem = openItem
            params = {}
            content = stream.modul.getContent(None, None)
            params['lst_items'] = content[0]
            self.session.openWithCallback(self.openArchiveCB, StreamContentScreen, stream, params)

    def updateGUI(self):
        it = self.getSelectedItem()
        if it is not None:
            if self.archive_dict.has_key(it.id):
                archive = self.archive_dict[it.id]
                self["image"].instance.setPixmap(archive.get_info('image'))
                self["title"].setText(archive.get_info('name').encode('utf-8'))
                self["author"].setText(_("Author: ") + archive.get_info('author').encode('utf-8'))
                self["version"].setText(_("Version: ") + archive.version.encode('utf-8'))
                self["about"].setText(archive.get_info('description').encode('utf-8'))
            else:
                self["image"].instance.setPixmap(None)
                self["title"].setText("")
                self["author"].setText("")
                self["version"].setText("")
                self["about"].setText("")

    def updateMenuList(self, lst=None):
        if lst is None:
            lst = self.tv_archives
        self.menu_list = []
        for x in self.menu_list:
            del self.menu_list[0]
        list = []
        idx = 0
        for x in lst:
            list.append(PanelListEntry(x.id.encode('utf-8'), idx))
            self.menu_list.append(x)
            idx += 1
        self["menu"].setList(list)

    def ok(self):
        if not self.working:
            it = self.getSelectedItem()
            if it is not None:
                self.openArchive(self.getSelectedItem())
            else:
                self.working = False
            
        
    def openArchive(self, it):
        
        def successArchiveCB(content):
            self.loading_screen.stop()
            (params['lst_items'], command, args) = content
            self.session.openWithCallback(self.openArchiveCB, ContentScreen, archive, params)
            
        @self.exception_dec        
        def errorArchiveCB(failure):
            self.loading_screen.stop()
            failure.raiseException()
                
        params = {}
        if self.archive_dict.has_key(it.id):
            archive = self.archive_dict[it.id]
            self.loading_screen.start()
            d = archive.openItem(self.session, None)
            d.addCallbacks(successArchiveCB, errorArchiveCB)
                        
    def openArchiveCB(self, xml_sc=None):             
        if xml_sc is not None:
            xml_sc.writeArchiveFile()
        self.working = False
           
    def up(self):
        if not self.working:
            self["menu"].up()
            self.updateGUI()
    
    def down(self):
        if not self.working:
            self["menu"].down()
            self.updateGUI()

    def cancel(self):
        #we are trying to close loading of archive
        if self.working:
            if Task.getInstance() is not None:
                Task.getInstance().stop()
        #ask close plugin
        elif not self.working:
            self.session.openWithCallback(self.closePlugin, MessageBox, _('Do you want to exit ArchivCZSK?'), type=MessageBox.TYPE_YESNO)

    def closePlugin(self, callback=None):
        if callback:
            if config.plugins.archivCZSK.clearMemory.value:
                self.freeMemory()
                
            #We dont need ThreadPool anymore so we stop it  
            Task.stopWorkerThread()
            #del Task.thread_pool
            
            self.close()

    def freeMemory(self):
        os.system("echo 1 > /proc/sys/vm/drop_caches")

        

