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

import re,os,urllib,sys,mimetypes
try:
    import Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools.util as util
    import Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools.resolver as resolver
    import Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools.server.youtuberesolver as youtube
    from Plugins.Extensions.archivCZSK.resources.tools.doplnky import add_dir, add_video, add_play, set_command
except ImportError:
    import resources.archives.xbmc_doplnky.tools.util as util
    import resources.archives.xbmc_doplnky.tools.resolver as resolver
    import resources.archives.xbmc_doplnky.tools.server.youtuberesolver as youtube
    from resources.tools.doplnky import add_dir, add_video, add_play
try:
    from Plugins.Extensions.archivCZSK import _
except ImportError:
    print 'unit test'

__scriptid__   = 'plugin.video.videacesky.cz'
__scriptname__ = 'videacesky.cz'

__addon__="videacesky"
BASE_URL='http://www.videacesky.cz/'

def getContent(url, **kwargs):
    name=kwargs['name'] 
    p = {} 
    if url is not None:
        p = url   
    if p=={}:
        categories()
    if 'top' in p.keys():
        list_top(util.request(p['top']))
    if 'cat' in p.keys():
        list_content(util.request(p['cat']),p['cat'])
    if 'play' in p.keys():
        play(p['play'],name)

def furl(url):
        if url.startswith('http'):
                return url
        url = url.lstrip('./')
        return BASE_URL+url

def categories():
        #add_dir(__addon__,{'top':BASE_URL+'/videozebricky/poslednich-50-videi'},util.icon('new.png')) nefunguje
        add_dir('Top 200',{'top':furl('/videozebricky/top-100')},util.icon('top.png'))
      #  util.add_local_dir(__language__(30037),__addon__.getSetting('downloads'),util.icon('download.png'))
        data = util.request(BASE_URL)
        data = util.substr(data,'<ul id=\"headerMenu2\">','</ul>')
        pattern = '<a href=\"(?P<url>[^\"]+)(.+?)>(?P<name>[^<]+)'
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL ):
                if m.group('url') == '/':
                        continue
                add_dir(m.group('name'),{'cat':furl(m.group('url'))})

def list_top(page):
        data = util.substr(page,'<div class=\"postContent','</ul>')
        pattern = '<li>[^<]*<a href="(?P<url>[^\"]+)[^>]*>(?P<name>[^<]+)'
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL ):
                add_video(
                        m.group('name'),
                        {'play':furl(m.group('url'))},
                       # menuItems={xbmc.getLocalizedString(33003):{'name':m.group('name'),'download':m.group('url')}}
                )

def list_content(page,url=BASE_URL):
        data = util.substr(page,'<div class=\"contentArea','<div class=\"pagination\">')
        pattern = '<h\d class=\"postTitle\"><a href=\"(?P<url>[^\"]+)(.+?)<span>(?P<name>[^<]+)</span></a>(.+?)<div class=\"postContent\">[^<]+<a[^>]+[^<]+<img src=\"(?P<img>[^\"]+)[^<]+</a>[^<]*<div class=\"obs\">[^>]+>(?P<plot>(.+?))</p>'
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL ):
                plot = re.sub('<br[^>]*>','',m.group('plot'))
                #sprint plot ,'444'
                add_video(
                        m.group('name'),
                        {'play':furl(m.group('url'))},
                        m.group('img'),
                        infoLabels={'plot':plot}
                        #menuItems={xbmc.getLocalizedString(33003):{'name':m.group('name'),'download':furl(m.group('url'))}}
                )    
        data = util.substr(page,'<div class=\"pagination\">','</div>')
        m = re.search('<li class=\"info\"><span>([^<]+)',data)
        n = re.search('<li class=\"prev\"[^<]+<a href=\"(?P<url>[^\"]+)[^<]+<span>(?P<name>[^<]+)',data)
        k = re.search('<li class=\"next\"[^<]+<a href=\"(?P<url>[^\"]+)[^<]+<span>(?P<name>[^<]+)',data)
        # replace last / + everyting till the end
        myurl = re.sub('\/[\w\-]+$','/',url)
        if not m == None:
                if not n == None:
                        add_dir('%s - %s' % (m.group(1),n.group('name')),{'cat':myurl+n.group('url')})
                if not k == None:
                        add_dir('%s - %s' % (m.group(1),k.group('name')),{'cat':myurl+k.group('url')})
        
def resolve(url):
        data = util.substr(util.request(url),'<div class=\"postContent\"','</div>')
        m = re.search('file=(?P<url>[^\&]+)',data,re.IGNORECASE | re.DOTALL)
        subs = re.search('captions.file=(?P<url>[^\&]+)',data,re.IGNORECASE | re.DOTALL)
        if not subs == None:
            subtitles=subs.group('url')
        else:
            subtitles=None
        if not m == None:
                youtube.__eurl__ = 'http://www.videacesky.cz/wp-content/plugins/jw-player-plugin-for-wordpress/player.swf'
                url=m.group('url')
                if url.startswith('www'):
                    url='http://'+url
                streams = resolver.resolve2(url)
                if not streams == None and len(streams)>0:
                        return streams,subtitles

def play(url,name): 
        streams,subs = resolve(url)
        if len(streams)>0:
            for stream in streams:
                add_play(stream['name']+' - '+stream['quality'],stream['url'],subs,filename=name)

