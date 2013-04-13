# -*- coding: UTF-8 -*-
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


import urllib2
import re
import random

from util import addDir, addLink
from Plugins.Extensions.archivCZSK.archivczsk import ArchivCZSK

__baseurl__ = 'http://www.barrandov.tv'
_UserAgent_ = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0'

__settings__ = ArchivCZSK.get_xbmc_addon('plugin.video.barrandov')
home = __settings__.getAddonInfo('path')
icon = os.path.join(home, 'icon.png')
nexticon = os.path.join(home, 'nextpage.png') 

CATEGORIES_START = '<div id="videoContent">'
CATEGORIES_END = '<div class="cols footerMenu">'
CATEGORIES_ITER = '<div class=\"videosGenre.*?\">.*?<h3>(?P<title>.*?)</h3>.*?<a href=\"(?P<url>[^"]+)\">Všechna videa</a>.*?</div>'
LISTING_START = '<ul class="videoHpList">'
LISTING_END = '<div class="cols footerMenu">'
LISTING_ITER = '<li.*?><h5><a href=\"(?P<url>[^"]+).*?<img src=\"(?P<img>[^"]+)\" alt=\"(?P<title>[^"]+).*?</li>'
PAGER_RE = '<div class="largePager">.*?strana:\s*?(?P<actpage>[0-9]+)[^/]+\/.*?(?P<totalpage>[0-9]+).*?<a class=\"right\" href=\"(?P<nexturl>[^"]+)'
VIDEOLINK_RE = '<mediainfo.*?name=\"(?P<title>[^"]+).*?hd="(?P<hd>[^"]+).*?<file>(?P<file>[^<]+).*?<host>(?P<host>[^<]+)'


def CATEGORIES():
    req = urllib2.Request(__baseurl__+'/video')
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    httpdata = httpdata[httpdata.find(CATEGORIES_START):httpdata.find(CATEGORIES_END)]
    
    for item in re.compile(CATEGORIES_ITER, re.DOTALL | re.IGNORECASE).finditer(httpdata):
        title = item.group('title').encode('utf-8')
        link = __baseurl__ + item.group('url')
        addDir(title, link, 1, icon)
        
def LISTING(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    httpdata = httpdata[httpdata.find(LISTING_START):httpdata.find(LISTING_END)]
    
    for item in re.compile(LISTING_ITER, re.DOTALL | re.IGNORECASE).finditer(httpdata):
        title = item.group('title').encode('utf-8')
        img = __baseurl__ + item.group('img')
        link = item.group('url')
        addDir(title, link, 2, img)
        
    pager = re.search(PAGER_RE, httpdata, re.DOTALL)
    if pager:
        actpage = pager.group('actpage')
        totalpage = pager.group('totalpage')
        nexturl = pager.group('nexturl')
        idx = url.find('?')
        if idx != -1:
            nexturl = url[:idx] + nexturl
        else: 
            nexturl = url + nexturl
        addDir('Daľšia strana >> (%s / %s)' % (actpage, totalpage), nexturl, 1, nexticon)
        
def VIDEOLINK(url):
    videoid = re.search('\/([0-9]+)', url).group(1)
    url = 'http://www.barrandov.tv/special/voddata/' + videoid + '?r=' + str(random.randint(1000, 9999))
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    
    video = re.search(VIDEOLINK_RE, httpdata, re.DOTALL)
    title = video.group('title')
    hd = video.group('hd')
    if hd: 
        title = 'HD ' + title
    else: 
        title = 'SD ' + title
    playpath = video.group('file')
    app = video.group('host').split('/')[-1]
    tcurl = 'rtmpe://' + video.group('host')
    swfurl = 'http://www.barrandov.tv/flash/tvbPlayer22.swf?itemid=' + videoid
    rtmp_url = tcurl + ' playpath=' + playpath + ' swfUrl=' + swfurl + ' app=' + app + ' token=#ed%h0#w@1'
    addLink(title, rtmp_url, None, title)

            
url = None
name = None
thumb = None
mode = None

try:
        url = params["url"]
except:
        pass
try:
        name = urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode = int(params["mode"])
except:
        pass

if mode is None or url is None:
        CATEGORIES()
       
elif mode == 1:
        LISTING(url)
        
elif mode == 2:
        VIDEOLINK(url)
