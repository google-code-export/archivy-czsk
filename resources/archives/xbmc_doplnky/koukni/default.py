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

import re, os, urllib, urllib2, shutil, traceback
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
try:
    from Plugins.Extensions.archivCZSK import _
except ImportError:
    print 'Unit test'

__scriptid__ = 'plugin.video.koukni.cz'
__scriptname__ = 'koukni.cz'
BASE_URL = 'http://koukni.cz/'

def getContent(url, **kwargs):
    search=kwargs['input'] 
    p = {} 
    if url is not None:
        p = url
    if p == {}:
        root()
    if 'list' in p.keys():
        list(p['list'])
   # if 'download' in p.keys():
        #download(p['download'],p['name'])
    if 'play' in p.keys():
        play(p['play'])
    if 'tag-remove' in p.keys():
        tag_remove(p['tag-remove'])
    if 'tag-add' in p.keys():
        tag_add(search)
    if 'search' in p.keys() and search:
        p['search'] = search	
        
    search2.main(addonName, 'search_history', p, _search_cb)             

def _search_cb(what):
        return list(BASE_URL + 'hledej?hledej=' + urllib.quote(what))

#def _search(what):
 #       return list(BASE_URL+'hledej?hledej='+urllib.quote(what))    

def furl(url):
        if url.startswith('http'):
                return url
        url = url.lstrip('./')
        return BASE_URL + url

def root():
        search2.item()
        add_dir(_('New videos'), {'list':furl('new')}, util.icon('new.png'), menuItems={_('Add tag'):{'tag-add':''}})
        add_dir(_('Popular videos'), {'list':furl('nej')}, util.icon('top.png'), menuItems={_('Add tag'):{'tag-add':''}})
        #util.add_local_dir(__language__(30037),__addon__.getSetting('downloads'),util.icon('download.png'),menuItems={__addon__.getLocalizedString(30005):{'tag-add':''}})
        tags = util.get_searches(addonName, 'tags')
        if tags == []:
                # add default/known tags
                tags = ['clipz', 'simpsons', 'serialz', 'znovy', 'zoufalky', 'vypravej', 'topgear', 'COWCOOSH']
                for t in tags:
                    util.add_search(addonName, 'tags', t, 9999)
        tags.sort()
        for tag in tags:
                add_dir(tag, {'list':furl(tag)}, menuItems={
                _('Add tag'):{'tag-add':''},
                _('Remove tag'):{'tag-remove':tag}
                })

def tag_remove(tag):
        util.remove_search(addonName, 'tags', tag)
        set_command("refreshnow")

def tag_add(what):
        if what is None:
            set_command("addtag")
        else:
            util.add_search(addonName,'tags', what, 9999)
            set_command("refreshnow")

def list(url):
        return list_page(util.request(url), url)

def list_page(data, url):
        for m in re.finditer('<div class=\"row\"(.+?)<a href=\"(?P<url>[^\"]+)(.+?)src=\"(?P<logo>[^\"]+)(.+?)<h1>(?P<name>[^<]+)', data, re.IGNORECASE | re.DOTALL):
                iurl = furl(m.group('url'))
                add_video(m.group('name'),
                        {'play':iurl},
                        furl(m.group('logo')), 
                        #menuItems={_('Download'):{'name':m.group('name'),'download':iurl}}
                        )
        prev = re.search('<a href=\"(?P<url>[^\"]+)\">[^<]*<img src=\"\./style/images/predchozi.png', data, re.IGNORECASE | re.DOTALL)
        navurl = url
        index = url.find('?')
        if index > 0:
                navurl = url[:index]
        if prev:
                print prev.group('url')
                add_dir(_('Back'), {'list':navurl + prev.group('url')}, util.icon('prev.png'))
        next = re.search('<a href=\"(?P<url>[^\"]+)\">[^<]*<img src=\"\./style/images/dalsi.png', data, re.IGNORECASE | re.DOTALL)
        if next:
                print next.group('url')
                add_dir(_('Next'), {'list':navurl + next.group('url')}, util.icon('next.png'))

def play(url):
        stream, subs = resolve(url)
        add_play('VIDEO', stream, subs)

def getSubtitles(data):
        data = util.substr(data, '$f(\"a.player\",', '</script>')
        m = re.search('captionUrl\: \'(?P<url>[^\']+)', data, re.IGNORECASE | re.DOTALL)
        if m:
                subs = furl(m.group('url'))
                return subs
        return None

def resolve(url):
        util.init_urllib()
        data = util.request(url)
        m = re.search('id=\"player\" href=\"(?P<url>[^\"]+)', data, re.IGNORECASE | re.DOTALL)
        if m:
                req = urllib2.Request(furl(m.group('url')))
                req.add_header('User-Agent', util.UA)
                response = urllib2.urlopen(req)
                response.close()
                return (response.geturl(), getSubtitles(data))


