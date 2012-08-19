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

import re, os, urllib, urllib2
try:
    import Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools.search as search2
    import Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools.util as util
    from Plugins.Extensions.archivCZSK.resources.tools.doplnky import add_dir, add_video, add_play
    from Plugins.Extensions.archivCZSK.resources.exceptions import archiveException
except ImportError:
    import resources.archives.xbmc_doplnky.tools.util as util
    import resources.archives.xbmc_doplnky.tools.search as search2
    from resources.tools.doplnky import add_dir, add_video, add_play
    from resources.exceptions import archiveException
try:
    from Plugins.Extensions.archivCZSK import _
    from Components.config import config
except ImportError:
    print 'Unit test'

__scriptid__ = 'plugin.video.bezvadata.cz'
__scriptname__ = 'bezvadata.cz'

def getContent(url, **kwargs): 
    p = {}
    search=kwargs['input'] 
    if url is not None:
        p = url
    if p == {}:
        categories()
    if 'stats' in p.keys():
        stats(p['stats'])
    if 'play' in p.keys():
        play(p['play'])
    if 'list' in p.keys():
        parse_page(util.request(p['list']))
    if 'search' in p.keys() and search:
        p['search'] = search
   # if 'download' in p.keys():
    #    download(p['download'],p['name'])
    search2.main(addonName, 'search_history', p, _search_cb)             


BASE_URL = 'http://bezvadata.cz/'

def _search_cb(what):
        url = BASE_URL + 'vyhledavani/?s=' + what.replace(' ', '+')
        page = util.request(url)
        return parse_page(page)

def parse_page(page):
        ext_filter = create_filter()
        ad = re.search('<a href=\"(?P<url>/vyhledavani/souhlas-zavadny-obsah[^\"]+)', page, re.IGNORECASE | re.DOTALL)
        if ad and config.plugins.archivCZSK.archives.bezvadata.adult.value:
                page = util.request(furl(ad.group('url')))
        data = util.substr(page, '<div class=\"content', '<div class=\"stats')
        pattern = '<section class=\"img[^<]+<a href=\"(?P<url>[^\"]+)(.+?)<img src=\"(?P<img>[^\"]+)\" alt=\"(?P<name>[^\"]+)(.+?)<b>velikost:</b>(?P<size>[^<]+)'
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
                if can_show(ext_filter, m.group('name')):
                        iurl = furl(m.group('url'))
                        name = '%s (%s)' % (m.group('name'), m.group('size').strip())
                        add_video(
                                name,
                                {'play':iurl}, m.group('img'),
                                infoLabels={'Title':m.group('name')},
                               # menuItems={xbmc.getLocalizedString(33003):{'name':m.group('name'),'download':iurl}}
                        )
        data = util.substr(page, '<div class=\"pagination', '</div>')
        m = re.search('<li class=\"previous[^<]+<a href=\"(?P<url>[^\"]+)', data, re.DOTALL | re.IGNORECASE)
        if m:
                add_dir('Předchozí', {'list':furl(m.group('url'))}, util.icon('prev.png'))
        n = re.search('<li class=\"next[^<]+<a href=\"(?P<url>[^\"]+)', data, re.DOTALL | re.IGNORECASE)
        if n:
                add_dir('Další', {'list':furl(n.group('url'))}, util.icon('next.png'))
        #xbmcplugin.endOfDirectory(int(sys.argv[1]))

def furl(url):
        if url.startswith('http'):
                return url
        url = url.lstrip('./')
        return BASE_URL + url

def categories():
        search2.item()
        #util.add_local_dir(__language__(30037),__addon__.getSetting('downloads'),util.icon('download.png'))
        data = util.substr(util.request(BASE_URL), 'div class=\"stats\"', '<footer')
        pattern = '<section class=\"(?P<section>[^\"]+)(.+?)<h3>(?P<name>[^<]+)'
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
                add_dir(m.group('name'), {'stats':m.group('section')})

def can_show(ext_filter, item):
        extension = os.path.splitext(item)[1]
        if extension in ext_filter:
                return False
        return True

def create_filter():
        ext_filter = 'exe,rar,srt,zip'.split(',')#__addon__.getSetting('ext-filter').split(',')
        return ['.' + f.strip() for f in ext_filter]

def stats(section):
        data = util.substr(util.request(BASE_URL), 'section class=\"' + section + '\"', '</section')
        pattern = '<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)'
        ext_filter = create_filter()
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
                if can_show(ext_filter, m.group('name')):
                        iurl = furl(m.group('url'))
                        add_video(
                                m.group('name'),
                                {'play':iurl},
                               # menuItems={xbmc.getLocalizedString(33003):{'name':m.group('name'),'download':iurl}}
                        )


def play(url):
        stream = resolve(url)
        if stream:
            add_play('VIDEO', stream, None)

def resolve(url):
        data = util.request(url)
        request = urllib.urlencode({'stahnoutSoubor':'Stáhnout'})
        req = urllib2.Request(url + '?do=stahnoutForm-submit', request)
        req.add_header('User-Agent', util.UA)    
        resp = urllib2.urlopen(req)
        return resp.geturl()

#def download(url,name):
      #  downloads = __addon__.getSetting('downloads')
       # if '' == downloads:
       #         xbmcgui.Dialog().ok(__scriptname__,__language__(30031))
       #         return
       # stream = resolve(url)
       # if stream:
       #         util.reportUsage(__scriptid__,__scriptid__+'/download')
       #         util.download(__addon__,name,stream,os.path.join(downloads,name))
                
    
  
  
#categories()
#_search_cb('survivor s23')
##p['search']=search
#root()
#list('http://koukni.cz/simpsons')
#play('http://koukni.cz/38041719')

#p = util.params()
#util.init_urllib()

