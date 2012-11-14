# -*- coding: UTF-8 -*-
'''
Created on 28.2.2012

@author: marko
'''
import os, traceback

from Plugins.Plugin import PluginDescriptor
from Screens.PluginBrowser import *
from Components.PluginComponent import plugins
from Components.config import config

import gui.download as dwnld
from archivczsk import ArchivCZSK
from engine.repository import Repository
from engine.downloader import DownloadManager
import version
import settings

# loading repositories and their addons

print '[ArchivCZSK] looking for repositories in %s' % settings.REPOSITORY_PATH
for repo in os.listdir(settings.REPOSITORY_PATH):
	repo_path = os.path.join(settings.REPOSITORY_PATH, repo)
	if os.path.isfile(repo_path):
		continue
	print '[ArchivCZSK] founded repository %s' % repo
	repo_xml = os.path.join(repo_path, 'addon.xml')
	try:
		repository = Repository(repo_xml)
	except Exception:
		traceback.print_exc()
		print '[ArchivCZSK] cannot load repository %s' % repo
		print "[ArchivCZSK] skipping"
		continue
	else:
		ArchivCZSK.add_repository(repository)
	

def sessionstart(reason, session):
	dwnld.setGlobalSession(session)
	#saving active downloads to session
	if not hasattr(session, 'archivCZSKdownloads'):
		session.archivCZSKdownloads = []	
	if DownloadManager.getInstance() is None:
		DownloadManager(session.archivCZSKdownloads)

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
	if config.plugins.archivCZSK.extensions_menu.getValue():
		list.append(PluginDescriptor(name=nameA, description=descr, where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main))
	if config.plugins.archivCZSK.main_menu.getValue():
		list.append(PluginDescriptor(name=nameA, description=descr, where=PluginDescriptor.WHERE_MENU, fnc=startSetup))
	return list
