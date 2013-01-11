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
from controller import VideoPlayerController
from infobar import ArchivCZSKMoviePlayerInfobar

from Plugins.Extensions.archivCZSK import _
from Plugins.Extensions.archivCZSK import log
from Plugins.Extensions.archivCZSK.engine.items import RtmpStream
from Plugins.Extensions.archivCZSK.engine.tools import util
from Plugins.Extensions.archivCZSK.engine.exceptions.archiveException import CustomInfoError, CustomError
from Plugins.Extensions.archivCZSK.gui.base import BaseArchivCZSKScreen

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
		get real start of service
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
		return self.session.nav.getCurrentlyPlayingServiceReference().getPath().split('/')[-1]
		

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
		
class ArchivCZSKLCDScreen(Screen):
	skin = (
	"""<screen name="ArchivCZSKLCDScreen" position="0,0" size="132,64" id="1">
		<widget name="text1" position="4,0" size="132,35" font="Regular;16"/>
		<widget name="text3" position="4,36" size="132,14" font="Regular;10"/>
		<widget name="text4" position="4,49" size="132,14" font="Regular;10"/>
	</screen>""",
	"""<screen name="ArchivCZSKLCDScreen" position="0,0" size="96,64" id="2">
		<widget name="text1" position="0,0" size="96,35" font="Regular;14"/>
		<widget name="text3" position="0,36" size="96,14" font="Regular;10"/>
		<widget name="text4" position="0,49" size="96,14" font="Regular;10"/>
	</screen>""")

	def __init__(self, session, parent):
		Screen.__init__(self, session)
		self["text1"] = Label("ArchivCZSK")
		self["text3"] = Label("")
		self["text4"] = Label("")

	def setText(self, text, line):
		if len(text) > 10:
			if text[-4:] == ".mp3":
				text = text[:-4]
		textleer = "    "
		text = text + textleer * 10
		if line == 1:
			self["text1"].setText(text)
		elif line == 3:
			self["text3"].setText(text)
		elif line == 4:
			self["text4"].setText(text)
		

# some older e2 images dont have this infobar, source from taapat-enigma2-pli
class InfoBarAspectSelection: 
	STATE_HIDDEN = 0 
	STATE_ASPECT = 1 
	STATE_RESOLUTION = 2 
	def __init__(self): 
		self["AspectSelectionAction"] = HelpableActionMap(self, "InfobarAspectSelectionActions",
 			{ 
 				"aspectSelection": (self.ExGreen_toggleGreen, _("Aspect list...")),
 			}) 

		self.__ExGreen_state = self.STATE_HIDDEN 

	def ExGreen_doAspect(self): 
		self.__ExGreen_state = self.STATE_ASPECT 
		self.aspectSelection() 

	def ExGreen_doResolution(self): 
		self.__ExGreen_state = self.STATE_RESOLUTION 
		self.resolutionSelection() 

	def ExGreen_doHide(self): 
		self.__ExGreen_state = self.STATE_HIDDEN 

	def ExGreen_toggleGreen(self, arg=""): 
		print self.__ExGreen_state 
		if self.__ExGreen_state == self.STATE_HIDDEN: 
			print "self.STATE_HIDDEN" 
			self.ExGreen_doAspect() 
		elif self.__ExGreen_state == self.STATE_ASPECT: 
			print "self.STATE_ASPECT" 
			self.ExGreen_doResolution() 
		elif self.__ExGreen_state == self.STATE_RESOLUTION: 
			print "self.STATE_RESOLUTION" 
			self.ExGreen_doHide() 

	def aspectSelection(self): 
		selection = 0 
		tlist = [] 
		tlist.append(("Resolution", "resolution")) 
		tlist.append(("", "")) 
		tlist.append(("Letterbox", "letterbox")) 
		tlist.append(("PanScan", "panscan")) 
		tlist.append(("Non Linear", "non")) 
		tlist.append(("Bestfit", "bestfit")) 

		mode = open("/proc/stb/video/policy").read()[:-1] 
		print mode 
		for x in range(len(tlist)): 
			if tlist[x][1] == mode: 
				selection = x 

		keys = ["green", "", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" ] 


		self.session.openWithCallback(self.aspectSelected, ChoiceBox, title=_("Please select an aspect ratio..."), list=tlist, selection=selection, keys=keys) 
	def aspectSelected(self, aspect): 
		if not aspect is None: 
			if isinstance(aspect[1], str): 
				if aspect[1] == "resolution":
					self.ExGreen_toggleGreen()
				else:
					open("/proc/stb/video/policy", "w").write(aspect[1]) 
					self.ExGreen_doHide()
		return
	
	def resolutionSelection(self): 

		xresString = open("/proc/stb/vmpeg/0/xres", "r").read()
		yresString = open("/proc/stb/vmpeg/0/yres", "r").read()
		fpsString = open("/proc/stb/vmpeg/0/framerate", "r").read()
		xres = int(xresString, 16)
		yres = int(yresString, 16)
		fps = int(fpsString, 16)
		fpsFloat = float(fps)
		fpsFloat = fpsFloat / 1000


		selection = 0 
		tlist = [] 
		tlist.append(("Exit", "exit")) 
		tlist.append(("Auto(not available)", "auto")) 
		tlist.append(("Video: " + str(xres) + "x" + str(yres) + "@" + str(fpsFloat) + "hz", "")) 
		tlist.append(("--", "")) 
		tlist.append(("576i", "576i50")) 
		tlist.append(("576p", "576p50")) 
		tlist.append(("720p", "720p50")) 
		tlist.append(("1080i", "1080i50")) 
		tlist.append(("1080p@23.976hz", "1080p23")) 
		tlist.append(("1080p@24hz", "1080p24")) 
		tlist.append(("1080p@25hz", "1080p25")) 
		

		keys = ["green", "yellow", "blue", "", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9" ] 

		mode = open("/proc/stb/video/videomode").read()[:-1] 
		print mode 
		for x in range(len(tlist)): 
			if tlist[x][1] == mode: 
				selection = x 

		self.session.openWithCallback(self.ResolutionSelected, ChoiceBox, title=_("Please select a resolution..."), list=tlist, selection=selection, keys=keys) 

	def ResolutionSelected(self, Resolution): 
		if not Resolution is None: 
			if isinstance(Resolution[1], str): 
				if Resolution[1] == "exit":
					self.ExGreen_toggleGreen()
				elif Resolution[1] != "auto":
					open("/proc/stb/video/videomode", "w").write(Resolution[1]) 
					from enigma import gFBDC
					gFBDC.getInstance().setResolution(-1, -1)
					self.ExGreen_toggleGreen()
		return 


class ArchivCZSKMoviePlayer(BaseArchivCZSKScreen, SubsSupport, ArchivCZSKMoviePlayerInfobar, InfoBarBase, InfoBarShowHide, \
		InfoBarSeek, InfoBarAudioSelection, HelpableScreen, InfoBarNotifications, \
		InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarSimpleEventView, \
		InfoBarMoviePlayerSummarySupport, \
		InfoBarServiceErrorPopupSupport, InfoBarAspectSelection):
	
	ENABLE_RESUME_SUPPORT = True
	ALLOW_SUSPEND = True
	
	def __init__(self, session, service, subtitles):
		BaseArchivCZSKScreen.__init__(self, session)
		self.videoPlayerSetting = config.plugins.archivCZSK.videoPlayer
		if self.videoPlayerSetting.useDefaultSkin.getValue():
			self.setSkinName("MoviePlayer")
		else:
			HD = getDesktop(0).size().width() == 1280
			if HD:
				self.setSkin("ArchivCZSKMoviePlayer_HD")
			else:
				self.setSkinName("MoviePlayer")
			
		ArchivCZSKMoviePlayerInfobar.__init__(self)
			
		self["actions"] = HelpableActionMap(self, "ArchivCZSKMoviePlayerActions",
        	{
         	"leavePlayer": (self.leavePlayer, _("leave player?"))
          	}, -3) 
			
		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
		{
			iPlayableService.evStart: self.__serviceStarted,
			iPlayableService.evUser + 10: self.__evAudioDecodeError,
			iPlayableService.evUser + 11: self.__evVideoDecodeError,
			iPlayableService.evUser + 12: self.__evPluginError
		})
		
		for x in HelpableScreen, InfoBarShowHide, \
				InfoBarBase, InfoBarSeek, \
				InfoBarAudioSelection, InfoBarNotifications, InfoBarSimpleEventView, \
				InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, \
				InfoBarMoviePlayerSummarySupport, \
				InfoBarServiceErrorPopupSupport, InfoBarAspectSelection:
				x.__init__(self)
				
		SubsSupport.__init__(self, subPath=subtitles, defaultPath=config.plugins.archivCZSK.subtitlesPath.getValue(), forceDefaultPath=True)
		self.sref = service	
		self.returning = False
		self.video_length = 0
		self.video = Video(session)
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
		self.summaries.setText(serviceName, 3)
		
	def _serviceNotStarted(self, failure):
		print 'cannot get service reference'
		
	def createSummary(self):
		return ArchivCZSKLCDScreen
						
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
		self.setSeekState(self.SEEK_STATE_PLAY) 
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
		self.useVideoController = config.plugins.archivCZSK.videoPlayer.useVideoController.getValue()
		self.playAndDownload = playAndDownload
	
	def _serviceStartedReal(self, callback=None):
		super(CustomVideoPlayer, self)._serviceStartedReal(None)
		if self.useVideoController:
			self.videoPlayerController.start(self, self.playAndDownload)
			
##################  default MP methods ################

		
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
			self.videoPlayerController._exit_video_player()
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
		def createSref(name, path):
			sref = eServiceReference(4097, 0, path)
			sref.setName(name)
			return sref
		
		if self.playAndDownload:
			return
		path = self.sref.getPath()
		name = self.sref.getName()
		# use prefill buffer
		if mode == 1:
			log.debug("use prefill buffer")
			newpath = path + ' buffer=1'
			self.sref = createSref(name, newpath)
			
		# progressive streaming
		elif mode == 2:
			log.debug("use progressive streaming")
			newpath = path + ' buffer=2'
			self.sref = createSref(name, newpath)
			
		elif mode == 3:
			log.debug("manual control")
			self.useBufferControl = True
			
	def setBufferSize(self, size):
		# set buffer size for streams in Bytes
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
		self.port = 8902 # streaming port for rtmpgw
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		
		#if we are playing and downloading
		self.download = None
		self.rtmpgwProcess = None
		
		#default player settings
		self.seekable = True 
		self.pausable = True
		
		self.playDelay = int(config.plugins.archivCZSK.videoPlayer.playDelay.getValue())
		self.autoPlay = config.plugins.archivCZSK.videoPlayer.autoPlay.getValue()
		self.playerBuffer = int(config.plugins.archivCZSK.videoPlayer.bufferSize.getValue()) 
			
		self.it = None
		self.name = u'unknown stream'
		self.subtitles = None
		self.playUrl = None
		self.picon = None
		self.live = False
		self.rtmpBuffer = 20000
		self.stream = None
		
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
		
		if it.stream is not None:
			self.stream = it.stream
			
		if self.stream is None and self.live:
			self.rtmpBuffer = int(config.plugins.archivCZSK.videoPlayer.liveBuffer.getValue())
			
		elif self.stream is None and not self.live:
			self.rtmpBuffer = int(config.plugins.archivCZSK.videoPlayer.archiveBuffer.getValue())
	
		elif self.stream is not None:
			self.playDelay = int(self.stream.playDelay)
			self.playerBuffer = int(self.stream.playerBuffer)
			if isinstance(self.stream, RtmpStream):
				self.rtmpBuffer = int(self.stream.rtmpBuffer)
		
	def play(self):
		"""starts playing video stream"""
		if self.playUrl is not None:
			# rtmp stream
			if self.playUrl.startswith('rtmp'):
				
				# internal player has rtmp support
				if config.plugins.archivCZSK.videoPlayer.seeking.getValue():
					if self.stream is not None:
						self._playStream(self.stream.getUrl(), self.subtitles, verifyLink=False)
					else:
						self._playStream(str(self.playUrl + ' buffer=' + str(self.rtmpBuffer)), self.subtitles, verifyLink=False)
						
				# internal player doesnt have rtmp support so we use rtmpgw
				else:
					#to make sure that rtmpgw is not running
					os.system('killall rtmpgw')
					self.seekable = False
					self._startRTMPGWProcess()
					self._playStream('http://0.0.0.0:' + str(self.port), self.subtitles, verifyLink=False)
			
			# not a rtmp stream
			else:
				self._playStream(str(self.playUrl), self.subtitles)
		else:
			log.info("Nothing to play. You need to set VideoItem first.")
			
			
	def playAndDownload(self):
		"""starts downloading and then playing after playDelay value"""
		from Plugins.Extensions.archivCZSK.gui.download import DownloadManagerMessages
		if self.content_provider is None:
			log.info('Cannot download.. You need to set your content provider first')
			return
		try:
			self.content_provider.download(self.it, self._showPlayDownloadDelay, DownloadManagerMessages.finishDownloadCB, playDownload=True)
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
								
			
	def _playStream(self, streamURL, subtitlesURL, playAndDownload=False, verifyLink=config.plugins.archivCZSK.linkVerification.getValue()):
		if verifyLink:
			ret = util.url_exist(streamURL, int(config.plugins.archivCZSK.linkVerificationTimeout.getValue()))
			if ret is not None and not ret:
				log.debug("Video url %s doesnt exist" , streamURL)
				raise CustomInfoError(_("Video url doesnt exist, try to check it on web page of addon if it works."))
		
		self.session.nav.stopService()
		if isinstance(streamURL, unicode):
			streamURL = streamURL.encode('utf-8')
		sref = eServiceReference(4097, 0, streamURL)
		sref.setName(self.name.encode('utf-8', 'ignore'))
		
		videoPlayerSetting = config.plugins.archivCZSK.videoPlayer.type.getValue()
		videoPlayerController = None
		playerType = config.plugins.archivCZSK.videoPlayer.detectedType.getValue()
		useVideoController = config.plugins.archivCZSK.videoPlayer.useVideoController.getValue()
		
		if useVideoController:
			videoPlayerController = VideoPlayerController(self.session, download=self.download, \
													 seekable=self.seekable, pausable=self.pausable)
		
		
		if videoPlayerSetting == 'standard':
			self.session.openWithCallback(self.exit, StandardVideoPlayer, sref, videoPlayerController, subtitlesURL)
		
		elif videoPlayerSetting == 'custom':
			if playerType == 'gstreamer':
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

		if self.download.downloaded:
			self.session.openWithCallback(saveDownload, MessageBox, _("Do you want to save") + ' ' + self.download.name.encode('utf-8', 'ignore')\
										 + ' ' + _("to disk?"), type=MessageBox.TYPE_YESNO)
			
		elif not self.download.downloaded and self.download.running:
			self.session.openWithCallback(saveDownload, MessageBox, _("Do you want to continue downloading") + ' '\
										 + self.download.name.encode('utf-8', 'ignore') + ' ' + _("to disk?"), type=MessageBox.TYPE_YESNO)
		else:
			saveDownload(False)


	def exit(self, callback=None):
		if self.rtmpgwProcess is not None:
			self.rtmpgwProcess.sendCtrlC()
		if self.download is not None:
			self._askSaveDownloadCB()
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
	
		
		
