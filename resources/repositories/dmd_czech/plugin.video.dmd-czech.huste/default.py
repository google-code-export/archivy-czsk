# -*- coding: utf-8 -*-
import urllib2,urllib,re,os,time
from parseutils import *
from urlparse import urlparse
from datetime import datetime
from util import addDir, addLink
from Plugins.Extensions.archivCZSK.archivczsk import ArchivCZSK

_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
__settings__ = ArchivCZSK.get_addon('plugin.video.dmd-czech.huste')
home = __settings__.get_info('path')
icon = os.path.join(home, 'icon.png')
nexticon = os.path.join(home, 'nextpage.png') 

def OBSAH():
    addDir('Hudba','http://hudba.huste.tv',1,icon)
    addDir('Šport','http://sport.huste.tv',4,icon)
    addDir('Relálie a seriály','http://zabava.huste.tv',2,icon)    
    addDir('Filmy','http://filmy.huste.tv',3,icon)
    addDir('Hlášky','http://hlasky.huste.tv',4,icon)
    addDir('Sport Live & Archiv(BETA)','http://www.huste.tv/services/CurrentLive.xml?nc=6946',11,icon)     

def OBSAH_HUDBA(url):
    addDir('= Interpreti podle abecedy =','http://hudba.huste.tv',5,icon)
    PROUZEK(url)

def OBSAH_RELACE(url):
    addDir('= Podle názvu =','http://zabava.huste.tv',6,icon)
    PROUZEK(url)

def OBSAH_FILMY(url):
    addDir('= Filmy podle abecedy =','http://filmy.huste.tv',8,icon)
    PROUZEK(url)
    
def PROUZEK(url):
    doc = read_page(url)
    items = doc.find('div', id='s-secondary')
    for item in items.findAll('li'):
        name = item.a['title'].encode('utf-8')
        url = str(item.a['href']) 
        addDir(name,url,7,icon)

def ABC(url):
    doc = read_page(url)
    items = doc.find('div', 'b-wrap b-list-alphabet')
    match = re.compile('<a href="(.+?)" title="(.+?)">').findall(str(items))
    for link,name in match:
        addDir(name,link,7,icon)

def FILMY_ABC(url):
    doc = read_page(url)
    items = doc.find('div', 'b-wrap b-list-alphabet')
    match = re.compile('<a href="(.+?)" title="(.+?)">').findall(str(items))
    for link,name in match:
        addDir(name,link,9,icon)
        
def NAZEV(url):
    doc = read_page(url)
    items = doc.find('div', 'b-wrap b-list-simple')
    for item in items.findAll('li'):
        name = item.a['title'].encode('utf-8')
        url = str(item.a['href']) 
        addDir(name,url,7,icon)

    
def INDEX(url):
    doc = read_page(url)
    try:
        items = doc.find('ul', 'l c')
        for item in items.findAll('li','i'):
            title = item.a['title'].encode('utf-8')
            interpret = item.find('p')
            interpret = interpret.getText(" ").encode('utf-8')
            url = str(item.a['href']) 
            thumb = str(item.img['src'])   
            #print name+interpret,url,thumb
            name = title+' - '+interpret
            addDir(name,url,10,thumb)
    except:        
        items = doc.find('div', 'b-wrap b-video')
        items = items.find('ul', 'l c')
        for item in items.findAll('li','i'):
            name = item.a['title'].encode('utf-8')
            interpret = item.find('p')
            interpret = interpret.getText(" ").encode('utf-8')
            url = str(item.a['href']) 
            thumb = str(item.img['src'])   
            name = title+' - '+interpret
            #print name+interpret,url,thumb
            addDir(name,url,10,thumb)
    try:
        pager = doc.find('ul', 'j-center m-page')
        act_page_a = pager.find('li', 'active')
        act_page = act_page_a.getText(" ").encode('utf-8')
        for item in pager.findAll('a'):
            page_url = item['href'].encode('utf-8')
            page_no = item.getText(" ").encode('utf-8')
            #print page_url,page_no
            next_label = '= Strana '+act_page+' >> Další '+page_no+' ='
            if int(page_no) < int(act_page):
                continue
            addDir(next_label,page_url,7,nexticon)
            #print next_label,page_url
    except:
        print 'STRÁNKOVÁNÍ NENALEZENO'

def FILMY_INDEX(url):
    doc = read_page(url)
    items = doc.find('div', 'b-wrap b-video')
    items = items.find('ul', 'l c')
    for item in items.findAll('li','i'):
            name = item.a['title'].encode('utf-8')
            interpret = item.find('p')
            interpret = interpret.getText(" ").encode('utf-8')
            url = str(item.a['href']) 
            thumb = str(item.img['src'])   
            name = name+' - '+interpret
            #print name+interpret,url,thumb
            addDir(name,url,10,thumb)
    try:
        pager = doc.find('ul', 'j-center m-page')
        act_page_a = pager.find('li', 'active')
        act_page = act_page_a.getText(" ").encode('utf-8')
        for item in pager.findAll('a'):
            page_url = item['href'].encode('utf-8')
            page_no = item.getText(" ").encode('utf-8')
            #print page_url,page_no
            next_label = '= Strana '+act_page+' >> Další '+page_no+' ='
            if int(page_no) < int(act_page):
                continue
            addDir(next_label,page_url,7,nexticon)
            #print next_label,page_url
    except:
        print 'STRÁNKOVÁNÍ NENALEZENO'


def LIVE(url):
    doc = read_page(url)
    zapasy = doc.find('events')
    for zapas in zapasy.findAll('event'):
        title = str(zapas['title'].encode('utf-8'))
        nahled = str(zapas['large_image'])
        cas = str(zapas['starttime'])
        cas = cas.replace("+01:00", "");
        if hasattr(datetime, 'strptime'):
            #python 2.6
            strptime = datetime.strptime
        else:
            #python 2.4 equivalent
            strptime = lambda date_string, format: datetime(*(time.strptime(date_string, format)[0:6]))
        cas = strptime(cas, '%Y-%m-%dT%H:%M:%S')
        cas = cas.strftime('%d.%m. %H:%M')
        archiv = str(zapas['archive'])
        link = str(zapas['url'])
        #print title,nahled,cas,archiv,link
        try:
            soubory = zapas.find('files')
            for soubor in soubory.findAll('file'):
                rtmp_url = str(soubor['url'])
                kvalita = str(soubor['quality'])
                rtmp_cesta = str(soubor['path'])
                #print rtmp_url,kvalita,rtmp_cesta
            server = re.compile('rtmp://(.+?)/').findall(rtmp_url)
            tcurl = 'rtmp://'+server[0]
            swfurl = 'http://c.static.huste.tv/fileadmin/templates/swf/HusteMainPlayer.swf'
            if archiv == "1":
                rtmp_url = tcurl+' playpath='+rtmp_cesta+' pageUrl=http://live.huste.tv/ swfurl='+swfurl+' swfVfy=true'  
                name = 'Záznam - ' + cas + ' ' + title
            else:
                rtmp_url = tcurl+' playpath='+rtmp_cesta+' pageUrl=http://live.huste.tv/ swfurl='+swfurl+' swfVfy=true  live=true'
                name = 'Live - ' + cas + ' ' + title
            print name,rtmp_url,nahled
            addLink(name,rtmp_url,nahled,name)
        except:
            name = 'Nedostupné - ' + cas + ' ' + title
            addLink(name,'',nahled,name)
            continue
                
def VIDEOLINK(url,name):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    cast_url = urlparse(url)
    videoid = re.compile('videoId=(.+?)&').findall(httpdata)
    playlisturl = 'http://'+cast_url[1]+'/services/Video.php?clip='+videoid[0]
    print playlisturl
    doc = read_page(playlisturl)
    title = str(doc.event['title'].encode('utf-8'))    
    thumb = str(doc.event['image'])    
    items = doc.find('files')
    for item in items.findAll('file'):
        link = str(item['url'])    
        cesta = str(item['path'])
        kvalita = str(item['label'])             
        server = re.compile('rtmp://(.+?)/').findall(link)
        name = kvalita+ ' - ' + title
        tcurl = 'rtmp://'+server[0]
        swfurl = 'http://b.static.huste.tv/fileadmin/templates/swf/HusteMainPlayer.swf'
        rtmp_url = tcurl+' playpath='+cesta+' pageUrl='+url+' swfUrl='+swfurl+' swfVfy=true'  
        print name,rtmp_url,thumb[0]
        addLink(name,rtmp_url,thumb[0],name)

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
       
elif mode==1:
        print ""+url
        OBSAH_HUDBA(url)

elif mode==2:
        print ""+url
        OBSAH_RELACE(url)

elif mode==3:
        print ""+url
        OBSAH_FILMY(url)

elif mode==4:
        print ""+url
        PROUZEK(url)

elif mode==5:
        print ""+url
        ABC(url)

elif mode==6:
        print ""+url
        NAZEV(url)

elif mode==7:
        print ""+url
        INDEX(url)

elif mode==8:
        print ""+url
        FILMY_ABC(url)

elif mode==9:
        print ""+url
        FILMY_INDEX(url)

elif mode==11:
        print ""+url
        LIVE(url)
        
elif mode==10:
        print ""+url
        VIDEOLINK(url,name)
