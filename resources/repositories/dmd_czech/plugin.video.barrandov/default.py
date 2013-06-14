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

CATEGORIES_START = '<div id="right-menu">'
CATEGORIES_END = '<div class="block tip">'
CATEGORIES_ITER = '<li.*?<a href=\"(?P<url>[^"]+)">(?P<title>.+?)</a><\/li>'

LISTING_START = '<div class="block video show-archive">'
LISTING_END = '<div id="right-menu">'
LISTING_ITER = '<div class=\"item.*?\">.+?<a href=\"(?P<url>[^"]+)\">(?P<title>.+?)<.+?<p class=\"desc\">(?P<desc>.+?)</p>.+?<img src=\"(?P<img>[^"]+)".+?</div>'
PAGER_RE = '<span class=\"pages">(?P<actpage>[0-9]+)/(?P<totalpage>[0-9]+)</span>.*?<a href=\"(?P<nexturl>[^"]+)'
VIDEOLINK_ITER = 'file:.*?\"(?P<url>[^"]+)".+?label:.*?\"(?P<quality>[^"]+)\"'

def CATEGORIES():
    req = urllib2.Request(__baseurl__ + '/video')
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    httpdata = httpdata[httpdata.find(CATEGORIES_START):httpdata.find(CATEGORIES_END)]
    
    for item in re.compile(CATEGORIES_ITER, re.DOTALL | re.IGNORECASE).finditer(httpdata):
        title = item.group('title')
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
        desc = item.group('desc')
        title = item.group('title')
        title = title + ' ' + desc
        img = __baseurl__ + item.group('img')
        link = __baseurl__ + item.group('url')
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
        
def VIDEOLINK(url, name):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    
    for video in re.compile(VIDEOLINK_ITER, re.DOTALL | re.IGNORECASE).finditer(httpdata):
        url = __baseurl__ + video.group('url')
        quality = video.group('quality')
        title = name + ' - ' + quality
        addLink(title, url, None, title)

            
url = None
name = None
thumb = None
mode = None

try:
        url = params["url"]
except:
        pass
try:
        name = params["name"]
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
        VIDEOLINK(url, name)
