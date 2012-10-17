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
import os, re, sys
import util
from Plugins.Extensions.archivCZSK.resources.tools.doplnky import set_command, add_dir
from Plugins.Extensions.archivCZSK.gui import common


def _list(addon, history, key, value):
        params = {}
        menuItems = {}
        if key:
                params[key] = value
                menuItems[key] = value
        params['search'] = ''
        add_dir(_("New search"), params, util.icon('search.png'))
        for what in util.get_searches(addon, history):
                params = {}
                params['search'] = what
                menuItems['search-remove'] = what
                add_dir(what.encode('utf-8'), params, menuItems={_('Remove'):menuItems})

def _remove(addon, history, search):
        util.remove_search(addon, history, search)
        set_command('refreshnow')

def _search(session, addon, history, what, update_history, callback):
        if what == '':
            what = common.getTextInput(session, _("Set your search expression"))

        if not what == '':
                maximum = 20
                try:
                    maximum = int(addon.get_setting('keep-searches'))
                except:
                        util.error('Unable to parse convert addon setting to number')
                        pass
                if update_history:
                        util.add_search(addon, history, what, maximum)
                callback(what)

def item(items={}, label=_("Search")):
        items['search-list'] = ''
        add_dir(label, items, util.icon('search.png'))

def main(addon, history, p, callback, key=None, value=None):
        if (key == None) or (key in p and p[key] == value):
                if 'search-list' in p.keys():
                        _list(addon, history, key, value)
                if 'search' in p.keys():
                        update_history = True
                        if 'search-no-history' in p.keys():
                                update_history = False
                        _search(addon, history, p['search'], update_history, callback)
                if 'search-remove' in p.keys():
                        _remove(addon, history, p['search-remove'])
