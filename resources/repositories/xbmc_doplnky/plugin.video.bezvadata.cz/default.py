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

import re,os,urllib,urllib2
from Plugins.Extensions.archivCZSK.archivczsk import ArchivCZSK

__scriptid__   = 'plugin.video.bezvadata.cz'
__scriptname__ = 'bezvadata.cz'
__addon__ = ArchivCZSK.get_xbmc_addon(__scriptid__)
__language__ = __addon__.getLocalizedString


import util

import xbmcutil
import bezvadata
import xbmcprovider



# filter function
def can_show(ext_filter,item):
	extension = os.path.splitext(item['title'])[1]
	if extension in ext_filter:
		return False
	elif '18+' in item.keys() and not __addon__.getSetting('18+content') != 'true':
		return False
	return True

def create_filter():
	ext_filter = __addon__.getSetting('ext-filter').split(',')
	return ['.'+f.strip() for f in ext_filter]

def filter(item):
	return can_show(create_filter(),item)

provider = bezvadata.BezvadataContentProvider(username='',password='',filter=filter,tmp_dir='/tmp/')

settings = {
    'vip':'0'
}
xbmcprovider.XBMCLoginOptionalDelayedContentProvider(provider,settings,__addon__,session).run(params)
