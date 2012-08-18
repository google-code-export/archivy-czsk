# -*- coding: utf-8 -*-
import urllib2, urllib, re, os
from urlparse import urlparse
try:
    from Plugins.Extensions.archivCZSK.resources.archives.dmd_czech.tools.parseutils import *
    from Plugins.Extensions.archivCZSK.resources.tools.dmd import addDir, addLink
except ImportError:
    from resources.archives.dmd_czech.tools.parseutils import *
    from resources.tools.dmd import addDir, addLink
try:
    from Plugins.Extensions.archivCZSK import _
    from Components.config import config
except ImportError:
    print 'Unit test'
    stream_server = ''

__dmdbase__ = 'http://iamm.netuje.cz/emulator/joj/image/'
_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
nexticon = None
icon = None

def getContent(url, name, mode, **kwargs):  
    page = kwargs['page']
    
    if page != '' and page is not None:
        page = int(page)
        
    if mode==None or url==None or len(url)<1:
        print ""
        OBSAH()
       
    elif mode==1:
        print ""
        OBSAH_PUB()

    elif mode==2:
        print ""
        OBSAH_SER()

    elif mode==3:
        print ""
        OBSAH_ZAB()

    elif mode==4:
        print ""+url
        print ""+str(page)        
        LIST(url,page)

    elif mode==5:
        print ""+url
        LIST_2(url)

    elif mode==6:
        print ""+url
        LIST_3(url)        

    elif mode==7:
        print ""+url
        LIST_4(url) 

    elif mode==8:
        print ""+url
        LIST_5(url)

    elif mode==9:
        print ""+url
        VIDEOPORTAL(url)
      
    elif mode==10:
        print ""+url
        VIDEOLINK(url,name)
    elif mode==11:
        print ""+url
        TALENT(url,name)
    elif mode==12:
        print ""+url
        VP_LIST(url)
    elif mode==13:
        print ""+url
        VP_PLAY(url,name)

    elif mode==20:
        print ""+url
        PARADISE_CAT_LIST(url)
    elif mode==21:
        print ""+url
        PARADISE_LIST(url)


def OBSAH():
    addDir('Publicistika','http://www.joj.sk',1,icon,1)
    addDir('Seriály','http://www.joj.sk',2,icon,1)
    addDir('Zábava','http://www.joj.sk',3,icon,1)
    addDir('Videoportal.sk','http://www.videoportal.sk/kategorie.html',9,icon,1)
    addDir('Speciál Hotel Paradise','http://hotelparadise.joj.sk/hotelparadise-video/video-epizody.html',20,icon,1)        
def OBSAH_PUB():
    addDir('Črepiny *','http://crepiny.joj.sk/crepiny-s-hviezdickou-archiv.html',4,__dmdbase__+'crepiny-s-hviezdickou.jpg',1)
    addDir('Exclusiv','http://www.joj.sk/exclusiv/exclusiv-archiv.html',4,__dmdbase__+'exclusiv.jpg',1)
    addDir('Krimi noviny','http://krimi.joj.sk/krimi-noviny-archiv.html',4,__dmdbase__+'krimi-noviny.jpg',1)
    addDir('Najlepšie počasie','http://www.joj.sk/najlepsie-pocasie/najlepsie-pocasie-archiv.html',4,__dmdbase__+'najlepsie-pocasie.jpg',1)
    addDir('Noviny','http://www.joj.sk/relacia-noviny/noviny-archiv.html',4,__dmdbase__+'noviny_01.jpg.jpg',1)
    addDir('Noviny o 12:00','http://www.joj.sk/noviny-o-12-00/noviny-o-12-00-archiv.html',4,__dmdbase__+'noviny-o-12-00.jpg.jpg',1)
    addDir('Noviny o 17:00','http://www.joj.sk/noviny-o-17-00/noviny-o-17-00-archiv.html',4,'http://c.static.joj.sk/uploads/tx_media/thumbs/310x175/noviny-o-17-00_79970.jpg',1)
    addDir('Top Star','http://www.joj.sk/top-star/top-star-archiv.html',4,'http://b.static.joj.sk/uploads/tx_media/thumbs/150x82/joj-2-122004-0401-h264-pal_142574.jpg',1)
    addDir('Šport','http://www.joj.sk/relacia-sport/sport-archiv.html',4,__dmdbase__+'sport.jpg',1)
def OBSAH_SER():
    addDir('Aféry','http://afery.joj.sk/afery-epizody.html',4,__dmdbase__+'afery.jpg',1)
    addDir('Ako som prežil','http://www.joj.sk/ako-som-prezil/ako-som-prezil-epizody.html',4,'http://media.televize.cz/film/n1p7zky90ogv.jpg',1)
    addDir('Dr.Ludský','http://www.joj.sk/dr-ludsky/dr-ludsky-epizody.html',4,__dmdbase__+'dr-ludsky.jpg',1)
    addDir('Hoď svišťom','http://hodsvistom.joj.sk/hod-svistom-epizody.html',4,'http://img.csfd.cz/posters/30/300577_1.jpg',1)
    addDir('Keby bolo keby','http://www.joj.sk/keby-bolo-keby/keby-bolo-keby-epizody.html',4,__dmdbase__+'kbk.jpg',1)
    addDir('Mafstory','http://mafstory.joj.sk/mafstory-epizody.html',4,__dmdbase__+'mafstory.jpg',1)
    addDir('Nevinní','http://nevinni.joj.sk/nevinni-epizody.html',4,__dmdbase__+'nevinni.jpg',1)    
    addDir('Panelák','http://panelak.joj.sk/panelak-epizody.html',4,__dmdbase__+'panelak.jpg',1)
    addDir('Profesionáli','http://profesionali.joj.sk/profesionali-epizody.html',4,__dmdbase__+'profesionali.jpg',1)
    addDir('Prvé oddelenie','http://www.joj.sk/prve-oddelenie/prve-oddelenie-epizody.html',4,__dmdbase__+'prve-oddelenie.jpg',1)

def OBSAH_ZAB():
    addDir('Ano, šéfe!','http://anosefe.joj.sk/anosefe-epizody.html',4,__dmdbase__+'anosefe.jpg',1)
    addDir('Bordelári','http://www.bordelari.sk/bordelari-archiv.html',4,'http://a.static.joj.sk/uploads/tx_media/thumbs/306x172/bordelari_79969.jpg',1)
    addDir('ČS má Talent','http://www.csmatalent.cz/video-cz.html',6,__dmdbase__+'talent.jpg',1)
    addDir('Hladá sa milionár','http://www.joj.sk/hlada-sa-milionar/hlada-sa-milionar-archiv.html',4,__dmdbase__+'hlada-sa-milionar.jpg',1)
    addDir('Chutíš mi','http://www.chutismi.sk/chutis-mi-archiv.html',4,__dmdbase__+'chutismi.jpg',1)
    addDir('Extrémne rodiny','http://extremnerodiny.joj.sk/extremne-rodiny-archiv.html',4,'http://c.static.joj.sk/uploads/tx_media/thumbs/306x172/extremne-rodiny_84528.jpg',1)
    addDir('Farmár hľadá ženu 2','http://www.farmarhladazenu.sk/epizody.html',8,'http://t2.gstatic.com/images?q=tbn:ANd9GcRRJbqnrXcT-Ius3Qo29sc-KPVKuNkVjRq5zx51P3FSdpzLL0VD',1)
    addDir('Kapor na torte','http://www.joj.sk/kapor-na-torte-den-prvy/kapor-na-torte-den-prvy-archiv.html',4,__dmdbase__+'kapor-na-torte.jpg',1)
    addDir('Kutyil s.r.o','http://www.joj.sk/kutyil/kutyil-epizody.html',4,__dmdbase__+'kutyil-logo.jpg',1)
    addDir('Mama ožeň ma','http://www.mamaozenma.sk/mama-ozen-ma-epizody.html',7,'http://reality-show.panacek.com/wp-content/2015-mama_ozen_ma2.jpg',1)
    addDir('Nebožies','http://plus.joj.sk/neboziec/epizody.html',4,'http://a.static.joj.sk/uploads/tx_media/thumbs/310x175/logo_77360.jpg',1)
    addDir('Nové bývanie','http://novebyvanie.joj.sk/nove-byvanie-archiv.html',4,__dmdbase__+'nove-byvanie.jpg',1)
    addDir('Sedem','http://www.joj.sk/sedem/sedem-archiv.html',4,__dmdbase__+'sedem.jpg',1)
    addDir('Odsůdené','http://www.joj.sk/odsudene/odsudene-epizody.html',4,__dmdbase__+'odsudene.jpg',1)
    addDir('Sůdna sieň','http://www.joj.sk/sudna-sien/sudna-sien-archiv.html',4,__dmdbase__+'sudna-sien.jpg',1)
    addDir('Šéfka','http://www.sefka.sk/epizody.html',5,__dmdbase__+'sefka-logo.jpg',1)
    addDir('Tajný sen','http://www.joj.sk/tajny-sen/tajny-sen-archiv.html',4,__dmdbase__+'tajny-sen.jpg',1)
    addDir('Riskni milión','http://risknimilion.joj.sk/archiv.html',4,__dmdbase__+'riskni.jpg',1)    


    
def LIST(url,strana):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    if strana !=1:
        strankovani = re.compile('<form action="services(.+?)">').findall(httpdata)  
        cast_url = urlparse(url)
        paging = re.sub('&amp;','&',strankovani[0])        
        paging = 'http://'+cast_url[1]+'/services'+paging
        data = "paging=1&pagingOffset="+str(strana)       
        request = urllib2.Request(paging)
        request.add_data(data)
        request.add_header("Referer",url)    
        request.add_header("Origin","http://"+cast_url[1])
        request.add_header("X-Requested-With","XMLHttpRequest")
        request.add_header("User-Agent",_UserAgent_)
        request.add_header("Content-Type","application/x-www-form-urlencoded")
        con = urllib2.urlopen(request)
        data = con.read()
        con.close()
        httpdata = str(data)
        match = re.compile('<td><strong><a title=".+?" href="(.+?)">(.+?)</a>').findall(httpdata)
    else:        
        match = re.compile('<td><strong><a title=".+?" href="(.+?)">(.+?)</a>').findall(httpdata)        
    for link,name in match:
        #print link,name
        addDir(name,link,10,icon,1)
    try:
        strankovani = re.compile('title="Nasledujúce" href="#" data-name="pagingOffset" data-value="(.+?)"').findall(httpdata)
        next_page = strankovani[0]
        print next_page                
        addDir('>> Další strana >>',url,4,nexticon,str(next_page))
    except:
        print 'strankovani nenalezeno'

def LIST_2(url):
    #self.core.setSorting('NONE')
    doc = read_page(url)
    items = doc.find('div', 'b-body c')
    for item in items.findAll('li'):
        try:
            name = item.a['title'].encode('utf-8')
        except:
            name = 'Bezejmenný titul'
        url = str(item.a['href']) 
        thumb = str(item.img['src'])   
        addDir(name,'http://www.sefka.sk/'+url,10,thumb,1)

def LIST_3(url):
    doc = read_page(url)
    items = doc.find('ul', 'l c')
    for item in items.findAll('li'):
        try:
            name = item.a['title'].encode('utf-8')
        except:
            name = 'Bezejmenný titul'
        url = str(item.a['href']) 
        thumb = str(item.img['src'])   
        addDir(name,'http://www.csmatalent.cz/'+url,11,thumb,1)
    try:
        items = doc.find('ul', 'b-box b-pager-x c')
        dalsi = items.find('li', 'next')
        if len(dalsi) != 0:
            next_url = str(dalsi.a['href']) 
            addDir('>> Další strana >>','http://www.csmatalent.cz/'+next_url,6,nexticon,1)
    except:
        print 'strankovani nenalezeno'

def LIST_4(url):
    doc = read_page(url)
    items = doc.find('ul', 'l c')
    for item in items.findAll('li'):
        try:
            name = item.a['title'].encode('utf-8')
        except:
            name = 'Bezejmenný titul'
        url = str(item.a['href']) 
        thumb = str(item.img['src'])   
        addDir(name,'http://www.mamaozenma.sk/'+url,10,thumb,1)
    try:
        items = doc.find('ul', 'b-box b-pager-x c')
        dalsi = items.find('li', 'next')
        if len(dalsi) != 0:
            next_url = str(dalsi.a['href']) 
            addDir('>> Další strana >>','http://www.mamaozenma.sk/'+next_url,7,nexticon,1)
    except:
        print 'strankovani nenalezeno'

def LIST_5(url):
    doc = read_page(url)
    items = doc.find('ul', 'l c')
    for item in items.findAll('li','i'):
        try:
            name = item.a['title'].encode('utf-8')
        except:
            name = 'Bezejmenný titul'
        url = str(item.a['href']) 
        thumb = str(item.img['src'])   
        addDir(name,'http://www.farmarhladazenu.sk/'+url,10,'http://www.farmarhladazenu.sk/'+thumb,1)
    try:
        items = doc.find('ul', 'b-box b-pager-x c')
        dalsi = items.find('li', 'next')
        if len(dalsi) != 0:
            next_url = str(dalsi.a['href']) 
            addDir('>> Další strana >>','http://www.farmarhladazenu.sk/'+next_url,8,nexticon,1)
    except:
        print 'strankovani nenalezeno'

def VIDEOPORTAL(url):
    doc = read_page(url)
    items = doc.find('div', 'c-full c')
    for item in items.findAll('div','b-wrap b-video b-video-grid b-video-category'):
        name = item.find('a')
        name = name.getText(" ").encode('utf-8')
        url = str(item.a['href']) 
        #print name,url
        addDir(name,'http://www.videoportal.sk/'+url,12,icon,1)

def VP_LIST(url):
    doc = read_page(url)
    items = doc.find('ul', 'l c')
    for item in items.findAll('li'):
        try:
            name = item.a['title'].encode('utf-8')
        except:
            name = 'Bezejmenný titul'
        url = str(item.a['href']) 
        thumb = str(item.img['src'])
        #print name,url, thumb
        addDir(name,'http://www.videoportal.sk/'+url,13,thumb,1)
    try:
        items = doc.find('ul', 'm-move right c')
        match = re.compile('<li><a class="next" href="(.+?)"').findall(str(items))
        addDir('>> Další strana >>','http://www.videoportal.sk/'+match[0],12,nexticon,1)
    except:
        print 'strankovani nenalezeno'
        
def VIDEOLINK(url,name):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    try:
        basepath = re.compile('basePath: "(.+?)"').findall(httpdata)
        videoid = re.compile('videoId: "(.+?)"').findall(httpdata)
        pageid = re.compile('pageId: "(.+?)"').findall(httpdata)
        if len (pageid[0]) != 0:
          playlisturl = basepath[0]+'services/Video.php?clip='+videoid[0]+'pageId='+pageid[0]
        else:
          playlisturl = basepath[0]+'services/Video.php?clip='+videoid[0]
        print playlisturl
        req = urllib2.Request(playlisturl)
        req.add_header('User-Agent', _UserAgent_)
        response = urllib2.urlopen(req)
        doc = response.read()
        response.close()
        title = re.compile('title="(.+?)"').findall(doc)
        thumb = re.compile('large_image="(.+?)"').findall(doc)
        joj_file = re.compile('<file type=".+?" quality="(.+?)" id="(.+?)" label=".+?" path="(.+?)"/>').findall(doc)
        for kvalita,serverno,cesta in joj_file:
            name = str.swapcase(kvalita)+ ' - ' + title[0]
            if config.plugins.archivCZSK.archives.joj.server.value:
                server = 'n09.joj.sk'
            else:
                server = 'n0'+serverno+'.joj.sk'
            tcurl = 'rtmp://'+server
            swfurl = 'http://player.joj.sk/JojPlayer.swf?no_cache=137034'
            port = '1935'
            rtmp_url = tcurl+' playpath='+cesta+' pageUrl='+url+' swfUrl='+swfurl+' swfVfy=true'
            addLink(name,rtmp_url,thumb[0],name)
    except:
        try:
            basepath = re.compile('basePath=(.+?)&amp').findall(httpdata)
            basepath = re.sub('%3A',':',basepath[0])
            basepath = re.sub('%2F','/',basepath)
            videoid = re.compile('videoId=(.+?)&amp').findall(httpdata)
        except:
            videoid = re.compile('video:(.+?).html').findall(str(url))
            basepath = 'http://hotelparadise.joj.sk/'
        playlisturl = basepath+'services/Video.php?clip='+videoid[0]
        print playlisturl
        req = urllib2.Request(playlisturl)
        req.add_header('User-Agent', _UserAgent_)
        response = urllib2.urlopen(req)
        doc = response.read()
        response.close()
        title = re.compile('title="(.+?)"').findall(doc)
        joj_file = re.compile('<file type=".+?" quality="(.+?)" id="(.+?)" label=".+?" path="(.+?)"/>').findall(doc)
        for kvalita,serverno,cesta in joj_file:
            name = str.swapcase(kvalita)+ ' - ' + title[0]
            if config.plugins.archivCZSK.archives.joj.server.value:
                server = 'n09.joj.sk'
            else:
                server = 'n0'+serverno+'.joj.sk'
            tcurl = 'rtmp://'+server
            swfurl = basepath+'fileadmin/templates/swf/csmt_player.swf?no_cache=171307'
            port = '1935'
            rtmp_url = tcurl+' playpath='+cesta+' pageUrl='+url+' swfUrl='+swfurl+' swfVfy=true'
            addLink(name,rtmp_url,icon,name)
def TALENT(url,name):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    basepath = re.compile('basePath: "(.+?)"').findall(httpdata)
    videoid = re.compile('videoId: "(.+?)"').findall(httpdata)
    playlisturl = basepath[0]+'services/Video.php?clip='+videoid[0]
    req = urllib2.Request(playlisturl)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    doc = response.read()
    response.close()
    thumb = re.compile('thumb="(.+?)"').findall(doc)
    joj_file = re.compile('<file type=".+?" quality="(.+?)" id="(.+?)" label=".+?" path="(.+?)"/>').findall(doc)
    for kvalita,serverno,cesta in joj_file:
        titul = str.swapcase(kvalita)+ ' - ' + name
        if config.plugins.archivCZSK.archives.joj.server.value:
            server = 'n09.joj.sk'
        else:
                server = 'n0'+serverno+'.joj.sk'
        tcurl = 'rtmp://'+server
        swfurl = 'http://b.static.csmatalent.sk/fileadmin/templates/swf/CsmtPlayer.swf?no_cache=168842'
        port = '1935'
        rtmp_url = tcurl+' playpath='+cesta+' pageUrl='+url+' swfUrl='+swfurl+' swfVfy=true'
        addLink(titul,rtmp_url,thumb[0],titul)

def VP_PLAY(url,name):
    req = urllib2.Request(url)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    httpdata = response.read()
    response.close()
    videoid = re.compile('videoId=(.+?)&').findall(httpdata)
    playlisturl = 'http://www.videoportal.sk/services/Video.php?clip='+videoid[0]+'&article=undefined'
    req = urllib2.Request(playlisturl)
    req.add_header('User-Agent', _UserAgent_)
    response = urllib2.urlopen(req)
    doc = response.read()
    response.close()
    thumb = re.compile('image="(.+?)"').findall(doc)

    joj_file = re.compile('<file type=".+?" quality="(.+?)" id="(.+?)" label=".+?" path="(.+?)"/>').findall(doc)
    for kvalita,serverno,cesta in joj_file:
        titul = str.swapcase(kvalita)+ ' - ' + name
        if config.plugins.archivCZSK.archives.joj.server.value:
            server = 'n09.joj.sk'
        else:
                server = 'n'+serverno+'.joj.sk'
        tcurl = 'rtmp://'+server
        swfurl = 'http://player.joj.sk/VideoportalPlayer.swf?no_cache=173329'
        port = '1935'
        rtmp_url = tcurl+' playpath='+cesta+' pageUrl='+url+' swfUrl='+swfurl+' swfVfy=true'
        addLink(titul,rtmp_url,thumb[0],titul)

def PARADISE_CAT_LIST(url):
    doc = read_page(url)
    items = doc.find('div', 'sub active')
    for item in items.findAll('a'):
        link = item['href'].encode('utf-8')
        name = item['title'].encode('utf-8')
        print link,name
        addDir(name,link,21,icon,1)

def PARADISE_LIST(url):
    doc = read_page(url)
    items = doc.find('div', 'c-630 c')
    for item in items.findAll('li','i c'):
        try:
            name = item.img['alt'].encode('utf-8')
            if re.search('image not found', name, re.U):
                name = 'Video nelze přehrát!!!'
        except:
            name = 'Bezejmenný titul'
        url = str(item.a['href']) 
        thumb = str(item.img['src'])   
        #print name,url,thumb
        addDir(name,url,10,thumb,1)
    try:
        items = doc.find('ul', 'x-pager x-pager-center j-centerer-bull c')
        dalsi = items.find('li', 'next')
        if len(dalsi) != 0:
            next_url = str(dalsi.a['href']) 
            addDir('>> Další strana >>',next_url,21,nexticon,1)
    except:
        print 'strankovani nenalezeno'

    
