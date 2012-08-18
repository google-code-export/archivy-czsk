# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2011 Libor Zoubek
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

__scriptid__ = 'plugin.video.nastojaka.cz'
__scriptname__ = 'nastojaka.cz'
#__addon__      = xbmcaddon.Addon(id=__scriptid__)
#__language__   = __addon__.getLocalizedString

BASE_URL = 'http://www.nastojaka.cz/'


def getContent(url, **kwargs):
	search = kwargs['input']
	name = kwargs['name']
	p = {} 
	if url is not None:
		p = url 
	if p == {}:
		root()
	if 'show' in p.keys():
		list(p['show'])
	if 'search' in p.keys() and search:
		p['search'] = search
	if 'play' in p.keys():
		play(p['play'], name)
	search2.main(addonName, 'search_history', p, _search_cb)


def _search_cb(what):
	data = util.post(BASE_URL + 'vyhledavani', {'btnsearch':'OK', 'txtsearch':what});
	return show(data)

def furl(url):
	if url.startswith('http'):
		return url
	url = url.lstrip('./')
	return BASE_URL + url

def icon():
	return util.icon('dsadsa')
	#return os.path.join(__addon__.getAddonInfo('path'),'icon.png')

def root():
	search2.item()
	#util.add_local_dir(__language__(30037),__addon__.getSetting('downloads'),util.icon('download.png'),menuItems={__addon__.getLocalizedString(30005):{'tag-add':''}})
	add_dir(_("By date"), {'show':'scenky/?sort=date'}, icon())
	add_dir(_("By performer"), {'show':'scenky/?sort=performer'}, icon())
	add_dir(_("By rating"), {'show':'scenky/?sort=rating'}, icon())
	#xbmcplugin.endOfDirectory(int(sys.argv[1]))

def list(url):
	return show(util.request(furl(url)))

def show(page):
	data = util.substr(page, '<div id=\"search', '<hr>')
	for m in re.finditer('<div.+?class=\"scene[^>]*>.+?<img src="(?P<img>[^\"]+)\" alt=\"(?P<name>[^\"]+).+?<div class=\"sc-name\">(?P<author>[^<]+).+?<a href=\"(?P<url>[^\"]+)', data, re.IGNORECASE | re.DOTALL):
		name = "%s (%s)" % (m.group('name'), m.group('author'))
		add_video(
			name,
			{'play':m.group('url')},
			image=furl(m.group('img')),
			infoLabels={'Title':name},
			#menuItems={xbmc.getLocalizedString(33003):{'name':name,'download':m.group('url')}}
			)
	data = util.substr(page, 'class=\"pages\">', '</div>')
	next = re.search('<a href=\"(?P<url>[^\"]+)\"[^<]+<img src=\"/images/page-right.gif', data)
	prev = re.search('<a href=\"(?P<url>[^\"]+)\"[^<]+<img src=\"/images/page-left.gif', data)
	if prev:
		add_dir(_("Previous"), {'show':prev.group('url')}, util.icon('prev.png'))
	if next:
		add_dir(_("Next"), {'show':next.group('url')}, util.icon('next.png'))
	#xbmcplugin.endOfDirectory(int(sys.argv[1]))

def play(url, name):
	streams = resolve(url)
	if streams:
		#util.reportUsage(__scriptid__,__scriptid__+'/play')
		print 'Sending %s to player' % streams
		if len(streams) > 0:
			for stream in streams:
				add_play(stream['name'] + ' - ' + stream['quality'], stream['url'], filename=name)
		#li = xbmcgui.ListItem(path=stream['url'],iconImage='DefaulVideo.png')
		#xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
		#util.load_subtitles(stream['subs'])

def resolve(url):
	util.init_urllib()
	data = util.request(furl(url))	
	data = util.substr(data, '<div class=\"video', '</div>')
	resolved = resolver.findstreams(data, ['<embed( )src=\"(?P<url>[^\"]+)'])
	print resolved
	if resolved == None:
		#xbmcgui.Dialog().ok(__scriptname__,__language__(30001))
		return
	if not resolved == {}:
		return resolved
	#xbmcgui.Dialog().ok(__scriptname__,__language__(30001))

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


