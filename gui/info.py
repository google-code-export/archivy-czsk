# -*- coding: UTF-8 -*-
'''
Created on 28.4.2012

@author: marko
'''
from Plugins.Extensions.archivCZSK import _
from Screens.Screen import Screen
from Components.Label import Label
from Components.ActionMap import ActionMap, NumberActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from Screens.MessageBox import MessageBox
from Components.AVSwitch import AVSwitch
from enigma import ePicLoad, getDesktop
from twisted.web.client import downloadPage
import os

class ChangelogScreen(Screen):
	skin = """
			<screen position="center,center" size="720,576" title="Info" >
				<widget name="changelog" position="0,0" size="720,576" font="Regular;23" transparent="1" foregroundColor="white" />
			</screen>"""

	def __init__(self, session, archive):
		Screen.__init__(self, session)
		self.changelog = archive.changelog
		self.title = archive.name
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
	def __init__(self, session, it, callback):
		self.session = session
		self.it = it
		self.callback = callback
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
		self.callback()
		
	def showInfo(self):
		print '[Info] showInfo'
		self.session.openWithCallback(self.closeInfo, InfoScreen, self.it)

class InfoScreen(Screen):
	skin = """
			<screen position="center,center" size="720,576" title="Info" >
				<widget name="genre" position="320,50" size="400,30" font="Regular;22" transparent="1" foregroundColor="yellow" />
				<widget name="year" position="320,90" size="400,30" font="Regular;22" transparent="1" foregroundColor="yellow" />
				<widget name="rating" position="320,130" size="400,30" font="Regular;22" transparent="1" foregroundColor="yellow" />
				<widget name="plot" position="0,310" size="720,306" font="Regular;23" transparent="1" foregroundColor="white" />
				<widget name="img" position="10,0" zPosition="2" size="300,300"  alphatest="on"/>
			</screen>"""

	def __init__(self, session, it):
		Screen.__init__(self, session)
		self.session = session
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

		
