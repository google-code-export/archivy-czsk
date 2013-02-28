# -*- coding: UTF-8 -*-
'''
Created on 20.3.2012

@author: marko
'''
import os

from subprocess import Popen, PIPE, STDOUT
from twisted.internet import defer

from enigma import  eServiceCenter, iServiceInformation, eServiceReference, iSeekableService, iPlayableService, iPlayableServicePtr, eTimer, eConsoleAppContainer, getDesktop
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InfoBar import MoviePlayer
from Screens.HelpMenu import HelpableScreen
from Screens.ChoiceBox import ChoiceBox

from Screens.InfoBarGenerics import InfoBarShowHide, \
	InfoBarSeek, InfoBarAudioSelection, InfoBarAdditionalInfo, InfoBarNotifications, \
	InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarSimpleEventView, \
	InfoBarSummarySupport, InfoBarMoviePlayerSummarySupport, InfoBarServiceErrorPopupSupport
	
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.ActionMap import HelpableActionMap

from Components.Sources.Boolean import Boolean
from Components.ProgressBar import ProgressBar
from Components.Label import Label
from Components.ServiceEventTracker import ServiceEventTracker
from Components.ActionMap import HelpableActionMap
from Components.config import config, ConfigInteger, ConfigSubsection
from Components.AVSwitch import AVSwitch
from Components.Sources.StaticText import StaticText


from subtitles.subtitles import SubsSupport
from controller import VideoPlayerController, GStreamerDownloadController
from infobar import ArchivCZSKMoviePlayerInfobar
import setting

from Plugins.Extensions.archivCZSK import _
from Plugins.Extensions.archivCZSK import log
from Plugins.Extensions.archivCZSK.engine.items import RtmpStream
from Plugins.Extensions.archivCZSK.engine.tools import util
from Plugins.Extensions.archivCZSK.engine.exceptions.archiveException import CustomInfoError, CustomError
from Plugins.Extensions.archivCZSK.gui.base import BaseArchivCZSKScreen

SERVICEMP4_ID = 0x1011
SERVICEMRUA_ID = 4370

RTMPGW_PATH = '/usr/bin/rtmpgw'
NETSTAT_PATH = 'netstat'


class Video(object):
	def __init__(self, session, serviceTryLimit=20):
		self.session = session
		self.service = None
		self.__serviceTimer = eTimer()
		self.__serviceTimerTryDelay = 500 #ms
		self.__serviceTryTime = 0
		self.__serviceTryLimit = serviceTryLimit * 1000
		self.__deferred = defer.Deferred()
		

	def startService(self):
		"""
		Get real start of service
		@return: deferred, fires success when gets service or errback when dont get service in time limit
		"""
		
		
		def fireDeferred():
			self.__deferred.callback(None)
			self.__deferred = None
			
		def fireDeferredErr():
			self.__deferred.errback(None)
			self.__deferred = None
			
		def getService():
			if self.__deferred is None:
				return
			
			if self.service is None:
				if self.__serviceTryTime < self.__serviceTryLimit:
					self.__serviceTimer.start(self.__serviceTimerTryDelay, True)
				else:
					del self.__serviceTimer
					fireDeferredErr()
			else:
				del self.__serviceTimer
				fireDeferred()
			return self.__deferred
				
		def setService():
			self.__serviceTryTime += self.__serviceTimerTryDelay
			self.service = self.session.nav.getCurrentService()
			getService()
		
		self.__serviceTimer.callback.append(setService)
		getService()
		return self.__deferred	
		
	
		
	
	def __getSeekable(self):
		if self.service is None:
			return None
		return self.service.seek()
	
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
	
	def getName(self):
		if self.service is None:
			return ''
		return self.session.nav.getCurrentlyPlayingServiceReference().getName()
		

####################################################

class ArchivCZSKMoviePlayerSummary(Screen):
	skin = """
	<screen position="0,0" size="132,64">
    <widget source="item" render="Label" position="0,0" size="132,64" font="Regular;15" halign="center" valign="center" />
	</screen>"""

	def __init__(self, session, parent):
		Screen.__init__(self, session)
		self["item"] = StaticText("")

	def updateOLED(self, what):
		self["item"].setText(what)
			

class InfoBarAspectChange:
	"""
	Simple aspect ratio changer
	"""
	
	def __init__(self):
		self.AVswitch = AVSwitch()
		self.aspectChanged = False
		self.defaultAVmode = self.AVswitch.getAspectRatioSetting()
		self.currentAVmode = 3
		self["aspectChangeActions"] = HelpableActionMap(self, "InfobarAspectChangeActions",
        	{
         	"aspectChange":(self.aspectChange, ("changing aspect"))
          	}, -3)
		
		self.onClose.append(self.__onClose)
		
	def aspectChange(self):
		log.debug("aspect mode %d" , self.currentAVmode)
		self.aspectChanged = True
		if self.currentAVmode == 1: #letterbox
			self.AVswitch.setAspectRatio(0)
			self.currentAVmode = 2
		elif self.currentAVmode == 2: #panscan
			self.AVswitch.setAspectRatio(4)
			self.currentAVmode = 3
		elif self.currentAVmode == 3: #bestfit
			self.AVswitch.setAspectRatio(2)
			self.currentAVmode = 4
		elif self.currentAVmode == 4: #nonlinear
			self.AVswitch.setAspectRatio(3)
			self.currentAVmode = 1
			
			
	def __onClose(self):
		if self.aspectChanged:
			self.AVswitch.setAspectRatio(self.defaultAVmode)
		#self.AVswitch.setAspectRatio(2)
		
	


class ArchivCZSKMoviePlayer(BaseArchivCZSKScreen, SubsSupport, ArchivCZSKMoviePlayerInfobar, InfoBarBase, InfoBarShowHide, \
		InfoBarSeek, InfoBarAudioSelection, HelpableScreen, InfoBarNotifications, \
		InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, \
		InfoBarAspectChange, InfoBarServiceErrorPopupSupport):
	
	ENABLE_RESUME_SUPPORT = True
	ALLOW_SUSPEND = True
	
	def __init__(self, session, service, subtitles):
		BaseArchivCZSKScreen.__init__(self, session)
		self.videoPlayerSetting = config.plugins.archivCZSK.videoPlayer
		
		
		## set default/non-default skin according to SD/HD mode
		if self.videoPlayerSetting.useDefaultSkin.getValue():
			self.setSkinName("MoviePlayer")
		else:
			HD = getDesktop(0).size().width() == 1280
			if HD:
				self.setSkin("ArchivCZSKMoviePlayer_HD")
			else:
				self.setSkinName("MoviePlayer")
				
		
		## init custom infobar (added info about download speed, buffer level..)
		ArchivCZSKMoviePlayerInfobar.__init__(self)
		
		
		## custom actions for MP	
		self["actions"] = HelpableActionMap(self, "ArchivCZSKMoviePlayerActions",
        	{
         	"leavePlayer": (self.leavePlayer, _("leave player?")),
         	"toggleShow": (self.toggleShow, _("show/hide infobar"))
          	}, -3) 
			
		## bindend some video events to functions
		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
		{
			iPlayableService.evStart: self.__serviceStarted,
			iPlayableService.evUser + 10: self.__evAudioDecodeError,
			iPlayableService.evUser + 11: self.__evVideoDecodeError,
			iPlayableService.evUser + 12: self.__evPluginError,
		})
		
		InfoBarBase.__init__(self, steal_current_service=True)
		# init of all inherited screens
		for x in HelpableScreen, InfoBarShowHide, \
			    InfoBarSeek, InfoBarAudioSelection, InfoBarNotifications, \
				InfoBarServiceNotifications, HelpableScreen, InfoBarPVRState, InfoBarCueSheetSupport, \
				InfoBarAspectChange, InfoBarServiceErrorPopupSupport:
				x.__init__(self)
		
		# init subtitles		
		SubsSupport.__init__(self, subPath=subtitles, defaultPath=config.plugins.archivCZSK.subtitlesPath.getValue(), forceDefaultPath=True)
		
		# to get real start of service, and for queries for video length/position
		self.video = Video(session)
		
		self.sref = service	
		self.returning = False
		self.onClose.append(self._onClose)
	
	def __evAudioDecodeError(self):
		currPlay = self.session.nav.getCurrentService()
		sAudioType = currPlay.info().getInfoString(iServiceInformation.sUser + 10)
		print "[__evAudioDecodeError] audio-codec %s can't be decoded by hardware" % (sAudioType)
		self.session.open(MessageBox, _("This Dreambox can't decode %s streams!") % sAudioType, type=MessageBox.TYPE_INFO, timeout=20)

	def __evVideoDecodeError(self):
		currPlay = self.session.nav.getCurrentService()
		sVideoType = currPlay.info().getInfoString(iServiceInformation.sVideoType)
		print "[__evVideoDecodeError] video-codec %s can't be decoded by hardware" % (sVideoType)
		self.session.open(MessageBox, _("This Dreambox can't decode %s streams!") % sVideoType, type=MessageBox.TYPE_INFO, timeout=20)

	def __evPluginError(self):
		currPlay = self.session.nav.getCurrentService()
		message = currPlay.info().getInfoString(iServiceInformation.sUser + 12)
		print "[__evPluginError]" , message
		self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=20)
		
	def __serviceStarted(self):
		# we wait for service reference, and then trigger serviceStartedNow/setvice
		d = self.video.startService()
		d.addCallbacks(self._serviceStartedReal, self._serviceNotStarted)
	
	def _serviceStartedReal(self, callback=None):
		serviceName = self.video.getName()
		self.summaries.updateOLED(serviceName)
		
	def _serviceNotStarted(self, failure):
		log.info('cannot get service reference')
		
	def createSummary(self):
		return ArchivCZSKMoviePlayerSummary
	
	# override InfobarShowhide method
	def epg(self):
		pass
			
	def playService(self):
		self.session.nav.playService(self.sref)
		
	def leavePlayer(self):
		self.handleLeave()
		
	def doEofInternal(self, playing):
		log.debug("get EOF playing-%s execing %s" , playing, self.execing)
		self.exitVideoPlayer()
		
	def handleLeave(self):
		self.is_closing = True
		self.session.openWithCallback(self.leavePlayerConfirmed, MessageBox, text=_("Stop playing this movie?"), type=MessageBox.TYPE_YESNO)

	def leavePlayerConfirmed(self, answer):
		if answer:
			self.exitVideoPlayer()
				
	def exitVideoPlayer(self):
		# from tdt duckbox
		# make sure that playback is unpaused otherwise the  
		# player driver might stop working 
		
		# disabled because on gstreamer freezes e2 after stopping live rtmp stream
		
		#self.setSeekState(self.SEEK_STATE_PLAY) 
		
		self.close()
		
	def _onClose(self):
		pass

class StandardVideoPlayer(MoviePlayer):
	"""Standard MoviePlayer without any modifications"""
	def __init__(self, session, sref, controller, subtitles):
		MoviePlayer.__init__(self, session, sref)
		#SubsSupport.__init__(self, subPath=subtitles, alreadyPlaying=True)
		self.skinName = "MoviePlayer" 


class CustomVideoPlayer(ArchivCZSKMoviePlayer):
	def __init__(self, session, sref, videoPlayerController, playAndDownload=False, subtitles=None):
		ArchivCZSKMoviePlayer.__init__(self, session, sref, subtitles)
		self.videoPlayerController = videoPlayerController
		self.useVideoController = self.videoPlayerController is not None
		self.playAndDownload = playAndDownload
		if self.useVideoController:
			self.videoPlayerController.set_video_player(self)
	
	def _serviceStartedReal(self, callback=None):
		super(CustomVideoPlayer, self)._serviceStartedReal(None)
		if self.useVideoController:
			self.videoPlayerController.start(self.playAndDownload)
			
##################  default MP methods ################
	def _seekFwd(self):
		super(CustomVideoPlayer, self).seekFwd()
		
	def _seekBack(self):
		super(CustomVideoPlayer, self).seekBack()
		
	def _doSeekRelative(self, pts):
		super(CustomVideoPlayer, self).doSeekRelative(pts)
		
	def _unPauseService(self):
		super(CustomVideoPlayer, self).unPauseService()
		
	def _pauseService(self):
		super(CustomVideoPlayer, self).pauseService()
		
	def _doEofInternal(self, playing):
		super(CustomVideoPlayer, self).doEofInternal(playing)
		
	def _exitVideoPlayer(self):
		super(CustomVideoPlayer, self).exitVideoPlayer()
		
#######################################################

	def seekFwd(self):
		if self.useVideoController:
			self.videoPlayerController.seek_fwd()
		else:
			self._seekFwd()
			
	def seekBack(self):
		if self.useVideoController:
			self.videoPlayerController.seek_fwd()
		else:
			self._seekBack()
		
	def doSeekRelative(self, pts):
		if self.useVideoController:
			self.videoPlayerController.do_seek_relative(pts)
		else:
			self._doSeekRelative(pts)

	def pauseService(self):
		if self.useVideoController:
			self.videoPlayerController.pause_service()
		else:
			self._pauseService()

	def unPauseService(self):
		if self.useVideoController:
			self.videoPlayerController.unpause_service()
		else:
			self._unPauseService()
		
	def doEofInternal(self, playing):
		if self.useVideoController:
			self.videoPlayerController.do_eof_internal(playing)
		else:
			self._doEofInternal(playing)
			
	def leavePlayerConfirmed(self, answer):
		if answer:
			self.exitVideoPlayer()
		
	def exitVideoPlayer(self):
		if self.useVideoController:
			self.videoPlayerController.exit_video_player()
		else:
			self._exitVideoPlayer()

		
class GStreamerVideoPlayer(CustomVideoPlayer):
	def __init__(self, session, sref, videoPlayerController, playAndDownload=False, subtitles=None):
		CustomVideoPlayer.__init__(self, session, sref, videoPlayerController, playAndDownload, subtitles)
		self.gstreamerSetting = self.videoPlayerSetting
		self.useBufferControl = False
		self.setBufferMode(int(self.gstreamerSetting.bufferMode.getValue()))
		
		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
            {
                iPlayableService.evBuffering: self.__evUpdatedBufferInfo,
            })
		self.playService()
		
	def __evUpdatedBufferInfo(self):
		if self.playAndDownload:
			return
		streamed = self.session.nav.getCurrentService().streamed()
		if streamed:
			bufferSeconds = 0
			bufferSecondsLeft = 0
			bufferInfo = streamed.getBufferCharge()
			bufferPercent = bufferInfo[0]
			bufferSize = bufferInfo[4]
			downloadSpeed = bufferInfo[1]
			bitrate = bufferInfo[2]
			if bitrate > 0:
				bufferSeconds = bufferSize / bitrate
				bufferSecondsLeft = bufferSeconds * bufferPercent / 100
			
			if(bufferPercent > 95):
				self.bufferFull()
				
			if(bufferPercent == 0 and (bufferInfo[1] != 0 and bufferInfo[2] != 0)):
				self.bufferEmpty()
				
			info = {
					'bitrate':bitrate,
				    'buffer_percent':bufferPercent,
				    'buffer_secondsleft':bufferSecondsLeft,
				    'buffer_size':bufferSize,
				    'download_speed':downloadSpeed,
				    'buffer_slider':0
				   }
			
			log.debug("BufferPercent %d\nAvgInRate %d\nAvgOutRate %d\nBufferingLeft %d\nBufferSize %d" 
					, bufferInfo[0], bufferInfo[1], bufferInfo[2], bufferInfo[3], bufferInfo[4])
			self.updateInfobar(info)
	
	def _serviceStartedReal(self, callback=None):
		super(GStreamerVideoPlayer, self)._serviceStartedReal(None)
		bufferSize = int(self.gstreamerSetting.bufferSize.getValue())
		if bufferSize > 0:
			self.setBufferSize(bufferSize)
		
	def setBufferMode(self, mode=None):
		if self.playAndDownload:
			return
			
		if mode == 3:
			log.debug("manual control")
			self.useBufferControl = True
			
	def setBufferSize(self, size):
		""" set buffer size for streams in Bytes """
		
		# servicemp4 already set bufferSize
		if self.gstreamerSetting.servicemp4.getValue():
			return
		
		streamed = self.session.nav.getCurrentService().streamed()
		if streamed:
			log.debug("setting buffer size to %s KB", size)
			size = long(size * 1024)
			streamed.setBufferSize(size)
		else:
			log.debug("cannot set buffer size to %s, service is not streamed")
			
	def bufferFull(self):
		if self.useBufferControl:
			if self.seekstate != self.SEEK_STATE_PLAY :
				log.debug("Buffer filled start playing")
				self.setSeekState(self.SEEK_STATE_PLAY)
				
	def bufferEmpty(self):
		if self.useBufferControl:
			if self.seekstate != self.SEEK_STATE_PAUSE :
				log.debug("Buffer drained pause")
				self.setSeekState(self.SEEK_STATE_PAUSE)

class EPlayer3VideoPlayer(CustomVideoPlayer):
	def __init__(self, session, sref, videoPlayerController, playAndDownload=False, subtitles=None):
		CustomVideoPlayer.__init__(self, session, sref, videoPlayerController, playAndDownload, subtitles) 
		self.playService()
		

class EPlayer2VideoPlayer(CustomVideoPlayer):
	def __init__(self, session, sref, videoPlayerController, playAndDownload=False, subtitles=None):
		CustomVideoPlayer.__init__(self, session, sref, videoPlayerController, playAndDownload, subtitles) 
		self.playService()
	
##TO DO				
class BaseStreamVideoPlayer(ArchivCZSKMoviePlayer):
	instance = None
	def __init__(self, session, sref, videoPlayerController, useVideoController, playAndDownload, streamContent):
		ArchivCZSKMoviePlayer.__init__(self, session, sref, videoPlayerController, useVideoController, playAndDownload)
		self["actions"] = HelpableActionMap(self, "StreamPlayerActions",
            {
                "aspectChange": (self.aspectratioSelection, _("changing aspect Ratio")),
                "subtitles": (self.subtitlesSetup, _("show/hide subtitles")),
                "leavePlayer": (self.leavePlayer, _("leave player?")),
                "toggleList": (self.switchToList, _("list streams?"))
            }, 0)
		
		self.streamContent = streamContent
		self.instance = self
		
		
	def switchToList(self):
		if not self.playAndDownload:
			self.hide()

			self.streamContentScreen.show()
		else:
			log.debug("cannot switch to stream_list, download is running")
			
	def leavePlayer(self):
		if not self.playAndDownload:
			self.switchToList()
			
			
			
class StreamVideoPlayer():
	def __init__(self, player):
		self.player.playService()
		
		
class Player():
	"""Player for playing PVideo it content"""
	def __init__(self, session, callback=None, useVideoController=False, content_provider=None):
		self.session = session
		self.content_provider = content_provider
		self.settings = config.plugins.archivCZSK.videoPlayer
		self.port = 8902 # streaming port for rtmpgw
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		
		#if we are playing and downloading
		self.download = None
		self.gstDownload = None
		self.rtmpgwProcess = None
		
		#default player settings
		self.seekable = True 
		self.pausable = True
		
		self.playDelay = int(self.settings.playDelay.getValue())
		self.autoPlay = self.settings.autoPlay.getValue()
		self.playerBuffer = int(self.settings.bufferSize.getValue())
			
		self.it = None
		self.name = u'unknown stream'
		self.subtitles = None
		self.playUrl = None
		self.picon = None
		self.live = False
		self.rtmpBuffer = 20000
		self.stream = None
		
		# additional play settings
		self.playSettings = None
		
		# for amiko hdmu fix
		self.rassFuncs = []
		
		#setting ContentScreen callback		
		self.callback = callback
					
	
	def setContentProvider(self, content_provider):
		self.content_provider = content_provider
		
	def setVideoItem(self, it, seekable=True, pausable=True):
		#loading video item
		self.it = it
		self.name = it.name
		self.subtitles = it.subs
		self.playUrl = it.url
		self.picon = it.picon
		self.live = it.live
		
		self.seekable = seekable
		self.pausable = pausable
		self.playSettings = it.settings
		
		if it.stream is not None:
			self.stream = it.stream
			
		if self.stream is None and self.live:
			self.rtmpBuffer = int(self.settings.liveBuffer.getValue())
			
		elif self.stream is None and not self.live:
			self.rtmpBuffer = int(self.settings.archiveBuffer.getValue())
	
		elif self.stream is not None:
			self.playDelay = int(self.stream.playDelay)
			self.playerBuffer = int(self.stream.playerBuffer)
			if isinstance(self.stream, RtmpStream):
				self.rtmpBuffer = int(self.stream.rtmpBuffer)
		
	def play(self):
		"""starts playing video stream"""
		if self.playUrl is not None:
			verifyLink = config.plugins.archivCZSK.linkVerification.getValue()
			
			# rtmp stream
			if self.playUrl.startswith('rtmp'):
				
				# internal player has rtmp support
				if self.settings.seeking.getValue():
					if self.stream is not None:
						self._playStream(self.stream.getUrl(), self.subtitles, verifyLink=verifyLink)
					else:
						self._playStream(str(self.playUrl + ' buffer=' + str(self.rtmpBuffer)), self.subtitles, verifyLink=verifyLink)
				# internal player doesnt have rtmp support so we use rtmpgw
				else:
					#to make sure that rtmpgw is not running
					os.system('killall rtmpgw')
					self.seekable = False
					self._startRTMPGWProcess()
					self._playStream('http://0.0.0.0:' + str(self.port), self.subtitles, verifyLink=verifyLink)
			
			# not a rtmp stream
			else:
				self._playStream(str(self.playUrl), self.subtitles)
		else:
			log.info("Nothing to play. You need to set VideoItem first.")
			
			
	def playAndDownload(self, gstreamerDownload=False):
		"""starts downloading and then playing after playDelay value"""
		
		def playNDownload(callback=None):
			if callback:
				self.content_provider.download(self.it, self._showPlayDownloadDelay, DownloadManagerMessages.finishDownloadCB, playDownload=True)
		
		from Plugins.Extensions.archivCZSK.gui.download import DownloadManagerMessages
		from Plugins.Extensions.archivCZSK.engine.downloader import getFileInfo, GStreamerDownload
		
		if self.content_provider is None:
			log.info('Cannot download.. You need to set your content provider first')
			return
		
		# we use gstreamer to play and download stream
		if gstreamerDownload:
			
			# find out local path
			filename = self.it.filename
			name = self.it.name
			downloadsPath = self.content_provider.downloads_path
			if self.playUrl.startswith('http'):
				info = getFileInfo(self.playUrl, filename, self.playSettings['extra-headers'])
				path = os.path.join(downloadsPath, info[0])
			elif self.playUrl.startswith('rtmp'):
				if filename is None:
					filename = name + '.flv'
					filename = filename.replace(' ', '_')
					filename = filename.replace('/', '')
					filename = filename.replace('(', '')
					filename = filename.replace(')', '')
				path = os.path.join(downloadsPath, filename)
			path = path.encode('ascii', 'ignore')
			log.debug("download path: %s", path)
			
			# set prebuffering settings and play..
			prebufferSeconds = 0
			prebufferPercent = 2
			self.gstDownload = GStreamerDownload(path, prebufferSeconds, prebufferPercent)
			self._playStream(self.playUrl, self.subtitles, playAndDownloadGst=True)
			return
		
		
		# we are downloading by wget/twisted and playing it by gstreamer/eplayer2,3
		try:
			self.session.openWithCallback(playNDownload, MessageBox, _("""Play and download mode is not supported by all video formats, 
																		 Player can start behave unexpectedly or not play video at all. 
																		 Do you want to continue?""") , type=MessageBox.TYPE_YESNO)
		except CustomInfoError as er:
			self.session.open(MessageBox, er, type=MessageBox.TYPE_ERROR, timeout=3)		
		
			
	def playDownload(self, download):
		"""starts playing already downloading item"""
		from Plugins.Extensions.archivCZSK.engine.downloader import Download
		
		if download is not None and isinstance(download, Download):
			self.download = download
			self._playAndDownloadCB()
		else:
			log.info("Provided download instance is None or not instance of Download")
			
		
	def _startRTMPGWProcess(self):
		log.debug('starting rtmpgw process')
		ret = util.check_program(RTMPGW_PATH)
		if ret is None:
			log.info("Cannot found rtmpgw, make sure that you have installed it, or try to use Video player with internal rtmp support")
			raise CustomError(_("Cannot found rtmpgw, make sure that you have installed it, or try to use Video player with internal rtmp support"))
		
		netstat = Popen(NETSTAT_PATH + ' -tulna', stderr=STDOUT, stdout=PIPE, shell=True)
		out, err = netstat.communicate()
		if str(self.port) in out:
			log.debug("Port %s is not free" , self.port)
			self.port = self.port + 1
			log.debug('Changing port for rtmpgw to %d' , self.port)
		
		if self.stream is not None:
			cmd = "%s %s --sport %d" % (RTMPGW_PATH, self.stream.getRtmpgwUrl(), self.port)	
		else:
			urlList = self.playUrl.split()
			rtmp_url = []
			for url in urlList[1:]:
				rtmp = url.split('=')
				rtmp_url.append(' --' + rtmp[0])
				rtmp_url.append("'%s'" % rtmp[1])
			rtmpUrl = "'%s'" % urlList[0] + ' '.join(rtmp_url)
				
			cmd = '%s --quiet --rtmp %s --sport %d --buffer %d' % (RTMPGW_PATH, rtmpUrl, self.port, self.rtmpBuffer)		
		log.debug('rtmpgw server streaming: %s' , cmd)
		
		self.rtmpgwProcess = eConsoleAppContainer()
		self.rtmpgwProcess.appClosed.append(self._exitRTMPGWProcess)
		self.rtmpgwProcess.execute(cmd)
		

	def _exitRTMPGWProcess(self, status):
		log.debug('rtmpgw process exited with status %d' , status)
		self.rtmpgwProcess = None
		
	def _createServiceRef(self, streamURL):
		if self.settings.servicemp4.getValue():
			sref = eServiceReference(SERVICEMP4_ID, 0, streamURL)
		elif self.settings.servicemrua.getValue():
			sref = eServiceReference(SERVICEMRUA_ID, 0, streamURL)
		else:
			sref = eServiceReference(4097, 0, streamURL)
		sref.setName(self.name.encode('utf-8', 'ignore'))
		return sref	
								
			
	def _playStream(self, streamURL, subtitlesURL, playAndDownload=False, playAndDownloadGst=False, verifyLink=False):
		if verifyLink:
			ret = util.url_exist(streamURL, int(config.plugins.archivCZSK.linkVerificationTimeout.getValue()))
			if ret is not None and not ret:
				log.debug("Video url %s doesnt exist" , streamURL)
				raise CustomInfoError(_("Video url doesnt exist"))
		
		self.session.nav.stopService()
		
		if isinstance(streamURL, unicode):
			streamURL = streamURL.encode('utf-8')
			
		sref = self._createServiceRef(streamURL)
		
		# we dont need any special kind of play settings
		# since we play from local path
		if not playAndDownload:
			# load play settings
			setting.loadSettings(self.playSettings['user-agent'],
							 	self.playSettings['extra-headers'],
							 	playAndDownloadGst)
		
		videoPlayerSetting = self.settings.type.getValue()
		videoPlayerController = None
		
		playerType = self.settings.detectedType.getValue()
		useVideoController = self.settings.useVideoController.getValue()
		
		# fix for HDMU sh4 image..
		if config.plugins.archivCZSK.hdmuFix.getValue():
			self.rassFuncs = ServiceEventTracker.EventMap[14][:]
			ServiceEventTracker.EventMap[14] = []
		
				
		if useVideoController:
			videoPlayerController = VideoPlayerController(self.session, download=self.download, \
													 seekable=self.seekable, pausable=self.pausable)
		
		if videoPlayerSetting == 'standard':
			self.session.openWithCallback(self.exit, StandardVideoPlayer, sref, videoPlayerController, subtitlesURL)
		
		elif videoPlayerSetting == 'custom':
			if playerType == 'gstreamer':
				if playAndDownloadGst:
					path = self.gstDownload.path
					prebufferP = self.gstDownload.preBufferPercent
					prebufferS = self.gstDownload.preBufferSeconds
					videoPlayerController = GStreamerDownloadController(path, prebufferP, prebufferS)
					playAndDownload = True
				self.session.openWithCallback(self.exit, GStreamerVideoPlayer, sref, videoPlayerController, \
										 playAndDownload, subtitlesURL)
			elif playerType == 'eplayer3':
				self.session.openWithCallback(self.exit, EPlayer3VideoPlayer, sref, videoPlayerController, \
										playAndDownload, subtitlesURL)
			elif playerType == 'eplayer2':
				self.session.openWithCallback(self.exit, EPlayer2VideoPlayer, sref, videoPlayerController, \
										playAndDownload, subtitlesURL)
				
	def _playAndDownloadCB(self, callback=None):
		#what is downloading is always seekable and pausable
		self.seekable = True
		self.pausable = True
		
		url = self.download.local
		self.name = self.download.name
		subs_path = os.path.splitext(self.download.local)[0] + '.srt'
		
		if os.path.isfile(subs_path):
			subtitles = subs_path
		else:
			subtitles = None
			
		self._playStream(url, subtitles, True)
		
	def _showPlayDownloadDelay(self, download):
		"""called on download start"""
		self.download = download
		
		# download is not running already, so we dont continue
		if not self.download.downloaded and not self.download.running:
			log.debug("download not started at all")
			self.exit()
		else:
			self.session.openWithCallback(self._playAndDownloadCB, MessageBox, '%s %d %s' % (_('Video starts playing in'), \
									 self.playDelay, _("seconds.")), type=MessageBox.TYPE_INFO, timeout=self.playDelay, enable_input=False)
		
		
	def _askSaveDownloadCB(self):
		def saveDownload(callback=None):
			if not callback:
				from Plugins.Extensions.archivCZSK.engine.downloader import DownloadManager             
				DownloadManager.getInstance().removeDownload(self.download)
			else:
				self.download.wantSave = True

		if self.download.downloaded and not self.download.wantSave:
			self.session.openWithCallback(saveDownload, MessageBox, _("Do you want to save") + ' ' + self.download.name.encode('utf-8', 'ignore')\
										 + ' ' + _("to disk?"), type=MessageBox.TYPE_YESNO)
		elif self.download.downloaded and self.download.wantSave:
			pass
		
		elif not self.download.downloaded and self.download.running:
			self.session.openWithCallback(saveDownload, MessageBox, _("Do you want to continue downloading") + ' '\
										 + self.download.name.encode('utf-8', 'ignore') + ' ' + _("to disk?"), type=MessageBox.TYPE_YESNO)
		else:
			saveDownload(False)


	def exit(self, callback=None):
		# fix for HDMU sh4 image..
		if config.plugins.archivCZSK.hdmuFix.getValue():
			ServiceEventTracker.EventMap[14] = self.rassFuncs
		
		if self.rtmpgwProcess is not None:
			self.rtmpgwProcess.sendCtrlC()
		if self.download is not None:
			self._askSaveDownloadCB()
		setting.resetSettings()
		self.content_provider = None
		self.session.nav.playService(self.oldService)
		if self.callback:
			self.callback()
			

class StreamPlayer(Player):
	
	def exit(self, callback=None):
		StreamPlayer.instance = None
		if self.rtmpgwProcess is not None:
			self.rtmpgwProcess.sendCtrlC()
		if self.download is not None:
			self._askSaveDownloadCB()
		self.session.nav.playService(self.oldService)
		if self.callback is not None:
			self.callback()
	
		
		
