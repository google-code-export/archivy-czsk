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
# 			modified by mx3L */

import sys, os, re, traceback, util, resolver

from Plugins.Extensions.archivCZSK import _
from Plugins.Extensions.archivCZSK.resources.exceptions.archiveException import CustomInfoError
from Plugins.Extensions.archivCZSK.resources.tools import  client


class DoplnkyContentProvider(object):
	'''
	ContentProvider class provides an internet content. It should NOT have any xbmc-related imports
	and must be testable without XBMC runtime. This is a basic/dummy implementation.
	'''	
	
	def __init__(self, provider, settings, addon, session):
		'''
		XBMContentProvider constructor
		Args:
			name (str): name of provider
		'''
		self.provider = provider
		self.settings = settings
		self.session = session
		self.addon = addon
		self.addon_id = addon.id

	def check_setting_keys(self, keys):
		for key in keys:
			if not key in self.settings.keys():
				raise Exception('Invalid settings passed - [' + key + '] setting is required');


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
		util.add_dir(_("New Search"), params, util.icon('search.png'))
		for what in util.get_searches(self.addon, self.provider.name):
			params['search'] = what
			menuItems['search-remove'] = what
			util.add_dir(what, params, menuItems={u'remove':menuItems})

	def search_remove(self, what):
		util.remove_search(self.addon, self.provider.name, what)
		client.set_command("refreshnow")

	def do_search(self, what):
		if what == '':
			what = client.getTextInput(self.session, _("Set your search expression"))
		if not what == '':
			maximum = 20
			try:
				maximum = int(self.settings['keep-searches'])
			except:
				util.error('Unable to parse convert addon setting to number')
				pass
			util.add_search(self.addon, self.provider.name, what, maximum)
			self.search(what)
			
			
	def root(self):
		if 'search' in self.provider.capabilities():
			params = self.params()
			params.update({'search-list':''})
			util.add_dir(_("Search"), params, util.icon('search.png'))
		self.list(self.provider.categories())
	
	def play(self, params):
		streams = self.resolve(params['play'])
		if streams is not None:
			if type(streams) == type([]):
				for stream in streams:
					util.add_play('%s - %s[%s]' % (params['title'], stream['title'], stream['quality']), stream['url'], subs=stream['subs'])
			else:
				#ulozto,bezvadata..
				util.add_play("%s" % params['title'], streams['url'], subs=streams['subs'])
				

	def resolve(self, url):
		item = self.provider.video_item()
		item.update({'url':url})
		return self.provider.resolve(item)

	def search(self, keyword):
		self.list(self.provider.search(keyword))
	
	def list(self, items):
		params = self.params()
		for item in items:
			if item['type'] == 'dir':
				self.render_dir(item)
			elif item['type'] == 'next':
				params.update({'list':item['url']})
				util.add_dir(_("Next"), params, util.icon('next.png'))
			elif item['type'] == 'prev':
				params.update({'list':item['url']})
				util.add_dir(_("Previous"), params, util.icon('prev.png'))
			elif item['type'] == 'new':
				params.update({'list':item['url']})
				util.add_dir(_("New"), params, util.icon('new.png'))
			elif item['type'] == 'top':
				params.update({'list':item['url']})
				util.add_dir(_("Top"), params, util.icon('top.png'))
			elif item['type'] == 'video':
				self.render_video(item)
			else:
				self.render_default(item)

	def render_default(self, item):
		raise Exception("Unable to render item " + item)

	def render_dir(self, item):
		params = self.params()
		params.update({'list':item['url']})
		title = item['title']
		img = None
		if 'img' in item.keys():
			img = item['img']
		if title.find('$') == 0:
			title = self.addon.getLocalizedString(int(title[1:]))
		util.add_dir(title, params, img, infoLabels=self._extract_infolabels(item))

	def _extract_infolabels(self, item):
		infoLabels = {}
		if 'plot' in item.keys():
			infoLabels['plot'] = item['plot']
		return infoLabels

	def render_video(self, item):
		params = self.params()
		params.update({'play':item['url'], 'title':item['title']})
		downparams = self.params()
		downparams.update({'name':item['title'], 'down':item['url']})
		def_item = self.provider.video_item()
		if item['size'] == def_item['size']:
			item['size'] = ''
		else:
			item['size'] = ' (%s)' % item['size']
		title = '%s%s' % (item['title'], item['size'])
		menuItems = {} #{xbmc.getLocalizedString(33003):downparams}
		if 'menu' in item.keys():
			menuItems.update(item['menu'])
		util.add_dir(title,
			params,
			item['img'],
			infoLabels={'Title':item['title']},
			menuItems=menuItems
		)	
	
	def categories(self):
		self.list(self.provider.categories(keyword))

class DoplnkyMultiResolverContentProvider(DoplnkyContentProvider):

	def __init__(self, provider, settings, addon, session):
		DoplnkyContentProvider.__init__(self, provider, settings, addon, session)
		self.check_setting_keys(['quality'])

	def resolve(self, url):
		def select_cb(resolved):
			resolved = resolver.filter_by_quality(resolved, self.settings['quality'] or '0')
			return resolved

		item = self.provider.video_item()
		item.update({'url':url})
		return self.provider.resolve(item, select_cb=select_cb)

class DoplnkyLoginRequiredContentProvider(DoplnkyContentProvider):

	def root(self):
		if not self.provider.login():
			raise CustomInfoError(_("Cannot login, incorrect login data"))
		else:
			return DoplnkyContentProvider.root(self)
		
class DoplnkyLoginOptionalContentProvider(DoplnkyContentProvider):
	

	def __init__(self, provider, settings, addon, session):
		DoplnkyContentProvider.__init__(self, provider, settings, addon, session)
		self.check_setting_keys(['vip'])

	def ask_for_captcha(self, params):
		return client.getCaptcha(self.session, params['img'])

	def ask_for_account_type(self):
		if len(self.provider.username) == 0:
			return False
		if self.settings['vip'] == '0':
			ret = client.getYesNoInput(self.session, text=_("Do you want to use vip account"))
			return ret
		return self.settings['vip'] == '1'

	def resolve(self, url):
		item = self.provider.video_item()
		item.update({'url':url})
		if not self.ask_for_account_type():
			# set user/pass to null - user does not want to use VIP at this time
			self.provider.username = None
			self.provider.password = None
		else:
			if not self.provider.login():
				CustomInfoError(_("Cannot login, incorrect login data"))
				return
		return self.provider.resolve(item, captcha_cb=self.ask_for_captcha)
