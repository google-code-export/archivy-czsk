# -*- coding: UTF-8 -*-
'''
Created on 28.4.2012

@author: marko
'''
from Plugins.Extensions.archivCZSK import _
from Screens.Screen import Screen
from Components.Button import Button
from Components.Label import Label, MultiColorLabel
from Screens.MessageBox import MessageBox
from enigma import loadPNG, RT_HALIGN_RIGHT, RT_VALIGN_TOP, eSize, eListbox, ePoint, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont, getDesktop, ePicLoad, eServiceCenter, iServiceInformation, eServiceReference, iSeekableService, iPlayableService, iPlayableServicePtr
from Components.ActionMap import ActionMap, NumberActionMap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.MenuList import MenuList
from Tools.Directories import resolveFilename, pathExists, fileExists


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

class ShortcutsScreen(Screen):
	skin = """
			<screen position="center,center" size="610,435" title="Shortcuts" >
				<widget name="key_red" position="10,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
				<widget name="key_green" position="160,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
				<widget name="key_yellow" position="310,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
				<widget name="key_blue" position="460,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
				<eLabel position="-1,55" size="612,1" backgroundColor="#999999" />
				<widget name="menu" position="0,55" size="610,350" scrollbarMode="showOnDemand" />
				<widget name="xml" position="10,415" size="590,25" zPosition="2" valign="left" halign="center" font="Regular;20" transparent="1" foregroundColor="white" />
			</screen>"""
			
	def __init__(self, session, archive):
		Screen.__init__(self, session)
		self.session = session
		self["key_red"] = Button(_("Remove shortcut"))
		self["key_green"] = Button("")
		self["key_yellow"] = Button("")
		self["key_blue"] = Button("")
		self["menu"] = PanelList([])
		self["xml"] = Label("")
		self.onShown.append(self.setWindowTitle)
		self.working = False
		self.archive = archive
		self.lst_items = self.archive.getShortcuts()
		self.title = _("Shortcut") + ' ' + archive.name.encode('utf-8')

		self["actions"] = NumberActionMap(["archivCZSKActions"],
			{
				"ok": self.okClicked,
				"cancel": self.exit,
				"red": self.askRemoveShortcut,
				"up": self.up,
				"down": self.down,
			}, -2)
			
		self.onLayoutFinish.append(self.updateGUI)

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

	def okClicked(self):
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
