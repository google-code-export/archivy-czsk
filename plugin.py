# -*- coding: UTF-8 -*-
'''
Created on 28.2.2012

@author: marko
'''
import os, traceback

from . import _
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.PluginBrowser import *
from Components.PluginComponent import plugins
from Components.config import config

from gui.archive import ArchiveScreen
import gui.download as dwnld
import resources.tools.updater as updater
import resources.archives as archive_modul
from resources.tools.contentprovider import Archive, DmdArchive, DoplnkyArchive
from resources.tools.downloader import DownloadManager
from resources.archives import config as archive_cfg
import version





def sessionstart(reason, session):
	dwnld.setGlobalSession(session)
	#saving active downloads to session
	if not hasattr(session, 'archivCZSKdownloads'):
		session.archivCZSKdownloads = []	
	if DownloadManager.getInstance() is None:
		DownloadManager(session.archivCZSKdownloads)

def loadArchives():
	_pluginPath = "/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/"
	archives = archive_cfg.archives
	arch_dict = {}
	tv_archives = []
	video_archives = []
	for archs_dir in archives:
		for arch_dir in os.listdir(archs_dir):
			if arch_dir in ['tools', '__init__.py', '__init__.pyc', '__init__.pyo']:
				continue
			print 'import Plugins.Extensions.archivCZSK.resources.archives.%s.%s' % (archs_dir.split('/')[-1], arch_dir)
			exec 'import Plugins.Extensions.archivCZSK.resources.archives.%s.%s.%s' % (archs_dir.split('/')[-1], arch_dir, 'default')
			md = getattr(archive_modul, archs_dir.split('/')[-1])
			mm = getattr(md, arch_dir)
			modul = getattr(mm, 'default')
			
			if arch_dir in archive_cfg.dmd:
				archive = DmdArchive(modul)
			elif arch_dir == 'streamy':
				archive = Archive(modul)
			elif arch_dir in archive_cfg.doplnky:
				archive = DoplnkyArchive(modul)
				
			if archive.id in archive_cfg.tv_archives:
				tv_archives.append(archive)
			elif archive.id in archive_cfg.video_archives:
				video_archives.append(archive)	 
				
			arch_dict[archive.id] = archive 
			
	tv_archives.sort()
	video_archives.sort()
	
	return arch_dict, tv_archives, video_archives

archive_dict, tv_archives, video_archives = loadArchives()

class ArchivCZSK():

	def __init__(self, session):
		self.session = session
		self.toolsUpdate = []
		self.archivesUpdate = []
		self.newArchivesUpdate = []
		
		#if config.plugins.archivCZSK.autoUpdate.value:
			#self.checkUpdates()
		#else:
		self.openArchiveScreen()

	def checkUpdates(self):
		self.archivesUpdate, self.toolsUpdate , self.newArchivesUpdate = updater.checkArchiveVersions(tv_archives + video_archives)
			
		archivesUpdateString = ' '.join([arch.name for arch in self.archivesUpdate])
		newArchivesUpdateString = ' '.join([arch.name for arch in self.newArchivesUpdate])
		toolsUpdateString = ' '.join(s['name'] for s in self.toolsUpdate)
			
		updateString = archivesUpdateString + ' ' + newArchivesUpdateString + ' ' + toolsUpdateString + '?'
			
		if len(self.archivesUpdate) > 0 or len(self.newArchivesUpdate) > 0 or len(self.toolsUpdate) > 0:
			self.session.openWithCallback(self.updateArchives, MessageBox, _('Do you want to update/add archives/tools: ') + updateString.encode('utf-8'), type=MessageBox.TYPE_YESNO)

		else:
			self.openArchiveScreen()   

	def updateArchives(self, answer=None):
		if answer:
			archivesUpdateInfo = updater.updateArchives(self.archivesUpdate + self.newArchivesUpdate)
			toolsUpdateInfo = updater.updateArchiveTools(self.toolsUpdate)
			if archivesUpdateInfo != '' or toolsUpdateInfo != '':
				self.showInfoRestart(_('Following items were successfully updated:') + ' ' + archivesUpdateInfo.encode('utf-8') + ' ' + toolsUpdateInfo.encode('utf-8'))
			else:
				self.showError(_('Problems appeared during updating, try again later...'))
		else:
			self.openArchiveScreen()

	def openArchiveScreen(self, callback=None):
		self.session.open(ArchiveScreen, tv_archives, video_archives, archive_dict)
		
	def askE2Restart(self, callback=None):
		self.session.openWithCallback(self.restartGUI, MessageBox, _('The changes will appear after restart of E2. Do you want to restart E2 now? '), type=MessageBox.TYPE_YESNO)

	def restartGUI(self, answer):
		if answer is True:
			from Screens.Standby import TryQuitMainloop
			self.session.open(TryQuitMainloop, 3)
		else:
			self.openArchiveScreen()
	
	def showInfoRestart(self, info):
		self.session.openWithCallback(self.askE2Restart, MessageBox, _(info), type=MessageBox.TYPE_INFO, timeout=3)
	
	def showError(self, info):
		self.session.openWithCallback(self.openArchiveScreen, MessageBox, _(info), type=MessageBox.TYPE_ERROR, timeout=3)

def menu(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(version.title, main, "mainmenu", 32)]
	else:
		return []

def main(session, **kwargs):
	ArchivCZSK(session)

def startSetup(menuid, **kwargs):
	if menuid == "mainmenu":
		return [(version.description, main, "archivy_czsk", 32)]
	return []

def Plugins(path, **kwargs):
	descr = version.description
	nameA = version.title
	list = [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart), PluginDescriptor(name=nameA, description=descr, where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main, icon="czsk.png"), ]
	if config.plugins.archivCZSK.extensions_menu.value:
		list.append(PluginDescriptor(name=nameA, description=descr, where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main))
	if config.plugins.archivCZSK.main_menu.value:
		list.append(PluginDescriptor(name=nameA, description=descr, where=PluginDescriptor.WHERE_MENU, fnc=startSetup))
	return list
