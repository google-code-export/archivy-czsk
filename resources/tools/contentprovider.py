'''
Created on 3.10.2012

@author: marko
'''
import os
from xml.etree.cElementTree import ElementTree
from twisted.internet import defer
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigYesNo, ConfigText, configfile, getConfigListEntry
from Tools.LoadPixmap import LoadPixmap

from Plugins.Extensions.archivCZSK import _
from Plugins.Extensions.archivCZSK.resources.exceptions.archiveException import CustomInfoError
from task import Task as TaskInThread
from downloader import DownloadManager
from items import PVideo
import Plugins.Extensions.archivCZSK.resources.archives.config as archive_config
import xml_archive as xmlarchive
import util2 as util

PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/"
VIDEO_EXTENSIONS = ['.avi', '.mkv', '.mp4', '.flv', '.mpg', '.mpeg', '.wmv']
SUBTITLES_EXTENSIONS = ['.srt']
 

def debug(text):
    if config.plugins.archivCZSK.debug.value:
        print '[ArchivCZSK] Archive', text.encode('utf-8')
        
class Archive(object):
    resolving_archive = None
    gui_item_list = [[], None, {}] #[0] for items, [1] for command to GUI [2] arguments for command
    
    @staticmethod
    def clear_list():
        del Archive.gui_item_list[0][:]
        Archive.gui_item_list[1] = None
        Archive.gui_item_list[2].clear()
        
    def __init__(self, modul):
        self.modul = modul
        self.name = u'Unknown'
        self.version = u'0.0'
        self.type = u'tv'
        self.broken = False
        self.need_update = False
        self.dir = os.path.split(modul.__file__)[0]
        self.rel_dir = os.path.relpath(self.dir, PLUGIN_PATH)
        self.id = self.dir.split('/')[-1]
        files = []
        
        # info
        self.info = ArchiveInfo(self, os.path.join(self.dir, 'addon.xml'))

        # lang strings
        try:
            lang = util.load_module(os.path.join(self.dir, 'language.py'))
        except Exception, e:
            debug("not using language file")
            self.language = None
        else:
            self.language = lang.strings
            lang = None
        
        # settings
        self.settings = ArchiveSettings(self, os.path.join(self.dir, 'settings.xml'))
        self.settings.initialize()
 
        #shortcuts
        self.xml_sc = xmlarchive.shortcutXML(self.id)
            
        debug('Archive: "%s" ver: %s successfully loaded' % (self.name, self.version))
        
 
        
    def get_localized_string(self, id):
        if self.language is not None and id in self.language:
            return self.language[id]
        else:
            debug("cannot get localized string, missing language.py or is corrupted")
            return str(id)
    
    def get_settings(self, setting):
        setting = getattr(self.settings.main, '%s' % setting)
        return getattr(setting, 'value', setting)
    
    def get_info(self, info):
        try:
            atr = getattr(self.info, '%s' % info)
        except Exception:
            debug("get_info cannot retrieve info")
            return None
        else:
            return atr
    
     
    def create_shortcut(self, item):
        return self.xml_sc.createShortcut(item)

    def remove_shortcut(self, id):
        return self.xml_sc.removeShortcut(id)
    
    def get_shortcuts(self):
        return self.xml_sc.getShortcuts()
            
    def get_downloads(self):
        downloads_path = config.plugins.archivCZSK.downloadsPath.value
        video_lst = []
        if os.path.exists(downloads_path):
            lst = os.listdir(downloads_path)
        else:
            lst = []
        for item in lst:
            if os.path.isdir(item):
                continue
            if os.path.splitext(item)[1] in VIDEO_EXTENSIONS:
                it = PVideo()
                it.name = unicode(os.path.splitext(item)[0], 'utf-8')
                it.url = unicode(os.path.join(self.path, item), 'utf-8')
                if os.path.splitext(item)[0] in [os.path.splitext(x)[0] for x in lst if os.path.splitext(x)[1] in SUBTITLES_EXTENSIONS]:
                    it.subs = os.path.splitext(item)[0] + ".srt"  
                video_lst.append(it)
        return video_lst
    
    def remove_download(self, it):
        if it is not None:
            debug('removing download')
            os.remove(it['params'].encode('utf-8'))
        
    def download(self, it, startCB, finishCB, playDownload=False):
        """Downloads it PVideo item calls startCB when download starts and finishCB when download finishes"""
        
        quiet = False
        downloadManager = DownloadManager.getInstance()
        self.downloadsPath = os.path.join(config.plugins.archivCZSK.downloadsPath.value, self.id)
        d = downloadManager.createDownload(name=it.name, url=it.url, stream=it.stream, filename=it.filename, \
                                           live=it.live, destination=self.downloadsPath, \
                                           startCB=startCB, finishCB=finishCB, quiet=quiet, playDownload=playDownload)
        if it.subs is not None:
            subsFilename = os.path.split(os.path.splitext(d.filename)[0] + '.srt')[1]
            subdownload = downloadManager.createDownload(name='subtitles', url=it.subs, destination=self.downloadsPath, \
                                                          filename=subsFilename)
            if subdownload is not None:
                subdownload.start()
        if d is not None:
            downloadManager.addDownload(d) 
        else:
            raise CustomInfoError(_("Cannot download") + it.name.encode('utf-8') + _("not supported protocol"))
        
        
    def openItem(self, session, it):
        pass
    
    def do_archive_action(self, session, params):
        self.content_deferred = defer.Deferred()
        thread_task = TaskInThread(self._get_content_cb, self.modul.getContent, session, params)
        thread_task.run()
        
        
    
    def get_content(self, session, params):
        Archive.resolving_archive = self
        debug('get_content params:%s' % str(params))
        self.content_deferred = defer.Deferred()
        thread_task = TaskInThread(self._get_content_cb, self.modul.getContent, session, params)
        thread_task.run()
        return self.content_deferred
        
    def _get_content_cb(self, success, result):
        Archive.resolving_archive = None
        debug('get_content_cb success:%s result: %s' % (str(success), str(result)))
        if success:
            self.content_deferred.callback(self.gui_item_list)
        else:
            self.content_deferred.errback(result)
            
     
     
class ArchiveSettings(object):
    def __init__(self, archive, settings_file):
        debug("initializing settings")
        
        self.archive = archive
        self.main = getattr(config.plugins.archivCZSK.archives, archive.id)
        self.entries = []
        self.categories = []
        
        el = util.load_xml(settings_file)
        if el is not None:
            settings = el.getroot()
            main_category = {'label':'general', 'subentries':[]}
            
            for category in settings.findall('category'):
                entry = {'label':category.attrib.get('label'), 'subentries':[]}
                for setting in category.findall('setting'):
                    entry['subentries'].append(self.get_setting_entry(setting))
                self.entries.append(entry)
                
            for setting in settings.findall('setting'):
                main_category['subentries'].append(self.get_setting_entry(setting))
            
            self.entries.append(main_category)
            el = None
            
    def initialize(self):
        for entry in self.entries:
            if entry['label'] == 'general': 
                if len(entry['subentries']) == 0 :
                    continue
                else:
                    category = {'label':'general', 'subentries':[]}
            else:
                category = {'label':self.get_label(entry['label']), 'subentries':[]}
                
            for subentry in entry['subentries']:
                self.initialize_entry(self.main, subentry)
                category['subentries'].append(getConfigListEntry(self.get_label(subentry['label']), subentry['setting_id']))
            debug("initialized category %s" % str(category))
            self.categories.append(category)                                      

                
                    
    def get_configlist_categories(self):
        return self.categories
             
       
    def get_setting_entry(self, setting):
        entry = {}
        entry['label'] = setting.attrib.get('label')
        entry['id'] = setting.attrib.get('id')
        entry['type'] = setting.attrib.get('type')
        entry['default'] = setting.attrib.get('default')
        if entry['type'] == 'enum':
            entry['lvalues'] = setting.attrib.get('lvalues')
        debug("getting entry from xml %s" % str(entry))
        return entry
    
    def get_label(self, label):
        try:
            string_id = int(label)
        except ValueError:
            
            if isinstance(label, unicode):
                return label
            
            encodings = ['utf-8', 'windows-1250', 'iso-8859-2']
            for encoding in encodings:
                try:
                    return label.decode(encoding)
                except:
                    if encoding == encodings[-1]:
                        debug("getlabel cannot decode string")
                        return 'cannot_decode'
                    else:
                        continue
        else:
            label = self.archive.get_localized_string(string_id)
            return label
            
    
    def initialize_entry(self, setting, entry):
        if entry['type'] == 'bool':
            setattr(setting, entry['id'], ConfigYesNo(default=(entry['default'] == 'true')))
            entry['setting_id'] = getattr(setting, entry['id'])
        elif entry['type'] == 'text':
            setattr(setting, entry['id'], ConfigText(default=entry['default'], fixed_size=False))
            entry['setting_id'] = getattr(setting, entry['id'])
        elif entry['type'] == 'enum':
            choicelist = [(str(idx), self.get_label(e)) for idx, e in enumerate(entry['lvalues'].split("|"))]
            setattr(setting, entry['id'], ConfigSelection(default=entry['default'], choices=choicelist))
            entry['setting_id'] = getattr(setting, entry['id'])
        else:
            debug('cannot initialize unknown entry %s' % entry['type'])


class ArchiveInfo(object):
    def __init__(self, archive, info_file):
        debug("initializing info")
        self.archive = archive
        self.name = u"Unknown"
        self.version = u"0.0"
        self.author = u'Unknown'
        self.description = u""
        self.changelog = u"" 
        self.dir = archive.dir
        self.path = self.dir
        self.rel_dir = archive.rel_dir
        self.image = LoadPixmap(cached=True, path=os.path.join(self.dir, 'icon.png'))
        
        el = util.load_xml(info_file)
        if el is not None:
            addon = el.getroot()
            self.id = self.dir.split('/')[-1]
            self.name = addon.attrib.get('name')
            self.archive.name = self.name
            self.version = addon.attrib.get('version')
            self.archive.version = self.version
            self.author = addon.attrib.get('provider-name')
            for info in addon.findall('extension'):
                if info.attrib.get('point') == 'xbmc.addon.metadata':
                    if info.attrib.get('broken') is not None:
                        self.broken = True
                    for desc in info.findall('description'):
                        if desc.attrib.get('lang') == 'cs':
                            self.description = desc.text
    
            el = None
    
        #changelog
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
                self.changelog = text.decode('windows-1250')
            except Exception, e:
                debug("cannot decode changelog: %s" % str(e))
        

class DmdArchive(Archive):
    def openItem(self, session, item=None):
        self.clear_list()
        
        params = {}
        if item is not None:
            params['url'] = item.url
            params['name'] = item.name.encode('utf-8') 
            params['mode'] = item.mode
            params['page'] = item.page
            params['kanal'] = item.kanal
        return self.get_content(session, params)
        
        
class DoplnkyArchive(Archive):
    def openItem(self, session, item=None):
        self.clear_list()
        
        params = {}
        if item is not None:
            params=item.params
        return self.get_content(session, params)
        
        
