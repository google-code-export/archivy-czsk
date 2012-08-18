# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2011 Libor Zoubek
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
import re, urllib, urllib2, random, sys, os, traceback, cookielib
try:
    import Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools.util as util
    from Plugins.Extensions.archivCZSK.resources.tools.doplnky import set_command, add_dir, add_video
    import Plugins.Extensions.archivCZSK.resources.archives.simplejson as json
except ImportError:
    import resources.archives.xbmc_doplnky.tools.util as util
    import resources.archives.simplejson as json
    from resources.tools.doplnky import set_command, add_dir, add_video
try:
    from Plugins.Extensions.archivCZSK import _
    from Components.config import config
except ImportError:
    pass
from base64 import b64decode

addonName = "movielibrary"

def descape(url):
    return re.sub('&amp;', '&', url)

def supports(url):
        return not _regex(url) == None

def full_url(url):
        if url.startswith('http'):
                return url
        return 'http://www.ulozto.cz/' + url.lstrip('/')

def _get_file_url(page, post_url, redirecthandler, headers, opener):
    try:
        code = config.plugins.archivCZSK.archives.movielibrary.captcha_text.getValue()
    except:
        code = ''
    if len(code) < 1:
        # empty code in settings? set something to query user for beeter code
        code = 'abcd'
    
    ts = re.search('<input type=\"hidden\" name=\"ts\".+?value=\"([^\"]+)"', page, re.IGNORECASE | re.DOTALL)
    cid = re.search('<input type=\"hidden\" name=\"cid\".+?value=\"([^\"]+)"', page, re.IGNORECASE | re.DOTALL)
    sign = re.search('<input type=\"hidden\" name=\"sign\".+?value=\"([^\"]+)"', page, re.IGNORECASE | re.DOTALL)
    key = re.search('<input type=\"hidden\" id=\"captcha_key\".+?value=\"([^\"]+)"', page, re.IGNORECASE | re.DOTALL)
    if not (sign and ts and cid and key):
        util.error('[uloz.to] - unable to parse required params from page, plugin needs fix')
        return
    request = urllib.urlencode({'captcha_key':key.group(1), 'ts':ts.group(1), 'cid':cid.group(1), 'sign':sign.group(1), 'captcha_id':config.plugins.archivCZSK.archives.movielibrary.captcha_id.getValue(), 'captcha_value':code, 'freeDownload':'Stáhnout'})
    req = urllib2.Request(post_url, request)
    req.add_header('User-Agent', util.UA)
    req.add_header('Referer', post_url)
    sessid = []
    for cookie in re.finditer('(ULOSESSID=[^\;]+)', headers.get('Set-Cookie'), re.IGNORECASE | re.DOTALL):
        sessid.append(cookie.group(1))
    req.add_header('Cookie', 'uloz-to-id=' + cid.group(1) + '; ' + sessid[-1])
    print 'Request:' + str(req.headers)
    try:
        redirecthandler.throw = True
        resp = opener.open(req)
        page = resp.read()
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
    stream = redirecthandler.location
    # we did not get 302 but 200
    if stream == None:
        captcha_id = re.search('<input type=\"hidden\" id=\"captcha_id\".+?value=\"([^\"]+)"', page, re.IGNORECASE | re.DOTALL).group(1)
        try:
            config.plugins.archivCZSK.archives.movielibrary.captcha_id.setValue(captcha_id)
            config.plugins.archivCZSK.archives.movielibrary.captcha_id.save()
        except:
            print '[ulozto]', captcha_id
        param = [_get_file_url, page, post_url, redirecthandler, headers, opener]
        return param

    if stream.find('full=y') > -1:
        util.error('[uloz.to] - out of free download slots, use payed account or try later')
        return -1
    if stream.find('neexistujici') > -1:
        util.error('[uloz.to] - movie was not found on server')
        return -2
    #return stream only when captcha was accepted and there
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


# returns the steam url
# returns the steam url
def url(url):
    if supports(url):
        if url.startswith('#'):
            ret = json.loads(util.request(url[1:]))
            if not ret['result'] == 'null':
                url = b64decode(ret['result'])
                url = full_url(url)
        if url.startswith('#'):
            util.error('[uloz.to] - url was not correctly decoded')
            return -2
        util.init_urllib()
        cj = cookielib.LWPCookieJar()
        hcp = urllib2.HTTPCookieProcessor(cj)
        redirecthandler = UloztoHTTPRedirectHandler()
        redirecthandler.throw = False
        redirecthandler.location = None
        opener = urllib2.build_opener(hcp, redirecthandler)
        #urllib2.install_opener(opener)
        try:
            request = urllib2.Request(url)
            response = opener.open(request)
            page = response.read()
            response.close()
        except urllib2.HTTPError, e:
                traceback.print_exc()
                return -2
        if page.find('Stránka nenalezena!') > 0:
            util.error('[uloz.to] - page with movie was not found on server')
            return -2
        data = util.substr(page, '<h3>Omezené stahování</h3>', '<script')
        m = re.search('<form(.+?)action=\"(?P<action>[^\"]+)\"', data, re.IGNORECASE | re.DOTALL)
        if not m == None:
            return _get_file_url(page, full_url(m.group('action')), redirecthandler, response.headers, opener)

def _regex(url):
        return re.search('(#(.*)|ulozto\.cz|uloz\.to)', url, re.IGNORECASE | re.DOTALL)
    
class UloztoHTTPRedirectHandler(urllib2.HTTPRedirectHandler):

    def http_error_302(self, req, fp, code, msg, headers):
        if self.throw:
            self.location = headers.getheader('Location')
            raise RedirectionException()
        else:
            return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
            # this will lead to exception when 302 is recieved
            # exactly what we want - not to open url that's being redirected to
    #http_error_301 = http_error_303 = http_error_307 = http_error_302
    
    
class RedirectionException(Exception):
        pass

def search_list():
        add_dir(_('New search'), {'search-ulozto':''}, util.icon('search.png'))
        for what in util.get_searches(addonName, 'search_history_ulozto'):
                add_dir(what, {'search-ulozto':what}, None, {}, menuItems={_('Remove'):{'search-ulozto-remove':what}})
       # xbmcplugin.endOfDirectory(int(sys.argv[1]))

def search_remove(search):
        util.remove_search(addonName, 'search_history_ulozto', search)
        set_command('refreshnow')
       # xbmc.executebuiltin('Container.Refresh')

def search(params):
        what = params['search-ulozto']
        if what == '':
            set_command('search')
        if not what == '':
                maximum = 20
                try:
                        maximum = int(config.plugins.archivCZSK.keep_searches.value)
                except:
                        util.error('Unable to parse convert addon setting to number')
                        pass
                if not 'search-no-history' in params.keys():
                        util.add_search(addonName, 'search_history_ulozto', what, maximum)
                        #GItem_lst[1]='refreshafter'
                return list_page('http://www.ulozto.cz/hledej/?media=video&q=' + urllib.quote(what))

def list_page(url):
        util.init_urllib()
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
                return
        burl = b64decode('I2h0dHA6Ly9jcnlwdG8tenNlcnYucmhjbG91ZC5jb20vYXBpL3YyL2RlY3J5cHQvP2tleT0lcyZ2YWx1ZT0lcwo=')
        data = util.substr(page, '<ul class=\"chessFiles', '</ul>') 
        for m in re.finditer('<li>.+?<div data-icon=\"(?P<key>[^\"]+)[^<]+<img(.+?)src=\"(?P<logo>[^\"]+)(.+?)alt=\"(?P<name>[^\"]+)(.+?)<span class=\"fileSize[^>]+>(?P<size>[^<]+)<span class=\"fileTime[^>]+>(?P<time>[^<]+)', data, re.IGNORECASE | re.DOTALL):
                value = keymap[m.group('key')]
                iurl = burl % (keymap[key], value)
                add_video('%s (%s | %s)' % (m.group('name'), m.group('size').strip(), m.group('time')),
                        {'play':iurl},
                        full_url(m.group('logo')),
                        infoLabels={'Title':m.group('name')},
                       # menuItems={xbmc.getLocalizedString(33003):{'name':m.group('name'),'download':iurl}}
                        )
        # page naviagation
        data = util.substr(page, '<div class=\"paginator', '</div')
        mprev = re.search('<a href=\"(?P<url>[^\"]+)\" class=\"prev', data)
        if mprev:
                add_dir(_("Previous"), {'list-ulozto':full_url(descape(mprev.group('url')))}, util.icon('prev.png'))
        mnext = re.search('<a href=\"(?P<url>[^\"]+)\" class="next', data)
        if mnext:
                add_dir(_("Next"), {'list-ulozto':full_url(descape(mnext.group('url')))}, util.icon('next.png'))
