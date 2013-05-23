'''
Created on 25.9.2012

@author: marko
'''
from Screens.Screen import Screen
from Components.ProgressBar import ProgressBar
from Components.Label import Label
from Components.AVSwitch import AVSwitch
from Components.config import config
from Components.ActionMap import HelpableActionMap, ActionMap, NumberActionMap
from Components.Sources.StaticText import StaticText
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import loadPNG, RT_HALIGN_RIGHT, RT_VALIGN_TOP, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont

from Plugins.Extensions.archivCZSK import _, settings, log
from Plugins.Extensions.archivCZSK.gui.base import BaseArchivCZSKMenuListScreen
from Plugins.Extensions.archivCZSK.gui.common import PanelList

PNG_PATH = settings.IMAGE_PATH + '/'
VIDEO_PNG = PNG_PATH + 'movie.png'
PLAY_PNG = PNG_PATH + 'play.png'  

def toUTF8(text):
    if isinstance(text, unicode):
        text = text.encode('utf-8', 'ignore')
    return text

def BtoKB(byte):
    return int(float(byte) / float(1024))
    
def BtoMB(byte):
    return float(float(byte) / float(1024 * 1024))

class ArchivCZSKMoviePlayerInfobar(object):
    def __init__(self):
        self["buffer_slider"] = ProgressBar()
        self["buffer_size_label"] = Label(_("Buffer size"))
        self["buffer_size"] = Label(_("0"))
        self["buffer_label"] = Label("Buffer")
        self["buffer_state"] = Label(_("N/A"))
        self["download_label"] = Label(_("Speed"))
        self["download_speed"] = Label(_("N/A"))
        self["bitrate_label"] = Label(_("Bitrate"))
        self["bitrate"] = Label("")
        self.onFirstExecBegin.append(self.__resetBufferSlider) 
        
    def __resetBufferSlider(self):
        self["buffer_slider"].setValue(0)    
        
    def setBufferSliderRange(self, video_length):
        #doesnt work
        self["buffer_slider"].setRange([(0), (video_length)])
        
    def __updateBufferSecondsLeft(self, seconds, limit=20):
        if seconds <= limit:
            self['buffer_state'].setText("%ss" % seconds)
        else:
            self['buffer_state'].setText(">%ss" % limit)
        
    def __updateBufferPercent(self, percent):
        self['buffer_state'].setText("%s%%" % percent)
        
    def __updateBufferSize(self, size):
        self['buffer_size'].setText("%d KB" % size)
        
    def __updateBufferSlider(self, percent):
        self["buffer_slider"].setValue(percent)
        
    def __updateBitrate(self, value):
        self["bitrate"].setText("%d KB/s" % BtoKB(value))
        
    def __updateDownloadSpeed(self, speed):
        speedKB = BtoKB(speed)
        if speedKB <= 1000 and speedKB > 0:
            self['download_speed'].setText(("%d KB/s" % speedKB))
        elif speedKB > 1000:
            self['download_speed'].setText(("%.2f MB/s" % BtoMB(speed)))
        else:
            self['download_speed'].setText(("%d KB/s" % 0))
        
    def updateInfobar(self, info, bufferStateMode=0, limit=50):
        if bufferStateMode == 0:
            self.__updateBufferPercent(info['buffer_percent'])
        else:
            self.__updateBufferSecondsLeft(info['buffer_secondsleft'], limit)
        self.__updateBufferSize(info['buffer_size'])
        self.__updateDownloadSpeed(info['download_speed'])
        self.__updateBitrate(info['bitrate'])
        self.__updateBufferSlider(info['buffer_slider'])
        
        
        
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
            

class InfoBarAspectChange(object):
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

        
class PlayerSettingsSupport(object):
    def __init__(self):
        self.onPlayService.append(self.__updateSettings)
        self.__updateSettings()
        
    def __updateSettings(self):
        path = self.sref.getPath()
        headers = path.split(' ')[-1]
        headers = dict((key, value) for key, value in [head.split(':') for head in headers.split('|')])
        log.debug('[PlayerSettingsSupport] __updateSettings: %s', str(headers))
        userAgent = ''
        extraHeaders = {}
        if 'User-Agent:' in headers:
            userAgent = headers['User-Agent']
            del headers['User-Agent']
        if userAgent or extraHeaders:
            self.sref = self.__createSref()
            setting.loadSettings(userAgent, headers)
        
    def __createSref(self):
        ref = ServiceReference(self.sref)
        sid = ref.getType()
        name = ref.getName()
        path = ref.getPath()
        path = path[:path.find(path.split(' ')[-1])]
        sref = eServiceReference(sid, 0, path)
        sref.setName(name)
        return sref
    
class PlayListPanelList(PanelList):
    def __init__(self, list):
        PanelList.__init__(self, list, 35)       


def PlaylistEntry(name, png):
    res = [(name)]
    res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(32, 32), png=loadPNG(png)))
    res.append(MultiContentEntryText(pos=(55, 5), size=(580, 30), font=0, flags=RT_VALIGN_CENTER|RT_HALIGN_LEFT, text=toUTF8(name)))
    return res         
            
class Playlist(BaseArchivCZSKMenuListScreen):
    instance = None
    def __init__(self, session, title, playlist, current=0):
        Playlist.instance = self
        BaseArchivCZSKMenuListScreen.__init__(self, session, PlayListPanelList)
        self.lst_items = playlist
        self.current = current
        self["title"] = Label(title.encode('utf-8', 'ignore'))
        self["actions"] = NumberActionMap(["archivCZSKActions"],
                {
                "ok": self.ok,
                "cancel": self.cancel,
                "up": self.up,
                "down": self.down,
                }, -2)
        self.onLayoutFinish.append(self.setSelection)
        self.onClose.append(self._onClose)
    
    
    def updateMenuList(self):
        menu_list = []
        for idx, name in enumerate(self.lst_items):
            if idx != self.current:
                menu_list.append(PlaylistEntry(name, VIDEO_PNG))
            else:
                menu_list.append(PlaylistEntry(name, PLAY_PNG))
        self["menu"].setList(menu_list)
            
    def setSelection(self):
        self["menu"].moveToIndex(self.current)
            
    def ok(self):
        if len(self.lst_items) > 0:
            self.current = self["menu"].getSelectionIndex()
        self.cancel()
        
    def _onClose(self):
        Playlist.instance = None
            
    def cancel(self):
        self.close(self.current)  
    
    
class InfoBarPlaylist(object):
    """
    @param name: name of playlist
    @param playlist: list of service references
    @param nextShow: show playlist before next show should be played
    @param endShow: show playlist after end of last entry in playlist
    @param repeat: start play from beggining of playlist after end of 
                   last entry in playlist
    """
    def __init__(self, playlist, playlistCB, name=None, startShow=False, nextShow=False, endShow=False, repeat=False, showProtocol=False):
        self.__playlist = playlist
        if name is None:
            self.__name = self.__playlist[0]
        else:
            self.__name = name
        self.__repeat = repeat
        self.__endShowPlaylist = endShow
        self.__nextShowPlaylist = nextShow
        self.__showProtocol = showProtocol
        self.__callback = playlistCB
        self.__current = 0
        self.__last = len(playlist) - 1
        self["playlistShowActions"] = NumberActionMap(["DirectionActions"],
            {
             "up":self.showPlaylist,
             "down":self.showPlaylist,
              }, -2)
        
        self.__callback and self.__callback({"init":""})
        if startShow:
            self.onFirstExecBegin.append(self.showPlaylist)
        
        
    def setPlaylist(self, playlist, choice=None):
        self.__playlist = playlist
        self.__current = choice or self.__current
         
    def showPlaylist(self):
        if Playlist.instance:return
        if self.__showProtocol:
            list = ["[%s] %s" % (video.get_protocol(), video.name) for video in self.__playlist]
        else:
            list = ["%s" % (video.name) for video in self.__playlist]
        self.session.openWithCallback(self.__showPlaylistCb, Playlist, self.__name, list, self.__current)
        
    def __showPlaylistCb(self, current=None):
        log.info('[InfoBarPlaylist] %s %s', str(current), str(self.__current))
        if current is not None and self.__current != current:
            self.__current = current
            log.debug('[InfoBarPlaylist] __showPlaylistCb - [%s/%s] %s', self.__current, self.__last, self.__playlist[self.__current])
            self.__callback({'play_idx':self.__current})
        else:
            log.debug('[InfoBarPlaylist] __showPlaylistCb - same service')
            if self.session.nav.getCurrentlyPlayingServiceReference() is None:
                self.leavePlayerConfirmed((True, 'quit'))
            
    def playNext(self):
        if self.__current != self.__last:
            self.__current += 1
            log.debug('[InfoBarPlaylist] playNext - [%s/%s] %s', self.__current, self.__last, self.__playlist[self.__current])
            self.__callback({'play_idx':self.__current})
        else:
            self.__current = 0
            log.debug('[InfoBarPlaylist] playNext - [%s/%s] %s', self.__current, self.__last, self.__playlist[self.__current])
            self.__callback({'play_idx':self.__current})
            
    def doEofInternal(self, playing):
        if self.__current != self.__last or self.__repeat:
            if self.__nextShowPlaylist:
                self.showPlaylist()
            else:
                self.playNext()
        elif self.__endShowPlaylist:
            self.showPlaylist()
        else:
            self.leavePlayerConfirmed((True, 'quit'))
