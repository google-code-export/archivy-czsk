# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2011 Ivo Brhel
# *
# *
# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# */

import re, os, urllib, urllib2, shutil, traceback
try:
    import Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools.search as search2
    import Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools.util as util
    import Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools.resolver as resolver
    from Plugins.Extensions.archivCZSK.resources.tools.doplnky import add_dir, add_video, add_play, set_command
    from Plugins.Extensions.archivCZSK.resources.exceptions import archiveException
except ImportError:
    import resources.archives.xbmc_doplnky.tools.util as util
    import resources.archives.xbmc_doplnky.tools.search as search2
    import resources.archives.xbmc_doplnky.tools.resolver as resolver
    from resources.tools.doplnky import add_dir, add_video, add_play
    from resources.exceptions import archiveException
try:
    from Plugins.Extensions.archivCZSK import _
    from Components.config import config
except ImportError:
    print 'unit test'

__scriptid__ = 'plugin.video.playserial.cz'
__scriptname__ = 'playserial.cz'


BASE_URL = 'http://www.playserial.cz/'


def getContent(url, **kwargs):
	#search = kwargs['input']
	name = kwargs['name']
	p = {} 
	if url is not None:
		p = url 
	if p == {}:
	#xbmc.executebuiltin('RunPlugin(plugin://script.usage.tracker/?do=reg&cond=31000&id=%s)' % __scriptid__)
		categories()
	if 'cat' in p.keys():
		list_cat(p['cat'])
	if 'show' in p.keys():
		list(p['show'])
	if 'play' in p.keys():
		play(p['play'], name)
#if 'download' in p.keys():
	#download(p['download'],p['name'])
#search.main(__addon__,'search_history',p,_search_cb)





def _search_cb(what):
	data = util.post(BASE_URL + 'vyhledavani', {'btnsearch':'OK', 'txtsearch':what});
	return show(data)

def furl(url):
	if url.startswith('http'):
		return url
	url = url.lstrip('./')
	return BASE_URL + url

def icon():
	return 'dsadas'


def categories():
	#search.item()
	data = util.substr(util.request(BASE_URL), '<ul>', '</ul>')
	pattern = '<li><a href=\'(?P<url>[^\']+)[^>]+>(?P<name>[^<]+)' 
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
		add_dir(m.group('name'), {'cat':furl(m.group('url'))})
	#xbmcplugin.endOfDirectory(int(sys.argv[1]))

def categories_det(page):
	data = util.substr(page, '<div class=\'obsah\'>', '</div>')
	pattern = '<a href=\'(?P<url>[^\']+)[^>]+>(?P<name>[^<]+)' 
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
		add_dir(m.group('name'), {'show':furl(m.group('url'))})
	#xbmcplugin.endOfDirectory(int(sys.argv[1]))

def list_cat(url):
	return categories_det(util.request(furl(url)))
	
def list(url):
	return show(util.request(furl(url)))

def show(page):
	data = util.substr(page, '<div class=\'obsah\'', '</div>')
	for m in re.finditer('<a href=\'(?P<url>[^\']+)[^>]+>(?P<name>[^<]+)', data, re.IGNORECASE | re.DOTALL):
		name = "%s" % (m.group('name'))
		add_video(
			name,
			{'play':m.group('url')},
			#logo=furl(m.group('img')),
			'',
			infoLabels={'Title':name},
			#menuItems={xbmc.getLocalizedString(33003):{'name':name,'download':m.group('url')}}
			)
	#xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(url, name):
	print 'URL: ' + url
	streams = resolve(url)
	if streams:
		if len(streams) > 0:
			for stream in streams:
				add_play(stream['name'] + ' - ' + stream['quality'], stream['url'], filename=name, subs=stream['subs'])

		
def resolve(url):
	util.init_urllib()
	data = util.request(furl(url))	
	data = util.substr(data, '<div class=\'obsah\'', '</div>')
	resolved = resolver.findstreams(data, ['[\"|\']+(?P<url>http://[^\"|\']+)', 'flashvars=\"file=(?P<url>[^\"]+)'])
	print resolved
	if resolved == None:
		#xbmcgui.Dialog().ok(__scriptname__, __language__(30001))
		return
	if not resolved == {}:
		return resolved
	#xbmcgui.Dialog().ok(__scriptname__, __language__(30001))

def download(url, name):
	downloads = __addon__.getSetting('downloads')
	if '' == downloads:
		xbmcgui.Dialog().ok(__scriptname__, __language__(30031))
		return
	stream = resolve(url)
	if stream:
		name += '.mp4'
		util.reportUsage(__scriptid__, __scriptid__ + '/download')
		util.download(__addon__, name, stream['url'], os.path.join(downloads, name))

#p = util.params()

