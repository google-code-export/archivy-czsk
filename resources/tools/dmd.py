'''
Created on 18.6.2012

@author: marko
'''
from items import PFolder, PVideo, PSearch, PNotSupportedVideo
#try:
import Plugins.Extensions.archivCZSK.resources.tools.util2 as util
import Plugins.Extensions.archivCZSK.resources.exceptions.archiveException as exceptions
from Plugins.Extensions.archivCZSK import _
from task import Task
import contentprovider

GItem_lst = contentprovider.Archive.gui_item_list

def set_command(name, **kwargs):
    GItem_lst[1] = name
    for arg in kwargs:
        GItem_lst[2][arg] = kwargs[arg]
 
nexticon = None #_pluginPath + 'icon/nexticon.png'
fanart = None
search = [_('Search'), _('New search')]  

def addDir(name, url, mode, image, page=None, kanal=None, **kwargs):
    #controling if task shouldnt be _aborted(ie. we pushed exit button when loading)
    print 'adddir'
    task = Task.getInstance()
    if task and task._aborted:
        raise exceptions.ArchiveThreadException
    else:
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
    #controling if task shouldnt be _aborted(ie. we pushed exit button when loading)
    task = Task.getInstance()
    if task and task._aborted:
        raise exceptions.ArchiveThreadException
    else:
        if util.isSupportedVideo(url):
            it = PVideo()
        else:
            it = PNotSupportedVideo()
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
