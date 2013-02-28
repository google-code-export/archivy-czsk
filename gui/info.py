# -*- coding: UTF-8 -*-
'''
Created on 28.4.2012

@author: marko
'''
import os
from twisted.web.client import downloadPage

from Components.Label import Label, MultiColorLabel
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Components.AVSwitch import AVSwitch
from Components.config import config
from enigma import ePicLoad, getDesktop

from base import BaseArchivCZSKScreen
from Plugins.Extensions.archivCZSK import _, settings
from Plugins.Extensions.archivCZSK.gui.common import showYesNoDialog, showInfoMessage, PanelColorListEntry, PanelList
from Plugins.Extensions.archivCZSK.engine.player.info import videoPlayerInfo

def showChangelog(session, changelog_title, changelog_text):
	session.open(ChangelogScreen, changelog_title, changelog_text)

def showItemInfo(session, item):
	Info(session, item)
	
def showCSFDInfo(session, name):
	try:
		from Plugins.Extensions.CSFD.plugin import CSFD
	except ImportError:
		showInfo(session, _("Plugin CSFD is not installed."))
	else:
		session.open(CSFD, name, False)
	
def showInfo(session, text):
	session.open(MessageBox, text=text, type=MessageBox.TYPE_INFO, timeout=5)
	
	
def showVideoPlayerInfo(session, cb=None):
	if cb:
		session.openWithCallback(cb, VideoPlayerInfoScreen)
	else:
		session.open(VideoPlayerInfoScreen)


class ChangelogScreen(BaseArchivCZSKScreen):
	def __init__(self, session, title, text=None):
		BaseArchivCZSKScreen.__init__(self, session)
		self.changelog = text
		self.title = title
		
		if self.changelog is not None:
			self["changelog"] = ScrollLabel(self.changelog.encode('utf-8', 'ignore'))
		else:
			self["changelog"] = ScrollLabel('')
				
		self["actions"] = NumberActionMap(["archivCZSKActions"],
		{
			"cancel": self.close,
			"up": self.pageUp,
			"down": self.pageDown,
		}, -2)	
		self.title = self.title.encode('utf-8', 'ignore') + ' changelog'
	
	def pageUp(self):
		self["changelog"].pageUp()

	def pageDown(self):
		self["changelog"].pageDown()


class Info(object):
	def __init__(self, session, it):
		self.session = session
		self.it = it
		self.dest = ''
		self.imagelink = ''
		if it.image is not None:
			self.imagelink = it.image.encode('utf-8', 'ígnore')
			self.dest = os.path.join('/tmp/', self.imagelink.split('/')[-1])

			if os.path.exists(self.dest):
				self.showInfo()
			else:
				self.downloadPicture()
		else:
			self.showInfo()
		
	def downloadPicture(self):
		print '[Info] downloadPicture'
		print '[Info]', self.imagelink, self.dest
		downloadPage(self.imagelink, self.dest).addCallback(self.downloadPictureCallback).addErrback(self.downloadPictureErrorCallback)
		
	def downloadPictureCallback(self, txt=""):
		print '[Info] picture was succesfully downloaded'
		self.showInfo()
		
	def downloadPictureErrorCallback(self, err):
		print '[Info] picture was not succesfully downloaded', err
		self.showInfo()
		
	def closeInfo(self):
		print '[Info] closeInfo'
		
	def showInfo(self):
		print '[Info] showInfo'
		self.session.openWithCallback(self.closeInfo, ItemInfoScreen, self.it)

class ItemInfoScreen(BaseArchivCZSKScreen):
	def __init__(self, session, it):
		BaseArchivCZSKScreen.__init__(self, session)
		self.image_link = None
		self.it = it
		self.image_dest = None
		if it.image is not None:
			self.image_link = it.image.encode('utf-8', 'ignore')
			self.image_dest = os.path.join('/tmp/', self.image_link.split('/')[-1])
		self.plot = ''
		self.genre = ''
		self.rating = ''
		self.year = ''
		
		for key, value in it.info.iteritems():		
			if key == 'Plot' or key == 'plot':
				self.plot = value.encode('utf-8', 'ignore')
			if key == 'Genre' or key == 'genre':
				self.genre = value.encode('utf-8', 'ignore')
			if key == 'Rating' or key == 'rating':
				self.rating = value.encode('utf-8', 'ignore')
			if key == 'Year' or key == 'year':
				self.year = value.encode('utf-8', 'ignore')
			
		self["img"] = Pixmap()
		self["genre"] = Label(_("Genre: ") + self.genre)
		self["year"] = Label(_("Year: ") + self.year)
		self["rating"] = Label(_("Rating: ") + self.rating)
		self["plot"] = ScrollLabel(self.plot)
			
		self["actions"] = NumberActionMap(["archivCZSKActions"],
		{
			"cancel": self.close,
			"up": self.pageUp,
			"down": self.pageDown,
		}, -2)	
		self.title = self.it.name.encode('utf-8', 'ignore')
		self.Scale = AVSwitch().getFramebufferScale()
		self.picLoad = ePicLoad()
		self.picLoad.PictureData.get().append(self.decodePicture)
		self.onLayoutFinish.append(self.showPicture)
	
	def pageUp(self):
		self["plot"].pageUp()

	def pageDown(self):
		self["plot"].pageDown()
		
	def showPicture(self):
		if self.image_dest is not None:
			self.picLoad.setPara([self["img"].instance.size().width(), self["img"].instance.size().height(), self.Scale[0], self.Scale[1], 0, 1, "#002C2C39"])
			self.picLoad.startDecode(self.image_dest)

	def decodePicture(self, PicInfo=""):
		ptr = self.picLoad.getData()
		self["img"].instance.setPixmap(ptr)
		
		
		
class VideoPlayerInfoScreen(BaseArchivCZSKScreen):
	GST_INSTALL = 0
	GST_INSTALL_OPENPLI = 1
	GST_REINSTALL = 2
	
	WIDTH_HD = 355
	WIDTH_SD = 200
	
	def __init__(self, session):
		BaseArchivCZSKScreen.__init__(self, session)
		self.__settings = config.plugins.archivCZSK.videoPlayer
		self.selectedInstallType = self.GST_INSTALL
		# initialize GUI
		self["key_red"] = Label(_("Install GStreamer libraries"))
		self["key_green"] = Label(_("Install GStreamer libraries (Openpli feeds)"))
		self["key_yellow"] = Label(_("Re-Install GStreamer libraries"))
		self["key_blue"] = Label(_("Refresh"))
		
		self["detected player"] = Label(_("Detected player:"))
		self["detected player_val"] = Label("")
		
		self["protocol"] = Label(_("Supported protocols:"))
		self["protocol_list"] = PanelList([])
		#self["protocol_list_info"] = PanelList([])
		self["container"] = Label(_("Supported containers:"))
		self["container_list"] = PanelList([])
		#self["container_list_info"] = PaneList([])
		self["info_scrolllabel"] = ScrollLabel()
			
		self["actions"] = NumberActionMap(["archivCZSKActions"],
		{
			#"up": self["info_scrolllabel"].up(),
			#"down": self["info_scrolllabel"].down(),
			"right": self.pageDown,
			"left": self.pageUp,
			"cancel":self.close,
			"blue": self.updateGUI,
			"yellow": self.askReinstallGstPlugins,
			"red": self.askInstallGstPlugins,
			"green": self.askInstallGstPluginsOpenpli,
		}, -2)
		
		self.onShown.append(self.setWindowTitle)
		self.onLayoutFinish.append(self.disableSelection)
		self.onLayoutFinish.append(self.setPlayer)
		self.onLayoutFinish.append(self.setInfo)
		self.onLayoutFinish.append(self.updateGUI)
	
	def setWindowTitle(self):
		self.title = _("VideoPlayer Info")
		
	def disableSelection(self):
		self["container_list"].selectionEnabled(False)
		self["protocol_list"].selectionEnabled(False)
		
	def updateGUI(self):
		self.updateProtocolList()
		self.updateContainerList()
		
	def setPlayer(self):
		self["detected player_val"].setText(videoPlayerInfo.getName())
		
	def setInfo(self):
		info = _("""* If some of the tests FAIL you should try to install Gstreamer plugins in following order:
1. Press Red, If it doesnt help go to point 2
2. Press Green, If it doesnt help go to point 3
3. Press Yellow\n\n
* Status UNKNOWN means, that I dont know how to get info, it doesnt meant that protocol/container isn't supported.\n
* Videos are encoded by various codecs, to play them you need to have HW support of your receiver to decode them.\n
For example if you have ASF(WMV) - OK state, it doesnt already mean that you can play WMV file, it just means that player
can open WMV container and get ENCODED video out of it. In WMV container is used VC1 encoded video. IF your player cannot decode VC1 codec, than you cannot play this video.""")
		
		self["info_scrolllabel"].setText(info)
		
	def updateProtocolList(self):
		menu_list = []
		width = self.WIDTH_HD
		if not self.HD:
			width = self.WIDTH_SD
		menu_list.append(self.buildEntry(_("HTTP Protocol"), videoPlayerInfo.isHTTPSupported(), width))
		menu_list.append(self.buildEntry(_("MMS Protocol"), videoPlayerInfo.isMMSSupported(), width))
		menu_list.append(self.buildEntry(_("RTMP Protocol"), videoPlayerInfo.isRTMPSupported(), width))
		menu_list.append(self.buildEntry(_("RTSP Protocol"), videoPlayerInfo.isRTSPSupported(), width))
		self["protocol_list"].setList(menu_list)
		
	def updateContainerList(self):
		menu_list = []
		width = self.WIDTH_HD
		if not self.HD:
			width = self.WIDTH_SD
		menu_list.append(self.buildEntry(_("3GP container"), videoPlayerInfo.isMP4Supported(), width))
		menu_list.append(self.buildEntry(_("ASF(WMV) Container"), videoPlayerInfo.isASFSupported(), width))
		menu_list.append(self.buildEntry(_("AVI Container"), videoPlayerInfo.isAVISupported(), width))
		menu_list.append(self.buildEntry(_("FLV Container"), videoPlayerInfo.isFLVSupported(), width))
		menu_list.append(self.buildEntry(_("MKV Container"), videoPlayerInfo.isMKVSupported(), width))
		menu_list.append(self.buildEntry(_("MP4 Container"), videoPlayerInfo.isMP4Supported(), width))
		self["container_list"].setList(menu_list)

		
	def buildEntry(self, name, res, width):
		if res is None:
			return PanelColorListEntry(name, _("UNKNOWN"), 0xffff00, width)
		elif res:
			return PanelColorListEntry(name, _("OK"), 0x00ff00, width)
		else:
			return PanelColorListEntry(name, _("FAIL"), 0xff0000, width)
		
	def pageUp(self):
		self["info_scrolllabel"].pageUp()

	def pageDown(self):
		self["info_scrolllabel"].pageDown()
		
	
	def askReinstallGstPlugins(self):
		if settings.ARCH != 'mipsel' :
			showInfoMessage(self.session, _("You can only install this plugins on mipsel platform"))
		else:
			self.selectedInstallType = self.GST_REINSTALL
			showYesNoDialog(self.session, _("Do you want to re-install gstreamer plugins?"), self.installGstPlugins)
	
	
	def askInstallGstPluginsOpenpli(self):
		if settings.ARCH != 'mipsel' :
			showInfoMessage(self.session, _("You can only install this plugins on mipsel platform"))
		else:
			self.selectedInstallType = self.GST_INSTALL_OPENPLI
			showYesNoDialog(self.session, _("Do you want to install gstreamer plugins by using openpli feed?"), self.installGstPlugins)
	
	
	def askInstallGstPlugins(self):
		if settings.ARCH != 'mipsel' :
			showInfoMessage(self.session, _("You can only install this plugins on mipsel platform"))
		else:
			self.selectedInstallType = self.GST_INSTALL
			showYesNoDialog(self.session, _("Do you want to install gstreamer plugins?"), self.installGstPlugins)
		
	def installGstPlugins(self, callback=None):
		if callback:
			scriptPath = os.path.join(settings.PLUGIN_PATH, 'script/gst-plugins-archivczsk.sh')
			if self.selectedInstallType == self.GST_INSTALL_OPENPLI:
				params = " N openpli"
			elif self.selectedInstallType == self.GST_INSTALL:
				params = " N"
			elif self.selectedInstallType == self.GST_REINSTALL:
				params = " A"
			cmdList = [scriptPath + params]
			self.session.openWithCallback(self.installGstPluginsCB, Console, cmdlist=cmdList)
		
	def installGstPluginsCB(self, callback=None):
		self.updateGUI()
		self.updatePlayerSettings()
		
	def updatePlayerSettings(self):
		if videoPlayerInfo.isRTMPSupported():
			self.__settings.seeking.setValue(True)
			self.__settings.seeking.save()
			
			
		
				
		
		
	
	

		
