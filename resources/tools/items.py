import os
PNG_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/gui/icon/"

class PContextMenuItem():
    def __init__(self, name, action, thumb=None, params={}):
        self.name = name
        self.action = action
        self.thumb = thumb
        self.params = params


class PItem(object):
    def __init__(self):
        self.name = u''
        self.url = u''
        self.url_text = u''
        self.mode = u''
        self.mode_text = u''
        self.folder = True
        self.info = {}
        self.menu = {}
        self.context_menu = []
        self.thumb = u''
        self.image = None
        self.page = None
        self.kanal = None
        
    def add_context_menu_item(self, item, action, params={}):
        item = PContextMenuItem(item, action, params)
        self.context_menu.append(item)
        
        
class PFolder(PItem):
    def __init__(self):
        PItem.__init__(self)
        self.root = False
        self.folder = True
        self.thumb = PNG_PATH + 'folder.png'
        
class PVideo(PItem):
    def __init__(self):
        PItem.__init__(self)
        self.folder = False
        self.thumb = PNG_PATH + 'movie.png'
        self.live = False 
        self.filename = None
        self.subs = None 
        self.picon = None
        #stream object, can be stream/rtmp stream
        self.stream = None
               
class PNotSupportedVideo(PVideo):
    def __init__(self):
        PVideo.__init__(self)
        self.thumb = PNG_PATH + 'movie_warning.png'
        
class PExit(PFolder):
    def __init__(self):
        PFolder.__init__(self)
        self.thumb = PNG_PATH + 'up.png'
        self.name = u'..'

class PSearch(PFolder):
    def __init__(self):
        PFolder.__init__(self)
        self.thumb = PNG_PATH + 'search.png'
    
class PDownloads():
    def __init__(self, archive):
        self.path = archive.downloadsPath
        self.videoEXT = ['.avi', '.mkv', '.mp4', '.flv', '.mpg', '.mpeg', '.wmv']
        self.subEXT = ['.srt']
        
    def getDownloads(self):
        video_lst = []
        if os.path.exists(self.path):
            lst = os.listdir(self.path)
        else:
            lst = []
        for item in lst:
            if os.path.isdir(item):
                continue
            if os.path.splitext(item)[1] in self.videoEXT:
                it = PVideo()
                it.name = unicode(os.path.splitext(item)[0], 'utf-8')
                it.url = unicode(os.path.join(self.path, item), 'utf-8')
                if os.path.splitext(item)[0] in [os.path.splitext(x)[0] for x in lst if os.path.splitext(x)[1] in self.subEXT]:
                    it.subs = os.path.splitext(item)[0] + ".srt"  
                video_lst.append(it)
        return video_lst
    
    def removeDownload(self, it):
        if it is not None:
            os.remove(it.url.encode('utf-8'))
            
            
class Stream():
    """Additional parameters for streams"""
    def __init__(self, url):
        self.url = url
        self.playerBuffer = 8000
        self.playDelay = 7


class RtmpStream(Stream):
    """Parameters for RTMP Stream"""
    def __init__(self, url, playpath, pageUrl, swfUrl, advanced):
        Stream.__init__(self, url)
        self.playpath = playpath
        self.pageUrl = pageUrl
        self.swfUrl = swfUrl
        self.rtmpBuffer = 3000
        self.advanced = advanced
        
    def getUrl(self):
        url = []
        url.append("'%s'" % self.url)
        if self.live: url.append("live=0")
        else: url.append("live=1")
        if self.swfUrl != "":url.append("swfUrl='%s'" % self.swfUrl)
        if self.pageUrl != "":url.append("pageUrl='%s'" % self.pageUrl)
        if self.playpath != "":url.append("playpath='%s'" % self.playpath)
        url.append("buffer=%d" % self.rtmpBuffer)
        url.append(self.advanced)
        return ' '.join(url)
    
    def getRtmpgwUrl(self):
        url = []
        if self.live: url.append("--live")
        url.append("--rtmp '%s'", self.url)
        if self.swfUrl != "":url.append("--swfUrl '%s'" % self.swfUrl)
        if self.pageUrl != "":url.append("--pageUrl '%s'" % self.pageUrl)
        if self.playpath != "":url.append("--playpath '%s'" % self.playpath)
        url.append("--buffer %d" % self.rtmpBuffer)
        url.append(self.advanced)
        return ' '.join(url)
