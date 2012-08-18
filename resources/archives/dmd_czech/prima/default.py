# -*- coding: utf-8 -*-
import urllib2, urllib, re, os, random, decimal
try:
    from Plugins.Extensions.archivCZSK.resources.archives.dmd_czech.tools.parseutils import *
    from Plugins.Extensions.archivCZSK.resources.tools.dmd import addDir,addLink
except ImportError:
    from resources.archives.dmd_czech.tools.parseutils import *
    from resources.tools.dmd import addDir,addLink
try:
    from Plugins.Extensions.archivCZSK import _
except ImportError:
    print 'Unit test'

name = 'Prima PLAY'
name_sc = 'prima'
author = 'Jiri Vyhnalek'
version = '2.4'
about = _('Plugin to play TV video archive iprima.cz/videoarchiv')

__baseurl__ = 'http://www.iprima.cz/videoarchiv'
__cdn_url__ = 'http://cdn-dispatcher.stream.cz/?id='
__dmdbase__ = 'http://iamm.uvadi.cz/xbmc/prima/'
_UserAgent_ = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'

prima = None
love = None
family = None
cool = None
icon = None
nexticon = None

def getContent(url, name, mode, **kwargs):  
    page = kwargs['page']
    kanal = kwargs['kanal']
    
    if page != '' and page is not None:
        page = int(page)
    if kanal != '' and kanal is not None:
        kanal = int(kanal)
        
    if mode == None or url == None or len(url) < 1:
        OBSAH()
       
    elif mode == 1:
        print "" + str(url)
        print "" + str(kanal)
        print "" + str(page)
        KATEGORIE(url, page, kanal)

    elif mode == 4:
        print "" + str(url)
        print "" + str(kanal)
        print "" + str(page)
        INDEX(url, page, kanal)
        
    elif mode == 10:
        print "" + url
        VIDEOLINK(url, name)

def replace_words(text, word_dic):
    rc = re.compile('|'.join(map(re.escape, word_dic)))
    def translate(match):
        return word_dic[match.group(0)]
    return rc.sub(translate, text)


word_dic = {
'\u00e1': 'á',
'\u00e9': 'é',
'\u00ed': 'í',
'\u00fd': 'ý',
'\u00f3': 'ó',
'\u00fa': 'ú',
'\u016f': 'ů',
'\u011b': 'ě',
'\u0161': 'š',
'\u0165': 'ť',
'\u010d': 'č',
'\u0159': 'ř',
'\u017e': 'ž',
'\u010f': 'ď',
'\u0148': 'ň',
'\u00C0': 'Á',
'\u00c9': 'É',
'\u00cd': 'Í',
'\u00d3': 'Ó',
'\u00da': 'Ú',
'\u016e': 'Ů',
'\u0115': 'Ě',
'\u0160': 'Š',
'\u010c': 'Č',
'\u0158': 'Ř',
'\u0164': 'Ť',
'\u017d': 'Ž',
'\u010e': 'Ď',
'\u0147': 'Ň'
}

def OBSAH():
    addDir('Family','http://play.iprima.cz/iprima',1,family,'','1')
    addDir('Love','http://play.iprima.cz/love',1,love,'','3')
    addDir('COOL','http://play.iprima.cz/cool',1,cool,'','2')
    
def KATEGORIE(url,page,kanal):
    porady = []
    request = urllib2.Request(url)
    con = urllib2.urlopen(request)
    data = con.read()
    con.close()
    data = re.compile('var topcat = \[(.+?)\];').findall(data)
    match = re.compile('"name":"(.+?)","tid":"(.+?)"').findall(data[0])
    for porad,porad_id in match:
        porady.append([porad,porad_id])
        porady.sort()   
    for porad, porad_id in porady:
        #print porad, porad_id
        #porad=replace_words(porad)
        addDir(replace_words(porad, word_dic),porad_id,4,__dmdbase__+porad_id+'.jpg',0,kanal)


    
def INDEX(url,page,kanal):
    if int(page) != 0:
        strquery = '?method=json&action=relevant&per_page=12&channel='+str(kanal)+'&page='+str(page)
    else:
        strquery = '?method=json&action=relevant&per_page=12&channel='+str(kanal)
    doc = read_page('http://play.iprima.cz/videoarchiv_ajax/all/'+str(url)+strquery)
    tid = re.compile('"tid":"(.+?)"').findall(str(doc))
    match = re.compile('"nid":"(.+?)","title":"(.+?)","image":"(.+?)","date":"(.+?)"').findall(str(doc))
    for videoid,name,thumb,datum in match:
            name = replace_words(name, word_dic)
            thumb = replace_words(thumb, word_dic)
            thumb = re.sub('98x55','280x158',thumb)
            if kanal == 1:
                addDir(str(name),'http://play.iprima.cz/iprima/'+videoid+'/'+tid[0],10,'http://www.iprima.cz/'+thumb,'','')
            elif kanal == 2:
                addDir(str(name),'http://play.iprima.cz/cool/'+videoid+'/'+tid[0],10,'http://www.iprima.cz/'+thumb,'','')
            elif kanal == 3:
                addDir(str(name),'http://play.iprima.cz/love/'+videoid+'/'+tid[0],10,'http://www.iprima.cz/'+thumb,'','')
    strankovani = re.compile('"total":(.+?),"from":.+?,"to":.+?,"page":(.+?),').findall(str(doc))
    for page_total,act_page in strankovani:
        print page_total,act_page
        if int(page_total) > 12:
            act_page = act_page.replace('"','')
            next_page = int(act_page)  + 1
            max_page =  int(round(int(page_total)/12 ) )
            if next_page < max_page+1:
                max_page = str(max_page+1)
                #print '>> Další strana >>',url,1,next_page
                addDir('>> Další strana ('+str(next_page+1)+' z '+max_page+')',url,4,nexticon,next_page,kanal)
        
def VIDEOLINK(url,name):
    strquery = '?method=json&action=video'
    request = urllib2.Request(url, strquery)
    con = urllib2.urlopen(request)
    data = con.read()
    con.close()
    print url
    stream_video = re.compile('cdnID=([0-9]+)').findall(data)
    if len(stream_video) > 0:
        print 'LQ '+__cdn_url__+name,stream_video[0],icon,''
        addLink('LQ '+name,__cdn_url__+stream_video[0],icon,'')        
    else:
        hq_stream = re.compile("'hq_id':'(.+?)'").findall(data)
        lq_stream = re.compile("'lq_id':'(.+?)'").findall(data)
        hd_stream = re.sub('_1000','_1500',hq_stream[0])
        geo_zone = re.compile("'zoneGEO':(.+?),").findall(data)        
        try:
            thumb = re.compile("'thumbnail': '(.+?)'").findall(data)
            nahled = thumb[0]
        except:
            nahled = icon
        key = 'http://embed.livebox.cz/iprimaplay/player-embed-v2.js?__tok'+str(gen_random_decimal(1073741824))+'__='+str(gen_random_decimal(1073741824))
        req = urllib2.Request(key)
        req.add_header('User-Agent', _UserAgent_)
        req.add_header('Referer', url)
        response = urllib2.urlopen(req)
        keydata = response.read()
        response.close()
        keydata = re.compile("auth=(.*?)'").findall(keydata)
        if geo_zone[0] == "1":
            hd_url = 'rtmp://bcastiw.livebox.cz:80/iprima_token_'+geo_zone[0]+'?auth='+keydata[0]+'/mp4:'+hd_stream
            hq_url = 'rtmp://bcastiw.livebox.cz:80/iprima_token_'+geo_zone[0]+'?auth='+keydata[0]+'/mp4:'+hq_stream[0]
            lq_url = 'rtmp://bcastiw.livebox.cz:80/iprima_token_'+geo_zone[0]+'?auth='+keydata[0]+'/mp4:'+lq_stream[0]
        else:
            if re.match('Prima', hq_stream[0], re.U): 
                hd_url = 'rtmp://bcastnw.livebox.cz:80/iprima_token?auth='+keydata[0]+'/mp4:'+hd_stream
                hq_url = 'rtmp://bcastnw.livebox.cz:80/iprima_token?auth='+keydata[0]+'/mp4:'+hq_stream[0]
                lq_url = 'rtmp://bcastnw.livebox.cz:80/iprima_token?auth='+keydata[0]+'/mp4:'+lq_stream[0]
            else:
                hd_url = 'rtmp://bcastnw.livebox.cz:80/iprima_token?auth='+keydata[0]+'/'+hd_stream
                hq_url = 'rtmp://bcastnw.livebox.cz:80/iprima_token?auth='+keydata[0]+'/'+hq_stream[0]
                lq_url = 'rtmp://bcastnw.livebox.cz:80/iprima_token?auth='+keydata[0]+'/'+lq_stream[0] 

        addLink('HD '+name,hd_url,nahled,name)
        addLink('HQ '+name,hq_url,nahled,name)            
        addLink('LQ '+name,lq_url,nahled,name)


def gen_random_decimal(d):
        return decimal.Decimal('%d' % (random.randint(0, d)))


#print 'skuska'        
#LIST_VOYO('http://voyo.markiza.sk/relacie/776-adela-show')
#VIDEOLINK_VOYO('http://voyo.markiza.sk/produkt/relacie/792-adela-show-25-10-2011-22-30','haluz')
#sk= createRTMPGwAddress('rtmpe://vod.markiza.sk/voyosk playpath=mp4:2011/10/25/2011-10-25_ADELA-1.mp4 app=voyosk flashVer=WIN11,1,102,62 conn=O:1 conn=NN:0:2279338.000000 conn=NS:1: conn=NN:2:1847.000000 conn=NS:3:null conn=O:0 pageUrl=http://voyo.markiza.sk/produkt/relacie/792-adela-show-25-10-2011-22-30 swfUrl=http://voyo.markiza.sk/static/shared/app/flowplayer/13-flowplayer.cluster-3.2.1-01-004.swf swfVfy=true')
#http://voyo.markiza.sk/produkt/relacie/792-adela-show-25-10-2011-22-30
#_root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
#print _root_dir
