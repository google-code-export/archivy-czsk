'''
Created on 2.2.2013

@author: marko
'''
from Components.config import config, ConfigInteger, ConfigSubsection, ConfigYesNo, ConfigText
from Plugins.Extensions.archivCZSK import log
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0'

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
        
    def setHTTPTimeout(self, timeout):
        self.__config.httpTimeout.setValue(str(timeout))
        self.__config.httpTimeout.save()
    
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
            # servicemp3 uses config.mediaplayer.alternateUserAgent to set UserAgent for gstreamer
            if not hasattr(config, 'mediaplayer'):
                config.mediaplayer = ConfigSubsection()
                config.mediaplayer.useAlternateUserAgent = ConfigYesNo(default=True)
                config.mediaplayer.alternateUserAgent = ConfigText(default="")
            if not hasattr(config.mediaplayer, 'useAlternateUserAgent'):
                config.mediaplayer.useAlternateUserAgent = ConfigYesNo(default=True)
            if not hasattr(config.mediaplayer, 'alternateUserAgent'):
                config.mediaplayer.alternateUserAgent = ConfigText(default="")
                 
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
        self.vpsp.setUserAgent(USER_AGENT)
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
    
    
        
        
        

