# GUI items
import os

from Plugins.Extensions.archivCZSK import settings, _
PNG_PATH = settings.IMAGE_PATH

class PContextMenuItem(object):
    def __init__(self, name, thumb, action=None, params={}):
        self.name = name
        self.thumb = thumb
        self.__action = action
        self.__kwargs = params
        
    def __eq__(self, other):
        if isinstance(other, PContextMenuItem):
            return self.name == other.name and self.__action == other.__action
        return NotImplemented
    
    def get_params(self):
        return self.__kwargs
    
    def can_execute(self):
        return self.__action != None
      
    def execute(self):
        if self.can_execute():
            self.__action(**self.__kwargs)
        

class PItem(object):
    def __init__(self):
        self.name = u''
        # parameters for addon scripts
        self.params = {}
        # info dict with supported item info (Title,Image,Rating,Genre,Plot)
        self.info = {}
        # list with PContextMenuItems for context item menu
        self.context = []
        
        self.thumb = u''
        self.image = None
        
    def add_context_menu_item(self, name, thumb=None, action=None, params={}):
        item = PContextMenuItem(name, thumb, action, params)
        if item not in self.context:
            self.context.append(item)
        
    def get_id(self):
        return str(len(self.name)) + str(len(self.params))
        
        
class PVideoAddon(PItem):
    def __init__(self, video_addon):
        PItem.__init__(self)
        self.addon = video_addon
        self.id = video_addon.get_info('id')
        self.name = video_addon.get_info('name')
        self.author = video_addon.get_info('author')
        self.description = video_addon.get_info('description')
        self.version = video_addon.get_info('version')
        self.image = video_addon.get_info('image')
        
        
class PFolder(PItem):
    def __init__(self):
        PItem.__init__(self)
        self.root = False
        self.thumb = PNG_PATH + '/folder.png'
        
        
class PVideo(PItem):
    def __init__(self):
        PItem.__init__(self)
        self.url = ""
        self.thumb = PNG_PATH + '/movie.png'
        self.live = False 
        self.filename = None
        self.subs = None 
        self.picon = None
        #stream object, can be stream/rtmp stream
        self.stream = None
        #download object, provides additional info for downloading
        self.settings = {"user-agent":{}, "extra-headers":{}}
        
    def get_protocol(self):
        return self.url[:self.url.find('://')].upper()
    
    def add_stream(self, stream):
        self.stream = stream
               
class PNotSupportedVideo(PVideo):
    def __init__(self):
        PVideo.__init__(self)
        self.thumb = PNG_PATH + '/movie_warning.png'
        
class PDownload(PVideo):
    def __init__(self, path):
        PVideo.__init__(self)
        self.path = path
        self.size = os.path.getsize(path)
        # for now we assume that all downloads succesfully finished
        self.state = 'success_finished'
        self.stateText = _('succesfully finished')
        self.start_time = None
        self.finish_time = os.path.getmtime(path)
        
        
class PExit(PFolder):
    def __init__(self):
        PFolder.__init__(self)
        self.thumb = PNG_PATH + '/up.png'
        self.name = u'..'

class PSearch(PFolder):
    def __init__(self):
        PFolder.__init__(self)
        self.thumb = PNG_PATH + '/search.png'
        
class PSearchItem(PFolder):
    def __init__(self):
        PFolder.__init__(self)
        self.thumb = PNG_PATH + '/search.png'

class Stream():
    """Additional parameters for streams"""
    def __init__(self, url):
        self.url = url
        self.live = True
        self.playerBuffer = 8000
        self.playDelay = 7


class RtmpStream(Stream):
    """Parameters for RTMP Stream"""
    def __init__(self, url, playpath, pageUrl, swfUrl, advanced):
        Stream.__init__(self, url)
        self.playpath = playpath
        self.pageUrl = pageUrl
        self.swfUrl = swfUrl
        self.rtmpBuffer = 20000
        self.advanced = advanced
        
    def getUrl(self):
        url = []
        url.append("%s" % self.url)
        if self.live: url.append("live=1")
        else: url.append("live=0")
        if self.swfUrl != "":url.append("swfUrl=%s" % self.swfUrl)
        if self.pageUrl != "":url.append("pageUrl=%s" % self.pageUrl)
        if self.playpath != "":url.append("playpath=%s" % self.playpath)
        url.append("buffer=%d" % self.rtmpBuffer)
        url.append(self.advanced)
        return ' '.join(url)
    
    def getRtmpgwUrl(self):
        url = []
        if self.live: url.append("--live")
        url.append("--rtmp '%s'" % self.url)
        if self.swfUrl != "":url.append("--swfUrl '%s'" % self.swfUrl)
        if self.pageUrl != "":url.append("--pageUrl '%s'" % self.pageUrl)
        if self.playpath != "":url.append("--playpath '%s'" % self.playpath)
        url.append("--buffer %d" % self.rtmpBuffer)
        url.append(self.advanced)
        return ' '.join(url)
