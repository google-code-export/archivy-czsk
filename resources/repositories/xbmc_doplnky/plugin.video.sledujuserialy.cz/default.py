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
import os
import util, xbmcprovider
from Plugins.Extensions.archivCZSK.archivczsk import ArchivCZSK
__scriptid__ = 'plugin.video.sledujuserialy.cz'
__scriptname__ = 'sledujuserialy.cz'
__addon__ = ArchivCZSK.get_xbmc_addon(__scriptid__)
__language__ = __addon__.getLocalizedString

sys.path.append(os.path.join (__addon__.getAddonInfo('path'), 'resources', 'lib'))
import sledujuserialy
settings = {'quality':__addon__.getSetting('quality')}

xbmcprovider.XBMCMultiResolverContentProvider(sledujuserialy.SledujuserialyContentProvider(), settings, __addon__, session).run(params)
