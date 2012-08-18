# -*- coding: UTF-8 -*-
'''
Created on 28.4.2012

@author: marko
'''
from Plugins.Extensions.archivCZSK import _
from Screens.Screen import Screen
from Plugins.Extensions.archivCZSK.resources.tools.util import PItem, PFolder, PVideo
from enigma import loadPNG, RT_HALIGN_RIGHT, RT_VALIGN_TOP, eSize, eListbox, ePoint, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont, getDesktop, ePicLoad, eServiceCenter, iServiceInformation, eServiceReference, iSeekableService, iPlayableService, iPlayableServicePtr
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Screens.MessageBox import MessageBox
from Components.Label import Label
from Components.MenuList import MenuList
from Tools.Directories import resolveFilename, pathExists, fileExists
from Screens.VirtualKeyBoard import VirtualKeyBoard
from download import DownloadManagerGUI

class PanelList(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, False, eListboxPythonMultiContent)
		self.l.setItemHeight(35)
		self.l.setFont(0, gFont("Regular", 22))
		
def PanelListEntry(name, idx, png=''):
	res = [(name)]
	#if fileExists(png):
	#	res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(35, 25), png=loadPNG(png)))
	res.append(MultiContentEntryText(pos=(0, 0), size=(500, 30), font=0, flags=RT_HALIGN_CENTER, text=name))
	return res		


class CtxMenu(Screen):
	instance = None
	skin = """
        <screen name="CtxMenu" position="center,center" size="500,300">
                 <widget name="menu" position="0,0" size="500,290" scrollbarMode="showOnDemand" />
        </screen>"""
		
	def __init__(self, session, archive, it, refresh):
		Screen.__init__(self, session)
		CtxMenu.instance = self
		self["menu"] = PanelList([])
		#self["title"] = Label(it.name.encode('utf-8'))
		self.onShown.append(self.setWindowTitle)
		self.onClose.append(self.__onClose)
		self.working = False
		self.archive = archive
		self.refresh = refresh
		self.lst_items = it.menu
		self.it = it
		self.selected_it = None
		self.input = None
		self.title = 'Menu'#it.name.encode('utf-8')

		self["actions"] = NumberActionMap(["archivCZSKActions"],
			{
				"ok": self.okClicked,
				"cancel": self.exit,
				"up": self.up,
				"down": self.down,
			}, -2)
			
		self.onLayoutFinish.append(self.updateMenuList)

	def setWindowTitle(self):
		self.setTitle(self.title)
	
	def __onClose(self):
		CtxMenu.instance = None
		
	def updateMenuList(self):
		self.menu_dir = []
		for x in self.menu_dir:
			del self.menu_dir[0]
		idx = 0
		list = []
		if isinstance(self.it, PFolder):
			list.append(PanelListEntry(_('Open item'), 0))
			self.menu_dir.append(self.it)
			list.append(PanelListEntry(_('Add shortcut'), 1))
			self.menu_dir.append(self.it)
			idx += 2
		elif isinstance(self.it, PVideo):
				list.append(PanelListEntry(_('Play'), 0))
				self.menu_dir.append(self.it)
				list.append(PanelListEntry(_('Play and download'), 1))
				self.menu_dir.append(self.it)
				list.append(PanelListEntry(_('Download'), 2))
				self.menu_dir.append(self.it)
				idx += 3
		for key, value in self.lst_items.iteritems():
			x = PItem()
			x.url = value
			list.append(PanelListEntry(key.encode('utf-8'), idx))
			self.menu_dir.append(x)
			idx += 1
				
		self["menu"].setList(list)	
		
	def addShortcut(self, callback=None):
		if callback:
			if self.archive.createShortcut(self.it):
				self.showInfo(_('Shortcut was successfully added'))
			self.exit()
		else:
			self.workingFinished()
			self.exit()
		
	def askCreateShortcut(self):
			self.session.openWithCallback(self.addShortcut, MessageBox, _('Add shortcut') + ' ' + self.it.name.encode('utf-8') + '?', type=MessageBox.TYPE_YESNO)		
	
	def doMenuAction(self, idx):
		executed = False
		if isinstance(self.it, PFolder) and not executed:
			if idx == 0:
				executed = True
				command = {}
				command['text'] = 'openitem'
				command['it'] = self.it 
				self.exit(command)
			elif idx == 1:
				executed = True
				self.askCreateShortcut()
				
		if isinstance(self.it, PVideo) and not executed:
			command = {}
			if idx == 0:
				executed = True
				command['text'] = 'play'
				command['it'] = self.it
			elif idx == 1:
				executed = True
				command['text'] = None
				self.archive.download(self.it, DownloadManagerGUI.playDownloadCB, DownloadManagerGUI.finishDownloadCB, playDownload=True)
			elif idx == 2:
				executed = True
				command['text'] = None
				self.archive.download(self.it, DownloadManagerGUI.startDownloadCB, DownloadManagerGUI.finishDownloadCB, playDownload=False)
			self.exit(command)
	
		if not executed:
			executed = True
			command = self.archive.menuAction(self.menu_dir[idx], self.input)
			self.input = None
			if command['text'] == 'addtag':
				self.session.openWithCallback(self.searchCB, VirtualKeyBoard, title=_("Please enter tag name"))
			else:
				self.exit(command)
			
	def searchCB(self, word):
		if word is not None and len(word) > 0:
			self.input = word
			self.working = False
			self.okClicked()
		else:
			self.working = False
		
	
	def okClicked(self):
		if not self.working:
			self.working = True
			idx = self["menu"].getSelectedIndex()
			self.doMenuAction(idx)
				
	def up(self):
		if not self.working:
			self["menu"].up()

	def down(self):
		if not self.working:
			self["menu"].down()
	
	def exit(self, command=None):
		self.close(command)
	
	def workingFinished(self, callback=None):
		self.working = False 
		
	def showInfo(self, info):
		self.session.openWithCallback(self.workingFinished, MessageBox, info, type=MessageBox.TYPE_INFO, timeout=5)
