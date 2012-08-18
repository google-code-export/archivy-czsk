import os, mimetypes, sys, traceback, urllib2, urlparse
import xml_archive as xmlarchive
import downloader
from xml.etree.cElementTree import ElementTree
from Components.config import config
from Tools.LoadPixmap import LoadPixmap

_pluginPath = "/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/"
GItem_lst = [[], {}] #[0] for items, [1] for commands to GUI

def getGlobalList():
    return GItem_lst
    
class PArchive(object):
    """Class for loading archive objects"""
    def __init__(self, modul):
        self.modul = modul
        self.dir = os.path.split(modul.__file__)[0]
        self.relDir = os.path.relpath(self.dir, _pluginPath)
        print '[PArchive]', self.dir
        self.id = ''
        self.id_sc = ''
        self.name = 'Unknown'
        self.author = 'Unknown'
        self.version = '0.0'
        self.about = ''
        self.type = '' #video/tv
        self.xml = None
        self.broken = False
        self.needUpdate = False
        self.image = None   
        self.changelog = None
        self.loadInfo()
        self.modul.addonName = self.id
        self.downloadsPath = os.path.join(config.plugins.archivCZSK.downloadsPath.value, self.id)
        print '[PArchive]', self.name, 'loaded'

    def loadInfo(self):
        """Loading changelog and archive info"""
        #Changelog
        changelog_path = None
        if os.path.isfile(os.path.join(self.dir, 'changelog.txt')):
            changelog_path = os.path.join(self.dir, 'changelog.txt')
        elif os.path.isfile(os.path.join(self.dir, 'Changelog.txt')):
            changelog_path = os.path.join(self.dir, 'Changelog.txt')
        else:
            changelog_path = None
        if changelog_path is not None:
            with open(changelog_path, 'r') as f:
                text = f.read()
                f.close()
            try:
                self.changelog = text.decode('iso-8859-2')
            except Exception:
                print '[PArchive] cannot decode changelog'

        #Archive info from addon.xml
        el = ElementTree()
        try:
            el.parse(os.path.join(self.dir, 'addon.xml'))
        except IOError:
            print '[PArchive] cannot load addon.xml'
        else:
                addon = el.getroot()
                self.id = self.dir.split('/')[-1]#addon.attrib.get('id')
                #self.id_sc = self.id.split('.')[-2] if self.id_sc.split('.')[-1] == 'cz' else self.id_sc.split('.')[-1]
                self.id_sc = self.id
                self.name = addon.attrib.get('name')
                self.version = addon.attrib.get('version')
                self.author = addon.attrib.get('provider-name')
                for info in addon.findall('extension'):
                    if info.attrib.get('point') == 'xbmc.addon.metadata':
                        if info.attrib.get('broken') is not None:
                            self.broken = True
                        for desc in info.findall('description'):
                            if desc.attrib.get('lang') == 'cs':
                                self.about = desc.text
                el = None
        #archive image
        try:
            self.image = LoadPixmap(cached=True, path=os.path.join(self.dir, 'icon.png'))
        except:
            print '[PArchive] cannot load archive image'
            
        #config ,type of archive and xml   
        try:    
            self.config = getattr(config.plugins.archivCZSK.archives, self.id)
            self.type = self.config.type.value
            if self.config.xml.value:
                self.xml = xmlarchive.archiveXML(self.id)
        except:
            print '[PArchive] cannot load', self.id, 'xml'
        self.xml_sc = xmlarchive.shortcutXML(self.id_sc)
        #self.json_downloads = jsonarchive.downloadJSON()
        #self.downloads = self.json_downloads.getDownloads()
        

    def getContent(self, item, inpt=None):
        del GItem_lst[0][:]
        GItem_lst[1].clear()
        url = None
        name = None
        mode = None
        page = None
        kanal = None
        if item is not None:
            url = item.url
            name = item.name.encode('utf-8') 
            mode = item.mode
            page = item.page
            kanal = item.kanal
        self.modul.getContent(url=url, name=name, mode=mode, page=page, kanal=kanal, input=inpt)
        
    
    def menuAction(self, it, input=None):
        self.getContent(it, input)
        return GItem_lst[1].copy()
       
    def open(self, params):
        it = None
        update = None
        input = None
        parent_id = None

        xml = None
        if params.has_key('update'):
            update = params["update"]
        if params.has_key('it'):
            it = params["it"]
        if params.has_key('parent_id'):
            parent_id = params["parent_id"]
        if params.has_key('input'):
            input = params["input"]           
        lst_items, date = None, None

        if it is not None and input is not None: #vyhladavanie
            print 'vyhladavanie'
            self.getContent(it, input)

        elif it is None and input is None:
            print 'otvorenie bez xml'
            self.getContent(None, None)

        elif it is not None and input is None:
            print 'otvorenie bez xml'
            self.getContent(it, None)
        lst_itemscp = [[], {}]
        lst_itemscp[0] = GItem_lst[0][:]
        lst_itemscp[1] = GItem_lst[1].copy()
        return lst_itemscp, None

    def getShortcuts(self):
        return self.xml_sc.getShortcuts()

    def createShortcut(self, it):
        return self.xml_sc.createShortcut(it)

    def removeShortcut(self, id):
        return self.xml_sc.removeShortcut(id)

    def download(self, it, startCB, finishCB, playDownload=False):
        """Downloads it PVideo item calls startCB when download starts and finishCB when download finishes"""
        d = None
        e2download = True
        quite = False
        downloadManager = downloader.DownloadManager.getInstance()
        self.downloadsPath = os.path.join(config.plugins.archivCZSK.downloadsPath.value, self.id)
        d = downloadManager.createDownload(name=it.name, url=it.url, filename=it.filename, live=it.live, destination=self.downloadsPath, e2download=e2download, startCB=startCB, finishCB=finishCB, quite=quite, playDownload=playDownload)
        if it.subs is not None:
            subsFilename = os.path.splitext(d.filename)[0] + '.srt'
            subdownload = downloadManager.createDownload(name='subtitles', url=it.subs, destination=self.downloadsPath, filename=subsFilename, e2download=e2download)
            if subdownload is not None:
                subdownload.start()
        if d is not None:
            downloadManager.addDownload(d) 
    
    def reloadSettings(self):
        #if self.config.xml.value:
            #self.xml = xmlarchive.archiveXML(self.filename)
        #else:
        self.xml = None
            
    def getXMLContent(self, it):
        return self.xml.getContent(it)
        
    def updateXMLContent(self, lst_items, parent_id):
        return self.xml.updateShowList(lst_items, parent_id)
        

class PStream(object):
    def __init__(self, url, playpath, pageUrl, swfUrl, advanced):
        self.url = url
        self.playpath = playpath
        self.pageUrl = pageUrl
        self.swfUrl = swfUrl
        self.advanced = advanced
             
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
        self.page = None
        self.kanal = None
        
class PFolder(PItem):
    def __init__(self):
        PItem.__init__(self)
        self.folder = True
        self.thumb = _pluginPath + 'gui/icon/folder.png'
        
class PVideo(PItem):
    def __init__(self):
        PItem.__init__(self)
        self.thumb = _pluginPath + 'gui/icon/movie.png'
        self.folder = False
        self.live = False 
        self.filename = None
        self.subs = None 
        self.rtmpStream = None
        self.rtmpBuffer = None
        self.timeBuffer = None
        
class PExit(PItem):
    def __init__(self):
        PItem.__init__(self)
        self.folder = True
        self.thumb = _pluginPath + 'gui/icon/up.png'
        self.name = u'..'

class PSearch(PItem):
    def __init__(self):
        PItem.__init__(self)
        self.folder = True
        self.thumb = _pluginPath + 'gui/icon/search.png'
    
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
