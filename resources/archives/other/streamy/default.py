from xml.etree.cElementTree import ElementTree
import os

from Components.config import config
from Plugins.Extensions.archivCZSK.resources.tools.items import PFolder, PVideo, Stream, RtmpStream

PLUGIN_PATH = '/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/'
STREAM_PATH = os.path.join(PLUGIN_PATH, 'streams/streams.xml')
CONFIG = config.plugins.archivCZSK
DEBUG = CONFIG.debug.value

groups = []

def debug(data):
    if DEBUG:
        print '[Streamy]', data
    
def getContent(item, inpt=None):
    if item is not None:
        return [item.channels, None, {}]
    else:
        return [groups, None, {}]

def loadList():
    global groups
    del groups[:]
    tree = ElementTree()
    tree.parse(STREAM_PATH)
    for group in tree.findall('group'):
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
            if rtmp_buffer is None: rtmp_buffer = int(CONFIG.liveBuffer.getValue())
            if player_buffer is None: player_buffer = int(CONFIG.mipselPlayer.buffer.getValue())
            if play_delay is None: play_delay = int(CONFIG.playDelay.getValue())
            
            if stream_url.startswith('rtmp'):
                stream = RtmpStream(stream_url, playpath, page_url, swf_url, advanced)
                stream.rtmpBuffer = int(rtmp_buffer)
            else:
                stream = Stream(stream_url)
                
            stream.picon = picon
            stream.playBuffer = int(player_buffer)
            stream.playDelay = int(play_delay)
            
            it = PVideo()
            it.name = name
            it.url = stream_url
            it.live = live_stream
            it.stream = stream
            
            cat_channels.append(it)
            
        it = PFolder()
        it.name = group_name
        it.channels = cat_channels
        groups.append(it)
        
def saveList(channels):
    pass
    
    

