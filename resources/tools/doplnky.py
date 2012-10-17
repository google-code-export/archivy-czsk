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

search = [_('Search'), _('New search')] 


def set_command(name, **kwargs):
    GItem_lst[1] = name
    for arg in kwargs:
        GItem_lst[2][arg] = kwargs[arg]


def add_dir(name, url_dict, image=None, infoLabels={}, menuItems={}):
    #controlling if task shouldnt be _aborted(ie. we pushed exit button when loading)
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
        it.url = url_dict
        it.mode = None
        it.url = url_dict
        for key, value in url_dict.iteritems():
            it.url_text = value
            it.mode_text = key
        infolabel_uni = {}
        for key, value in infoLabels.iteritems():
            if isinstance(value, str):    
                infolabel_uni[key] = unicode(value, 'utf-8', 'ignore')
            elif isinstance(value, unicode):
                infolabel_uni[key] = value
            else:
                infolabel_uni[key] = unicode(str(value), 'utf-8', 'ignore')
        menuItems_uni = {}
        for key, value in menuItems.iteritems():
            if isinstance(key, str):    
                menuItems_uni[unicode(key, 'utf-8', 'ignore')] = value
            elif isinstance(key, unicode):
                menuItems_uni[key] = value
            else:
                menuItems_uni[unicode(str(key), 'utf-8', 'ignore')] = value
        
        params={}
        for key in url_dict.keys():
            value=url_dict[key]
            if not isinstance(value,unicode):
                unicode(value, 'utf-8', errors='ignore')
            params[key]=value        
            
        it.params=params
        it.info = infolabel_uni         
        it.image = image
        it.menu = menuItems_uni
        it.folder = True
        GItem_lst[0].append(it)


def add_video(name, url_dict, image=None, infoLabels={}, menuItems={}):
    #controling if task shouldnt be _aborted(ie. we pushed exit button when loading)
    task = Task.getInstance()
    if task and task._aborted:
        raise exceptions.ArchiveThreadException
    else:
        if name == _('Search'):
            it = PSearch()
        else:
            it = PFolder()
        if isinstance(name, str):
            it.name = unicode(name, 'utf-8', 'ignore')
        else:
            it.name = name
        it.url = url_dict
        it.mode = None
        for key, value in url_dict.iteritems():
            it.url_text = value
            it.mode_text = key
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
        menuItems_uni = {}
        for key, value in menuItems.iteritems():
            if isinstance(key, str):    
                menuItems_uni[unicode(key, 'utf-8', 'ignore')] = value
            elif isinstance(key, unicode):
                menuItems_uni[key] = value
            else:
                menuItems_uni[unicode(str(key), 'utf-8', 'ignore')] = value
        params={}
        for key in url_dict.keys():
            value=url_dict[key]
            if not isinstance(value,unicode):
                unicode(value, 'utf-8', errors='ignore')
            params[key]=value  
            
                  
        
        it.params = params    
        it.info = infolabel_uni      
        it.image = image
        it.menu = menuItems_uni
        it.folder = True
        GItem_lst[0].append(it)     


def add_play(name, url, subs=None, image=None, infoLabels={}, filename=None):
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
        infolabel_uni = {}
        for key, value in infoLabels.iteritems():
            if isinstance(value, str):
                infolabel_uni[key] = unicode(value, 'utf-8', 'ignore')
            else:
                infolabel_uni[key] = unicode(str(value), 'utf-8', 'ignore')
        if not 'Title' in infolabel_uni:
            infolabel_uni["Title"] = it.name
        it.params = url
        it.info = infolabel_uni
        it.url_text = url
        it.mode_text = ''
        it.image = image
        if filename is not None:
            it.filename = unicode(filename, 'utf-8') 
        it.subs = subs
        it.live = False    
        it.folder = False
        GItem_lst[0].append(it)    
