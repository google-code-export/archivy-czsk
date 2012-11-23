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

import sys,os,util,re,traceback

class ContentProvider(object):
    '''
    ContentProvider class provides an internet content. It should NOT have any xbmc-related imports
    and must be testable without XBMC runtime. This is a basic/dummy implementation.
    '''	

    def __init__(self,name,base_url,username,password,filter,tmp_dir='.'):
        '''
        ContentProvider constructor
        Args:
            name (str): name of provider
            base_url (str): base url of site being accessed
            username (str): login username
            password (str): login password
            filter (func{item}): function to filter results returned by search or list methods
            tmp_dir (str): temporary dir where provider can store/cache files
        '''
        self.name=name
        self.username=username
        self.password=password
        if not base_url[-1] == '/':
            base_url = base_url+'/'
        self.base_url=base_url
        self.filter = filter
        self.tmp_dir = tmp_dir

    def capabilities(self):
        '''
        This way class defines which capabilities it provides
        '''
        return ['login','search','resolve','categories']

    def video_item(self):
        '''
        returns empty video item - contains all required fields
        '''
        return {'type':'video','title':'','rating':0,'year':0,'size':'0MB','url':'','img':'','length':'','quality':'???','subs':'','surl':''}

    def dir_item(self):
        '''
            reutrns empty directory item
        '''
        return {'type':'dir','title':'','size':'0','url':''}

    def login(self):
        '''
        A login method returns True on successfull login, False otherwise
        '''
        return False

    def search(self,keyword):
        '''
        Search for a keyword on a site
        Args:
                    keyword (str)

        returns:
            array of video or directory items
        '''
        return []

    def list(self,url):
        '''
        Lists content on given url
        Args:
                    url (str): either relative or absolute provider URL

        Returns:
            array of video or directory items

        '''
        return []
    def categories(self):
        '''
        Lists categories on provided site

        Returns:
            array of video or directory items
        '''
        return []

    def resolve(self,item,captcha_cb=None,select_cb=None,wait_cb=None):
        '''
        Resolves given video item  to a downloable/playable file/stream URL

        Args:
            url (str): relative or absolute URL to be resolved
            captcha_cb(func{obj}): callback function when user input is required (captcha, one-time passwords etc).
            function implementation must be Provider-specific
        Returns:
            None - if ``url`` was not resolved. Video item with 'url' key pointing to resolved target
        '''
        return None

    def _url(self,url):
        '''
        Transforms relative to absolute url based on ``base_url`` class property
        '''
        if url.startswith('http'):
            return url
        return self.base_url+url.lstrip('./')

    def _filter(self,result,item):
        '''
        Applies filter, if filter passes `item` is appended to `result`

        Args:
            result (array) : target array
            item (obj) : item that is being applied filter on
        '''
        if self.filter:
            if self.filter(item):
                result.append(item)
        else:
            result.append(item)
    def info(self,msg):
        util.info('[%s] %s' % (self.name,msg)) 
    def error(self,msg):
        util.error('[%s] %s' % (self.name,msg)) 
