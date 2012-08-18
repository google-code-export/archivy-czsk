# -*- coding: utf-8 -*-
import urllib2, urllib, re, os, string, time, base64, datetime
try:
    import hashlib
except ImportError:
    import md5
try:
    from Plugins.Extensions.archivCZSK.resources.archives.dmd_czech.tools.parseutils import *
    from Plugins.Extensions.archivCZSK.resources.tools.dmd import addDir, addLink
    from Plugins.Extensions.archivCZSK.resources.exceptions import archiveException
except ImportError:
    from resources.archives.dmd_czech.tools.parseutils import *
    from resources.tools.dmd import addDir, addLink
    from resources.exceptions import archiveException
try:
    from Plugins.Extensions.archivCZSK import _
    from Components.config import config
    cfg = config
except ImportError:
    print 'Unit test'
    secret_token = ''

__baseurl__ = 'http://voyo.nova.cz'
__dmdbase__ = 'http://iamm.uvadi.cz/xbmc/voyo/'
_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

page_pole_url = []
page_pole_no = []
debug = False
rtmp_token = 'h0M*t:pa$kA'
nova_service_url = 'http://master-ng.nacevi.cz/cdn.server/PlayerLink.ashx'
nova_app_id = 'nova-vod'

nexticon = None
icon = None

def getContent(url, name, mode, **kwargs):  
    page = kwargs['page']     
    if mode == None or url == None or len(url) < 1:
        print ""
        OBSAH()
    elif mode == 1:
        print "" + url
        CATEGORIES_OLD(url)
    elif mode == 5:
        print "" + url
        CATEGORIES(url)
    elif mode == 2:
        print "" + url
        INDEX(url)
    elif mode == 4:
        print "" + url
        INDEX_OLD(url)        
    elif mode == 3:
        print "" + url
        VIDEOLINK(url, name)
       
    
def OBSAH():
    addDir('Seriály', 'http://voyo.nova.cz/serialy/', 5, icon)
    addDir('Pořady', 'http://voyo.nova.cz/porady/', 5, icon)
    addDir('Zprávy', 'http://voyo.nova.cz/zpravy/', 1, icon)
    
def CATEGORIES_OLD(url):
    doc = read_page(url)
    items = doc.find('div', 'productsList series')
    print items
    for item in items.findAll('div', 'section_item'):
        if re.search('Přehrát', str(item), re.U):
                continue
        item2 = item.find('div', 'poster')    
        url = item2.a['href'].encode('utf-8')
        title = item2.a['title'].encode('utf-8')
        thumb = item2.a.img['src'].encode('utf-8')
        #print title,url,thumb
        addDir(title, __baseurl__ + url, 4, thumb)
    try:
        items = doc.find('div', 'pagination')
        dalsi = items.find('span', 'next next_page')
        if len(dalsi) != 0:
            next_url = str(dalsi.a['href']) 
        addDir('>> Další strana >>', __baseurl__ + next_url, 1, nexticon)
    except:
        print 'Stránkování nenalezeno'

def CATEGORIES(url):
    zakazane = ['/porady/28368-duck-tv', '/tvod/serialy/27522-zvire', '/serialy/27540-powder-park', '/serialy/27483-osklive-kacatko-a-ja', '/serialy/26481-odvazny-crusoe', '/serialy/26482-5-dnu-do-pulnoci', '/serialy/3924-patty-hewes', '/serialy/27216-lazytown', '/serialy/3923-tudorovci', '/serialy/3906-kobra-11']
    doc = read_page(url)
    items = doc.find('div', 'productsList series')
    for item in items.findAll('li', 'item_ul'):
        if re.search('Přehrát', str(item), re.U):
                continue
        item2 = item.find('div', 'poster')    
        url = item2.a['href'].encode('utf-8')
        title = item2.a['title'].encode('utf-8')
        thumb = item2.a.img['src'].encode('utf-8')
        #print title,url,thumb
        if url in zakazane:
            continue
        addDir(title, __baseurl__ + url, 2, thumb)
    try:
        items = doc.find('div', 'pagination')
        dalsi = items.find('span', 'next next_page')
        if len(dalsi) != 0:
            next_url = str(dalsi.a['href']) 
        addDir('>> Další strana >>', __baseurl__ + next_url, 5, nexticon)
    except:
        print 'Stránkování nenalezeno'
        
def INDEX_OLD(url):
    doc = read_page(url)
    items = doc.find('div', 'productsList')
    for item in items.findAll('div', 'section_item'):
            item = item.find('div', 'poster')
            url = item.a['href'].encode('utf-8')
            title = item.a['title'].encode('utf-8')
            thumb = item.a.img['src'].encode('utf-8')
            print title, url, thumb
            addDir(title, __baseurl__ + url, 3, thumb)
    try:
        items = doc.find('div', 'pagination')
        for item in items.findAll('a'):
            page = item.text.encode('utf-8') 
            if re.match('další', page, re.U):
                next_url = item['href']
                #print next_url
                addDir('>> Další strana >>', __baseurl__ + next_url, 4, nexticon)                
    except:
        print 'strankovani nenalezeno'

def INDEX(url):
    vyjimka = ['/porady/29930-farma-komentare-vypadnutych', '/porady/29745-farma-cele-dily', '/porady/29564-farma-necenzurovane-dily', '/porady/29563-farma-deniky-soutezicich']
    doc = read_page(url)
    items = doc.find('div', 'productsList series')
    for item in items.findAll('li', 'item_ul'):
            item = item.find('div', 'poster')
            url = item.a['href'].encode('utf-8')
            title = item.a['title'].encode('utf-8')
            thumb = item.a.img['src'].encode('utf-8')
            if debug:
                print title, url, thumb
            if url in vyjimka:
                addDir(title, __baseurl__ + url, 2, thumb)
                continue
            addDir(title, __baseurl__ + url, 3, thumb)
    try:
        items = doc.find('div', 'pagination')
        for item in items.findAll('a'):
            page = item.text.encode('utf-8') 
            if re.match('další', page, re.U):
                next_url = item['href']
                #print next_url
                addDir('>> Další strana >>', __baseurl__ + next_url, 2, nexticon)                
    except:
        print 'strankovani nenalezeno'

        
def VIDEOLINK(url, name):
    secret_token = cfg.plugins.archivCZSK.archives.voyo.password.value
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    mediaid = re.compile('mainVideo = new mediaData\(.+?, .+?, (.+?),').findall(httpdata)
    thumb = re.compile('<link rel="image_src" href="(.+?)" />').findall(httpdata)
    popis = re.compile('<meta name="description" content="(.+?)" />').findall(httpdata)
    datum = datetime.datetime.now()
    timestamp = datum.strftime('%Y%m%d%H%M%S')
    videoid = urllib.quote(nova_app_id + '|' + mediaid[0])
    md5hash = nova_app_id + '|' + mediaid[0] + '|' + timestamp + '|' + secret_token
    try:
        md5hash = hashlib.md5(md5hash)
    except:
        md5hash = md5.new(md5hash)
    signature = urllib.quote(base64.b64encode(md5hash.digest()))
    config = nova_service_url + '?t=' + timestamp + '&d=1&tm=nova&h=0&c=' + videoid + '&s=' + signature    
    print config
    try:
        desc = popis[0]
    except:
        desc = name
    req = urllib2.Request(config)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    if debug:
        print httpdata
    error_secret_token = re.compile('<errorCode>(.+?)</errorCode>').findall(httpdata)
    try:
        chyba = int(error_secret_token[0])
    except:
        chyba = 0
    if chyba == 2:    
        print 'Nesprávné tajné heslo'
        raise archiveException.CustomError(_('Password is not correct'))     
    elif chyba == 1:    
        print 'Špatné časové razítko'
        raise archiveException.CustomInfoError(_('The show can only be played on Voyo.cz page'))      
    elif chyba == 0:
        baseurl = re.compile('<baseUrl>(.+?)</baseUrl>').findall(httpdata)
        streamurl = re.compile('<media>\s<quality>(.+?)</quality>.\s<url>(.+?)</url>\s</media>').findall(httpdata)        
        for kvalita, odkaz in streamurl:
            #print kvalita,odkaz
            if re.match('hd', kvalita, re.U):
                urlhd = odkaz.encode('utf-8')
            elif re.match('hq', kvalita, re.U):
                urlhq = odkaz.encode('utf-8')
            elif re.match('lq', kvalita, re.U):
                urllq = odkaz.encode('utf-8')
        print urlhq, urllq
        swfurl = 'http://voyo.nova.cz/static/shared/app/flowplayer/13-flowplayer.commercial-3.1.5-19-003.swf'
        if debug:          
            rtmp_url_lq = baseurl[0] + ' playpath=' + urllq + ' pageUrl=' + url + ' swfUrl=' + swfurl + ' swfVfy=true token=' + rtmp_token 
            rtmp_url_hq = baseurl[0] + ' playpath=' + urlhq + ' pageUrl=' + url + ' swfUrl=' + swfurl + ' swfVfy=true token=' + rtmp_token 
            try:
                rtmp_url_hd = baseurl[0] + ' playpath=' + urlhd + ' pageUrl=' + url + ' swfUrl=' + swfurl + ' swfVfy=true token=' + rtmp_token 
            except:
                rtmp_url_hd = 0
        else:
            rtmp_url_lq = baseurl[0] + ' playpath=' + urllq
            rtmp_url_hq = baseurl[0] + ' playpath=' + urlhq
            try:
                rtmp_url_hd = baseurl[0] + ' playpath=' + urlhd            
            except:
                rtmp_url_hd = 0
        #if __settings__.getSetting('kvalita_sel') == "HQ":
        addLink('HQ ' + name, rtmp_url_hq, icon, desc)
        #elif __settings__.getSetting('kvalita_sel') == "LQ":
        addLink('LQ ' + name, rtmp_url_lq, icon, desc)
        #elif __settings__.getSetting('kvalita_sel') == "HD":
        if rtmp_url_hd == 0:
            pass
                #addLink(name, rtmp_url_hq, icon, desc)                
        else:
            addLink('HD ' + name, rtmp_url_hd, icon, desc)
       # else:
           # addLink(name, rtmp_url_hq, icon, desc)  
