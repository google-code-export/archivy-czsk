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
from engine.downloader import DownloadManager
import version

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


if config.plugins.archivCZSK.preload.getValue() and not ArchivCZSK.isLoaded():
	ArchivCZSK.load_repositories()
