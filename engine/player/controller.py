from enigma import  eTimer
from Screens.MessageBox import MessageBox
from Components.config import config
from Plugins.Extensions.archivCZSK import _


def debug(text):
    if config.plugins.archivCZSK.debug.value:
        print '[ArchivCZSK] PlayerController', text.encode('utf-8')
    
def send_info_message(session, info, timeout=1):
    session.open(MessageBox, info, timeout=timeout, type=MessageBox.TYPE_INFO)
    
    
class Video():
    def __init__(self, session):
        self.session = session
        
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
    

class VideoPlayerController(object):
    """External Video Player Controller for video playback
    
        @param session: reference to active session for info messages
        @param download: reference for active download to control "download and play"
        @param video_check_interval: set video check interval in seconds
        @param seekable: set if video playing in videoplayer is seekable
        @param pausable: set if video playing in videoplayer is pausable 
    """
    
    instance = None
    def __init__(self, session, download=None, video_check_interval=5, buffer_time=10, seekable=True, pausable=True, autoplay=True):
        self.video_player = None
        self.session = session
        self.download = download
        
        self.seekable = seekable
        self.pausable = pausable
        self.autoplay = autoplay
        
        # buffering flag
        self._buffered = True
        
        #flag for manual pause of video
        self._user_pause = False
        
        # checking interval of video when downloading and playing
        self.video_check_interval = video_check_interval * 1000
        
        # check every second when in buffering state
        self.buffer_check_interval = 1 * 1000 
        
        # to update download status
        self.download_interval_check = self.video_check_interval
        
        # to make sure that we dont come to end of file when downloading(deadlock) we set time_limit
        self.time_limit = 5 * 90000 #5 seconds
        
        # set buffer time, its counting after time_limit
        # so realistically we have buffer of size: buffer_time + time_limit 
        self.buffer_time = buffer_time * 90000
        
        # I did couple of tests and seeking is not really precise,
        # so to make sure that we can seek when download we have seek_limit 
        self.seek_limit = 80 * 90000 
        
        # timers for checking and buffering
        self.check_timer = eTimer()
        self.check_timer.callback.append(self.check_position)
        self.check_timer.callback.append(self._update_download_status)
        self.check_timer.callback.append(self._update_info_bar)
        self.check_timer_running = False
        
        
        self.buffering_timer = eTimer()
        self.buffering_timer.callback.append(self.check_position)
        self.buffering_timer.callback.append(self._update_download_status)
        self.buffering_timer.callback.append(self._update_info_bar)
        self.buffering_timer_running = False
        
        self.buffered_percent = 0
        self.buffered_time = 0
        
        self.download_position = 0
        self.player_position = 0
        self.video_length = 0 
        self.video_length_total = 0
        
        debug('initializing %s'% self)
        
    def __repr__(self):
        return "downloading: %s, video_check_interval:%ss buffer_time: %s seekable: %s pausable: %s autoplay: %s" % \
                (self.download is not None, self.video_check_interval, self.buffer_time, self.seekable, self.pausable, self.autoplay)
        
    
    def set_video_player(self, video_player):
        self.video_player = video_player
        video_length_total = video_player.getCurrentLength()
        if video_length_total is not None:
            self.video_length_total = video_length_total
        self.update_video_length()
          
    def set_video_check_interval(self, interval):
        self.check_video_interval = interval
    
    def start_video_check(self):
        debug('starting video_checking')
        self.check_timer.start(self.video_check_interval)
        self.check_timer_running = True
        
        self.download_interval_check = self.video_check_interval
        self.check_position()
        
    def stop_video_check(self):
        debug('stopping video_checking')
        if self.check_timer_running:
            self.check_timer.stop()
            self.check_timer_running = False
        
    def start_buffer_check(self):
        debug('starting buffer_checking')
        self.buffering_timer.start(self.buffer_check_interval)
        self.buffering_timer_running = True
        
        self.download_interval_check = self.buffer_check_interval
        
    def stop_buffer_check(self):
        debug('stopping buffer_checking')
        if self.buffering_timer_running:
            self.buffering_timer.stop()
            self.buffering_timer_running = False
        
    def sec_to_pts(self, sec):
        return long(sec * 90000)
        
    def pts_to_sec(self, pts):
        return int(pts / 90000)
    
    def pts_to_hms(self, pts):
        sec = self.pts_to_sec(pts)
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        return (h, m, s)

    
    def get_download_position(self):
        download_pts = long(float(self.download.getCurrentLength()) / float(self.download.length) * self.video_length_total)
        debug('download_time: %dh:%02dm:%02ds' % self.pts_to_hms(download_pts))
        self.video_length = download_pts
        return download_pts
        
    def get_player_position(self):
        player_pts = self.video_player.getCurrentPosition()
        
        if player_pts is None:
            debug('cannot retrieve player_position')
            return None
        else:
            #debug('player_position: %lu' % player_pts)
            debug('player_time: %dh:%02dm:%02ds' % self.pts_to_hms(player_pts))
            self.player_position = player_pts
            return player_pts
    
    def update_video_length(self):
        if self.download is None or self.download.downloaded:
            if self.video_length == 0:
                video_length = self.video_player.getCurrentLength()
                if video_length is not None:
                    self.video_length = video_length
        else:
            self.video_length = self.get_download_position()
            
    def is_pts_available(self, pts):
        return pts >= 0 and pts < self.video_length
        
    def is_video_paused(self):
        return self.video_player.SEEK_STATE_PAUSE == self.video_player.seekstate
        


    def _update_download_status(self):
        self.download.status.update(self.download_interval_check / 1000)


#        Video Player Actions called by Video Controller                      
##############################################################
        
    
    def _update_info_bar(self):
        debug('updating infobar')
        
        buffering = not self._buffered
        buffered_percent = self.buffered_percent
        buffered_time = self.buffered_time
        buffered_video_length = self.video_length
        downloading = self.download.running
        download_speed = self.download.status.speed       
        self.video_player.updateInfobar(downloading=downloading,
                                        download_speed=download_speed,
                                        buffering=buffering,
                                        buffered_length=buffered_video_length,
                                        buffer_percent=buffered_percent,
                                        buffer_seconds=buffered_time
                                        )
        
    # not sure why but original MP doSeek method does nothing, so I use on seeking only doSeekRelative
    def _do_seek(self, pts):
        debug('seeking to %dh:%02dm:%02ds' % self.pts_to_hms(pts))
        self.video_player.doSeek(pts)
    
    def _do_seek_relative(self, pts):
        debug('seeking to %dh:%02dm:%02ds' % self.pts_to_hms(pts + self.player_position))
        self.video_player._doSeekRelative(pts)
        
    def _unpause_service(self):
        debug('unpausing service')
        self.video_player._unPauseService()
        
    def _pause_service(self):
        debug('pausing service')
        self.video_player._pauseService()
    
    def _do_eof_internal(self, playing):
        debug('stopping timers_eof')
        if self.check_timer_running and hasattr(self, "check_timer"):
            self.check_timer.stop()
        if self.buffering_timer_running and hasattr(self, "buffering_timer"):
            self.buffering_timer.stop()
        debug('do_eof_internal')
        self.video_player._doEofInternal(playing)
        
    def _exit_video_player(self):
        debug('stopping timers_exit')
        if self.check_timer_running:
            self.check_timer.stop()
        if self.buffering_timer_running:
            self.buffering_timer.stop()
            
        del self.check_timer
        del self.buffering_timer
        debug('exiting service')
        self.video_player._exitVideoPlayer()

#           Video Controller Actions called by Video Player
#####################################################################    
    def do_seek_relative(self, relative_pts):
        if not self.seekable:
            send_info_message(self.session, _("Its not possible to seek in this video"), 3)
        else:
            player_position = self.get_player_position()
                
            if player_position is not None:
                pts = player_position + relative_pts
                
                # whole video available
                if self.download is None or self.download.downloaded:
                    #we want to seek to pts
                    if self.is_pts_available(pts):
                        self._do_seek_relative(relative_pts)
                    else:
                        #If we are seeking over the end of the video, we end
                        if pts > self.video_length:
                            self._exit_video_player()
                        else:
                            #seek to start
                            self._do_seek_relative(-player_position)
                            
                # downloading video
                else:
                    pts_reserve = pts + self.time_limit + self.seek_limit
                    if self.is_pts_available(pts_reserve):
                        debug("position available")
                        self._do_seek_relative(relative_pts)
                    else:
                    #position is not yet available so seek where possible
                        debug("position not available")
                        if pts > self.video_length:
                            debug("trying to seek where possible...")
                            possible_seek = self.video_length - player_position - self.time_limit - self.seek_limit
                            if possible_seek > 0:
                                self._do_seek_relative(possible_seek)
                            else:
                                send_info_message(self.session, _("Cannot seek, not enough video is downloaded"), 2)
                                debug("cannot seek, not enough video is downloaded")
                        else:
                            self._do_seek_relative(-player_position)
            
            else:
                debug('seeking without control')
                self._do_seek_relative(relative_pts)
                
    def pause_service(self):
        if not self.pausable:
            send_info_message(self.session, _("Its not possible to pause this video"), 2)
        else:
            self._user_pause = True
            self._pause_service()
            
    def unpause_service(self):
        if not self._buffered:
            send_info_message(self.session, _("Cannot unpause, Video is not buffered yet..."), 2)
            #self.check_position()
        else:
            self._user_pause = False
            self._unpause_service()
            
    def exit_video_player(self):
        self._exit_video_player()
        
    def do_eof_internal(self, playing):
        self._do_eof_internal(playing)
        
############ Periodically called action by VideoController

    def check_position(self):
        """Checks if buffer is not empty. If it is then automatically pause video until buffer is not empty"""
        
        # if downloading is not finished
        if not self.download.downloaded and self.download.running:
            player_position = self.get_player_position()
            
            #we cannot retrieve player position, so we wait for next check 
            if player_position is None:
                return
            
            download_position = self.get_download_position()
            buffered_time = download_position - player_position - self.time_limit
            
            if buffered_time < 0:
                self.buffered_percent = 0
                self.buffered_time = 0 
            elif buffered_time >= self.buffer_time:
                self.buffered_percent = 100
                self.buffered_time = buffered_time
            else:
                self.buffered_percent = int(float(buffered_time) / float(self.buffer_time) * 100)
                self.buffered_time = buffered_time
            
            # We have to wait, so pause video
            if self.buffered_percent < 5:
                debug('buffering %d' % self.buffered_percent)
                self._buffered = False
                
                if not self.is_video_paused():
                    self._pause_service()
                    
                if self.check_timer_running:
                    self.stop_video_check()

                if not self.buffering_timer_running:
                    self.start_buffer_check()
                    
            # We can unpause video
            elif self.buffered_percent > 90:
                debug('buffered %d' % self.buffered_percent)
                self._buffered = True
                
                if self.is_video_paused() and not self._user_pause:
                    if self.autoplay:
                        self._unpause_service()
                
                if self.buffering_timer_running:
                    self.stop_buffer_check()
                
                if not self.check_timer_running:
                    self.start_video_check()
                    
                               
        # download finished, so stop checking timers
        else:
            self.stop_buffer_check()
            self.stop_video_check()
            self._buffered = True
            
    
        
        
