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

import urllib2, re, os, random
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

__scriptid__ = 'plugin.video.zkouknito.cz'
__scriptname__ = 'zkouknito.cz'

BASE_URL = 'http://zkouknito.cz/'

def getContent(url, **kwargs):
	#search = kwargs['input']
	name = kwargs['name']
	p = {} 
	if url is not None:
		p = url 
	if p == {}:
		list_categories()
	if 'cat' in p.keys():
		list_category(p['cat'])
	if 'play' in p.keys():
		play(p['play'], name)

def list_categories():
	data = util.substr(util.request(BASE_URL + 'videa'), '<ul class=\"category', '</ul')
	add_dir('Online TV', {'cat':'http://www.zkouknito.cz/online-tv'})
	pattern = '<a href=\"(?P<link>[^\"]+)[^>]+>(?P<cat>[^<]+)</a>'	
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
		if m.group('cat').find('18+') > 0:
			continue
		add_dir(m.group('cat'), {'cat':BASE_URL + m.group('link')})
	#xbmcplugin.endOfDirectory(int(sys.argv[1]))

def add_video2(name, params, logo, infoLabels):
	if not logo == '':
		if logo.find('/') == 0:
			logo = logo[1:]
		if logo.find('http://') < 0:
			logo = BASE_URL + logo
	return add_video(name, params, logo, infoLabels)

def list_category(url):
	page = util.request(url)
	q = url.find('?')
	if q > 0:
		url = url[:q]
	data = util.substr(page, '<div id=\"videolist', '<div class=\"paging-adfox\">')
	pattern = '<div class=\"img-wrapper\"><a href=\"(?P<url>[^\"]+)\" title=\"(?P<name>[^\"]+)(.+?)<img(.+?)src=\"(?P<img>[^\"]+)(.+?)<p class=\"dsc\">(?P<plot>[^<]+)'
	for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
		add_video2(m.group('name'), {'play':BASE_URL + m.group('url')}, m.group('img'), {'Plot':m.group('plot')})
	data = util.substr(page, '<div class=\"jumpto\"', '</div>')
	print data
	pages = re.search('<strong>([\d]+)', data, re.IGNORECASE | re.DOTALL).group(1)
	current = re.search('value=\"([\d]+)', data, re.IGNORECASE | re.DOTALL).group(1)
	
	data = util.substr(page, '<p class=\"paging', '</p>')
	for m in re.finditer('<a href=\"(?P<url>[^\"]+)\"><img(.+?)alt=\"(?P<name>[^\"]+)\" />', data, re.IGNORECASE | re.DOTALL):
		name = '[B] %s / %s - %s [/B]' % (current, pages, m.group('name'))
		add_dir(name, {'cat':url + m.group('url')})
	#xbmcplugin.endOfDirectory(int(sys.argv[1]))

def reportUsage():
	host = 'zkounito.cz'
	tc = 'UA-1904592-29'
	xbmc.executebuiltin('RunPlugin(plugin://script.usage.tracker/?id=%s&host=%s&tc=%s&action=%s)' % (__scriptid__, host, tc, __scriptid__ + '/play'))
	util.reportUsage(__scriptid__, __scriptid__ + '/play')


def play(url, name):
	data = util.request(url)
	data = util.substr(data, '<div class=\"player\"', '</div>')
	m = re.search('<param name=\"movie\" value=\"(?P<url>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
	if not m == None:
		streams = resolver.resolve(m.group('url'))
		if streams == None:
			return
		if len(streams) > 0:
			print 'Sending %s to player' % streams[0]
			add_play(name, streams[0], filename=name)
	n = re.search('<param name=\"url\" value=\"(?P<url>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
	if not n == None:
		print 'Sending %s to player' % n.group('url')
		add_play("Video", n.group('url'), filename=name)
	
#params=util.params()
	#xbmc.executebuiltin('RunPlugin(plugin://script.usage.tracker/?do=reg&cond=31000&id=%s)' % __scriptid__)
