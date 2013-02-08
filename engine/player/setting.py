'''
Created on 2.2.2013

@author: marko
'''
from Components.config import config
from Plugins.Extensions.archivCZSK import log

def loadSettings(url, download=False):
    if url.find('munkvideo') > 0:
        if download:
            DownloadMunkVideoPlayerSetting()
        else:
            MunkVideoPlayerSetting()    
    elif download:
        DownloadVideoPlayerSetting()
    else:
        DefaultVideoPlayerSetting()
        
def resetSettings():
    DefaultVideoPlayerSetting()
    

class VideoPlayerSettingsProvider(object):
    def __init__(self):
        self.__config = config.plugins.archivCZSK.videoPlayer 
    
    def setExtraHeaders(self, dictHeaders={}):
        headersString = ','.join([(key + ' ' + value) for key, value in dictHeaders.iteritems()])
        self.__config.extraHeaders.setValue(headersString)
        self.__config.extraHeaders.save()
        
    def setUserAgent(self, agent=""):
        if self.__config.servicemp4.getValue():
            if agent != "":
                self.__config.userAgent.setValue(agent)
                self.__config.userAgent.save()
        else:
            if not hasattr(config,'mediaplayer'):
                return
            if not hasattr(config.mediaplayer,'useAlternateUserAgent'):
                return
            if not hasattr(config.mediaplayer,'alternateUserAgent'):
                return
                 
            if agent != "":
                config.mediaplayer.useAlternateUserAgent.setValue(True)
                config.mediaplayer.useAlternateUserAgent.save()
                config.mediaplayer.alternateUserAgent.setValue(agent)
                config.mediaplayer.alternateUserAgent.save()
            else:
                config.mediaplayer.useAlternateUserAgent.setValue(False)
                config.mediaplayer.useAlternateUserAgent.save()
        
    def setDownloadMode(self, mode=False):
        if mode:
            self.__config.download.setValue("True")
        else:
            self.__config.download.setValue("False")
        self.__config.download.save()



class VideoPlayerSetting(object):
    def __init__(self):
        self.vpsp = VideoPlayerSettingsProvider()
        log.info("Loading %s", self.__class__.__name__)
        


class DefaultVideoPlayerSetting(VideoPlayerSetting):
    def __init__(self):
        super(DefaultVideoPlayerSetting, self).__init__()
        self.vpsp.setUserAgent("")
        self.vpsp.setExtraHeaders({})
        self.vpsp.setDownloadMode(False)
     
# Play and download mode for gstreamer
class DownloadVideoPlayerSetting(VideoPlayerSetting):
    def __init__(self):
        super(VideoPlayerSetting, self).__init__()
        self.vpsp.setDownloadMode(True)
    
    
class MunkVideoPlayerSetting(VideoPlayerSetting):
    def __init__(self):
        super(MunkVideoPlayerSetting, self).__init__()
        self.vpsp.setExtraHeaders({"Referer":"me"})


class DownloadMunkVideoPlayerSetting(VideoPlayerSetting):
    def __init__(self):
        super(DownloadMunkVideoPlayerSetting, self).__init__()
        self.vpsp.setDownloadMode(True)
        self.vpsp.setExtraHeaders({"Referer":"me"})
    
    
        
        
        

