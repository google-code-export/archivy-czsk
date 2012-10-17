'''
Created on 17.9.2012

@author: marko
'''
from content import ContentScreen
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Label import Label
from Components.Pixmap import PixmapConditional
from Screens.MessageBox import MessageBox
from Plugins.Extensions.archivCZSK.resources.tools.items import RtmpStream, Stream, PExit, PVideo, PFolder
from Components.config import config
from Components.Button import Button
from common import MyConditionalLabel, TipBar
from content import BaseContentScreen

PLUGIN_CONFIG = config.plugins.archivCZSK
LIVE_PIXMAP = None

class StreamContentScreen(BaseContentScreen, TipBar):
    def __init__(self, session, archive, params):
        BaseContentScreen.__init__(self, session, archive, params)
        TipBar.__init__(self)
         
        self["key_red"] = Button(_("Remove"))
        self["key_green"] = Button(_("Downloads"))
        self["key_yellow"] = Button("")
        self["key_blue"] = Button(_("Settings"))

        self['archive_label'] = Label(_("Stream player"))
        self['path_label'] = Label(_("Path Label"))
        self['streaminfo_label'] = MyConditionalLabel(_("STREAM INFO"), self.isStream)
        self['streaminfo'] = MyConditionalLabel("", self.isStream)
        self['protocol_label'] = MyConditionalLabel(_("PROTOCOL:"), self.isStream)
        self['protocol'] = MyConditionalLabel("", self.isStream)
        self['playdelay_label'] = MyConditionalLabel(_("PLAY DELAY:"), self.isStream)
        self['playdelay'] = MyConditionalLabel("", self.isStream)
        self['livestream_pixmap'] = PixmapConditional()
        self['rtmpbuffer_label'] = MyConditionalLabel(_("RTMP BUFFER:"), self.isRtmpStream)
        self['rtmpbuffer'] = MyConditionalLabel("", self.isRtmpStream)
        self['playerbuffer_label'] = MyConditionalLabel(_("PLAYER BUFFER:"), self.isMipselPlayerSelected)
        self['playerbuffer'] = MyConditionalLabel("", self.isMipselPlayerSelected)      

        
        self["actions"] = NumberActionMap(["archivCZSKActions"],
            {
                "ok": self.ok,
                "up": self.up,
                "down": self.down,
                "cancel": self.cancel,
                "green" : self.openArchiveDownloads,
                "blue": self.openArchiveSettings,
                "menu": self.openContextMenu,
            }, -2)
        
        
        self["StreamAction"] = NumberActionMap(["StreamActions"],
            {
                "incBuffer": self.increaseRtmpBuffer,
                "decBuffer": self.decreaseRtmpBuffer,
                "incPlayDelay" : self.increasePlayDelay,
                "decPlayDelay" : self.decreasePlayDelay,
               # "red" : self.removeStream,
               # "refresh":self.refreshList
            }, 0)
        
        self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()
        
        self.onLayoutFinish.append(self.updateGUI)
        self.onClose.append(self.__onClose) 
    
    
    def isStream(self):
        it = self.getSelectedItem()
        return isinstance(it, PVideo)
       
    def isRtmpStream(self):
        it = self.getSelectedItem()
        return isinstance(it, PVideo) and it.url.startswith('rtmp')
    
    def isMipselPlayerSelected(self):
        it = self.getSelectedItem()
        return isinstance(it, PVideo) and PLUGIN_CONFIG.player.getValue() == 'mipsel'
    
    def updateGUI(self):
        super(StreamContentScreen, self).updateGUI()
        it = self.getSelectedItem()
        if isinstance(it, PFolder):
            pass
        else:
            stream = it.stream
            if self.isStream():
                self['protocol'].setText(self.getProtocol(it).encode('utf-8'))
                self['playdelay'].setText(str(stream.playDelay))
                self['livestream_pixmap'].instance.setPixmap(LIVE_PIXMAP)
            if self.isRtmpStream():
                self['rtmpbuffer'].setText(str(stream.rtmpBuffer))
            if self.isMipselPlayerSelected():
                self['playerbuffer'].setText(str(stream.playerBuffer))
               
        self['streaminfo_label'].update()
        self['streaminfo'].update()
        self['protocol_label'].update()
        self['protocol'].update()
        self['playdelay_label'].update()
        self['playdelay'].update()
        self['livestream_pixmap'].update()
        self['rtmpbuffer_label'].update()
        self['rtmpbuffer'].update()
        self['playerbuffer_label'].update()
        self['playerbuffer'].update()
        
    
    def up(self):
        if not self.working:
            self["menu"].up()
            self.updateGUI()
            
    def down(self):
        if not self.working:
            self["menu"].down()
            self.updateGUI()    
        
    def increaseRtmpBuffer(self):
        if not self.working:
            stream = self.selected_it.stream 
            if stream is not None and isinstance(stream, RtmpStream):
                stream.rtmpBuffer += 1000
                self['rtmpbuffer'].setText(str(stream.rtmpBuffer))
            
    def decreaseRtmpBuffer(self):
        if not self.working:
            stream = self.selected_it.stream 
            if stream is not None and isinstance(stream, RtmpStream):
                if stream.rtmpBuffer > 1000:
                    stream.rtmpBuffer -= 1000
                    self['rtmpbuffer'].setText(str(stream.rtmpBuffer))
            
    def increasePlayDelay(self):
        if not self.working:
            stream = self.selected_it.stream
            if stream is not None and isinstance(stream, Stream):
                stream.playDelay += 1
                self['playdelay'].setText(str(stream.playDelay))
            
    def decreasePlayDelay(self):
        if not self.working:
            stream = self.selected_it.stream
            if stream is not None and isinstance(stream, Stream):
                if stream.playDelay > 3:
                    stream.playDelay -= 1
                    self['playdelay'].setText(str(stream.playDelay))
                
    def askRemoveStream(self):
        it = self.getSelectedItem()
        message = _("Do you really want to remove") + it.name.encode('utf-8') + _("stream?")
        self.session.openWithCallback(self.removeStream, MessageBox, message, type=MessageBox.TYPE_YESNO)
        
    def removeStream(self, callback=None):
        if callback is not None:
            it = self.getSelectedItem()
            self.menu_dir.remove(it)
            self["menu"].getCurrentIndex()
                
    def getProtocol(self, it):
        return it.url[:it.url.find('://')].upper()
    
    def playItem(self, it, playAndDownload=False):
        from Plugins.Extensions.archivCZSK.player.player import StreamPlayer
        player = StreamPlayer(self.session, it, self.archive, config.plugins.archivCZSK.useVideoController.getValue())
        if playAndDownload:
            player.playAndDownload()
        else:
            player.play()
    
    def __onClose(self):
        self.session.nav.playService(self.oldService)
    
