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

import re, os, urllib, urllib2, md5, sys
try:
    import Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools.search as search2
    import Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools.util as util
    import Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools.resolver as resolver
    from Plugins.Extensions.archivCZSK.resources.tools.doplnky import add_dir, add_video, add_play, set_command
    from Plugins.Extensions.archivCZSK.resources.exceptions import archiveException
except ImportError:
    import resources.archives.xbmc_doplnky.tools.util as util
    import resources.archives.xbmc_doplnky.tools.search as search2
    import resources.archives.xbmc_doplnky.tools.resolver as resolver
    from resources.tools.doplnky import add_dir, add_video, add_play
    from resources.exceptions import archiveException
import ulozto
try:
    from Plugins.Extensions.archivCZSK import _
    from Components.config import config
except ImportError:
    print 'unit test'

__scriptid__ = 'plugin.video.movie-library.cz'
__scriptname__ = 'movie-library.cz'
    
ulozto.__scriptid__ = __scriptid__

BASE_URL = 'http://movie-library.cz/'

def getContent(url, **kwargs): 
    search = kwargs['input']
    p = {} 
    if url is not None:
        p = url
    if p == {}:
        categories()
    if 'cat' in p.keys():
        list_page(p['cat'])
    if 'countries' in p.keys():
        countries(p['countries'])
    if 'item' in p.keys():
        list_item(p['item'])
    if 'play' in p.keys():
        play(p['play'])
    if 'popular' in p.keys():
        list_page(furl('popularni'))
    #if 'download' in p.keys():
        #download(p['download'],p['name'])
    if 'search' in p.keys() and search:
        p['search'] = search
    if 'search-ulozto-list' in p.keys():
        ulozto.search_list()
    if 'search-ulozto' in p.keys():
        if search:
            p['search-ulozto'] = search
        ulozto.search(p)
    if 'list-ulozto' in p.keys():
        ulozto.list_page(p['list-ulozto'])
    if 'search-ulozto-remove' in p.keys():
        ulozto.search_remove(p['search-ulozto-remove'])    
    search2.main(addonName, 'search_history', p, _search_cb)

def icon(icon):
        icon_file = os.path.join(__file__, 'resources', 'icons', icon)
        if not os.path.isfile(icon_file):
                return 'DefaultFolder.png'
        return icon_file

def _search_cb(what):
                req = urllib2.Request(BASE_URL + 'search.php?q=' + what.replace(' ', '+'))
                response = urllib2.urlopen(req)
                data = response.read()
                response.close()
                if response.geturl().find('search.php') > -1:
                        if data.find('tagy:</h2>') > 0:
                                parse_tag_page(data)
                        return parse_page(data, response.geturl())
                else:
                        #single movie was found
                        return parse_item(data)
def furl(url):
        if url.startswith('http'):
                return url
        url = url.lstrip('./')
        return BASE_URL + url

def categories():
        search2.item()
        add_dir(_('Search on ulozto.cz'), {'search-ulozto-list':''}, icon('ulozto.png'))
        #util.add_local_dir(__language__(30037),__addon__.getSetting('downloads'),util.icon('download.png'))
        add_dir(_('Popular'), {'popular':''}, icon('top.png'))
        data = util.substr(util.request(BASE_URL), 'div id=\"menu\"', '</td')
        pattern = '<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)'
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
                if m.group('url').find('staty') > 0:
                        add_dir(m.group('name'), {'countries':furl(m.group('url'))})
                else:
                        add_dir(m.group('name'), {'cat':furl(m.group('url'))})

def countries(url):
        data = util.substr(util.request(url), 'Filmy podle států</h2>', '<div id=\"footertext\">')
        pattern = '<a(.+?)href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)'
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
                add_dir(m.group('name'), {'cat':furl(m.group('url'))})

def list_page(url):
        order = orderby()
        if url.find('?') < 0:
                order = '?' + order
        url += order
        page = util.request(url)
        return parse_page(page, url)

def parse_tag_page(page):
        data = util.substr(page, '<h2>Nalezené tagy:</h2>', '</ul>')
        for m in re.finditer('<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)', data, re.IGNORECASE | re.DOTALL):
                add_dir('[tag] ' + m.group('name'), {'cat':furl(m.group('url'))})

def parse_page(page, url):
        try:
            lang_filter = config.plugins.archivCZSK.archives.movielibrary.lang_filter.value.split(',')
            lang_filter_inc = config.plugins.archivCZSK.archives.movielibrary.lang_filter_include.value
        except:
            lang_filter = ['cz', 'sk'].split(',')
            lang_filter_inc = True
            
        # set as empty list when split returns nothing
        if len(lang_filter) == 1 and lang_filter[0] == '':
                lang_filter = []
        data = util.substr(page, '<iframe id=\"listade', '<div class=\"pagelist')
        pattern = '<tr><td[^>]+><a href=\"(?P<url>[^\"]+)[^>]+><img src=\"(?P<logo>[^\"]+)(.+?)<a class=\"movietitle\"[^>]+>(?P<name>[^<]+)</a>(?P<data>.+?)/td></tr>'
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
                info = m.group('data')
                year = 0
                plot = ''
                genre = ''
                lang = ''
                rating = 0
                lang_list = []
                for q in re.finditer('<img src=\"(.+?)flags/(?P<lang>[^\.]+)\.png\"', info):
                        lang += ' [%s]' % q.group('lang')
                        lang_list.append(q.group('lang'))
                if not lang_filter == []:
                        filtered = True
                        if len(lang_list) > 0:
                                for l in lang_list:
                                        if l in lang_filter:
                                                filtered = False
                        elif lang_filter_inc:
                                filtered = False
                        if filtered:
                                continue

                s = re.search('<div style=\"color[^<]+</div>(?P<genre>.*?)<br[^>]*>(?P<year>.*?)<', info)
                if s:
                        genre = s.group('genre')
                        try:
                                year = int(re.sub(',.*', '', s.group('year')))
                        except:
                                pass
                r = re.search('<div class=\"ratingval\"(.+?)width:(?P<rating>\d+)px', info)
                if r:
                        try:
                                rating = float(r.group('rating')) / 5
                        except:
                                pass
                t = re.search('<div style=\"margin-top:5px\">(?P<plot>[^<]+)', info)
                if t:
                        plot = t.group('plot')
                add_dir(m.group('name') + lang, {'item':furl(m.group('url'))}, m.group('logo'), infoLabels={'Plot':plot, 'Genre':genre, 'Rating':rating, 'Year':year})
        data = util.substr(page, '<div class=\"pagelist\"', '<div id=\"footertext\">')
        for m in re.finditer('<a style=\"float:(right|left)(.+?)href=\"(.+?)(?P<page>page=\d+)[^>]+>(?P<name>[^<]+)', data, re.IGNORECASE | re.DOTALL):
                logo = 'DefaultFolder.png'
                if m.group('name').find('Další') >= 0:
                        logo = util.icon('next.png')
                if m.group('name').find('Předchozí') >= 0:
                        logo = util.icon('prev.png')
                add_dir(m.group('name'), {'cat':url + '&' + m.group('page')}, logo)

def orderby():
        return '&sort=%s' % config.plugins.archivCZSK.archives.movielibrary.order.value

def list_item(url):
        return parse_item(util.request(url))

def parse_item(page):
        #search for series items
        data = util.substr(page, 'Download:</h3><table>', '</table>')
        pattern = '<a href=\"(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)</a></div></td><td[^>]+>(?P<size>[^<]+)'
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
                iurl = furl(m.group('url'))
                add_video(
                        '%s (%s)' % (m.group('name'), m.group('size')),
                        {'play':iurl},
                        infoLabels={'Title':m.group('name')},
                        #menuItems={_('Download'):{'name':m.group('name'),'download':iurl}}
                )

        # search for movie items
        data = util.substr(page, 'Download:</h3>', '<div id=\"login-password-box')
        pattern = '<a class=\"under\" href="(?P<url>[^\"]+)[^>]+>(?P<name>[^<]+)</a>(.+?)<abbr[^>]*>(?P<size>[^<]+)'
        for m in re.finditer(pattern, data, re.IGNORECASE | re.DOTALL):
                iurl = furl(m.group('url'))
                add_video(
                        '%s (%s)' % (m.group('name'), m.group('size')),
                        {'play':iurl},
                        infoLabels={'Title':m.group('name')},
                        #menuItems={_('Download'):{'name':m.group('name'),'download':iurl}}
                )

def play(url):
        stream = resolve(url)
        if type(stream) == type([]):
            set_command('captcha', captchaCB=stream)
        else:
            add_play('Video', stream)
            

def resolve(url):
        if ulozto.supports(url):
                uloztourl = url
        else:
                data = util.request(url)
                # find uloz.to url
                m = re.search('window\.location=\'(?P<url>[^\']+)', data, re.IGNORECASE | re.DOTALL)
                if m:
                        uloztourl = m.group('url')
                else:
                        # daily maximum of requested movies reached (150)
                        util.error('daily maximum (150) requests for movie was reached, try it tomorrow')
                        raise CustomInfoError(_("Daily maximum (150) requests for movie was reached, try it tomorrow"))
                        return
        stream = ulozto.url(uloztourl)
        print 'stream', stream
        if stream == -1:
               #"Video není dostupné, zkontrolujte, zda funguje přehrávání na webu."
               # Video is not available, check out if its working on the webpage of archive
                raise CustomInfoError(_("Video is not available, check out if its working on the web page of archive"))
                return
        if stream == -2:
                # Byl překročen limit volných slotů na stahování zkuste to později nebo použijte placený účet
                raise CustomInfoError(_("Limit for downloading slots was exceeded, please try again later"))
                return
        return stream
