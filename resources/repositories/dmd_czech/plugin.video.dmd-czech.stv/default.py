# -*- coding: utf-8 -*-

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

import urllib2, urllib, re, os
from util import addDir, addLink, getSearch
from Plugins.Extensions.archivCZSK.archivczsk import ArchivCZSK

_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
__baseurl__ = 'http://www.rtvs.sk/'
__settings__ = ArchivCZSK.get_addon('plugin.video.dmd-czech.stv')
home = __settings__.get_info('path')
icon = os.path.join(home, 'icon.png')
nexticon = os.path.join(home, 'nextpage.png')

START_TOP= '<h2 class="nadpis">Najsledovanejšie</h2>'
END_TOP =  '<h2 class="nadpis">Najnovšie</h2>'
TOP_ITER_RE = '<li(.+?)<a title=\"(?P<title>[^"]+)\"(.+?)href=\"(?P<url>[^"]+)\"(.+?)<img src=\"(?P<img>[^"]+)\"(.+?)<p class=\"day\">(?P<date>[^<]+)<\/p>(.+?)<span class=\"programmeTime\">(?P<time>[^<]+)(.+?)<\/li>'

START_NEWEST = END_TOP
END_NEWEST = '<div class="footer'
NEWEST_ITER_RE = '<li(.+?)<a href=\"(?P<url>[^"]+)\"(.+?)title=\"(?P<title>[^"]+)\"(.+?)<img src=\"(?P<img>[^"]+)\"(.+?)<p class=\"day\">(?P<date>[^<]+)<\/p>(.+?)<span class=\"programmeTime\">(?P<time>[^<]+)(.+?)<\/li>'

START_AZ = '<h2 class="az"'
END_AZ = START_TOP
AZ_ITER_RE = TOP_ITER_RE

START_LISTING='<div class="boxRight archiv">'
END_LISTING='<div class="boxRight soloBtn white">'
LISTING_PAGER_RE= "<a class=\'prev calendarRoller' href=\'(?P<prevurl>[^\']+)\'.+?<a class=\'next calendarRoller\' href=\'(?P<nexturl>[^\']+)"
LISTING_DATE_RE = "<div class=\'calendar-header\'>\s+<h6>(?P<date>.+?)</h6>"
LISTING_ITER_RE = '<td class=(\"day\"|\"active day\")>\s+<a href="(?P<url>[^\"]+)\">(?P<daynum>[\d]+)</a>\s+</td>'

VIDEO_ID_RE = 'LiveboxPlayer.flash\(.+?stream_id:+.\"(.+?)\"'
#VIDEO_INFO_RE = '<div class="thumbnail showPromo">'

#<div class="article-header">

#INFO_START='<div class="span9">'
#INFO_END

def request(url,referer=None):
    request = urllib2.Request(url)
    request.add_header('User-Agent', _UserAgent_)
    if referer:
        request.add_header("Referer", url)
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
        

def fix_url(url):
    return re.sub('&amp;','&',url)
    

def CATEGORIES():
    addDir("Najsledovanejšie", __baseurl__ +'/tv.archive.alphabet', 1, icon)
    addDir("Najnovšie", __baseurl__ +'/tv.archive.alphabet',2,icon)
    addDir("A-Z", __baseurl__ +'/tv.archive.alphabet',3,icon)
    
def CATEGORY_AZ(url):
    az = [str(unichr(c)) for c in range(65,90,1)]
    for c in range(65,90,1):
        chr = str(unichr(c))
        addDir(chr,url+'?letter=%s'%chr.lower(),4,icon)

def LIST_AZ(url):
    data = request(url)
    data = substr(data,START_AZ,END_AZ)
    for item in re.finditer(AZ_ITER_RE,data,re.IGNORECASE|re.DOTALL):
        title = substr(item.group('title'),end=':').strip()
        link = __baseurl__+item.group('url')
        img = __baseurl__+item.group('img')
        addDir(title,link,5,img)
    
         
def LIST_TOP(url):
    data = request(url)
    data = substr(data,START_TOP,END_TOP)
    for item in re.finditer(TOP_ITER_RE,data,re.IGNORECASE|re.DOTALL):
        title = item.group('title')
        date = item.group('date')
        time = item.group('time')
        link = __baseurl__+item.group('url')
        img = __baseurl__+item.group('img')
        addDir("%s (%s - %s)"%(title,date,time),link,10,img)
        
          
def LIST_NEWEST(url):
    data = request(url)
    data = substr(data,START_NEWEST,END_NEWEST)
    for item in re.finditer(NEWEST_ITER_RE,data,re.IGNORECASE|re.DOTALL):
        title = item.group('title')
        date = item.group('date')
        time = item.group('time')
        link = __baseurl__+item.group('url')
        img = __baseurl__+item.group('img')
        addDir("%s (%s - %s)"%(title,date,time),link,10,img)
    
        
def LIST_TITLE(url):
    data = request(url)
    data = substr(data,START_LISTING,END_LISTING)
    current_date = re.search(LISTING_DATE_RE,data,re.IGNORECASE).group('date')
    prev_url = re.search(LISTING_PAGER_RE,data,re.IGNORECASE|re.DOTALL).group('prevurl')
    prev_url = fix_url(__baseurl__+prev_url)
    for item in re.finditer(LISTING_ITER_RE,data,re.IGNORECASE|re.DOTALL):
        title = "%s. %s"%(item.group('daynum'),current_date)
        link = fix_url(__baseurl__+item.group('url'))
        #img = __baseurl__+item.group('img')
        addDir(title,link,10,icon)
    addDir("<< Minulý mesiac",prev_url,5,icon)
    
    
    
def VIDEOLINK(url, name):
    httpdata = request(url)
    title = re.compile('<title>(.+?)</title>').findall(httpdata)
    title = title[0] + ' ' + name
    video_id = re.search(VIDEO_ID_RE, httpdata, re.IGNORECASE | re.DOTALL).group(1)
    keydata = request("http://embed.stv.livebox.sk/v1/tv-arch.js",referer=url)
    
    rtmp_url_regex="'(rtmp:\/\/[^']+)'\+videoID\+'([^']+)'"
    m3u8_url_regex="'(http:\/\/[^']+)'\+videoID\+'([^']+)'"
    rtmp = re.search(rtmp_url_regex,keydata,re.DOTALL)
    m3u8 = re.search(m3u8_url_regex,keydata,re.DOTALL)
    
    m3u8_url = m3u8.group(1) + video_id + m3u8.group(2)
    
    # rtmp[t][e|s]://hostname[:port][/app[/playpath]]
    # tcUrl=url URL of the target stream. Defaults to rtmp[t][e|s]://host[:port]/app. 
    
    # rtmp url- fix podla mponline2 projektu
    rtmp_url = rtmp.group(1)+video_id+rtmp.group(2)
    stream_part = 'mp4:'+video_id
    playpath = rtmp_url[rtmp_url.find(stream_part):]
    tcUrl = rtmp_url[:rtmp_url.find(stream_part)-1]+rtmp_url[rtmp_url.find(stream_part)+len(stream_part):]
    app = tcUrl[tcUrl.find('/',tcUrl.find('/')+2)+1:]

    #rtmp_url = rtmp_url+ ' playpath=' + playpath + ' tcUrl=' + tcUrl + ' app=' + app
    rtmp_url = rtmp_url+ ' tcUrl=' + tcUrl + ' app=' + app
    
    addLink(name+' [rtmp]', rtmp_url, icon, name)
    addLink(name+' [hls]', m3u8_url, icon, name)

url = None
name = None
thumb = None
mode = None

try:
        url = urllib.unquote_plus(params["url"])
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

print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)

if mode == None or url == None or len(url) < 1:
        print ""
        CATEGORIES()
       
        
elif mode == 1:
        print "" + url
        LIST_TOP(url)
        
elif mode == 2:
        print "" + url
        LIST_NEWEST(url)

elif mode == 3:
        print "" + url
        CATEGORY_AZ(url)
        
elif mode == 4:
        print "" + url
        LIST_AZ(url)
        
elif mode == 5:
        print "" + url
        LIST_TITLE(url)

      
elif mode == 10:
        print "" + url
        VIDEOLINK(url, name)
