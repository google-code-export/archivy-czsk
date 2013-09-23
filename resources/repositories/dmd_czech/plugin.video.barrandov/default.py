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
from threading import Lock

from util import addDir, addLink
from Plugins.Extensions.archivCZSK.archivczsk import ArchivCZSK

__baseurl__ = 'http://www.barrandov.tv'
_UserAgent_ = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0'

__settings__ = ArchivCZSK.get_xbmc_addon('plugin.video.barrandov')
home = __settings__.getAddonInfo('path')
icon = os.path.join(home, 'icon.png')
nexticon = os.path.join(home, 'nextpage.png')

NEW_URL = 'http://www.barrandov.tv/video/vypis/nejnovejsi-videa/'
TOP_URL = 'http://www.barrandov.tv/video/vypis/nejsledovanejsi-videa/'

CATEGORIES_START = '<div id="right-menu">'
CATEGORIES_END = '<div class="block tip">'
CATEGORIES_ITER_RE = '<li.*?<a href=\"(?P<url>[^"]+)">(?P<title>.+?)</a><\/li>'

CATEGORY_IMG_RE= '<div class=\"header-container\">\s+<div class=\"content\">\s+<img src=\"(?P<img>[^\"]+)\"'

LISTING_START = '<div class="block video show-archive">'
LISTING_END = '<div id="right-menu">'
LISTING_ITER_RE = '<div class=\"item.*?\">.+?<a href=\"(?P<url>[^"]+)\">(?P<title>[^<]+)<.+?<p class=\"desc\">(?P<desc>[^<]+)</p>.+?<img src=\"(?P<img>[^\"]+)\".+?<span class=\"play\"><img src=\"(?P<playimg>[^\"]+)\".+?</div>'
PAGER_RE = '<span class=\"pages">(?P<actpage>[0-9]+)/(?P<totalpage>[0-9]+)</span>.*?<a href=\"(?P<nexturl>[^"]+)'
VIDEOLINK_ITER_RE = 'file:.*?\"(?P<url>[^"]+)".+?label:.*?\"(?P<quality>[^"]+)\"'

YELLOW_IMG = 'video-play-yellow'




def categories():
    def fill_list_parallel(list, categories):
            def process_category(title, url):
                req = urllib2.Request(url)
                req.add_header('User-Agent', _UserAgent_)
                response = urllib2.urlopen(req)
                httpdata = response.read()
                response.close()
                m = re.search(CATEGORY_IMG_RE, httpdata, re.IGNORECASE)
                img = m and __baseurl__ + m.group(1)
                data2 = httpdata[httpdata.find(LISTING_START):httpdata.find(LISTING_END)]
                finditer = False
                for m in re.finditer(LISTING_ITER_RE, data2, re.DOTALL | re.IGNORECASE):
                    finditer = True
                    # payed content
                    if m.group('playimg').find(YELLOW_IMG) != -1:
                        return
                    break
                # no links
                if not finditer:
                    return
                with lock:
                    list.append((title, url, img))
            lock = Lock()
            run_parallel_in_threads(process_category, categories)
    
    req = urllib2.Request(__baseurl__ + '/video')
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    httpdata = httpdata[httpdata.find(CATEGORIES_START):httpdata.find(CATEGORIES_END)]
    
    result = []
    categories = []
    for item in re.finditer(CATEGORIES_ITER_RE, httpdata, re.DOTALL | re.IGNORECASE):
        title = item.group('title')
        url = __baseurl__ + item.group('url')
        categories.append((title,url))
    
    fill_list_parallel(result, categories)
    sorted(categories,key=lambda x:x[0])
    addDir('Nejnovější',NEW_URL, 3, icon)
    addDir('Nejsledovanější',TOP_URL, 4, icon)
    for category in result:
        addDir(category[0], category[1], 1, category[2])
        
        
def top(url):
    return listing(url)
    
def new(url):
    return listing(url)
        

def listing(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    httpdata = httpdata[httpdata.find(LISTING_START):httpdata.find(LISTING_END)]
    for item in re.finditer(LISTING_ITER_RE, httpdata, re.DOTALL | re.IGNORECASE):
        if item.group('playimg').find(YELLOW_IMG) != -1:
            continue
        desc = item.group('desc')
        title = item.group('title')
        m = re.search('(\d{1,2})\.(\d{1,2})\.(\d{4})',desc)
        day = len(m.group(1))>1 and m.group(1)[0] =='0' and m.group(1)[1] or m.group(1)
        month = len(m.group(2))>1 and m.group(2)[0] == '0' and m.group(2)[1]  or m.group(2)
        year = m.group(3)
        date = '%s.%s.%s'% (day, month, year)

        title = "%s %s"%(title, date) if title.find(date) == -1 else title
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
        
def videolink(url, name):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    
    for video in re.compile(VIDEOLINK_ITER_RE, re.DOTALL | re.IGNORECASE).finditer(httpdata):
        url = __baseurl__ + video.group('url')
        quality = video.group('quality')
        title = '[%s] %s'%(quality, name)
        addLink(title, url, None, title)
        
        
import threading
import Queue

def run_parallel_in_threads(target, args_list):
    result = Queue.Queue()
    # wrapper to collect return value in a Queue
    def task_wrapper(*args):
        result.put(target(*args))
    threads = [threading.Thread(target=task_wrapper, args=args) for args in args_list]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return result

            
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
        categories()
       
elif mode == 1:
        listing(url)
        
elif mode == 2:
        videolink(url, name)
    
elif mode == 3:
        new(url)

elif mode == 4:
        top(url)
