# -*- coding: UTF-8 -*-
'''
Created on 20.3.2012

@author: marko
'''
import logging
import os
from subprocess import Popen, PIPE, STDOUT
from subtitles import Subtitles

from enigma import  eServiceCenter, iServiceInformation, eServiceReference, iSeekableService, iPlayableService, iPlayableServicePtr, eAVSwitch, eConsoleAppContainer
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InfoBar import MoviePlayer
from Components.ServiceEventTracker import ServiceEventTracker
from Components.ActionMap import HelpableActionMap
from Components.config import config, ConfigInteger, ConfigSubsection

from Plugins.Extensions.archivCZSK import _
from Plugins.Extensions.archivCZSK.gui.download import DownloadList

DEFAULT_LOGGING_LEVEL = 'INFO' #logging.INFO
DEFAULT_LOGGING_FORMAT = '%(levelname)s: %(message)s'
log = logging.getLogger(__name__)
log.setLevel('DEBUG')

aspectratiomode = "1"
RTMPGW_PATH = '/usr/bin/rtmpgw'
NETSTAT_PATH = 'netstat'


class BasePlayer(MoviePlayer, DownloadList):
	def __init__(self, session, sref, seekable=True, pausable=True):
		self.seekable = seekable
		self.pausable = pausable
		MoviePlayer.__init__(self, session, sref)
		DownloadList.__init__(self)
		
		self.skinName = "MoviePlayer"   
		self.onClose.append(self.__onClose)
		
	def __getSeekable(self):
		service = self.session.nav.getCurrentService()
		if service is None:
			return None
		return service.seek()

	def getCurrentPosition(self):
		seek = self.__getSeekable()
		if seek is None:
			return None
		r = seek.getPlayPosition()
		if r[0]:
			return None
		return long(r[1])

	def getCurrentLength(self):
		seek = self.__getSeekable()
		if seek is None:
			return None
		r = seek.getLength()
		if r[0]:
			return None
		return long(r[1])
	
	def isSeekable(self):
		if self.seekable:
			return super(BasePlayer, self).isSeekable()
		return None
	
	def __onClose(self):
		pass
	

class StandardPlayer(BasePlayer):
	instance = None
	def __init__(self, session, sref):
		BasePlayer.__init__(self, session, sref)
		StandardPlayer.instance = self
		
	def __onClose(self):
		StandardPlayer.instance = None


class CustomPlayer(BasePlayer):
	instance = None
	def __init__(self, session, sref, subtitles=None):
		CustomPlayer.instance = self
		BasePlayer.__init__(self, session, sref)
		self.session = session
		self.subtitles = Subtitles(self.session, subtitles)
		self["actions"] = HelpableActionMap(self, "CustomPlayerActions",
            {
                "aspectChange": (self.aspectratioSelection, _("changing aspect Ratio")),
                "subtitles": (self.subtitlesSetup, _("show/hide subtitles")),
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
	
	def subtitlesSetup(self):
		self.subtitles.setup() 
	
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

	def handleLeave(self, how):
		self.is_closing = True
		self.exitVideoPlayer(True)
		
	def doEofInternal(self, playing):
		if not self.execing:
			return
		if not playing :
			return
		self.handleLeave(None)  
			
	def leavePlayerConfirmed(self, answer):
		self.exitVideoPlayer(True)
		
		
	def leavePlayer(self):
		self.session.openWithCallback(self.exitVideoPlayer, MessageBox, _("Do you want to exit player?"), type=MessageBox.TYPE_YESNO)
		
	def exitVideoPlayer(self, message=None):
		if message:
			if hasattr(self, 'subtitles'):
				self.subtitles.exit()
				del self.subtitles
			# make sure that playback is unpaused otherwise the  
			# player driver might stop working 
			self.setSeekState(self.SEEK_STATE_PLAY)
			self.close()
	
	def __onClose(self):
		CustomPlayer.instance = None
		
		
class MipselPlayer(CustomPlayer):
	instance = None
	def __init__(self, session, sref, subfile=None):
		self.session = session
		self.bufferSeconds = 0
		self.bufferPercent = 0
		self.bufferSecondsLeft = 0
		self.autoPlay = config.plugins.archivCZSK.mipselPlayer.autoPlay.value
		CustomPlayer.__init__(self, session, sref)
		session.nav.getCurrentService().streamed().setBufferSize(config.plugins.archivCZSK.mipselPlayer.buffer.value)
		MipselPlayer.instance = self
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
				
	def __onClose(self):
		MipselPlayer.instance = None
	
			
class Player():
	"""Player for playing PVideo it content"""
	instance = None
	def __init__(self, session, it, callback=None, downloadCB=None, seekable=True, pausable=True):
		self.session = session
		
		self.port = 8902 # streaming port for rtmpgw
		self.videoController = None 
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		self.seekable = seekable
		self.pausable = pausable
		
		self.it = it
		self.name = it.name
		self.live = it.live
		self.subtitles = it.subs
		self.playUrl = it.url
		self.rtmpBuffer = '3000'
		self.rtmpStream = None
		self.rtmpgwProcess = None
		
		if self.live:
			self.rtmpBuffer = config.plugins.archivCZSK.liveBuffer.getValue()
			self.rtmpStream = it.stream
		else:
			self.rtmpBuffer = config.plugins.archivCZSK.archiveBuffer.getValue()
		if it.rtmpBuffer is not None:
			self.rtmpBuffer = it.rtmpBuffer
		
		self.callback = callback
		self.downloadCB = downloadCB
		
		if self.live:
			self.rtmpStream = it.stream
			
		#to make sure that rtmpgw is not running (ie. player crashed)	
		os.system('killall rtmpgw')
					
		
	def _setPort(self):
		"""Sets streaming port for rmtpgw"""
		netstat = Popen(NETSTAT_PATH + ' -tulna', stderr=STDOUT, stdout=PIPE, shell=True)
		out, err = netstat.communicate()
		if str(self.port) in out:
			self.port = self.port + 1
			log.debug('Changing port for rtmpgw to %s', self.port)
		
	def _startRTMPGWProcess(self):
		log.info('starting rtmpgw process')
		if self.live:
			cmd = "%s -v -q -r %s -W %s -p %s -y %s --buffer %s --sport %s --buffer %s" % (RTMPGW_PATH, self.rtmpStream.url, self.rtmpStream.swfUrl, self.pageUrl, self.playpath, str(self.port), str(self.rtmpBuffer))
		else:
			rtmpUrl = ' --'.join(self.playUrl.split()[0:])
			cmd = '%s -q -r %s --sport %s --buffer %s' % (RTMPGW_PATH, rtmpUrl, str(self.port), str(self.rtmpBuffer))
		log.info('rtmpgw server streaming: %s', cmd)
		
		self.rtmpgwProcess = eConsoleAppContainer()
		self.rtmpgwProcess.appClosed.append(self._exitRTMPGWProcess)
		self.rtmpgwProcess.execute(cmd)
		
	def _exitRTMPGWProcess(self, status):
		log.info('rtmpgw process exited with status %d', status)
		self.rtmpgwProcess = None	

	def play(self):
		self.session.nav.stopService()
		if self.playUrl.startswith('rtmp'):
			if config.plugins.archivCZSK.seeking.value:
				self._playStream(str(self.playUrl + ' buffer=' + self.rtmpBuffer), self.subtitles)
			else:
				self._setPort()
				self._startRTMPGWProcess()
				self._playStream('http://0.0.0.0:' + str(self.port), self.subtitles)	
		else:
			self._playStream(str(self.playUrl), self.subtitles)
					
	def stop(self):
		self.videoController.exitbox(True)
			
			
	def _playStream(self, streamURL, subtitles=None):
		sref = eServiceReference(4097, 0, streamURL)
		sref.setName(self.name.encode('utf-8'))
		
		if config.plugins.archivCZSK.player.value == 'standard':
			self.session.openWithCallback(self.exit, StandardPlayer, sref)
			self.videoController = StandardPlayer.instance
		
		elif config.plugins.archivCZSK.player.value == 'custom':
			self.session.openWithCallback(self.exit, CustomPlayer, sref, subtitles)
			self.videoController = CustomPlayer.instance
			
		elif config.plugins.archivCZSK.player.value == 'mipsel':
			self.session.openWithCallback(self.exit, MipselPlayer, sref, subtitles)
			self.videoController = MipselPlayer.instance

	def exit(self, callback=None):
		if self.rtmpgwProcess is not None:
			self.rtmpgwProcess.sendCtrlC()
		self.session.nav.playService(self.oldService)
		if self.callback:
			self.callback()
		if self.downloadCB:
			self.downloadCB(self.it)
