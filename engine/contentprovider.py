'''
Created on 3.10.2012

@author: marko
'''
import os
from twisted.internet import defer
from xml.etree.cElementTree import ElementTree

from Components.config import config

from Plugins.Extensions.archivCZSK import _
from Plugins.Extensions.archivCZSK.engine.exceptions.archiveException import CustomInfoError
from Plugins.Extensions.archivCZSK import settings
import xmlshortcuts 
from tools import task, util
from downloader import DownloadManager
from items import PVideo, PFolder, PDownload, Stream, RtmpStream, PExit



VIDEO_EXTENSIONS = ['.avi', '.mkv', '.mp4', '.flv', '.mpg', '.mpeg', '.wmv']
SUBTITLES_EXTENSIONS = ['.srt']
 

def debug(text):
    if config.plugins.archivCZSK.debug.value:
        print '[ArchivCZSK] contentprovider', text.encode('utf-8')        
        
class ContentProvider(object):
    def __init__(self, downloads_path):
        self.downloads_path = downloads_path
        
    def is_seekable(self):
        return True
    
    def is_pausable(self):
        return True
    
    def get_content(self, params={}):
        """get content from params"""
        pass
        
    def get_downloads(self):
        video_lst = []
        if not os.path.exists(self.downloads_path):
            return []
        
        downloads = os.listdir(self.downloads_path)
        for download in downloads:
            download_path = os.path.join(self.downloads_path, download)
            
            if os.path.isdir(download_path):
                continue
            
            if os.path.splitext(download_path)[1] in VIDEO_EXTENSIONS:
                filename = os.path.basename(os.path.splitext(download_path)[0])
                url = download_path
                subs = None
                if filename in [os.path.splitext(x)[0] for x in downloads if os.path.splitext(x)[1] in SUBTITLES_EXTENSIONS]:
                    subs = filename + ".srt"
                     
                it = PDownload(download_path)
                it.name = filename
                it.url = url
                it.subs = subs
                video_lst.append(it)
                
        return video_lst
    
    def remove_download(self, item):
        if item is not None and isinstance(item, PDownload):
            debug('removing item %s from disk' % item.name)
            os.remove(item.path.encode('utf-8'))
        else:
            debug('cannot remove item %s from disk, not PDownload instance' % str(item))
            
        
    def download(self, item, startCB, finishCB, playDownload=False):
        """Downloads item PVideo itemem calls startCB when download starts and finishCB when download finishes"""
        
        quiet = False
        downloadManager = DownloadManager.getInstance()
        d = downloadManager.createDownload(name=item.name, url=item.url, stream=item.stream, filename=item.filename,
                                           live=item.live, destination=self.downloads_path,
                                           startCB=startCB, finishCB=finishCB, quiet=quiet, playDownload=playDownload)
        if item.subs is not None and item.subs != '':
            debug('subtitles link: %s' % item.subs)
            subs_file_path = os.path.join(self.downloads_path, os.path.splitext(d.filename)[0] + '.srt')
            util.download_to_file(item.subs, subs_file_path)
        if d is not None:
            downloadManager.addDownload(d) 
        else:
            raise CustomInfoError(_("Cannot download") + item.name.encode('utf-8') + _("not supported protocol"))
        
class SysPath(list):
    """to append sys path only to addon which belongs to""" 
    def __init__(self, addons):
        self.addons = addons
    def append(self, val):
        for addon in self.addons:
            if val.find(addon.id) != -1:
                addon.loader.add_path(val)
    
class AddonSys():
    "sys for addons"
    def __init__(self):
        self.addons = []
        self.path = SysPath(self.addons)
    
    def __setitem__(self, key, val):
        if key == 'path':
            print 'you cannot replace AddonSysPath'
        else:
            dict.__setitem__(self, key, val)
        
    def add_addon(self, addon):
        self.addons.append(addon)
        
    def remove_addon(self, addon):
        self.addons.remove(addon)
        
    def clear_addons(self):
        self.addons = []

            

class AddonContentProvider(ContentProvider):
    
    gui_item_list = [[], None, {}] #[0] for items, [1] for command to GUI [2] arguments for command
    addon_sys = AddonSys()
        
    @staticmethod
    def clear_list():
        del AddonContentProvider.gui_item_list[0][:]
        AddonContentProvider.gui_item_list[1] = None
        AddonContentProvider.gui_item_list[2].clear()
        
    
    def __init__(self, video_addon, downloads_path, shortcuts_path):
        ContentProvider.__init__(self, downloads_path)
        self.video_addon = video_addon
        self.shortcuts = xmlshortcuts.ShortcutXML(shortcuts_path)
        
        self.dependencies = [video_addon]
        self.resolved_dependencies = False
        self.addon_sys.add_addon(video_addon)
        
    def resolve_dependecies(self, strict=False):
        from Plugins.Extensions.archivCZSK import archivczsk
        if self.resolved_dependencies:
            return
        
        self.video_addon.include()
        debug("trying to resolve dependencies for %s" % (self.video_addon))
        for dependency in self.video_addon.requires:
            addon_id, version = dependency['addon'], dependency['version']
            debug("%s requires %s addon, version %s" % (self.video_addon, addon_id, version))
            if archivczsk.ArchivCZSK.has_addon(addon_id):
                tools_addon = archivczsk.ArchivCZSK.get_addon(addon_id)
                debug("required %s founded" % tools_addon)
                if  not util.check_version(tools_addon.version, version):
                    debug("version %s>=%s" % (tools_addon.version, version))
                    self.dependencies.append(tools_addon)
                else:
                    debug("version %s<=%s" % (tools_addon.version, version))
                    if strict:
                        debug("cannot execute %s " % self.video_addon)
                        raise Exception("Cannot execute addon %s, dependency %s version %s needs to be at least version %s" 
                                        % (self.video_addon, tools_addon.id, tools_addon.version, version))
                    else:
                        debug("skipping")
                        continue
            else:
                debug("required %s addon not founded" % addon_id)
                if strict:
                    debug("cannot execute %s addon" % self.video_addon)
                    raise Exception("Cannot execute %s, missing dependency %s" % self.video_addon, addon_id)
                else:
                    debug("skipping")
        self.resolved_dependencies = True
        self.include_dependencies()
        
    def include_dependencies(self):
        for addon in self.dependencies:
            addon.include()
            self.addon_sys.add_addon(addon)
                 
    def release_dependencies(self):
        debug("trying to release dependencies for %s" % self.video_addon)
        for addon in self.dependencies:
            addon.deinclude()
        self.addon_sys.clear_addons()
        self.resolved_dependencies = False
        self.dependencies = []
      
      
      
        
    def get_content(self, session, params, successCB, errorCB):
        self.resolve_dependecies(strict=True)
        self.clear_list()
        
        debug('get_content params:%s' % str(params))
        self.content_deferred = defer.Deferred()
        self.content_deferred.addCallbacks(successCB, errorCB)
        
        thread_task = task.Task(self._get_content_cb, self.run_script, session, params)
        thread_task.run()
        return self.content_deferred
    
    def run_script(self, session, params):
        script_path = os.path.join(self.video_addon.path, self.video_addon.script)
        execfile(script_path, {'session':session, 'params':params, '__file__':script_path, 'sys':self.addon_sys, 'os':os})
        
    def _get_content_cb(self, success, result):
        debug('get_content_cb success:%s result: %s' % (success, result))
        if success:
            debug("successfully loaded %d items" % len(self.gui_item_list[0]))
            lst_itemscp = [[], None, {}]
            lst_itemscp[0] = self.gui_item_list[0][:]
            lst_itemscp[0].insert(0, PExit())
            lst_itemscp[1] = self.gui_item_list[1]
            lst_itemscp[2] = self.gui_item_list[2].copy()
            self.content_deferred.callback(lst_itemscp)
        else:
            self.content_deferred.errback(result)
            

    
    def is_seekable(self):
        return self.video_addon.get_setting('seekable')
    
    def is_pausable(self):
        return self.video_addon.get_setting('pausable')
    

    def create_shortcut(self, item):
        return self.shortcuts.createShortcut(item)

    def remove_shortcut(self, id_shortcut):
        return self.shortcuts.removeShortcut(id_shortcut)
    
    def get_shortcuts(self):
        return self.shortcuts.getShortcuts()
    
    def save_shortcuts(self):
        self.shortcuts.writeFile()
    
    
    
class StreamContentProvider(ContentProvider):
    
    def __init__(self, downloads_path, streams_path):
        ContentProvider.__init__(self, downloads_path)
        self.streams_path = streams_path
        self.stream_root = None
        self.groups = []
        self.load_streams()
        self.seekable = False
        self.pausable = False
        
    def get_content(self, item):
        if item is None:
            return self.groups
        elif isinstance(item, PFolder):
            return item.channels
        

    def load_streams(self):
        groups = []
        self.stream_root = util.load_xml(self.streams_path)
        
        for group in self.stream_root.findall('group'):
            group_name = ''
            group_name = group.findtext('name')
            cat_channels = []
        
            for channel in group.findall('channel'):    
                name = channel.findtext('name')
                stream_url = channel.findtext('stream_url')
                picon = channel.findtext('picon')
                swf_url = channel.findtext('swfUrl')
                page_url = channel.findtext('pageUrl')
                playpath = channel.findtext('playpath')
                advanced = channel.findtext('advanced')
                live_stream = channel.findtext('liveStream')
                player_buffer = channel.findtext('playerBuffer')
                rtmp_buffer = channel.findtext('rtmpBuffer')
                play_delay = channel.findtext('playDelay')
            
                if name is None or stream_url is None:
                    debug('skipping stream, cannot find name or url')
                    continue
                if picon is None: pass
                if playpath is None: playpath = u''
                if swf_url is None: swf_url = u''
                if page_url is None: page_url = u''
                if advanced is None: advanced = u''
                if live_stream is None: live_stream = True
                else: live_stream = not live_stream == 'False'
                if rtmp_buffer is None: rtmp_buffer = int(config.plugins.archivCZSK.videoPlayer.liveBuffer.getValue())
                if player_buffer is None: player_buffer = int(config.plugins.archivCZSK.videoPlayer.mipselPlayer.buffer.getValue())
                if play_delay is None: play_delay = int(config.plugins.archivCZSK.videoPlayer.playDelay.getValue())
            
                if stream_url.startswith('rtmp'):
                    stream = RtmpStream(stream_url, playpath, page_url, swf_url, advanced)
                    stream.rtmpBuffer = int(rtmp_buffer)
                else:
                    stream = Stream(stream_url)
                
                stream.picon = picon
                stream.playBuffer = int(player_buffer)
                stream.playDelay = int(play_delay)
                stream.live = live_stream
            
                it = PVideo()
                it.name = name
                it.url = stream_url
                it.live = live_stream
                it.stream = stream
                it.xml = channel
                it.root_xml = group
                cat_channels.append(it)
            
            cat_channels.insert(0, PExit())
            it = PFolder()
            it.name = group_name
            it.xml = group
            it.channels = cat_channels
            groups.append(it)
            
        groups.insert(0, PExit())
        self.groups = groups
        
    def is_seekable(self):
        return False
    
    def is_pausable(self):
        return False
            
        
    def save_streams(self):
        debug('saving streams to %s' % self.streams_path)
        ElementTree(self.xmlRootElement).write(self.streams_path)
    
    def remove_stream(self, stream):
        debug('removing stream %s' % stream.name)
        self.stream.root_xml.remove(stream.xml)
        del stream
            
    def remove_folder(self, folder):
        debug('removing folder %s' % folder.name)
        self.stream_root.remove(folder.xml)
        
        
        
