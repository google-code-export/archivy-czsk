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

import re, os, urllib
try:
    import Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools.util as util
    import Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools.resolver as resolver
    from Plugins.Extensions.archivCZSK.resources.tools.doplnky import add_dir, add_video, add_play, set_command
except ImportError:
    import resources.archives.xbmc_doplnky.tools.util as util
    import resources.archives.xbmc_doplnky.tools.resolver as resolver
    from resources.tools.doplnky import add_dir, add_video, add_play
try:
    from Plugins.Extensions.archivCZSK import _
except ImportError:
    print 'unit test'

__scriptid__ = 'plugin.video.re-play.cz'
__scriptname__ = 're-play.cz'
#__addon__      = xbmcaddon.Addon(id=__scriptid__)
#__language__   = __addon__.getLocalizedString

BASE_URL = 'http://re-play.cz/category/videoarchiv/'

def getContent(url, **kwargs):
    name = kwargs['name'] 
    p = {} 
    if url is not None:
        p = url   
    if p == {}:
        list_page()
    if 'page' in p.keys():
        list_page(p['page'])
    if 'play' in p.keys():
        play(p['play'], name)


def list_page(number= -1):
        url = BASE_URL
        if number > 0:
                url += 'page/' + str(number)
        page = util.request(url)
        data = util.substr(page, '<div id=\"archive', 'end #archive')
        pattern = '<div class=\"cover\"><a href=\"(?P<url>[^\"]+)(.+?)title=\"(?P<name>[^\"]+)(.+?)<img src=\"(?P<logo>[^\"]+)(.+?)<p class=\"postmetadata\">(.+?)<p>(?P<plot>[^<]+)'
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
                name = ('%s' % (m.group('name')))
                add_video(
                        name,
                        {'play':m.group('url')},
                        m.group('logo'),
                        {'Plot':m.group('plot')}
                        #menuItems={xbmc.getLocalizedString(33003):{'name':name+'.mp4','download':m.group('url')}}
                )
        data = util.substr(page, '<div class=\"navigation\">', '</div>')
        for m in re.finditer('<a href=\"(.+?)/page/(?P<page>[\d]+)', data, re.IGNORECASE | re.DOTALL):
                name = 'Na stranu %s' % m.group('page')
                add_dir(name, {'page':m.group('page')})

def resolve(url):
        data = util.substr(util.request(url), '<div class=\"zoomVideo', '</div>')
        resolved = resolver.findstreams(data, ['<object(.+?)data=\"(?P<url>http\://www\.youtube\.com/v/[^\&]+)'])
        if resolved == None:
                return None
        if not resolved == []:
               # print resolved
               return resolved

def play(url,name):
        streams = resolve(url)
        if streams:
            if len(streams) > 0:
                for stream in streams:
                    add_play(stream['name'] + ' - ' + stream['quality'], stream['url'], filename=name)
