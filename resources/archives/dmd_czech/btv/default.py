# -*- coding: utf-8 -*-
import urllib2, urllib, re, os
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

__baseurl__ = 'http://www.b-tv.cz/videoarchiv'
_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'


icon = None
nexticon = None

def getContent(session, params):
    mode = None
    url = None
    name = None
    
    if 'url' in params:
        url = params['url']
    if 'mode' in params:
        mode = params['mode']
    if 'name' in params:
        name = params['name']
    if mode == None or url == None or len(url) < 1:
        print ""
        OBSAH()
       
    elif mode == 1:
        print ""
        INDEX(url)

def OBSAH():
    #self.core.setSorting('NONE')
    req = urllib2.Request(__baseurl__)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    match = re.compile('<li><a  href="(.+?)" title="(.+?)">.+?</a></li>').findall(httpdata)
    for url, name in match:
        addDir(name, __baseurl__ + url, 1, icon)    

            
def INDEX(url):
    doc = read_page(url)
    items = doc.find('table', 'norm')
    items = doc.find('tbody')
    for item in items.findAll('tr'):
        name = re.compile('<a href=".+?">(.+?)</a><br />').findall(str(item))
        link = 'http://www.b-tv.cz' + str(item.a['href']) 
        thumb = str(item.img['src'])  
        try:
            popis = item.find('p')
            popis = popis.getText(" ").encode('utf-8')
        except:
            popis = name[0]
        doc = read_page(link)
        video_url = re.compile('file=(.+?)&').findall(str(doc))
        addLink(name[0], 'http://www.b-tv.cz' + video_url[0], 'http://www.b-tv.cz' + thumb, popis)
    


