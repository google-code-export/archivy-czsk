# -*- coding: UTF-8 -*-
'''
Created on 28.4.2012

@author: marko
'''

from Screens.MessageBox import MessageBox
from Tools.Directories import resolveFilename, pathExists, fileExists
from enigma import loadPNG, RT_HALIGN_RIGHT, RT_VALIGN_TOP, eSize, eListbox, ePoint, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont, getDesktop, ePicLoad, eServiceCenter, iServiceInformation, eServiceReference, iSeekableService, iPlayableService, iPlayableServicePtr
from Components.Button import Button
from Components.Label import Label, MultiColorLabel
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.MenuList import MenuList


from Plugins.Extensions.archivCZSK import _
from base import BaseArchivCZSKScreen


class PanelList(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, False, eListboxPythonMultiContent)
		self.l.setItemHeight(35)
		self.l.setFont(0, gFont("Regular", 22))
		
def PanelListEntry(name, idx, png=''):
	res = [(name)]
	if fileExists(png):
		res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(35, 25), png=loadPNG(png)))
	res.append(MultiContentEntryText(pos=(60, 5), size=(550, 30), font=0, flags=RT_VALIGN_TOP, text=name))
	return res		

class ShortcutsScreen(BaseArchivCZSKScreen):
	def __init__(self, session, archive):
		BaseArchivCZSKScreen.__init__(self, session)
		
		self.working = False
		self.archive = archive
		self.lst_items = self.archive.getShortcuts()
		self.title = _("Shortcut") + ' ' + archive.name.encode('utf-8')
		
		self["key_red"] = Button(_("Remove shortcut"))
		self["key_green"] = Button("")
		self["key_yellow"] = Button("")
		self["key_blue"] = Button("")
		self["menu"] = PanelList([])
		self["actions"] = NumberActionMap(["archivCZSKActions"],
			{
				"ok": self.ok,
				"cancel": self.exit,
				"red": self.askRemoveShortcut,
				"up": self.up,
				"down": self.down,
			}, -2)
			
		self.onLayoutFinish.append(self.updateGUI)
		self.onShown.append(self.setWindowTitle)

	def setWindowTitle(self):
		self.setTitle(self.title)
		
	
	def updateGUI(self):
		self.working = True
		self.updateMenuList()
		self.working = False
		
	def askRemoveShortcut(self):
		if not self.working:
			if len(self.menu_dir) == 0:
				pass
			else:
				self.working = True
				idx = self["menu"].getSelectedIndex()
				it = self.menu_dir[idx]
				self.session.openWithCallback(self.removeShortcut, MessageBox, _('Do you want to delete') + ' ' + it.name.encode('utf-8') + '?', type=MessageBox.TYPE_YESNO)	
	
	def removeShortcut(self, callback=None):
		if callback:
			self.working = True
			idx = self["menu"].getSelectedIndex()
			it = self.menu_dir[idx]
			id_shortcut = it.url_text + it.mode_text
			self.archive.removeShortcut(id_shortcut)
			print 'removing shortcut'
			self.lst_items = self.archive.getShortcuts()
			self.updateGUI()
		else:
			self.working = False

	def updateMenuList(self):
		self.menu_dir = []
		for x in self.menu_dir:
			del self.menu_dir[0]
		list = []
		idx = 0
		if self.lst_items is None:
			self.lst_items = []
		for x in self.lst_items:
			list.append(PanelListEntry(x.name.encode('utf-8'), idx, x.thumb))
			self.menu_dir.append(x)
			idx += 1	
		self["menu"].setList(list)		

	def keyNumberGlobal(self):
		pass
	
	def exit(self):
		self.close(None)

	def ok(self):
		if not self.working:
			self.working = True
			idx = self["menu"].getSelectedIndex()
			it = self.menu_dir[idx]
			self.close(it)
				
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
