# -*- coding: UTF-8 -*-
'''
Created on 28.4.2012

@author: marko
'''
import os
from twisted.web.client import downloadPage

from Components.Label import Label
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from Screens.MessageBox import MessageBox
from Components.AVSwitch import AVSwitch
from enigma import ePicLoad, getDesktop

from base import BaseArchivCZSKScreen
from Plugins.Extensions.archivCZSK import _

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


class ChangelogScreen(BaseArchivCZSKScreen):
	def __init__(self, session, title, text=None):
		BaseArchivCZSKScreen.__init__(self, session)
		self.changelog = text
		self.title = title
		
		if self.changelog is not None:
			self["changelog"] = ScrollLabel(self.changelog.encode('utf-8'))
		else:
			self["changelog"] = ScrollLabel('')
				
		self["actions"] = NumberActionMap(["archivCZSKActions"],
		{
			"cancel": self.close,
			"up": self.pageUp,
			"down": self.pageDown,
		}, -2)	
		self.title = self.title.encode('utf-8') + ' changelog'
	
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
			self.imagelink = it.image.encode('utf-8')
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
		self.session.openWithCallback(self.closeInfo, InfoScreen, self.it)

class InfoScreen(BaseArchivCZSKScreen):
	def __init__(self, session, it):
		BaseArchivCZSKScreen.__init__(self, session)
		self.image_link = None
		self.it = it
		self.image_dest = None
		if it.image is not None:
			self.image_link = it.image.encode('utf-8')
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
		self.title = self.it.name.encode('utf-8')
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

		
