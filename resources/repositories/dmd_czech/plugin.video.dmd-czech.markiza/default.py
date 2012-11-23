# -*- coding: utf-8 -*-
import urllib2,urllib,re,os
from parseutils import *
from util import addDir, addLink
from Plugins.Extensions.archivCZSK.archivczsk import ArchivCZSK

__baseurl__= 'http://voyo.markiza.sk'
_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

__settings__ = ArchivCZSK.get_addon('plugin.video.dmd-czech.markiza')
home = __settings__.get_info('path')
icon = os.path.join(home, 'icon.png')
nexticon = os.path.join(home, 'nextpage.png') 

def OBSAH():
    addDir('Seriály',__baseurl__+'/serialy/',1,icon)
    addDir('Relácie',__baseurl__+'/relacie/',1,icon)
    addDir('Šport',__baseurl__+'/sport/',1,icon)
    addDir('Spravodajstvo',__baseurl__+'/spravodajstvo/',1,icon)        


def CAT_VOYO(url):
    doc = markiza_read(url)
    zakazane = ['/serialy/1691-comeback-i','/serialy/1693-dokonaly-svet-i']
    items = doc.find('div', 'productsList')    
    for item in items.findAll('div', 'section_item'):
        porad = item.find('div', 'poster')
        info = item.find('div', 'item_info')
        info = info.find('a', 'watch_now only')
        if re.search('Prehrať', str(info), re.U):
            continue
        url = porad.a['href'].encode('utf-8')
        title = porad.a['title'].encode('utf-8')
        thumb = porad.a.img['src'].encode('utf-8')
        print title, url, thumb
        if url in zakazane:
            continue
        addDir(title,__baseurl__+url,5,thumb)
    try:
        items = doc.find('div', 'productsList')
        for item in items.findAll('li', 'item_ul'):
            porad = item.find('div', 'poster')
            url = porad.a['href'].encode('utf-8')
            title = porad.a['title'].encode('utf-8')
            thumb = porad.a.img['src'].encode('utf-8')
            print title, url, thumb
            if url in zakazane:
                continue
            addDir(title,__baseurl__+url,5,thumb)
    except:
        print 'Stránkování nenalezeno',url


def LIST_VOYO(url):
    doc = markiza_read(url)
    items = doc.find('div', 'productsList')
    for item in items.findAll('div', 'poster'):
        title = item.a['title'].encode('utf-8')
        name_a = item.a['href']
        url = __baseurl__+name_a
        thumb = str(item.img['src'])  
        addDir(title,url,10,thumb)
    try:
        pager = doc.find('div', 'pagination')
        next_item = pager.findAll('a')
        for item in next_item:
            if item.getText(" ").encode('utf-8') != '>':
                continue
            else:
                next_url = item['href']
        addDir('Další strana >>',__baseurl__+ next_url,5,nexticon)
    except:
        print 'STRANKOVANI NENALEZENO'

             
def VIDEOLINK_VOYO(url,name):
    #req = urllib2.Request(url)
    #req.add_header('User-Agent', _UserAgent_)
    #response = urllib2.urlopen(req)
    #httpdata = response.read()
    #response.close()
    #param1 = re.compile('mainVideo = new mediaData\((.+?), (.+?), (.+?),').findall(httpdata)    
    #for prod,unit,media in param1:
        #conn1 = prod
        #conn2 = unit
        #conn3 = media
    URL2ALIAS = {'rodinna-kliatba':'rodkliatba',
                 'druhy-dych':'druhydych',
                 'mesto-tienov':'mestotienov',
                 'televizne-noviny':'tn',
                 'prve-televizne-noviny':'ptn',
                 'rychle-televizne-noviny-13-00':'rtn1300',
                 'rychle-televizne-noviny-14-00':'rtn1400',
                 'rychle-televizne-noviny-15-00':'rtn1500',
                 'rychle-televizne-noviny-16-00':'rtn1600',
                 'rychle-televizne-noviny-17-00':'rtn1700',
                 'rychle-televizne-noviny-18-00':'rtn1800',
                 'prve-pocasie':'ppocasie',
                 'sportove-noviny':'sport',
                 'zo-zakulisia-markizy':'zakulisie',
                 'na-telo':'natelo',
                 'modre-z-neba':'mzn',
                 'bez-servitky':'servitka',
                 'mafianske-popravy':'popravy',
                 'tudorovci-sex-moc-a-intrigy':'tudors',
                 'sudkyna-hattchetova':'sudkyna',
                 'dr-oz':'droz',
                 'comeback-i':'comebacki',
                 'v-dobrom-aj-v-zlom':'vdobrom',                
                 'vo-stvorici-po-slovensku':'vostvorici',
                 'dokonaly-svet-i':'sveti'}
    if re.search('rychle-televizne-noviny', url, re.U):
        match = re.compile('\/[0-9]+-(.+?)-([0-9]+)-([0-9]+)-([0-9]+)-([0-9]+)-([0-9]+)-.+?').findall(url)
        for jmeno,hodina,minuta,mesic,den,rok in match:
            jmeno = jmeno+'-'+hodina+'-'+minuta
            if URL2ALIAS.has_key(jmeno):
                jmeno = URL2ALIAS[jmeno].swapcase()        
    else:            
        match = re.compile('\/[0-9]+-(.+?)-([0-9]+)-([0-9]+)-([0-9]+)-.+?').findall(url)
        for jmeno,mesic,den,rok in match:
            print jmeno,mesic,den,rok
            if URL2ALIAS.has_key(jmeno):
                jmeno = URL2ALIAS[jmeno]
            if re.search('-', jmeno, re.U):
                jmeno = re.compile('(.+?)-.+?').findall(jmeno)
                jmeno = jmeno[0]
        jmeno = jmeno.swapcase()
    cesta = 'mp4:'+rok+'/'+den+'/'+mesic+'/'+rok+'-'+den+'-'+mesic+'_'+jmeno+'-1.mp4'
    print jmeno,den,mesic,rok,cesta
    swfurl = 'http://voyo.markiza.sk/static/shared/app/flowplayer/13-flowplayer.cluster-3.2.1-01-004.swf'
    #lqurl = 'rtmpe://vod.markiza.sk/voyosk playpath='+cesta+' pageUrl='+url+' swfUrl='+swfurl+' swfVfy=true'
    #lqurl = 'rtmpe://vod.markiza.sk/voyosk playpath='+cesta+' app=voyosk flashver=WIN11,1,102,62 conn=O:1 conn=NN:0:2279338.000000 conn=NS:1: conn=NN:2:1847.000000 conn=NS:3:null conn=O:0 pageUrl='+url+' swfUrl='+swfurl+' swfVfy=true'
    #lqurl = 'rtmpe://vod.markiza.sk/voyosk playpath='+cesta+' app=voyosk flashver=WIN11,1,102,62 conn=O:1 conn=NN:0:'+conn3+'.000000 conn=NS:1: conn=NN:2:'+conn1+'.000000 conn=NS:3:null conn=O:0 pageUrl='+url+' swfUrl='+swfurl+' swfVfy=true'
    #lqurl = 'rtmpe://vod.markiza.sk/voyosk playpath='+cesta+' conn=O:1 conn=NN:0:'+conn3+'.000000 conn=NS:1:'+conn1+'.000000 conn=NN:2:'+conn2+'.000000 conn=NS:3:null conn=O:0 pageUrl='+url+' swfUrl='+swfurl+' swfVfy=true'    
    lqurl = 'rtmpe://vod.markiza.sk/voyosk playpath='+cesta+' conn=O:1 conn=NN:0:2274958.000000 conn=NS:1: conn=NN:2:1408.000000 conn=NS:3:null conn=O:0 pageUrl='+url+' swfUrl='+swfurl+' swfUrl=true'
    addLink(name,lqurl,icon,name)



def markiza_read(url):

    try:

        read_page(url)

    except:

        pass

    count = 0

    while (count < 20):

        count = count + 1

        try:

            doc1 = read_page(url)

            doc2 = read_page(url)

        except:

            pass

            break

        if doc1 == doc2:

            return doc1

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
        CAT_VOYO(url)

elif mode==5:
        print ""+url
        LIST_VOYO(url)

        
elif mode==10:
        print ""+url
        VIDEOLINK_VOYO(url,name)
