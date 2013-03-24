# -*- coding: utf-8 -*-
import urllib2,urllib,re,os
from parseutils import *
from urlparse import urlparse,parse_qs
from util import addDir, addLink, getSearch
from Plugins.Extensions.archivCZSK.archivczsk import ArchivCZSK

_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
__baseurl__ = 'http://www.stv.sk'
__settings__ = ArchivCZSK.get_addon('plugin.video.dmd-czech.stv')
home = __settings__.get_info('path')
icon = os.path.join(home, 'icon.png')
nexticon = os.path.join(home, 'nextpage.png') 

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
                
def VIDEOLINK(url, name):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    title = re.compile('<title>(.+?)</title>').findall(httpdata)
    title = title[0] + ' ' + name
    video_id = re.search('.*?LiveboxPlayer.flash\(.+?stream_id:+.\"(.+?)\"', httpdata, re.IGNORECASE | re.DOTALL)
    video_id = video_id.group(1)
    print video_id
    
    req = urllib2.Request("http://embed.stv.livebox.sk/v1/tv-arch.js")
    req.add_header('User-Agent', _UserAgent_)
    req.add_header('Referer', url)
    response = urllib2.urlopen(req)
    keydata = response.read()
    #print keydata
    response.close()
    auth = re.search(".*?auth=(.+?)\'", keydata, re.IGNORECASE | re.DOTALL)
    #auth = re.search(".*?auth=b64:(.+?)\'", keydata, re.IGNORECASE | re.DOTALL)
    auth = auth.group(1)#base64.decodestring(auth.group(1))
    streamer = re.search(".*?rtmp:\/\/(.+?)\/", keydata, re.IGNORECASE | re.DOTALL)
    streamer = streamer.group(1)
    
    url = 'rtmp://' + streamer + '/stv-tv-arch/_definst_/mp4:' + video_id + '?auth=' + auth
    #title = namehttp://embed.stv.livebox.sk/v1/LiveboxPlayer.swf?nocache=1364079106732
    swfurl = 'http://embed.stv.livebox.sk/v1/LiveboxPlayer.swf'
    #swfurl = 'http://www.stv.sk/online/player/player-licensed-sh.swf'
    rtmp_url = '"' + url + '"' + '-W ' + swfurl
    #print rtmp_url
    m3u8_url = 'http://'+streamer+'/stv-tv-arch/_definst_/' + video_id +  '/playlist.m3u8?auth='+ auth
    print m3u8_url
    
    # rtmp stream mi nefunguje, len hls...
    #addLink(title, rtmp_url, icon, name)
    addLink(name, m3u8_url, icon, name)

url=None
name=None
thumb=None
mode=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None or url==None or len(url)<1:
        print ""
        OBSAH()
       
elif mode==2:
        print ""+url
        OBSAH_RELACE(url)

      
elif mode==10:
        print ""+url
        VIDEOLINK(url,name)
