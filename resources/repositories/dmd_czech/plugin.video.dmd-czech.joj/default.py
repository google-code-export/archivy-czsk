# -*- coding: utf-8 -*-
import urllib2, urllib, re, os
import simplejson as json
from parseutils import *
from urlparse import urlparse
from util import addDir, addLink
from Plugins.Extensions.archivCZSK.archivczsk import ArchivCZSK
__dmdbase__ = 'http://iamm.netuje.cz/emulator/joj/image/'
_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
__settings__ = ArchivCZSK.get_addon('plugin.video.dmd-czech.joj')
home = __settings__.get_info('path')
icon = os.path.join(home, 'icon.png')
nexticon = os.path.join(home, 'nextpage.png') 


def VIDEOPORTAL(url):
    doc = read_page(url)
    items = doc.find('div', 'c-full c')
    for item in items.findAll('div', 'b-wrap b-video b-video-grid b-video-category'):
        name = item.find('a')
        name = name.getText(" ").encode('utf-8')
        url = str(item.a['href']) 
        #print name,url
        addDir(name, 'http://www.videoportal.sk/' + url, 12, icon, 1)

def VP_LIST(url):
    doc = read_page(url)
    items = doc.find('ul', 'l c')
    for item in items.findAll('li'):
        try:
            name = item.a['title'].encode('utf-8')
        except:
            name = 'Bezejmenný titul'
        url = str(item.a['href']) 
        thumb = str(item.img['src'])
        #print name,url, thumb
        addDir(name, 'http://www.videoportal.sk/' + url, 13, thumb, 1)
    try:
        items = doc.find('ul', 'm-move right c')
        match = re.compile('<li><a class="next" href="(.+?)"').findall(str(items))
        addDir('>> Další strana >>', 'http://www.videoportal.sk/' + match[0], 12, nexticon, 1)
    except:
        print 'strankovani nenalezeno'
        
def VIDEOLINK(url, name):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    try:
        basepath = re.compile('basePath: "(.+?)"').findall(httpdata)
        videoid = re.compile('videoId: "(.+?)"').findall(httpdata)
        pageid = re.compile('pageId: "(.+?)"').findall(httpdata)
        if len (pageid[0]) != 0:
          playlisturl = basepath[0] + 'services/Video.php?clip=' + videoid[0] + 'pageId=' + pageid[0]
        else:
          playlisturl = basepath[0] + 'services/Video.php?clip=' + videoid[0]
        print playlisturl
        req = urllib2.Request(playlisturl)
        req.add_header('User-Agent', _UserAgent_)
        response = urllib2.urlopen(req)
        doc = response.read()
        response.close()
        title = re.compile('title="(.+?)"').findall(doc)
        thumb = re.compile('large_image="(.+?)"').findall(doc)
        joj_file = re.compile('<file type=".+?" quality="(.+?)" id="(.+?)" label=".+?" path="(.+?)"/>').findall(doc)
        for kvalita, serverno, cesta in joj_file:
            name = str.swapcase(kvalita) + ' - ' + title[0]
            if __settings__.get_setting('stream_server'):
                server = 'n09.joj.sk'
            else:
                if int(serverno) > 20:
                    serverno = str(int(serverno) / 2)
                if len(serverno) == 2:
                    server = 'n' + serverno + '.joj.sk'
                else:
                    server = 'n0' + serverno + '.joj.sk'
            tcurl = 'rtmp://' + server
            swfurl = 'http://player.joj.sk/JojPlayer.swf?no_cache=137034'
            port = '1935'
            rtmp_url = tcurl + ' playpath=' + cesta + ' pageUrl=' + url + ' swfUrl=' + swfurl + ' swfVfy=true'
            addLink(name, rtmp_url, thumb[0], name)
    except:
        try:
            basepath = re.compile('basePath=(.+?)&amp').findall(httpdata)
            basepath = re.sub('%3A', ':', basepath[0])
            basepath = re.sub('%2F', '/', basepath)
            videoid = re.compile('videoId=(.+?)&amp').findall(httpdata)
        except:
            videoid = re.compile('video:(.+?).html').findall(str(url))
            basepath = 'http://hotelparadise.joj.sk/'
        playlisturl = basepath + 'services/Video.php?clip=' + videoid[0]
        print playlisturl
        req = urllib2.Request(playlisturl)
        req.add_header('User-Agent', _UserAgent_)
        response = urllib2.urlopen(req)
        doc = response.read()
        response.close()
        title = re.compile('title="(.+?)"').findall(doc)
        joj_file = re.compile('<file type=".+?" quality="(.+?)" id="(.+?)" label=".+?" path="(.+?)"/>').findall(doc)
        for kvalita, serverno, cesta in joj_file:
            name = str.swapcase(kvalita) + ' - ' + title[0]
            if __settings__.get_setting('stream_server'):
                server = 'n09.joj.sk'
            else:
                if int(serverno) > 20:
                    serverno = str(int(serverno) / 2)
                if len(serverno) == 2:
                    server = 'n' + serverno + '.joj.sk'
                else:
                    server = 'n0' + serverno + '.joj.sk'
            tcurl = 'rtmp://' + server
            swfurl = basepath + 'fileadmin/templates/swf/csmt_player.swf?no_cache=171307'
            port = '1935'
            rtmp_url = tcurl + ' playpath=' + cesta + ' pageUrl=' + url + ' swfUrl=' + swfurl + ' swfVfy=true'
            addLink(name, rtmp_url, icon, name)


def VP_PLAY(url, name):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    videoid = re.compile('videoId=(.+?)&').findall(httpdata)
    playlisturl = 'http://www.videoportal.sk/services/Video.php?clip=' + videoid[0] + '&article=undefined'
    req = urllib2.Request(playlisturl)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    doc = response.read()
    response.close()
    thumb = re.compile('image="(.+?)"').findall(doc)

    joj_file = re.compile('<file type=".+?" quality="(.+?)" id="(.+?)" label=".+?" path="(.+?)"/>').findall(doc)
    for kvalita, serverno, cesta in joj_file:
        titul = str.swapcase(kvalita) + ' - ' + name
        if __settings__.get_setting('stream_server'):
            server = 'n09.joj.sk'
        else:
                server = 'n' + serverno + '.joj.sk'
        tcurl = 'rtmp://' + server
        swfurl = 'http://player.joj.sk/VideoportalPlayer.swf?no_cache=173329'
        port = '1935'
        rtmp_url = tcurl + ' playpath=' + cesta + ' pageUrl=' + url + ' swfUrl=' + swfurl + ' swfVfy=true'
        addLink(titul, rtmp_url, thumb[0], titul)

#/*
# *      Copyright (C) 2013 mx3L
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

#
#  Credits to Jirka Vyhnalek - author of stv plugin from dmd-xbmc project
#  Some sources in this plugin are used from this project
#  
#

VYSIELANE_START = '<div class="archiveList preloader">'
VYSIELANE_ITER_RE = '<ul class=\"clearfix\">.*?<div class=\"titleBg">.*?<a href=\"(?P<url>[^"]+).*?title=\"(?P<title>[^"]+).+?<p>(?P<desc>.*?)</p>.+?</ul>'
NEVYSIELANE_START = '<div class="archiveNev">'
NEVYSIELANE_END = '<div class="clearfix padSection">'
NEVYSIELANE_ITER_RE = '<li.*?><a href=\"(?P<url>[^"]+).*?title=\"(?P<title>[^"]+).*?</li>'
EPISODE_START = '<div class="episodeListing relative overflowed">'
EPISODE_END = '<div class="centered pagerDots"></div>'
EPISODE_ITER_RE = '<li[^>]*>\s+?<a href=\"(?P<url>[^"]+)\" title=\"(?P<title>[^"]+)\">\s+?<span class=\"date\">(?P<date>[^<]+)</span>(.+?)<span class=\"episode\">(?P<episode>[^0]{1}[0-9]*)</span>(.+?)</li>'
SERIES_START = EPISODE_START
SERIES_END = EPISODE_END
SERIES_ITER_RE = '<option(.+?)data-ajax=\"(?P<url>[^\"]+)\">(?P<title>[^<]+)</option>'

MAX_PAGE_ENTRIES = 100

JOJ_URL = 'http://www.joj.sk'
JOJ_PLUS_URL = 'http://plus.joj.sk'
WAU_URL = 'http://wau.joj.sk/'
ZAKAZANE = []

RELACIE_FIX = ['anosefe']
SERIALY_FIX = []
VYMENIT_LINK = {'csmatalent':'http://www.csmatalent.cz/video-cz.html'}
LIST_MOD = {}

def request(url,headers=None):
    headers = headers or {}
    request = urllib2.Request(url,headers=headers)
    request.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(request)
    data = response.read()
    response.close()
    return data

def substr(st,start=None,end=None):
    start_idx = start and st.find(start)
    start_idx = start_idx > -1 and start_idx or None
    end_idx = end and st.find(end)
    end_idx = end_idx > -1 and end_idx or None
    
    if start_idx and end_idx:
        return st[start_idx:end_idx]
    elif start_idx:
        return st[start_idx:]
    elif end_idx:
        return st[:end_idx]
    else: return st


def zakazane(title):
    if title in ZAKAZANE:
        return True
    return False
   
def fix_link(url):
    if url in SERIALY_FIX:
        url = url[:url.rfind('-')] + '-epizody.html'
    elif url in RELACIE_FIX:
        url = url[:url.rfind('-')] + '-archiv.html'
    else:
        for rel in VYMENIT_LINK.keys():
            if rel in url:
                return VYMENIT_LINK[rel] 
    return url

def list_mod(url):
    for rel in LIST_MOD.keys():
        if rel in url:
            return LIST_MOD[rel]
    return 4

def image(url):
    return icon


def OBSAH():
    addDir('JOJ', JOJ_URL, 31, icon)
    addDir('JOJ Plus', JOJ_PLUS_URL, 32, icon)
    addDir('WAU', WAU_URL, 33, icon)
    addDir('Videoportal.sk', 'http://www.videoportal.sk/kategorie.html', 9, icon)
    
def OBSAH_JOJ():
    addDir('Relácie', JOJ_URL + '/archiv.html?type=relacie', 34, icon)
    addDir('Seriály', JOJ_URL + '/archiv.html?type=serialy', 34, icon)
    
def OBSAH_JOJ_PLUS():
    addDir('Relácie', JOJ_PLUS_URL + '/plus-archiv.html?type=relacie', 34, icon)
    addDir('Seriály', JOJ_PLUS_URL + '/plus-archiv.html?type=serialy', 34, icon)
    
def OBSAH_WAU():
    addDir('Relácie', WAU_URL + '/wau-archiv.html?type=relacie', 34, icon)
    addDir('Seriály', WAU_URL + '/wau-archiv.html?type=serialy', 34, icon)
    
def OBSAH_RELASER(url):
    addDir('Vysielané', url, 35, icon)
    addDir('Nevysielané', url, 36, icon)
    

def OBSAH_VYSIELANE(url):
    zoznam = []
    httpdata = request(url)
    httpdata = substr(httpdata,VYSIELANE_START,NEVYSIELANE_START)
    
    for item in re.compile(VYSIELANE_ITER_RE, re.DOTALL | re.IGNORECASE).finditer(httpdata):
        title = item.group('title')
        link = item.group('url')
        desc = item.group('desc')
        if not zakazane(title):
            mod = list_mod(link)
            img = image(url)
            infoLabels = {'title':title, 'plot':desc}
            zoznam.append((title, link, mod, img, 0, infoLabels))

    zoznam.sort(key=lambda x:x[0])
    for title, link, mod, img, page, infoLabels in zoznam:
        addDir(title, link, mod, img, page, infoLabels=infoLabels)
        
        
def OBSAH_NEVYSIELANE(url):
    zoznam = []
    httpdata = request(url)
    httpdata = substr(httpdata,NEVYSIELANE_START, NEVYSIELANE_END)
        
    for item in re.compile(NEVYSIELANE_ITER_RE, re.DOTALL | re.IGNORECASE).finditer(httpdata):
        title = item.group('title')
        link = item.group('url')
        mod = list_mod(link)
        img = image(url)
        if not zakazane(title):
            zoznam.append((title, link, mod, img, 0))
            
    zoznam.sort(key=lambda x:x[0])
    for title, link, mod, img, page in zoznam:
        addDir(title, link, mod, img, page)
        
        
def LIST_SERIES(url):
    httpdata = request(url)
    httpdata = substr(httpdata,SERIES_START,SERIES_END)

    series=False
    for item in re.compile(SERIES_ITER_RE, re.DOTALL | re.IGNORECASE).finditer(httpdata):
        series = True
        title = item.group('title')
        link =  'http://'+urlparse(url).netloc+'/ajax.json?'+item.group('url')
        addDir(title, link, 5, icon)
    if not series:
        LIST_EPISODES(url)

def LIST_EPISODES(url,page=0):
    if url.find('ajax.json')!=-1:
        headers = {'X-Requested-With':'XMLHttpRequest',
                   'Referer':substr(url,end=url.split('/')[-1])
                   }
        httpdata = request(url,headers)
        httpdata = json.loads(httpdata)['content']
    else:
        httpdata = request(url)
        httpdata = substr(httpdata,EPISODE_START, EPISODE_END)
        
    entries = 0
    skip_entries = MAX_PAGE_ENTRIES * page

    for item in re.compile(EPISODE_ITER_RE, re.DOTALL | re.IGNORECASE).finditer(httpdata):
        entries+=1
        if entries < skip_entries:
            continue
        title = item.group('title')
        datum = item.group('date')
        episode = item.group('episode')
        title = str(episode) + '. ' + title + ' (' + datum + ')'
        link = item.group('url')
        addDir(title, link, 10, icon, 1)
        
        if entries >= (skip_entries + MAX_PAGE_ENTRIES):
            page+=1
            addDir("Dalsia strana ->>",url,5,icon,page=page)
            break


url = None
name = None
thumb = None
mode = None
page = 0

try:
        url = urllib.unquote_plus(params["url"])
except:
        pass
try:
        name = urllib.unquote_plus(params["name"])
except:
        pass
try:
        page = int(params["page"])
except:
        pass
try:
        mode = int(params["mode"])
except:
        pass

#print "Mode: " + str(mode)
#print "URL: " + str(url)
#print "Name: " + str(name)
#print "Page: " + str(page)

if mode == None or url == None or len(url) < 1:
        print ""
        OBSAH()
       
elif mode == 31:
        print ""
        OBSAH_JOJ()

elif mode == 32:
        print ""
        OBSAH_JOJ_PLUS()
        
elif mode == 33:
        print ""
        OBSAH_WAU()

elif mode == 34:
        print ""
        OBSAH_RELASER(url)

elif mode == 35:
        print ""
        OBSAH_VYSIELANE(url)
        
elif mode == 36:
        print ""
        OBSAH_NEVYSIELANE(url)
        
elif mode == 4:
        LIST_SERIES(url)

elif mode == 5:
        print "" + url
        #print "" + str(page)        
        LIST_EPISODES(url,page)

elif mode == 9:
        print "" + url
        VIDEOPORTAL(url)
    
elif mode == 10:
        print "" + url
        VIDEOLINK(url, name)

elif mode == 12:
        print "" + url
        VP_LIST(url)
elif mode == 13:
        print "" + url
        VP_PLAY(url, name)
