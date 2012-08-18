# -*- coding: UTF-8 -*-
'''
Created on 20.3.2012

@author: marko
'''
from Plugins.Extensions.archivCZSK import _
from Plugins.Extensions.archivCZSK.gui.download import DownloadList
from enigma import  eServiceCenter, iServiceInformation, eServiceReference, iSeekableService, iPlayableService, iPlayableServicePtr, eAVSwitch
from Components.ServiceEventTracker import ServiceEventTracker
from Components.ActionMap import HelpableActionMap
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.config import config, ConfigInteger, ConfigSubsection
from Screens.InfoBar import MoviePlayer
from subprocess import Popen, PIPE, STDOUT
from subtitles import Subtitles

RTMP_LIVE_BUFFER = config.plugins.archivCZSK.liveBuffer.getValue()	#3000 #(ms) buffer pre live streamy
RTMP_ARCHIVE_BUFFER = config.plugins.archivCZSK.archiveBuffer.getValue() # 5000 #(ms) buffer pre archivy
ENIGMA_BUFFER = 512
aspectratiomode = "1"


class BasePlayer(MoviePlayer, DownloadList):
	instance = None
	def __init__(self, session, sref):
		BasePlayer.instance = self
		MoviePlayer.__init__(self, session, sref)
		DownloadList.__init__(self)
		self.skinName = "MoviePlayer"   
		self.onClose.append(self.__onClose)
		
	def __onClose(self):
		BasePlayer.instance = None
	

class StandardPlayer(BasePlayer):
	instance = None
	def __init__(self, session, sref):
		BasePlayer.__init__(self, session, sref)


class CustomPlayer(BasePlayer):
	instance = None
	def __init__(self, session, sref, subfile=None):
		CustomPlayer.instance = self
		self.session = session
		self.subs = False
		self.subtitles = Subtitles(self.session, subfile)

		BasePlayer.__init__(self, session, sref)
		self["actions"] = HelpableActionMap(self, "CustomPlayerActions",
            {
                "aspectChange": (self.aspectratioSelection, _("changing aspect Ratio")),
                "subtitles": (self.subsetup, _("show/hide subtitles")),
                "leavePlayer": (self.leavePlayer, _("leave player?"))
            }, 0)    
		self.subtitles.play()		 
		
	def doSeekRelative(self, pts):
		super(CustomPlayer, self).doSeekRelative(pts)
		self.subtitles.playAfterRewind()

	def pauseService(self):
		super(CustomPlayer, self).pauseService()
		self.subtitles.pause()

	def unPauseService(self):
		super(CustomPlayer, self).unPauseService()
		self.subtitles.resume()
	
	def aspectratioSelection(self):
		global aspectratiomode
		if aspectratiomode == "1": #letterbox
			eAVSwitch.getInstance().setAspectRatio(0)
			aspectratiomode = "2"
		elif aspectratiomode == "2": #nonlinear
			eAVSwitch.getInstance().setAspectRatio(4)
			aspectratiomode = "3"
		elif aspectratiomode == "2": #nonlinear
			eAVSwitch.getInstance().setAspectRatio(2)
			aspectratiomode = "3"
		elif aspectratiomode == "3": #panscan
			eAVSwitch.getInstance().setAspectRatio(3)
			aspectratiomode = "1"

	def subsetup(self):
		self.subtitles.setup() 

	def handleLeave(self, how):
		self.exitbox(True)  
		
	def doEofInternal(self, playing):
		self.exitbox(True)
			
	def leavePlayerConfirmed(self, answer):
		self.exitbox(True)
		
	def leavePlayer(self):
		self.session.openWithCallback(self.exitbox, MessageBox, _("Do you want to exit player?"), type=MessageBox.TYPE_YESNO)
		
	def exitbox(self, message=None):
		if message:
			if hasattr(self, 'subtitles'):
				self.subtitles.exit()
				del self.subtitles
			self.setSeekState(self.SEEK_STATE_PLAY)
			self.close()
		
class MipselPlayer(CustomPlayer):
	def __init__(self, session, sref, subfile=None):
		self.session = session
		self.bufferSeconds = 0
		self.bufferPercent = 0
		self.bufferSecondsLeft = 0
		self.autoPlay = config.plugins.archivCZSK.mipselPlayer.autoPlay.value
		CustomPlayer.__init__(self, session, sref)
		session.nav.getCurrentService().streamed().setBufferSize(config.plugins.archivCZSK.mipselPlayer.buffer.value)
		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
            {
                iPlayableService.evBuffering: self.__evUpdatedBufferInfo,
                
            })	 
		
	#buffer from airplayer	
	def __evUpdatedBufferInfo(self):
		bufferInfo = self.session.nav.getCurrentService().streamed().getBufferCharge()
		if bufferInfo[2] != 0:
			self.bufferSeconds = bufferInfo[4] / bufferInfo[2] #buffer size / avgOutRate
		else:
			self.bufferSeconds = 0
		self.bufferPercent = bufferInfo[0]
		self.bufferSecondsLeft = self.bufferSeconds * self.bufferPercent / 100
		if(self.bufferPercent > 90):
				self.bufferFull()
		if(self.bufferPercent < 3):
				self.bufferEmpty()
		print "Buffer", bufferInfo[4], "Info ", bufferInfo[0], "% filled ", bufferInfo[1], "/", bufferInfo[2], " buffered: ", self.bufferSecondsLeft, "s"
	
	def bufferFull(self):
		if self.autoPlay:
			if self.seekstate != self.SEEK_STATE_PLAY :
				self.setSeekState(self.SEEK_STATE_PLAY)

	def bufferEmpty(self):
		if self.autoPlay:
			if self.seekstate != self.SEEK_STATE_PAUSE :
				self.setSeekState(self.SEEK_STATE_PAUSE)
				
	def exitbox(self, message=None):
		if message:
			if hasattr(self, 'subtitles'):
				self.subtitles.exit()
				del self.subtitles
			#self.setSeekState(self.SEEK_STATE_PLAY)
			self.close()
	
			
class Player():
	"""Player for playing it content"""
	instance = None
	def __init__(self, session, it, callback=None, downloadCB=None):
		Player.instance = self
		self.videoController = None
		self.it = it
		self.session = session
		self.name = it.name
		self.port = 8902 #streaming port for rtmpgw
		self.ebuff = int(ENIGMA_BUFFER) #buffer for gstreamer/libeplayer if supported
		self.live = it.live #if stream is live
		self.streamObj = None
		self.callback = callback
		self.downloadCB = downloadCB
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.subs = it.subs

		if self.live:
			self.rtmpBuffer = RTMP_LIVE_BUFFER
			#self.timeBuffer = int(RTMP_LIVE_RECORD_BUFFER)
		else:
			self.rtmpBuffer = RTMP_ARCHIVE_BUFFER
			#self.timebuff = int(RTMP_ARCHIVE_RECORD_BUFFER)
		
		if it.rtmpBuffer is not None:
			self.rtmpBuffer = it.rtmpBuffer
		#if it.timebuff is not None:
		#	self.timebuff = int(it.timebuff)
		if self.live:
			self.streamObj = it.stream
				
		self.url = it.url		
		self.rtmpproc = None
		
	def isPortFree(self):
		"""Finds out if streaming port for rmtpgw is free"""
		netstat = Popen(['netstat', '-tulna'], stderr=STDOUT, stdout=PIPE)
		out, err = netstat.communicate()
		if str(self.port) in out:
			return False
		return True		

	def createRTMPAddress(self):
		cmd = self.url.split()
		address = ' --'.join(cmd[0:])
		return address
	
	
	def createRTMPGwProcessLive(self):
		cmd = []
		cmd.append('/usr/bin/rtmpgw')
		cmd.append('-q')
		cmd.append('-r')
		cmd.append('%s' % self.streamObj.url)
		cmd.append('-W')
		cmd.append('%s' % self.streamObj.swfUrl)
		cmd.append('-p')
		cmd.append('%s' % self.streamObj.pageUrl)
		cmd.append('-y')
		cmd.append('%s' % self.streamObj.playpath)
		cmd.append('--live')
		cmd.append('--sport')
		cmd.append(str(self.port))
		cmd.append('--buffer')
		cmd.append(str(self.rtmpBuffer))
		print cmd
		self.rtmpproc = Popen(cmd, shell=False)
		
	def createRTMPGwProcess(self, url):
			cmd = '/usr/bin/rtmpgw -q -r ' + str(url) + ' --buffer ' + str(self.rtmpBuffer) + ' --sport ' + str(self.port)
			print cmd
			self.rtmpproc = Popen(cmd.split(), shell=False)
			return 0	
		
	def stop(self):
		self.videoController.exitbox(True)
		

	def play(self, subs=None):
		url = self.url
		self.timeoutbool = False
		self.iter = 0
		if self.rtmpproc is not None:
			self.rtmpproc.terminate()
			self.rtmpproc.wait()
			self.rtmpproc = None	
			
		self.session.nav.stopService()
		
		if url[0:4] == 'rtmp':
			
			if  not self.isPortFree():
				self.port += 1
				
			if self.live: 
				if config.plugins.archivCZSK.seeking.value:
					self.playStream(str(url + ' buffer= ' + self.rtmpBuffer), self.subs)
				else:
					self.createRTMPGwProcessLive()
					self.playStream('http://0.0.0.0:' + str(self.port), self.subs)	
			else:
				if config.plugins.archivCZSK.seeking.value: 
					self.playStream(str(url + ' buffer= ' + self.rtmpBuffer), self.subs)
					print url
				else:
					self.createRTMPGwProcess(self.createRTMPAddress())
					self.playStream('http://0.0.0.0:' + str(self.port), self.subs)		
		else:
			self.playStream(str(url), self.subs)
			
			
	def playStream(self, streamURL, subs=None):
		#sref.setData(2, int(int(config.plugins.archivCZSK.playerBuffer.value) * 1024))
		sref = eServiceReference(4097, 0, streamURL)
		#sref.setName(self.name.encode('utf-8'))
		
		if config.plugins.archivCZSK.player.value == 'custom':
			self.session.openWithCallback(self.exit, CustomPlayer, sref, subs)
			self.videoController = CustomPlayer.instance
			
		elif config.plugins.archivCZSK.player.value == 'standard':
			self.session.openWithCallback(self.exit, StandardPlayer, sref)
			self.videoController = StandardPlayer.instance
			
		elif config.plugins.archivCZSK.player.value == 'mipsel':
			self.session.openWithCallback(self.exit, MipselPlayer, sref, subs)
			self.videoController = MipselPlayer.instance

	def exit(self):
		if self.rtmpproc is not None:
			self.rtmpproc.terminate()
			self.rtmpproc.wait()
			self.rtmpproc = None    
		self.session.nav.playService(self.oldService)
		if self.callback:
			self.callback()
		if self.downloadCB:
			self.downloadCB(self.it)
