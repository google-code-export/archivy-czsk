'''
Created on 3.7.2012

@author: marko
'''

'''
Created on 18.6.2012

@author: marko
'''
from util import PFolder,PVideo,PSearch
try:
    from Plugins.Extensions.archivCZSK import _
    import Plugins.Extensions.archivCZSK.resources.tools.util as util
except ImportError:
    import resources.tools.util as util
    
def _(string):
    return string
    
GItem_lst=[[],{}]
search='New search'  

def set_command(name,**kwargs):
    GItem_lst[1]['text']=name
    for command in kwargs:
        GItem_lst[1][command]=kwargs[command]

def add_dir(name, url_dict, image=None, infoLabels={}, menuItems={}):
        if name == search:
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
            else:
                infolabel_uni[key] = unicode(str(value), 'utf-8', 'ignore')
        menuItems_uni = {}
        for key, value in menuItems.iteritems():
            if isinstance(key, str):    
                menuItems_uni[unicode(key, 'utf-8', 'ignore')] = value
            else:
                menuItems_uni[unicode(str(key), 'utf-8', 'ignore')] = value    

        it.info = infolabel_uni         
        it.image = image
        it.menu = menuItems_uni
        it.folder = True
        GItem_lst[0].append(it)

               
def add_video(name, url_dict, image=None, infoLabels={}, menuItems={}):
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
            if isinstance(key, str):    
                infolabel_uni[key] = unicode(value, 'utf-8', 'ignore')
            else:
                infolabel_uni[key] = unicode(str(value), 'utf-8', 'ignore')  
        menuItems_uni = {}
        for key, value in menuItems.iteritems():
            if isinstance(key, str):    
                menuItems_uni[unicode(key, 'utf-8', 'ignore')] = value
            else:
                menuItems_uni[unicode(str(key), 'utf-8', 'ignore')] = value    
        it.info = infolabel_uni      
        it.image = image
        it.menu = menuItems_uni
        it.folder = True
        GItem_lst[0].append(it)     
        
def add_play(name, url, subs=None, image=None, infoLabels={}):
        it = PVideo()
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
        it.info = infolabel_uni
        it.url_text = url
        it.mode_text = ''
        it.image = image 
        it.subs = subs
        it.live = False    
        it.folder = False
        GItem_lst[0].append(it)    

def printGItem_lst():
    for it in GItem_lst[0]:
        print it.name,it.url
    del GItem_lst[0][:]

