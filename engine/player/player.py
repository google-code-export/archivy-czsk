# -*- coding: UTF-8 -*-
'''
Created on 20.3.2012

@author: marko
'''
import os
from subprocess import Popen, PIPE, STDOUT

from enigma import  eServiceCenter, iServiceInformation, eServiceReference, iSeekableService, iPlayableService, iPlayableServicePtr, eTimer, eConsoleAppContainer
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InfoBar import MoviePlayer
from Screens.HelpMenu import HelpableScreen

from Screens.InfoBarGenerics import InfoBarShowHide, \
	InfoBarSeek, InfoBarAudioSelection, InfoBarAdditionalInfo, InfoBarNotifications, \
	InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarSimpleEventView, \
	InfoBarSummarySupport, InfoBarMoviePlayerSummarySupport, InfoBarServiceErrorPopupSupport
	
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.ActionMap import HelpableActionMap

from Components.ProgressBar import ProgressBar
from Components.Label import Label
from Components.ServiceEventTracker import ServiceEventTracker
from Components.ActionMap import HelpableActionMap
from Components.config import config, ConfigInteger, ConfigSubsection
from Components.AVSwitch import AVSwitch


from subtitles.subtitles import SubsSupport
from controller import VideoPlayerController
from infobar import CustomPlayerInfobar

from Plugins.Extensions.archivCZSK import _
from Plugins.Extensions.archivCZSK.engine.items import RtmpStream
from Plugins.Extensions.archivCZSK.engine.exceptions.archiveException import CustomInfoError
from Plugins.Extensions.archivCZSK.gui.base import BaseArchivCZSKScreen

def debug(data):
	if config.plugins.archivCZSK.debug.getValue():
		print '[ArchivCZSK] Player:', data.encode('utf-8')

RTMPGW_PATH = '/usr/bin/rtmpgw'
NETSTAT_PATH = 'netstat'

class ArchivCZSKMoviePlayer(BaseArchivCZSKScreen, SubsSupport, CustomPlayerInfobar, InfoBarBase, InfoBarShowHide, \
		InfoBarSeek, InfoBarAudioSelection, HelpableScreen, InfoBarNotifications, \
		InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarSimpleEventView, \
		InfoBarMoviePlayerSummarySupport, \
		InfoBarServiceErrorPopupSupport):
	
		ENABLE_RESUME_SUPPORT = True
		ALLOW_SUSPEND = True
	
		def __init__(self, session, service, subtitles, useCustomInfobar=False):
			BaseArchivCZSKScreen.__init__(self, session)
			if config.plugins.archivCZSK.player.useDefaultSkin.value:
				self.setSkinName("MoviePlayer")
			else:
				if self.HD:
					self.setSkin("ArchivCZSKMoviePlayer_HD")
				else:
					self.setSkin("ArchivCZSKMoviePlayer_SD")
			
			CustomPlayerInfobar.__init__(self)
			SubsSupport.__init__(self, subPath=subtitles, defaultPath=config.plugins.archivCZSK.subtitlesPath.value, forceDefaultPath=True)
			
			self["actions"] = HelpableActionMap(self, "ArchivCZSKMoviePlayerActions",
            {
                "aspectChange": (self.aspectratioSelection, _("changing aspect Ratio")),
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
				InfoBarServiceErrorPopupSupport:
				x.__init__(self)
			
			self.service = service
				
			self.returning = False
			self.video_length = 0
				
			self.AVswitch = AVSwitch()
			self.defaultAVmode = 1#self.getAspectRatioMode()
			self.currentAVmode = self.defaultAVmode
			
			self.onClose.append(self._onClose)
		
		
		def getAspectRatioMode(self):
			aspects = {'letterbox':0, 'panscan':1, 'bestfit':2, 'non':3, 'nonlinear':3}
			mode = open("/proc/stb/video/policy").read()[:-1]
			return aspects[mode]
		
		def _play(self):	
			self.session.nav.playService(self.service)
			
		def __getSeekable(self):
			service = self.session.nav.getCurrentService()
			if service is None:
				return None
			return service.seek()
		
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
			if self.getCurrentLength() is not None:
				self.video_length = self.getCurrentLength()

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
		
		def leavePlayer(self):
			self.handleLeave()
		
		def doEofInternal(self, playing):
			if not self.execing:
				return
			if not playing :
				return
			self.exitVideoPlayer()
			
		
		def handleLeave(self):
			self.is_closing = True
			list = (
				(_("Yes"), "quit"),
				(_("No"), "continue")
				)
			from Screens.ChoiceBox import ChoiceBox
			self.session.openWithCallback(self.exitVideoPlayer, ChoiceBox, title=_("Stop playing this movie?"), list=list)
					
		
		def aspectratioSelection(self):
			debug("aspect mode %d" % self.currentAVmode)
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
				
		
		def leavePlayerConfirmed(self, answer):
			if answer == 'quit':
				self.exitVideoPlayer()
				
		def exitVideoPlayer(self):
			self.setSeekState(self.SEEK_STATE_PLAY) 
			self.close()
		
		def _onClose(self):
			pass
			#self.AVswitch.setAspectRatio(self.defaultAVmode)


class StandardVideoPlayer(SubsSupport, MoviePlayer):
	"""Standard MoviePlayer without any modifications"""
	def __init__(self, session, sref, controller, subtitles):
		MoviePlayer.__init__(self, session, sref)
		SubsSupport.__init__(self, subPath=subtitles, alreadyPlaying=True)
		self.skinName = "MoviePlayer"   
			
		
class CustomVideoPlayer(ArchivCZSKMoviePlayer):
	def __init__(self, session, sref, videoPlayerController, useVideoController=False, playAndDownload=False, subtitles=None):
		ArchivCZSKMoviePlayer.__init__(self, session, sref, subtitles)
		
		self.videoPlayerController = videoPlayerController
		self.useVideoController = useVideoController
		self.playAndDownload = playAndDownload
	
		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
			{
				iPlayableService.evStart: self.__serviceStarted,
			})
		self._play()
		
		self.doSeekRelative=self.__doSeekRelative
	
	def __serviceStarted(self):
		if self.useVideoController:
			self.videoPlayerController.set_video_player(self)
			if self.playAndDownload:
				self.videoPlayerController.start_video_check()
			
##################  default MP methods ################

	def __play(self):
		super(CustomVideoPlayer, self)._play()
		
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
	
	def play(self):
		if self.useVideoController:
			self.__play()
		else:
			self._play()
		
	def __doSeekRelative(self, pts):
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
		if answer == 'quit':
			self.exitVideoPlayer()
		
	def exitVideoPlayer(self, message=None):
		if message is not None and self.useVideoController:
			self.videoPlayerController._exit_video_player()
		elif message is not None:
			self._exitVideoPlayer()
	
	

class MipselVideoPlayer(CustomVideoPlayer):
	def __init__(self, session, sref, videoPlayerController, autoPlay, videoBuffer, useVideoController=False, playAndDownload=False, subtitles=None):
		self.session = session
		self.buffering = False
		self.bufferSeconds = 0
		self.bufferPercent = 0
		self.bufferSecondsLeft = 0
		self.updateTimer = eTimer()
		self.updateTimer.callback.append(self.updateInfo)
		self.videoBuffer = videoBuffer
		self.autoPlay = autoPlay
		CustomVideoPlayer.__init__(self, session, sref, videoPlayerController, useVideoController, playAndDownload, subtitles)
		streamed = session.nav.getCurrentService().streamed()
		
		if not playAndDownload:
			if streamed is not None:
				print '[MipselPlayer] setting buffer size of %d' % self.videoBuffer
				self.streamed.setBufferSize(self.videoBuffer)
			self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
            {
                iPlayableService.evBuffering: self.__evUpdatedBufferInfo,
                
            })
			self.updateTimer.start(1000)
			
		self.videoPlayerController.set_video_player(self)
		if self.playAndDownload and self.useVideoController:
			self.videoPlayerController.start_video_check()

	#buffer management from airplayer	
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
		print "[MipselPlayer]", "Buffer", bufferInfo[4], "Info ", bufferInfo[0], "% filled ", bufferInfo[1], "/", bufferInfo[2], " buffered: ", self.bufferSecondsLeft, "s"
		
	
	def updateInfo(self):
		downloading = False
		buffering = self.buffering
		buffer_time = self.bufferSecondsLeft
		buffer_percent = self.bufferPercent
		#video_length = self.getCurrentLength()
		#buffer_length = video_length + (self.bufferSeconds * 90000)
		self.updateInfobar(downloading=downloading, buffering=buffering, buffer_seconds=buffer_time)
		
	
	def bufferFull(self):
		self.buffering = False
		if self.autoPlay:
			if self.seekstate != self.SEEK_STATE_PLAY :
				self.setSeekState(self.SEEK_STATE_PLAY)

	def bufferEmpty(self):
		self.buffering = True
		if self.autoPlay:
			if self.seekstate != self.SEEK_STATE_PAUSE :
				self.setSeekState(self.SEEK_STATE_PAUSE)
		
	def _onClose(self):
		self.updateTimer.stop()
		self.updateTimer = None
		super(MipselVideoPlayer, self)._onClose()

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
			debug("cannot switch to stream_list, download is running")
			
	def leavePlayer(self):
		if not self.playAndDownload:
			self.switchToList()
			
			
			
class StreamVideoPlayer():
	def __init__(self, player):
		self.player._play()
		
		
			

			
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
		
		self.playDelay = int(config.plugins.archivCZSK.player.playDelay.getValue())
		self.autoPlay = config.plugins.archivCZSK.player.mipselPlayer.autoPlay.getValue()
		self.playerBuffer = int(config.plugins.archivCZSK.player.mipselPlayer.buffer.getValue())
		self.useVideoController = useVideoController 
			
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
			self.rtmpBuffer = int(config.plugins.archivCZSK.player.liveBuffer.getValue())
			
		elif self.stream is None and not self.live:
			self.rtmpBuffer = int(config.plugins.archivCZSK.player.archiveBuffer.getValue())
	
		elif self.stream is not None:
			self.playDelay = int(self.stream.playDelay)
			self.playerBuffer = int(self.stream.playerBuffer)
			if isinstance(self.stream, RtmpStream):
				self.rtmpBuffer = int(self.stream.rtmpBuffer)
		
	def setSubtitles(self, subtitles_path):
		self.subtitles = subtitles_path	
		
	def play(self):
		"""starts playing video stream"""
		if self.playUrl is not None:
			# rtmp stream
			if self.playUrl.startswith('rtmp'):
				
				# internal player has rtmp support
				if config.plugins.archivCZSK.player.seeking.getValue():
					if self.stream is not None:
						self._playStream(self.stream.getUrl(), self.subtitles)
					else:
						self._playStream(str(self.playUrl + ' buffer=' + str(self.rtmpBuffer)), self.subtitles)
						
				# internal player doesnt have rtmp support so we use rtmpgw
				else:
					#to make sure that rtmpgw is not running	
					os.system('killall rtmpgw')
					self.seekable = False
					self._startRTMPGWProcess()
					self._playStream('http://0.0.0.0:' + str(self.port), self.subtitles)
			
			# not a rtmp stream
			else:
				self._playStream(str(self.playUrl), self.subtitles)
		else:
			debug("nothing to play. You need to set VideoItem first.")
			
			
	def playAndDownload(self):
		"""starts downloading and then playing after playDelay value"""
		from Plugins.Extensions.archivCZSK.gui.download import DownloadManagerMessages
		if self.content_provider is None:
			debug('cannot download.. You need to set your content provider first')
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
			debug("provided download instance is None or not instance of Download")
			
		
	def _startRTMPGWProcess(self):
		debug('starting rtmpgw process')
		
		netstat = Popen(NETSTAT_PATH + ' -tulna', stderr=STDOUT, stdout=PIPE, shell=True)
		out, err = netstat.communicate()
		if str(self.port) in out:
			debug("Port %s is not free" % self.port)
			self.port = self.port + 1
			debug('Changing port for rtmpgw to %d' % self.port)
		
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
		print cmd			
		debug('rtmpgw server streaming: %s' % cmd)
		
		self.rtmpgwProcess = eConsoleAppContainer()
		self.rtmpgwProcess.appClosed.append(self._exitRTMPGWProcess)
		self.rtmpgwProcess.execute(cmd)
		
		
	def _exitRTMPGWProcess(self, status):
		debug('rtmpgw process exited with status %d' % status)
		self.rtmpgwProcess = None	
								
			
	def _playStream(self, streamURL, subtitlesURL, playAndDownload=False):
		self.session.nav.stopService()
		sref = eServiceReference(4097, 0, streamURL)
		sref.setName(self.name.encode('utf-8'))
		
		videoPlayerSetting = config.plugins.archivCZSK.player.type.getValue()
		videoPlayerController = None
		useVideoController = config.plugins.archivCZSK.player.useVideoController.getValue()
		
		if useVideoController:
			videoPlayerController = VideoPlayerController(self.session, download=self.download, \
													 seekable=self.seekable, pausable=self.pausable)
		
		
		if videoPlayerSetting == 'standard':
			self.session.openWithCallback(self.exit, StandardVideoPlayer, sref, videoPlayerController, subtitlesURL)
		
		elif videoPlayerSetting == 'custom':
			self.session.openWithCallback(self.exit, CustomVideoPlayer, sref, videoPlayerController, \
										 useVideoController, playAndDownload, subtitlesURL)
		elif videoPlayerSetting == 'mipsel':
			self.session.openWithCallback(self.exit, MipselVideoPlayer, sref, videoPlayerController, self.autoPlay, \
										 self.playerBuffer, useVideoController, playAndDownload, subtitlesURL)
		else:
			debug("unknown videoplayer %s" % videoPlayerSetting)
		
			
	def _playAndDownloadCB(self, callback=None):
		#what is downloading is always seekable and pausable
		self.seekable = True
		self.pausable = True
		
		url = self.download.local
		self.name = self.download.name
		
		subs_path = os.path.join(self.download.local, os.path.splitext(self.download.local)[0] + '.srt')
		
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
			debug("download not started at all")
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
			self.session.openWithCallback(saveDownload, MessageBox, _("Do you want to save") + ' ' + self.download.name.encode('utf-8')\
										 + ' ' + _("to disk?"), type=MessageBox.TYPE_YESNO)
			
		elif not self.download.downloaded and self.download.running:
			self.session.openWithCallback(saveDownload, MessageBox, _("Do you want to continue downloading") + ' '\
										 + self.download.name.encode('utf-8') + ' ' + _("to disk?"), type=MessageBox.TYPE_YESNO)
		else:
			saveDownload(False)


	def exit(self, callback=None):
		if self.rtmpgwProcess is not None:
			self.rtmpgwProcess.sendCtrlC()
		if self.download is not None:
			self._askSaveDownloadCB()
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
	
		
		
