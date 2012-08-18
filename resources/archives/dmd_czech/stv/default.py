# -*- coding: utf-8 -*-
import urllib2,urllib,re,os
from urlparse import urlparse
try:
    from Plugins.Extensions.archivCZSK.resources.archives.dmd_czech.tools.parseutils import *
    from Plugins.Extensions.archivCZSK.resources.tools.dmd import addDir, addLink
except ImportError:
    from resources.archives.dmd_czech.tools.parseutils import *
    from resources.tools.dmd import addDir, addLink
try:
    from Plugins.Extensions.archivCZSK import _

except ImportError:
    print 'Unit test'

name='STV Archiv'
name_sc='stv'
author='Jiri Vyhnalek'
version='0.1'
about= _('Plugin to play TV video archive www.stv.sk')


_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
__baseurl__ = 'http://www.stv.sk'

icon=None
nexticon=None

def getContent(url, name, mode, **kwargs):  
	if mode==None or url==None:
		print ""
		OBSAH()   
	elif mode==2:
		print ""+url
		OBSAH_RELACE(url)
	elif mode==10:
		print ""+url
		VIDEOLINK(url,name)

def OBSAH():
    doc = read_page(__baseurl__+'/online/archiv/')
    doc = doc.find('select', id='sel3')
    match = re.compile('<option value="(.+?)">(.+?)</option>').findall(str(doc))
    for link,name in match:
            print name,link
            addDir(name,__baseurl__+link,2,icon)    

def OBSAH_RELACE(url):
    doc = read_page(url)
    doc = doc.find('table')
    doc2 = doc.find('tbody')
    cast_url = urlparse(url)
    next = 1
    predchozi = re.compile('<a href="(.+?)" class="prew">.+?</a></th><th class="month" colspan="5">(.+?)</th><th class="arr"><a href="(.+?)" class="prew">.+?</a></th>').findall(str(doc))
    for starsical, nazevcal, dalsical in predchozi:
        continue
    if len(predchozi) < 1:
        predchozi = re.compile('<a href="(.+?)" class="prew">.+?</a></th><th class="month" colspan="5">(.+?)</th><th class="arr no-next">.+?</th>').findall(str(doc))
        next = 0
        for starsical, nazevcal in predchozi:
            continue
    porady = re.compile('<a href="(.+?)" class=".+?">(.+?)</a>').findall(str(doc2))    
    if len(porady) < 1:
        porady = re.compile('<a href="(.+?)" class=".+?" title=".+?">(.+?)</a>').findall(str(doc2))      
    print '<< Starší','http://' + cast_url[1] + cast_url[2] + starsical
    addDir('<< Starší','http://' + cast_url[1] + cast_url[2] + starsical,2,nexticon)   
    for poradlink, poradden in porady:
        poradlink = re.sub('&amp;','&',poradlink)
        poradden = poradden +' '+ nazevcal
        print poradlink,poradden
        addDir(poradden,'http://' + cast_url[1] + cast_url[2] + poradlink,10,icon)   
    if next == 1:
        print '>> Novější' ,'http://' + cast_url[1] + cast_url[2] + dalsical
        addDir('>> Novější','http://' + cast_url[1] + cast_url[2] + dalsical,2,nexticon)   
                
def VIDEOLINK(url,name):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    playlist = re.compile('playlistfile=(.+?)&autostart').findall(httpdata)
    title = re.compile('<title>(.+?)</title>').findall(httpdata)
    streamxml = re.sub('%26','&',playlist[0])  
    req = urllib2.Request(streamxml)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    doc = response.read()
    response.close()
    location = re.compile('<location>(.+?)</location>').findall(str(doc))
    streamer = re.compile('<meta rel="streamer">(.+?)</meta>').findall(str(doc))
    print location[0], streamer[0]
    cesta = 'mp4:'+location[0]
    server = streamer[0]   
    title = title[0] + ' ' + name
    swfurl = 'http://www.stv.sk/online/player/player-licensed-sh.swf'
    rtmp_url = server[9:-3]+' playpath='+cesta+' pageUrl='+url+' swfUrl='+swfurl+' swfVfy=true'  
    print rtmp_url
    addLink(title,rtmp_url,icon,name)
    
    


