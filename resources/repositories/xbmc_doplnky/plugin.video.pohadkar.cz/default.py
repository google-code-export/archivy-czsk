# -*- coding: UTF-8 -*-
#/*
# *      Copyright (C) 2013 Libor Zoubek
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
import os
import util, xbmcprovider, xbmcutil
from provider import ResolveException
from Plugins.Extensions.archivCZSK.archivczsk import ArchivCZSK
__scriptid__ = 'plugin.video.pohadkar.cz'
__scriptname__ = 'Pohádkář.cz'
__addon__ = ArchivCZSK.get_xbmc_addon(__scriptid__)
__language__ = __addon__.getLocalizedString

sys.path.append(os.path.join (__addon__.getAddonInfo('path'), 'resources', 'lib'))
import pohadkar
settings = {'downloads':__addon__.getSetting('downloads'), 'quality':__addon__.getSetting('quality')}

class PohadkarContentProvider(xbmcprovider.XBMCMultiResolverContentProvider):

    def play(self, params):
        stream = self.resolve(params['play'])
        print type(stream)
        if type(stream) == type([]):
            # resolved to mutliple files, we'll feed playlist and play the first one
            playlist = []
            i = 0
            for video in stream:
                i += 1
                if 'headers' in video.keys():
                    playlist.append(xbmcutil.create_play_it(params['title'] + " [" + str(i) + "]", "", video['quality'], video['url'], subs=video['subs'], filename=params['title'], headers=video['headers']))
                else:
                    playlist.append(xbmcutil.create_play_it(params['title'] + " [" + str(i) + "]", "", video['quality'], video['url'], subs=video['subs'], filename=params['title']))
            xbmcutil.add_playlist(params['title'], playlist)
        elif stream:
            if 'headers' in stream.keys():
                xbmcutil.add_play(params['title'], "", stream['quality'], stream['url'], subs=stream['subs'], filename=params['title'], headers=stream['headers'])
            else:
                xbmcutil.add_play(params['title'], "", stream['quality'], stream['url'], subs=stream['subs'], filename=params['title'])

    def resolve(self, url):
        def select_cb(resolved):
            # for this plugin we do not care about quality at all
            if len(resolved) == 1:
                return resolved[0]
            else:
                return resolved

        item = self.provider.video_item()
        item.update({'url':url})
        try:
            return self.provider.resolve(item, select_cb=select_cb)
        except ResolveException, e:
            self._handle_exc(e)

PohadkarContentProvider(pohadkar.PohadkarContentProvider(tmp_dir=__addon__.getAddonInfo('profile')), settings, __addon__, session).run(params)
