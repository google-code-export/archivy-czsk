'''
Created on 26.9.2012

@author: marko
'''

class ArchivCZSKMoviePlayer(BaseArchivCZSKScreen, InfoBarBase, InfoBarShowHide, \
        InfoBarSeek, InfoBarAudioSelection, HelpableScreen, InfoBarNotifications, \
        InfoBarServiceNotifications, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarSimpleEventView, \
        InfoBarMoviePlayerSummarySupport, \
        InfoBarServiceErrorPopupSupport, InfoBarResolutionSelection):
    
        ENABLE_RESUME_SUPPORT = True
        ALLOW_SUSPEND = True
    
        def __init__(self, session, service, subtitles):
            BaseArchivCZSKScreen.__init__(self, self)
            self.subtitles = Subtitles(session, subtitles, defaultPath=config.plugins.archivCZSK.subtitlesPath.value, forceDefaultPath=True)
            
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
                InfoBarServiceErrorPopupSupport, \
                InfoBarResolutionSelection:
                x.__init__(self)
                
            self.returning = False
            self.video_length = 0
                
            self.AVswitch = AVSwitch()
            self.defaultAVmode = self.AVswitch.getAspectRatioSetting()
            self.currentAVmode = self.defaultAVmode
            
            self.onClose.append(self._onClose)
            
            session.nav.playService(service)
                
            
        def __getSeekable(self):
            service = self.session.nav.getCurrentService()
            if service is None:
                return None
            return service.seek()
        
        def __serviceStarted(self):
            self.video_length = self.getCurrentLength()
            self.subtitles.play()
            
        
        def doSeekRelative(self, pts):
            super(ArchivCZSKMoviePlayer, self).doSeekRelative(pts)
            self.subtitles.playAfterSeek()
        
        def unPauseService(self):
            super(ArchivCZSKMoviePlayer, self).unPauseService()
            self.subtitles.resume()
        
        def pauseService(self):
            super(ArchivCZSKMoviePlayer, self).pauseService()
            self.subtitles.pause()

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
            self.handleLeave()
            
        
        def handleLeave(self):
            self.is_closing = True
            list = (
                (_("Yes"), "quit"),
                (_("No"), "continue")
                )
            from Screens.ChoiceBox import ChoiceBox
            self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, title=_("Stop playing this movie?"), list=list)
                    
        
        def aspectratioSelection(self):
            if self.currentAVmode == "1": #letterbox
                self.AVswitch.setAspectRatio(0)
                self.currentAVmode = "2"
            elif self.currentAVmode == "2": #nonlinear
                self.AVswitch.setAspectRatio(4)
                self.currentAVmode = "3"
            elif self.currentAVmode == "2": #nonlinear
                self.AVswitch.setAspectRatio(2)
                self.currentAVmode = "3"
            elif self.currentAVmode == "3": #panscan
                self.AVswitch.setAspectRatio(3)
                self.currentAVmode = "1"
                
        
        def leavePlayerConfirmed(self, answer):
            if answer == 'quit':
                if hasattr(self, 'subtitles'):
                    self.subtitles.exit()
                    del self.subtitles
                self.setSeekState(self.SEEK_STATE_PLAY) 
                self.close()
        
        def _onClose(self):
            self.AVswitch.setAspectRatio(self.defaultAVmode)
            
            
            



