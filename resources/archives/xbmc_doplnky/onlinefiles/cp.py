# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2012 Libor Zoubek
# *
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
import re,urllib,urllib2,cookielib,random,sys,os,traceback
from base64 import b64decode

import Plugins.Extensions.archivCZSK.resources.libraries.simplejson as json
from Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools import util, resolver
from Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools.contentprovider.provider import ContentProvider

class BezvadataContentProvider(ContentProvider):

    def __init__(self,username=None,password=None,filter=None):
        ContentProvider.__init__(self,'bezvadata.cz','http://bezvadata.cz/',username,password,filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['search','resolve']

    def search(self,keyword):
        return self.list('vyhledavani/?s='+urllib.quote(keyword))

        
    def list(self,url):
        page = util.request(self._url(url))
        ad = re.search('<a href=\"(?P<url>/vyhledavani/souhlas-zavadny-obsah[^\"]+)',page,re.IGNORECASE|re.DOTALL)
        if ad:
            page = util.request(self._url(ad.group('url')))
        data = util.substr(page,'<div class=\"content','<div class=\"stats')
        pattern = '<section class=\"img[^<]+<a href=\"(?P<url>[^\"]+)(.+?)<img src=\"(?P<img>[^\"]+)\" alt=\"(?P<name>[^\"]+)(.+?)<b>velikost:</b>(?P<size>[^<]+)'
        result = []
        for m in re.finditer(pattern,data,re.IGNORECASE | re.DOTALL ):
            item = self.video_item()
            item['title'] = m.group('name')
            item['size'] = m.group('size').strip()
            item['img'] = m.group('img')
            item['url'] = m.group('url')
            # mark 18+ content
            if ad:
                item['18+'] = True
            if self.filter:
                if self.filter(item):
                    result.append(item)
            else:
                result.append(item)

        # page navigation
        data = util.substr(page,'<div class=\"pagination','</div>')
        m = re.search('<li class=\"previous[^<]+<a href=\"(?P<url>[^\"]+)',data,re.DOTALL|re.IGNORECASE)
        if m:
            item = self.dir_item()
            item['type'] = 'prev'
            item['url'] = m.group('url')
            result.append(item)
        n = re.search('<li class=\"next[^<]+<a href=\"(?P<url>[^\"]+)',data,re.DOTALL|re.IGNORECASE)
        if n:
            item = self.dir_item()
            item['type'] = 'next'
            item['url'] = n.group('url')
            result.append(item)
        return result


    def resolve(self,item,captcha_cb=None):
        item = item.copy()
        url = self._url(item['url'])
        data = util.request(url)
        request = urllib.urlencode({'stahnoutSoubor':'Stáhnout'})
        req = urllib2.Request(url+'?do=stahnoutForm-submit',request)
        req.add_header('User-Agent',util.UA)    
        resp = urllib2.urlopen(req)
        item['url'] = resp.geturl()
        item['surl'] = url
        return item
    
    
    
    
class HellspyContentProvider(ContentProvider):

    def __init__(self, username=None, password=None, filter=None):
        ContentProvider.__init__(self, 'hellspy.cz', 'http://hellspy.cz/', username, password, filter)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar()))
        urllib2.install_opener(opener)

    def capabilities(self):
        return ['login', 'search', 'resolve', 'categories']

    def search(self, keyword):
        return self.list('search/?q=' + urllib.quote(keyword))

    def login(self):
        if self.username and self.password and len(self.username) > 0 and len(self.password) > 0:
            page = util.request(self.base_url + '?do=loginBox-loginpopup')
            data = util.substr(page, '<td class=\"popup-lef', '</form')
            m = re.search('<form action=\"(?P<url>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
            if m:
                login_url = self._url(m.group('url')).replace('&amp;', '&')
                data = util.post(login_url, {'username':self.username, 'password':self.password, 'pernament_login':'on', 'login':'1', 'redir_url':'http://www.hellspy.cz/?do=loginBox-login'})
                if data.find('href="/?do=loginBox-logout') > 0:
                    return True
        return False

    def list_favourites(self, url):
        url = self._url(url)
        page = util.request(url)
        data = util.substr(page, '<div class=\"file-list file-list-vertical', '<div id=\"layout-push')
        result = []
        for m in re.finditer('<div class=\"file-entry.+?<div class="preview.+?<div class=\"data.+?</div>', data, re.IGNORECASE | re.DOTALL):
            entry = m.group(0)
            item = self.video_item()
            murl = re.search('<[hH]3><a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)', entry)
            item['url'] = murl.group('url')
            item['title'] = murl.group('name')
            mimg = re.search('<img src=\"(?P<img>[^\"]+)', entry)
            if mimg:    
                item['img'] = mimg.group('img')
            msize = re.search('<span class=\"file-size[^>]+>(?P<size>[^<]+)', entry)
            if msize:
                item['size'] = msize.group('size').strip()
            mtime = re.search('<span class=\"duration[^>]+>(?P<time>[^<]+)', entry)
            if mtime:
                item['length'] = mtime.group('time').strip()
            self._filter(result, item)
        return result

    def list(self, url, filter=None):
        if url.find('ucet/favourites') >= 0 and self.login():
            return self.list_favourites(url)
        url = self._url(url)
        page = util.request(url)
        data = util.substr(page, '<div class=\"file-list file-list-horizontal', '<div id=\"push')
        result = []
        for m in re.finditer('<div class=\"file-entry.+?<div class="preview.+?<div class=\"data.+?</div>', data, re.IGNORECASE | re.DOTALL):
            entry = m.group(0)
            item = self.video_item()
            murl = re.search('<[hH]3><a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)', entry)
            item['url'] = murl.group('url')
            item['title'] = murl.group('name')
            mimg = re.search('<img src=\"(?P<img>[^\"]+)', entry)
            if mimg:    
                item['img'] = mimg.group('img')
            msize = re.search('<span class=\"file-size[^>]+>(?P<size>[^<]+)', entry)
            if msize:
                item['size'] = msize.group('size').strip()
            mtime = re.search('<span class=\"duration[^>]+>(?P<time>[^<]+)', entry)
            if mtime:
                item['length'] = mtime.group('time').strip()
            self._filter(result, item)
        # page navigation
        data = util.substr(page, '<div class=\"paginator', '</div')
        mprev = re.search('<li class=\"prev[^<]+<a href=\"(?P<url>[^\"]+)', data)
        if mprev:
            item = self.dir_item()
            item['type'] = 'prev'
            item['url'] = mprev.group('url')
            result.append(item)
        mnext = re.search('<li class=\"next[^<]+<a href=\"(?P<url>[^\"]+)', data)
        if mnext:
            item = self.dir_item()
            item['type'] = 'next'
            item['url'] = mnext.group('url')
            result.append(item)
        return result

    def categories(self):
        result = []

        item = self.dir_item()
        item['type'] = 'nejstahovanejsi-soubory'
        item['url'] = 'nejstahovanejsi-soubory'
        result.append(item)

        item = self.dir_item()
        item['type'] = 'currentdownloads'
        item['url'] = 'currentdownloads'
        result.append(item)
        
        item = self.dir_item()
        item['type'] = 'favourites'
        item['url'] = 'ucet/favourites'
        result.append(item)
        return result

    def resolve(self, item, captcha_cb=None):
        item = item.copy()
        url = self._url(item['url'])
        if not self.login():
            util.error('[hellspy] login failed, unable to resolve')
        if url.find('?') > 0:
            url += '&download=1'
        else:
            url += '?download=1'
        data = util.request(url)
        if data.find('Soubor nenalezen') > 0:
            util.error('[hellspy] - page with movie was not found on server')
            return
        m = re.search('launchFullDownload\(\'(?P<url>[^\']+)', data)
        if m:    
            item['url'] = m.group('url')
            item['surl'] = url
            return item

    def to_downloads(self, url):
        if not self.login():
            util.error('[hellspy] login failed, unable to add to downloads')
        util.info('adding to downloads')
        try:
            util.request(self._url(url + '&do=downloadControl-favourite'))
        except urllib2.HTTPError:
            traceback.print_exc()
            util.error('[hellspy] failed to add to downloads')
            return
        util.info('added, DONE')
        
        
        
class UloztoContentProvider(ContentProvider):

    def __init__(self, username=None, password=None, filter=None):
        ContentProvider.__init__(self, 'ulozto.cz', 'http://www.ulozto.cz/', username, password, filter)
        self.cp = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
        self.rh = UloztoHTTPRedirectHandler()
        self.rh.throw = False
        self.rh.location = None
        self.init_urllib()

    def capabilities(self):
        return ['login', 'search', 'resolve']

    def init_urllib(self):    
        opener = urllib2.build_opener(self.cp, self.rh)
        urllib2.install_opener(opener)

    def search(self, keyword):
        return self.list(self.base_url + 'hledej/?media=video&q=' + urllib.quote(keyword))

    def login(self):
        if self.username and self.password and len(self.username) > 0 and len(self.password) > 0:
            self.rh.throw = False
            page = util.request(self.base_url + '?do=web-login')
            data = util.substr(page, '<li class=\"menu-username', '</li')
            m = re.search('key=(?P<key>[^\"]+)\"', data, re.IGNORECASE | re.DOTALL)
            if m:
                login_url = self.base_url + 'login?key=' + m.group('key') + '&do=loginForm-submit'
                data = util.post(login_url, {'username':self.username, 'password':self.password, 'remember':'on', 'login':'Prihlasit'})
                if data.find('href="/?do=web-logout') > 0:
                    return True
        return False


    def list(self, url):
        url = self._url(url)
        page = util.request(url, headers={'X-Requested-With':'XMLHttpRequest', 'Referer':url, 'Cookie':'uloz-to-id=1561277170;'})

        script = util.substr(page, '</ul>', '</script>')
        keymap = None
        key = None
        k = re.search('{([^\;]+)"', script, re.IGNORECASE | re.DOTALL)
        if k:
            keymap = json.loads("{" + k.group(1) + "\"}")
        j = re.search('kapp\(kn\[\"([^\"]+)"', script, re.IGNORECASE | re.DOTALL)
        if j:
            key = j.group(1)
        if not (j and k):
            return []
        burl = b64decode('I2h0dHA6Ly9jcnlwdG8tenNlcnYucmhjbG91ZC5jb20vYXBpL3YyL2RlY3J5cHQvP2tleT0lcyZ2YWx1ZT0lcwo=')
        data = util.substr(page, '<ul class=\"chessFiles', '</ul>') 
        result = []
        for m in re.finditer('<li>.+?<div data-icon=\"(?P<key>[^\"]+)[^<]+<img(.+?)src=\"(?P<logo>[^\"]+)(.+?)alt=\"(?P<name>[^\"]+)(.+?)<span class=\"fileSize[^>]+>(?P<size>[^<]+)<span class=\"fileTime[^>]+>(?P<time>[^<]+)', data, re.IGNORECASE | re.DOTALL):
            value = keymap[m.group('key')]
            iurl = burl % (keymap[key], value)
            item = self.video_item()
            item['title'] = m.group('name')
            item['size'] = m.group('size').strip()
            item['length'] = m.group('time')
            item['url'] = iurl
            item['img'] = m.group('logo')
            if self.filter:
                if self.filter(item):
                    result.append(item)
            else:
                result.append(item)
        # page navigation
        data = util.substr(page, '<div class=\"paginator', '</div')
        mprev = re.search('<a href=\"(?P<url>[^\"]+)\" class=\"prev', data)
        if mprev:
            item = self.dir_item()
            item['type'] = 'prev'
            item['url'] = mprev.group('url')
            result.append(item)
        mnext = re.search('<a href=\"(?P<url>[^\"]+)\" class="next', data)
        if mnext:
            item = self.dir_item()
            item['type'] = 'next'
            item['url'] = mnext.group('url')
            result.append(item)
        return result


    def resolve(self, item, captcha_cb=None):
        item = item.copy()
        url = item['url']
        if url.startswith('#'):
            ret = json.loads(util.request(url[1:]))
            if not ret['result'] == 'null':
                url = b64decode(ret['result'])
                url = self._url(url)
        if url.startswith('#'):
            util.error('[uloz.to] - url was not correctly decoded')
            return
        self.init_urllib()
        logged_in = self.login()
        if logged_in:
            page = util.request(url)
        
        else:
            try:
                request = urllib2.Request(url)
                response = urllib2.urlopen(request)
                page = response.read()
                response.close()
            except urllib2.HTTPError, e:
                    traceback.print_exc()
                    return
        if page.find('Stránka nenalezena!') > 0:
            util.error('[uloz.to] - page with movie was not found on server')
            return
        
        if logged_in:
            data = util.substr(page, '<h3>Neomezené stahování</h3>', '</div')
            m = re.search('<a(.+?)href=\"(?P<url>[^\"]+)\"', data, re.IGNORECASE | re.DOTALL)
            if m:
                try:
                    self.rh.throw = True
                    resp = urllib2.urlopen(urllib2.Request(self._url(m.group('url'))))
                except RedirectionException:
                    # this is what we need, our redirect handler raises this
                    pass
                except urllib2.HTTPError:
                    # this is not OK, something went wrong
                    traceback.print_exc()
                    util.error('[uloz.to] cannot resolve stream url, server did not redirected us')
                    util.info('[uloz.to] POST url:' + post_url)
                    return
                stream = self.rh.location
                item['url'] = self._fix_stream_url(stream)
                item['surl'] = url
                return item

        else:
            data = util.substr(page, '<h3>Omezené stahování</h3>', '<script')
            m = re.search('<form(.+?)action=\"(?P<action>[^\"]+)\"', data, re.IGNORECASE | re.DOTALL)
            if m:
                self.rh.throw = True
                stream_url = self._get_file_url_anonymous(page, self._url(m.group('action')), response.headers, captcha_cb)
                if stream_url:
                    item['url'] = stream_url
                    item['surl'] = url
                    return item
    
    def _get_file_url_anonymous(self, page, post_url, headers, captcha_cb):
        
        captcha_id = re.search('<input type=\"hidden\" id=\"captcha_id\".+?value=\"([^\"]+)"', page, re.IGNORECASE | re.DOTALL).group(1)
        # ask callback to provide captcha code
        code = captcha_cb({'id':captcha_id, 'img': 'http://img.uloz.to/captcha/%s.png' % captcha_id})
        if not code:
            return
        
        ts = re.search('<input type=\"hidden\" name=\"ts\".+?value=\"([^\"]+)"', page, re.IGNORECASE | re.DOTALL)
        cid = re.search('<input type=\"hidden\" name=\"cid\".+?value=\"([^\"]+)"', page, re.IGNORECASE | re.DOTALL)
        sign = re.search('<input type=\"hidden\" name=\"sign\".+?value=\"([^\"]+)"', page, re.IGNORECASE | re.DOTALL)
        key = re.search('<input type=\"hidden\" id=\"captcha_key\".+?value=\"([^\"]+)"', page, re.IGNORECASE | re.DOTALL)
        if not (sign and ts and cid and key):
            util.error('[uloz.to] - unable to parse required params from page, plugin needs fix')
            return
        request = urllib.urlencode({'captcha_key':key.group(1), 'ts':ts.group(1), 'cid':cid.group(1), 'sign':sign.group(1), 'captcha_id':captcha_id, 'captcha_value':code, 'freeDownload':'Stáhnout'})
        req = urllib2.Request(post_url, request)
        req.add_header('User-Agent', util.UA)
        req.add_header('Referer', post_url)
        sessid = []
        for cookie in re.finditer('(ULOSESSID=[^\;]+)', headers.get('Set-Cookie'), re.IGNORECASE | re.DOTALL):
            sessid.append(cookie.group(1))
        req.add_header('Cookie', 'uloz-to-id=' + cid.group(1) + '; ' + sessid[-1])
        try:
            resp = urllib2.urlopen(req)
            page = resp.read()
            print 'sending requrest'    
            headers = resp.headers
        except RedirectionException:
            # this is what we need, our redirect handler raises this
            pass
        except urllib2.HTTPError:
            # this is not OK, something went wrong
            traceback.print_exc()
            util.error('[uloz.to] cannot resolve stream url, server did not redirected us')
            util.info('[uloz.to] POST url:' + post_url)
            return
        stream = self.rh.location
        print 'got something'
        # we did not get 302 but 200
        if stream == None:
            util.debug('Captcha was invalid, retrying..')
            return self._get_file_url_anonymous(page, post_url, headers, captcha_cb)
        if stream.find('full=y') > -1:
            util.error('[uloz.to] - out of free download slots, use payed account or try later')
            return
        if stream.find('neexistujici') > -1:
            util.error('[uloz.to] - movie was not found on server')
            return
        return self._fix_stream_url(stream)

    def _fix_stream_url(self, stream):    
        index = stream.rfind('/')
        if index > 0:
            fn = stream[index:]
            index2 = fn.find('?')
            if index2 > 0:
                fn = urllib.quote(fn[:index2]) + fn[index2:]
            else:
                fn = urllib.quote(fn)
            stream = stream[:index] + fn
        return stream



def _regex(url):
    return re.search('(#(.*)|ulozto\.cz|uloz\.to)', url, re.IGNORECASE | re.DOTALL)

class UloztoHTTPRedirectHandler(urllib2.HTTPRedirectHandler):

    def http_error_302(self, req, fp, code, msg, headers):
        if self.throw:
            self.location = headers.getheader('Location')
            raise RedirectionException()
        else:
            return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)

class RedirectionException(Exception):
    pass
