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

import sys,os,re,traceback,util,xbmcutil,resolver,time
from Plugins.Extensions.archivCZSK.engine import client
from Plugins.Extensions.archivCZSK.archivczsk import ArchivCZSK

class XBMContentProvider(object):
	'''
	ContentProvider class provides an internet content. It should NOT have any xbmc-related imports
	and must be testable without XBMC runtime. This is a basic/dummy implementation.
	'''	
	
	def __init__(self,provider,settings,addon,session):
		'''
		XBMContentProvider constructor
		Args:
			name (str): name of provider
		'''
		self.provider = provider
		self.settings = settings
		self.addon = addon
		self.addon_id = addon.get_info('id')
		self.session = session

	def check_setting_keys(self,keys):
		for key in keys:
			if not key in self.settings.keys():
				raise Exception('Invalid settings passed - ['+key+'] setting is required');


	def params(self):
		return {'cp':self.provider.name}

	def run(self, params):
		if params == {} or params == self.params():
			return self.root()
		elif 'list' in params.keys():
			self.list(self.provider.list(params['list']))
		elif 'play' in params.keys():
			return self.play(params)
		elif 'search-list' in params.keys():
			return self.search_list()
		elif 'search' in params.keys():
			return self.do_search(params['search'])
		elif 'search-remove' in params.keys():
			return self.search_remove(params['search-remove'])
		elif self.run_custom:
			return self.run_custom(params)

	def search_list(self):
		params = self.params()
		params.update({'search':''})
		menuItems = self.params()
		xbmcutil.add_search_item(xbmcutil.__lang__(30004),params,xbmcutil.icon('search.png'))
		for what in xbmcutil.get_searches(self.addon,self.provider.name):
			params={}
			menuItems={}
			params['search'] = what
			menuItems['search-remove'] = what
			xbmcutil.add_dir(what,params,menuItems={'remove':menuItems})

	def search_remove(self,what):
		xbmcutil.remove_search(self.addon,self.provider.name,what)
		client.refresh_screen()

	def do_search(self,what):
		if what == '':
			what = client.getTextInput(self.session,xbmcutil.__lang__(30003))
		if not what == '':
			maximum = 20
			try:
				maximum = int(self.settings['keep-searches'])
			except:
				util.error('Unable to parse convert addon setting to number')
				pass
			xbmcutil.add_search(self.addon,self.provider.name,what,maximum)
			self.search(what)

	def root(self):
		if 'search' in self.provider.capabilities():
			params = self.params()
			params.update({'search-list':''})
			xbmcutil.add_search_folder(xbmcutil.__lang__(30003),params,xbmcutil.icon('search.png'))
		self.list(self.provider.categories())
	
	def play(self,params):
		streams = self.resolve(params['play'])
		if streams is not None:
			if type(streams) == type([]):
				for stream in streams:
					xbmcutil.add_play('%s - %s[%s]' % (params['title'], stream['title'], stream['quality']), stream['url'], subs=stream['subs'])
			else:
				#ulozto,bezvadata..
				xbmcutil.add_play("%s" % params['title'], streams['url'], subs=streams['subs'])

	def resolve(self,url):
		item = self.provider.video_item()
		item.update({'url':url})
		return self.provider.resolve(item)

	def search(self,keyword):
		self.list(self.provider.search(keyword))
	
	def list(self,items):
		params = self.params()
		for item in items:
			if item['type'] == 'dir':
				self.render_dir(item)
			elif item['type'] == 'next':
				params.update({'list':item['url']})
				xbmcutil.add_dir(xbmcutil.__lang__(30007),params,xbmcutil.icon('next.png'))
			elif item['type'] == 'prev':
				params.update({'list':item['url']})
				xbmcutil.add_dir(xbmcutil.__lang__(30008),params,xbmcutil.icon('prev.png'))
			elif item['type'] == 'new':
				params.update({'list':item['url']})
				xbmcutil.add_dir(xbmcutil.__lang__(30012),params,xbmcutil.icon('new.png'))
			elif item['type'] == 'top':
				params.update({'list':item['url']})
				xbmcutil.add_dir(xbmcutil.__lang__(30013),params,xbmcutil.icon('top.png'))
			elif item['type'] == 'video':
				self.render_video(item)
			else:
				self.render_default(item)

	def render_default(self,item):
		raise Exception("Unable to render item "+item)

	def render_dir(self,item):
		params = self.params()
		params.update({'list':item['url']})
		title = item['title']
		img = None
		if 'img' in item.keys():
			img = item['img']
		if title.find('$') == 0:
			title = self.addon.get_localized_string(int(title[1:]))
		xbmcutil.add_dir(title,params,img,infoLabels=self._extract_infolabels(item))

	def _extract_infolabels(self,item):
		infoLabels = {}
		if 'plot' in item.keys():
			infoLabels['plot'] = item['plot']
		return infoLabels

	def render_video(self,item):
		params = self.params()
		params.update({'play':item['url'], 'title':item['title']})
		downparams = self.params()
		downparams.update({'name':item['title'],'down':item['url']})
		def_item = self.provider.video_item()
		if item['size'] == def_item['size']:
			item['size'] = ''
		else:
			item['size'] = ' (%s)' % item['size']
		title = '%s%s' % (item['title'],item['size'])
		menuItems = {}
		if 'menu' in item.keys():
			menuItems.update(item['menu'])
		xbmcutil.add_video(title,
			params,
			item['img'],
			infoLabels={'Title':item['title']},
			menuItems=menuItems
		)	
	
	def categories(self):
		self.list(self.provider.categories(keyword))

class XBMCMultiResolverContentProvider(XBMContentProvider):

	def __init__(self,provider,settings,addon,session):
		XBMContentProvider.__init__(self,provider,settings,addon,session)
		self.check_setting_keys(['quality'])

	def resolve(self,url):
		def select_cb(resolved):
			resolved = resolver.filter_by_quality(resolved,self.settings['quality'] or '0')
			if len(resolved) == 1:
				return resolved[0]
			return resolved

		item = self.provider.video_item()
		item.update({'url':url})
		return self.provider.resolve(item,select_cb=select_cb)
	

class XBMCLoginRequiredContentProvider(XBMContentProvider):

	def root(self):
		if not self.provider.login():
			client.showInfo(xbmcutil.__lang__(30011))
		else:
			return XBMContentProvider.root(self)
		
class XBMCLoginOptionalContentProvider(XBMContentProvider):
	
	def __init__(self,provider,settings,addon,session):
		XBMContentProvider.__init__(self,provider,settings,addon,session)
		self.check_setting_keys(['vip'])

	def ask_for_captcha(self,params):
		print 'captcha',params['img']
		return client.getCaptcha(self.session, params['img'])

	def ask_for_account_type(self):
		if len(self.provider.username) == 0:
			return False
		if self.settings['vip'] == '0':
			ret = client.getYesNoInput(self.session,xbmcutil.__lang__(30010))
			return ret
		return self.settings['vip'] == '1'

	def resolve(self,url):
		item = self.provider.video_item()
		item.update({'url':url})
		if not self.ask_for_account_type():
			# set user/pass to null - user does not want to use VIP at this time
			self.provider.username = None
			self.provider.password = None
		else:
			if not self.provider.login():
				client.showInfo(xbmcutil.__lang__(30011))
				return
		return self.provider.resolve(item,captcha_cb=self.ask_for_captcha)
	
	

class XBMCLoginOptionalDelayedContentProvider(XBMCLoginOptionalContentProvider):

    def wait_cb(self,wait):
        left = wait
        msg = xbmcutil.__lang__(30014).encode('utf-8') 
        while left > 0:
            #xbmc.executebuiltin("XBMC.Notification(%s,%s,1000,%s)" %(self.provider.name,msg % str(left),''))
            left-=1
            time.sleep(1)

    def resolve(self,url):
        item = self.provider.video_item()
        item.update({'url':url})
        if not self.ask_for_account_type():
            # set user/pass to null - user does not want to use VIP at this time
            self.provider.username = None
            self.provider.password = None
        else:
            if not self.provider.login():
                client.showInfo(xbmcutil.__lang__(30011))
                return
        return self.provider.resolve(item,captcha_cb=self.ask_for_captcha,wait_cb=self.wait_cb)