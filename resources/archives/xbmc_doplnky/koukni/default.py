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

import Plugins.Extensions.archivCZSK.resources.tools.doplnky as doplnky
from Plugins.Extensions.archivCZSK.resources.archives.xbmc_doplnky.tools import util, doplnkyprovider, search

import cp as koukni

def getContent(session, params):
    import Plugins.Extensions.archivCZSK.plugin as archivczsk
    __scriptid__ = 'koukni'
    __addon__ = archivczsk.archive_dict[__scriptid__]
    __language__ = __addon__.get_localized_string
    __settings__ = __addon__.get_settings
    settings = {}
    doplnkyprovider.DoplnkyContentProvider(koukni.KoukniContentProvider(), settings, __addon__, session).run(params)



