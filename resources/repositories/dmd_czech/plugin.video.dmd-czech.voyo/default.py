# -*- coding: utf-8 -*-
import urllib2, urllib, re, os, string, time, base64, datetime
from urlparse import urlparse
try:
    import hashlib
except ImportError:
    import md5

from util import addDir, addLink, showWarning
from Plugins.Extensions.archivCZSK.archivczsk import ArchivCZSK

from parseutils import *
__baseurl__ = 'http://voyo.nova.cz'
__dmdbase__ = 'http://iamm.uvadi.cz/xbmc/voyo/'
_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
__settings__ = ArchivCZSK.get_addon('plugin.video.dmd-czech.voyo')
home = __settings__.get_info('path')
icon = os.path.join(home, 'icon.png')
nexticon = os.path.join(home, 'nextpage.png') 
page_pole_url = []
page_pole_no = []
secret_token = __settings__.get_setting('secret_token')
rtmp_token = 'h0M*t:pa$kA'
nova_service_url = 'http://master-ng.nacevi.cz/cdn.server/PlayerLink.ashx'
nova_app_id = 'nova-vod'
if secret_token == '':
    showWarning(u"Doplněk DMD VOYO Zadejte tajné heslo!")
    #__settings__.open_settings(session) 
def OBSAH():
    addDir('Seriály', 'http://voyo.nova.cz/serialy/', 5, icon, 1)
    addDir('Pořady', 'http://voyo.nova.cz/porady/', 5, icon, 1)
    addDir('Zprávy', 'http://voyo.nova.cz/zpravy/', 4, icon, 1)
    
def CATEGORIES_OLD(url, page):
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
        addDir('>> Další strana >>', __baseurl__ + next_url, 1, nexticon, 1)
    except:
        print 'Stránkování nenalezeno'

def CATEGORIES(url, page):
    i = 0
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    section_id = re.compile('var ut_section_id = "(.+?)"').findall(httpdata)
    urlPath = urlparse(url)[2]
    try:
        match = re.compile('<div id="[0-9A-Za-z]+_productsListFoot">(.+?)Všechny seriály</p>', re.S).findall(httpdata)
        pageid = re.compile("'boxId': '(.+?)'", re.S).findall(str(match[0]))
        
    except:
        print "id nenalezeno"
    strquery = '?count=35&sectionId=' + section_id[0] + '&showAs=2013&urlPath=' + urlPath + '&boxId=' + pageid[0] + '&resultType=categories&disablePagination=n&page=' + str(page) + '&sortOrder=DESC&letterFilter=false'    
    request = urllib2.Request(url, strquery)
    request.add_header("Referer", url)
    request.add_header("Host", "voyo.nova.cz")
    request.add_header("Origin", "http://voyo.nova.cz")
    request.add_header("X-Requested-With", "XMLHttpRequest")
    request.add_header("User-Agent", _UserAgent_)
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    con = urllib2.urlopen(request)
    data = con.read()
    con.close()    
    doc = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    items = doc.find('div', 'productsList series')
    for item in items.findAll('li', 'item_ul'):
        if re.search('Přehrát', str(item), re.U):
                continue
        item2 = item.find('div', 'poster')    
        url2 = item2.a['href'].encode('utf-8')
        title = item2.a['title'].encode('utf-8')
        thumb = item2.a.img['src'].encode('utf-8')
        #print title,url,thumb
        i = i + 1
        addDir(title, __baseurl__ + url2, 2, thumb, 1)
    if i == 35:
        page = page + 1
        addDir('>> Další strana >>', url, 5, nexticon, page)
        
def INDEX_OLD(url, page):
    doc = read_page(url)
    items = doc.find('div', 'productsList')
    for item in items.findAll('div', 'section_item'):
            item = item.find('div', 'poster')
            url = item.a['href'].encode('utf-8')
            title = item.a['title'].encode('utf-8')
            thumb = item.a.img['src'].encode('utf-8')
            print title, url, thumb
            addDir(title, __baseurl__ + url, 3, thumb, 1)
    try:
        items = doc.find('div', 'pagination')
        for item in items.findAll('a'):
            page = item.text.encode('utf-8') 
            if re.match('další', page, re.U):
                next_url = item['href']
                #print next_url
                addDir('>> Další strana >>', __baseurl__ + next_url, 4, nexticon, 1)                
    except:
        print 'strankovani nenalezeno'

def INDEX(url, page):
    vyjimka = ['/porady/30359-farma-epizody', '/porady/30359-farma-nejnovejsi-dily', '/porady/29930-farma-komentare-vypadnutych', '/porady/29745-farma-cele-dily', '/porady/29564-farma-necenzurovane-dily', '/porady/29563-farma-deniky-soutezicich']
    i = 0
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    section_id = re.compile('var ut_section_id = "(.+?)"').findall(httpdata)
    product_id = re.compile('<input type="hidden" name="productId" value="(.+?)"').findall(httpdata)
    urlPath = urlparse(url)[2]
    try:
        match = re.compile('<div id="[0-9A-Za-z]+_productsListFoot">(.+?)Všechny seriály</p>', re.S).findall(httpdata)
        pageid = re.compile("'boxId': '(.+?)'", re.S).findall(str(match[0]))        
    except:
        print "strankovani nenalezeno"       
    strquery = '?count=35&sectionId=' + section_id[0] + '&productId=' + product_id[0] + '&showAs=2013&urlPath=' + urlPath + '&boxId=' + pageid[0] + '&disablePagination=n&page=' + str(page) + '&sortOrder=DESC&letterFilter=false'    
    request = urllib2.Request(url, strquery)
    request.add_header("Referer", url)
    request.add_header("Host", "voyo.nova.cz")
    request.add_header("Origin", "http://voyo.nova.cz")
    request.add_header("X-Requested-With", "XMLHttpRequest")
    request.add_header("User-Agent", _UserAgent_)
    request.add_header("Content-Type", "application/x-www-form-urlencoded")
    con = urllib2.urlopen(request)
    data = con.read()
    con.close()    
    doc = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    items = doc.find('div', 'productsList series')
    for item in items.findAll('li', 'item_ul'):
            item = item.find('div', 'poster')
            url2 = item.a['href'].encode('utf-8')
            title = item.a['title'].encode('utf-8')
            thumb = item.a.img['src'].encode('utf-8')
            if url2 in vyjimka:
                print title, url2, thumb
                addDir(title, __baseurl__ + url2, 2, thumb, 1)
                continue
            print title, url, thumb
            addDir(title, __baseurl__ + url2, 3, thumb, 1)
            i = i + 1
            print title
            if i == 35:
                page = page + 1
                addDir('>> Další strana >>', url, 5, nexticon, page)

        
def VIDEOLINK(url, name):
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
    if __settings__.get_setting('test_nastaveni'):
        print httpdata
    error_secret_token = re.compile('<errorCode>(.+?)</errorCode>').findall(httpdata)
    try:
        chyba = int(error_secret_token[0])
    except:
        chyba = 0
    if chyba == 2:    
        print 'Nesprávné tajné heslo'
        showWarning(u"Doplněk DMD VOYO Nesprávné tajné heslo!")
        #__settings__.open_settings(session)        
    elif chyba == 1:    
        print 'Špatné časové razítko'
        showError(u"Doplněk DMD VOYO Pořad lze přehrát pouze na webu Voyo.cz!")
        #xbmc.executebuiltin("XBMC.Notification('Doplněk DMD VOYO','Pořad lze přehrát pouze na webu Voyo.cz!',30000,"+icon+")")      
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
        if __settings__.get_setting('test_nastaveni'):          
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
        if __settings__.get_setting('kvalita_sel') == "HQ":
            addLink(name, rtmp_url_hq, icon, desc)
        elif __settings__.get_setting('kvalita_sel') == "LQ":
            addLink(name, rtmp_url_lq, icon, desc)
        elif __settings__.get_setting('kvalita_sel') == "HD":
            if rtmp_url_hd == 0:
                addLink(name, rtmp_url_hq, icon, desc)                
            else:
                addLink(name, rtmp_url_hd, icon, desc)
        else:
            addLink(name, rtmp_url_hq, icon, desc)                




url = None
name = None
thumb = None
mode = None
page = None

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
try:
        page = int(params["page"])
except:
        pass

print "Mode: " + str(mode)
print "URL: " + str(url)
print "Name: " + str(name)
print "Page: " + str(page)

if mode == None or url == None or len(url) < 1:
        print ""
        OBSAH()

elif mode == 1:
        print "" + url
        print "" + str(page)                
        CATEGORIES_OLD(url, page)
elif mode == 5:
        print "" + url
        print "" + str(page)        
        CATEGORIES(url, page)
     
       
elif mode == 2:
        print "" + url
        print "" + str(page)        
        INDEX(url, page)
elif mode == 4:
        print "" + url
        print "" + str(page)                
        INDEX_OLD(url, page)        

        
elif mode == 3:
        print "" + url
        VIDEOLINK(url, name)