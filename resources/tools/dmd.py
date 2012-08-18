'''
Created on 18.6.2012

@author: marko
'''
from util import PFolder, PVideo, PSearch
#try:
import Plugins.Extensions.archivCZSK.resources.tools.util as util
from Plugins.Extensions.archivCZSK import _
#except ImportError:
 #   import resources.tools.util.getGlobalList as ggL
GItem_lst = util.getGlobalList()

def set_command(name, **kwargs):
    GItem_lst[1]['text'] = name
    for command in kwargs:
        GItem_lst[1][command] = kwargs[command]
 
nexticon = None #_pluginPath + 'icon/nexticon.png'
fanart = None
search = [_('Search'), _('New search')]  


def addDir(name, url, mode, image, page=None, kanal=None, **kwargs):
        if name in search:
            it = PSearch()
        else:
            it = PFolder()
        if isinstance(name, str):
            it.name = unicode(name, 'utf-8', 'ignore')
        else:
            it.name = name
        it.url = url
        it.url_text = url
        it.mode_text = str(mode)
        it.mode = mode
        it.image = image
        it.info = {}
        it.page = page
        it.kanal = kanal
        infoLabels = {}
        if 'infoLabels' in kwargs:
            infoLabels = kwargs['infoLabels']
        infolabel_uni = {}
        for key, value in infoLabels.iteritems():
            if isinstance(value, str):    
                infolabel_uni[key] = unicode(value, 'utf-8', 'ignore')
            elif isinstance(value, unicode):
                infolabel_uni[key] = value
            else:
                infolabel_uni[key] = unicode(str(value), 'utf-8', 'ignore')
        if not 'Title' in infolabel_uni:
            infolabel_uni["Title"] = it.name
        it.info = infolabel_uni
        GItem_lst[0].append(it)
          
def addLink(name, url, image, name2):
        it = PVideo()
        if isinstance(name, str):
            it.name = unicode(name, 'utf-8', 'ignore')
        else:
            it.name = name
        it.url = url
        it.mode = None
        it.url_text = url
        it.mode_text = ''
        it.image = image
        it.info = {}
        it.sub = None
        it.live = False
        GItem_lst[0].append(it)
