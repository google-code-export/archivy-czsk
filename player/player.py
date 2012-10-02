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


from subtitles.subtitles import Subtitles
from controller import VideoPlayerController
from infobar import CustomPlayerInfobar

from Plugins.Extensions.archivCZSK import _
from Plugins.Extensions.archivCZSK.resources.tools.util import RtmpStream
from Plugins.Extensions.archivCZSK.resources.exceptions.archiveException import CustomInfoError
from Plugins.Extensions.archivCZSK.gui.base import BaseArchivCZSKScreen

def debug(data):
	if config.plugins.archivCZSK.debug.getValue():
		print '[ArchivCZSK] Player:', data.encode('utf-8')

RTMPGW_PATH = '/usr/bin/rtmpgw'
NETSTAT_PATH = 'netstat'


class ArchivCZSKMoviePlayer(BaseArchivCZSKScreen, CustomPlayerInfobar, InfoBarBase, InfoBarShowHide, \
		InfoBarSeek, InfoBarAudioSelection, HelpableScreen, InfoBarNotifications, \
		InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarSimpleEventView, \
		InfoBarMoviePlayerSummarySupport, \
		InfoBarServiceErrorPopupSupport):
	
		ENABLE_RESUME_SUPPORT = True
		ALLOW_SUSPEND = True
	
		def __init__(self, session, service, subtitles, useCustomInfobar=False):
			BaseArchivCZSKScreen.__init__(self, session)
			if self.HD:
				self.setSkin("ArchivCZSKMoviePlayer_HD")
			else:
				self.setSkin("ArchivCZSKMoviePlayer_SD")
			
			CustomPlayerInfobar.__init__(self)
			self.__subtitles = Subtitles(session, subtitles, defaultPath=config.plugins.archivCZSK.subtitlesPath.value, forceDefaultPath=True)
			self["actions"] = HelpableActionMap(self, "ArchivCZSKMoviePlayerActions",
            {
                "aspectChange": (self.aspectratioSelection, _("changing aspect Ratio")),
                "subtitles": (self.subtitlesSetup, _("show/hide subtitles")),
                "leavePlayer": (self.leavePlayer, _("leave player?"))
            }, 0) 
			
			self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
			{
				iPlayableService.evStart: self.__serviceStarted,
			})
			

			for x in HelpableScreen, InfoBarShowHide, \
				InfoBarBase, InfoBarSeek, \
				InfoBarAudioSelection, InfoBarNotifications, InfoBarSimpleEventView, \
				InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, \
				InfoBarMoviePlayerSummarySupport, \
				InfoBarServiceErrorPopupSupport:
				x.__init__(self)
			
			self.session = session
			self.service = service
				
			self.returning = False
			self.video_length = 0
				
			self.AVswitch = AVSwitch()
			self.defaultAVmode = self.AVswitch.getAspectRatioSetting()
			self.currentAVmode = self.defaultAVmode
			
			self.onClose.append(self._onClose)
			
			
		def _play(self):	
			self.session.nav.playService(self.service)
			
		def __getSeekable(self):
			service = self.session.nav.getCurrentService()
			if service is None:
				return None
			return service.seek()
		
		def __serviceStarted(self):
			self.video_length = self.getCurrentLength()
			#not working
			#self.setBufferSliderRange(self.video_length)
			self.__subtitles.play()
		
		def doSeekRelative(self, pts):
			super(ArchivCZSKMoviePlayer, self).doSeekRelative(pts)
			self.__subtitles.playAfterSeek()
		
		def unPauseService(self):
			super(ArchivCZSKMoviePlayer, self).unPauseService()
			self.__subtitles.resume()
		
		def pauseService(self):
			super(ArchivCZSKMoviePlayer, self).pauseService()
			self.__subtitles.pause()
			
		def subtitlesSetup(self):
			self.__subtitles.setup() 

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
			if self.currentAVmode == 0: #letterbox
				self.AVswitch.setAspectRatio(0)
				self.currentAVmode = 2
			elif self.currentAVmode == 2: #nonlinear
				self.AVswitch.setAspectRatio(4)
				self.currentAVmode = 3
			elif self.currentAVmode == 2: #nonlinear
				self.AVswitch.setAspectRatio(2)
				self.currentAVmode = 3
			elif self.currentAVmode == 3: #panscan
				self.AVswitch.setAspectRatio(3)
				self.currentAVmode = 0
				
		
		def leavePlayerConfirmed(self, answer):
			if answer == 'quit':
				self.exitVideoPlayer()
				
		def exitVideoPlayer(self):
			if hasattr(self, '_ArchivCZSKMoviePlayer__subtitles'):
				self.__subtitles.exit()
				del self.__subtitles
			self.setSeekState(self.SEEK_STATE_PLAY) 
			self.close()
		
		def _onClose(self):
			self.AVswitch.setAspectRatio(self.defaultAVmode)


class StandardVideoPlayer(MoviePlayer):
	"""Standard MoviePlayer without any modifications"""
	def __init__(self, session, sref):
		MoviePlayer.__init__(self, session, sref)
		self.skinName = "MoviePlayer"   
			
		
class CustomVideoPlayer(ArchivCZSKMoviePlayer, CustomPlayerInfobar):
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
	
	def __serviceStarted(self):
		self.videoPlayerController.set_video_player(self)
		if self.playAndDownload and self.useVideoController:
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
		if answer == 'quit':
			self._exitVideoPlayer()
		
	def exitVideoPlayer(self, message=None):
		if message is not None and self.videoPlayerController is not None:
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
		buffer_percent = self.bufferPercent
		video_length = self.getCurrentLength()
		buffer_length = video_length + (self.bufferSeconds * 90000)
		self.updateInfobar(downloading=downloading, buffering=buffering, buffered_length=buffer_length, buffer_percent=buffer_percent)
		
	
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
		del self.updateTimer
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
		
		
			

			
class Player():
	"""Player for playing PVideo it content"""
	def __init__(self, session, it=None, archive=None, callback=None, useVideoController=False):
		self.session = session
		self.port = 8902 # streaming port for rtmpgw
		self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
		
		#if we are playing and downloading
		self.download = None
		self.rtmpgwProcess = None
		
		#default player settings
		self.archive = None
		self.seekable = True
		self.pausable = True
		self.playDelay = int(config.plugins.archivCZSK.playDelay.getValue())
		self.autoPlay = config.plugins.archivCZSK.mipselPlayer.autoPlay.getValue()
		self.playerBuffer = int(config.plugins.archivCZSK.mipselPlayer.buffer.getValue())
		self.useVideoController = useVideoController 
		
		if archive is not None:
			self.setArchive(archive)
			
		self.it = None
		self.name = u'unknown stream'
		self.subtitles = None
		self.playUrl = None
		self.picon = None
		self.live = False
		self.rtmpBuffer = 20000
		self.stream = None
		
		if it is not None:
			self.setVideoItem(it)	
		
		# what is live is not seekable and pausable		
		if self.live:
			self.seekable = False
			self.pausable = False
	
		#setting ContentScreen callback		
		self.callback = callback
			
		#to make sure that rtmpgw is not running (ie. player crashed)	
		os.system('killall rtmpgw')
					
	
	def setArchive(self, archive):
		self.archive = archive
		self.seekable = archive.seekable
		self.pausable = archive.pausable
		
	def setVideoItem(self, it):
		#loading video item
		self.it = it
		self.name = it.name
		self.subtitles = it.subs
		self.playUrl = it.url
		self.picon = it.picon
		self.live = it.live
		
		if it.stream is not None:
			self.stream = it.stream
			
		if self.stream is None and self.live:
			self.rtmpBuffer = int(config.plugins.archivCZSK.liveBuffer.getValue())
			
		elif self.stream is None and not self.live:
			self.rtmpBuffer = int(config.plugins.archivCZSK.archiveBuffer.getValue())
	
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
				if config.plugins.archivCZSK.seeking.getValue():
					if self.stream is not None:
						self._playStream(self.stream.getUrl(), self.subtitles)
					else:
						self._playStream(str(self.playUrl + ' buffer=' + str(self.rtmpBuffer)), self.subtitles)
						
				# internal player doesnt have rtmp support so we use rtmpgw
				else:
					self.seekable = False
					self._startRTMPGWProcess()
					self._playStream('http://0.0.0.0:' + str(self.port), self.subtitles)
			
			# not rtmp stream
			else:
				self._playStream(str(self.playUrl), self.subtitles)
		else:
			debug("nothing to play. You need to set play Item first.")
			
			
	def playAndDownload(self):
		"""starts downloading and then playing after playDelay value"""
		from Plugins.Extensions.archivCZSK.gui.download import DownloadManagerMessages
		if self.archive is None:
			debug('cannot download.. You need to set your archive first')
			return
		try:
			self.archive.download(self.it, self._showPlayDownloadDelay, DownloadManagerMessages.finishDownloadCB, playDownload=True)
		except CustomInfoError as er:
			self.session.open(MessageBox, er, type=MessageBox.TYPE_ERROR, timeout=3)		
		
			
	def playDownload(self, download):
		"""starts playing already downloading item"""
		from Plugins.Extensions.archivCZSK.resources.tools.downloader import Download
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
		
		sref = eServiceReference(4097, 0, streamURL)
		sref.setName(self.name.encode('utf-8'))
		
		videoPlayerSetting = config.plugins.archivCZSK.player.getValue()
		videoPlayerController = VideoPlayerController(self.session, download=self.download, \
													 seekable=self.seekable, pausable=self.pausable)
		
		
		if videoPlayerSetting == 'standard':
			self.session.openWithCallback(self.exit, StandardVideoPlayer, sref, videoPlayerController)
		
		elif videoPlayerSetting == 'custom':
			self.session.openWithCallback(self.exit, CustomVideoPlayer, sref, videoPlayerController, \
										 self.useVideoController, playAndDownload, subtitlesURL)
		elif videoPlayerSetting == 'mipsel':
			self.session.openWithCallback(self.exit, MipselVideoPlayer, sref, videoPlayerController, self.autoPlay, \
										 self.playerBuffer, self.useVideoController, playAndDownload, subtitlesURL)
		else:
			debug("unknown videoplayer %s" % videoPlayerSetting)
		
			
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
			
		self.session.nav.stopService()
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
				from Plugins.Extensions.archivCZSK.resources.tools.downloader import DownloadManager             
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
		if self.callback:
			self.callback()
	
		
		
