# nitrogen14 - www.pristavka.de
from xml.etree.cElementTree import ElementTree
import os
import Plugins.Extensions.archivCZSK.resources.tools.util as util

iptv_list = []
groups = []

def getContent(item, inpt=None):
    if item is not None:
        return [item.channels, {}], None
    else:
    	return [groups, {}], None

def loadRTMPList():
		global iptv_list, groups
		del iptv_list[:], groups[:]
		tree = ElementTree()
		tree.parse("/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/streams/rtmplist.xml")
		group_name = 'rtmplist.xml'
		cat_channels = []
		for channel in tree.findall('stream'):		
			name = unicode(channel.findtext('title'), 'utf-8')
			stream_url = channel.findtext('link')
			rtmpdumpbuff = channel.findtext('rtmpdumpbuff')
			ebuff = channel.findtext('buffer_kb')
			timebuff = channel.findtext('timebuff')
			swf_url = channel.findtext('swfUrl')
			url = channel.findtext('pageUrl')
			playpath = channel.findtext('playpath')
			stream_obj = None
			#advanced=channel.findtext('advanced')
			#if advanced is None:
			#		advanced=' '
			
			if stream_url[0:4] == 'rtmp':
				stream_dict = {}
				stream_dict['url'] = stream_url
				stream_dict['playpath'] = playpath
				stream_dict['swf_url'] = swf_url
				stream_dict['page_url'] = url
				stream_dict['advanced'] = ''
				stream_url = stream_url + ' live=1 playpath=' + playpath + ' swfUrl=' + swf_url + ' pageUrl=' + url + ' '#+advanced
			
			stream_it = util.PVideo()
			stream_it.name = name
			stream_it.url = stream_url
			stream_it.live = True
			stream_it.stream = stream_obj
			stream_it.rtmpBuffer = rtmpdumpbuff
			stream_it.ebuff = ebuff

			cat_channels.append(stream_it)
		it = util.PFolder()
		it.name = group_name
		it.url = None
		it.channels = cat_channels	
		groups.append(it)

def loadList():
		global iptv_list, groups
		del iptv_list[:], groups[:]
		tree = ElementTree()
		tree.parse("/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/streams/streams.xml")
		for group in tree.findall('group'):
			group_name = ''
			group_name = unicode(group.findtext('name'), 'utf-8')
			cat_channels = []
			chan_id = 0
			for channel in group.findall('channel'):	
				name = unicode(channel.findtext('name'), 'utf-8')
				stream_url = channel.findtext('stream_url')
		#		ts_stream = channel.findtext('ts_stream')
				rtmpdumpbuff = channel.findtext('rtmpdumpbuff')
				ebuff = channel.findtext('buffer_kb')
				timebuff = channel.findtext('timebuff')
				swf_url = channel.findtext('swfUrl')
				url = channel.findtext('pageUrl')
				playpath = channel.findtext('playpath')
				advanced = channel.findtext('advanced')
				stream_obj = None
				if advanced is None:
					advanced = ' '
					
				if stream_url[0:4] == 'rtmp':
					stream_obj = util.PStream(stream_url, playpath, url, swf_url, advanced)
					stream_url = stream_url + ' live=1 playpath=' + playpath + ' swfUrl=' + swf_url + ' pageUrl=' + url + ' ' + advanced
					
				stream_it = util.PVideo()
				stream_it.name = name
				stream_it.url = stream_url
				stream_it.live = True
				stream_it.stream = stream_obj
				stream_it.rtmpBuffer = rtmpdumpbuff
				stream_it.ebuff = ebuff
				
				#iptv_list.append(chan_tulpe)
				cat_channels.append(stream_it)
			it = util.PFolder()
			it.name = group_name
			it.channels = cat_channels
			groups.append(it)

