
#### module for archives creators

from task import callFromThread
import twisted.internet.defer as defer
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.MessageBox import MessageBox
from Components.config import config
from Plugins.Extensions.archivCZSK.gui.captcha import Captcha
import Plugins.Extensions.archivCZSK.resources.exceptions.archiveException as exceptions
import Plugins.Extensions.archivCZSK.resources.libraries.simplejson as json
import util2 as util
import os
from Plugins.Extensions.archivCZSK import _
from items import PFolder, PVideo, PNotSupportedVideo, PSearch, PContextMenuItem
from task import Task
import contentprovider

GItem_lst = contentprovider.Archive.gui_item_list

def debug(info):
    if config.plugins.archivCZSK.debug.value:
        print '[archivCZSK]', info

@callFromThread
def getTextInput(session, text):
    def getTextInputCB(word):
        print "textinput: %s" % word
        d.callback(word)
    d = defer.Deferred()
    session.openWithCallback(getTextInputCB, VirtualKeyBoard, title=text)
    return d

@callFromThread
def getCaptcha(session, image):
    def getCaptchaCB(word):
        d.callback(word)
    d = defer.Deferred()
    Captcha(session, image, getCaptchaCB)
    return d

@callFromThread        
def getYesNoInput(session, text):
    def getYesNoInputCB(callback=None):
        if callback:
            d.callback(True)
        else:
            d.callback(False)
    d = defer.Deferred()
    session.openWithCallback(getYesNoInputCB, MessageBox, text=text, type=MessageBox.TYPE_YESNO)
    return d



def set_command(name, **kwargs):
    """set command for active content screen
    first argument is always name of the command, next arguments are arguments for command
    
    possible commands for content screen are: refreshafter - refreshes content screen when again loaded
                                              refreshnow- refreshes content screen immediately"""
    GItem_lst[1] = name
    for arg in kwargs:
        GItem_lst[2][arg] = kwargs[arg]


search = [_('Search'), _('New search')] 

def add_dir(name, params={}, image=None, infoLabels={}, menuItems={}):
    """adds directory item to content screen
    
        @param name : name of the directory
        @param params: dictationary of parameters for next resolving
        @param image: image to show in directories info
        @param infoLabels: dictationary of informations{'title':title,'plot':plot,'rating':rating,''}"
        @param menuItems: dictationary with menu items 
    
    """
    #controlling if task shouldnt be _aborted(ie. we pushed exit button when loading)
    task = Task.getInstance()
    if task and task._aborted:
        raise exceptions.ArchiveThreadException
    else:
        name = util.decode_html(name)
        if name in search:
            it = PSearch()
        else:
            it = PFolder()
        if isinstance(name, str):
            it.name = unicode(name, 'utf-8', 'ignore')
        else:
            it.name = name
        it.params = params
        
        infolabel_uni = {}
        
        for key, value in infoLabels.iteritems():
            if isinstance(value, str):
                    
                infolabel_uni[key] = unicode(value, 'utf-8', 'ignore')
            elif isinstance(value, unicode):
                infolabel_uni[key] = value
            else:
                infolabel_uni[key] = unicode(str(value), 'utf-8', 'ignore')
        
        for key, value in menuItems.iteritems():
            if isinstance(key, str):    
                item_name = unicode(key, 'utf-8', 'ignore')
            elif isinstance(key, unicode):
                item_name = key
            fnc = contentprovider.Archive.resolving_archive.do_menu_action
            params = {key:value}
            it.context_menu.append(PContextMenuItem(item_name, fnc, params))
                
        it.info = infolabel_uni         
        it.image = image
        GItem_lst[0].append(it)


def add_video(name, url, subs=None, image=None, infoLabels={}, menuItems={}, filename=None, live=False):
    """adds video item to content screen
        @param url: play url 
        @param subs: subtitles url
        @param image: image of video item
        @param infoLabels: dictationary of informations{'title':title,'plot':plot,'rating':rating,''}"
        @param filename: set this filename when downloading
        @param live: is video live stream
    """
    
    #controling if task shouldnt be _aborted(ie. we pushed exit button when loading)
    task = Task.getInstance()
    if task and task._aborted:
        raise exceptions.ArchiveThreadException
    else:
        name = util.decode_html(name)
        if util.isSupportedVideo(url):
            it = PVideo()
        else:
            it = PNotSupportedVideo()
            
        if isinstance(name, str):
            it.name = unicode(name, 'utf-8', 'ignore')
        else:
            it.name = name 
        it.url = url
        infolabel_uni = {}
        for key, value in infoLabels.iteritems():
            if isinstance(value, str):
                infolabel_uni[key] = unicode(value, 'utf-8', 'ignore')
            else:
                infolabel_uni[key] = unicode(str(value), 'utf-8', 'ignore')
        if not 'Title' in infolabel_uni:
            infolabel_uni["Title"] = it.name
            
        it.info = infolabel_uni
        
        for key, value in menuItems.iteritems():
            if isinstance(key, str):    
                item_name = unicode(key, 'utf-8', 'ignore')
            elif isinstance(key, unicode):
                item_name = key
            fnc = contentprovider.Archive.resolving_archive.do_menu_action
            params = {key:value}
            it.context_menu.append(PContextMenuItem(item_name, fnc, params))
    
        it.image = image
        
        if filename is not None:
            it.filename = unicode(filename, 'utf-8') 
        it.subs = subs
        it.live = live
        GItem_lst[0].append(it)
        
        
# source from xbmc_doplnky
def get_searches(addon, server):
        local = os.path.join(config.plugins.archivCZSK.dataPath.value, addon.id)
        if not os.path.exists(local):
                os.makedirs(local)
        local = os.path.join(local, server)
        if not os.path.exists(local):
                return []
        f = open(local, 'r')
        data = f.read()
        searches = json.loads(unicode(data.decode('utf-8', 'ignore')))
        f.close()
        return searches

# source from xbmc_doplnky
def add_search(addon, server, search, maximum):
        searches = []
        local = os.path.join(config.plugins.archivCZSK.dataPath.value, addon.id)
        if not os.path.exists(local):
                os.makedirs(local)
        local = os.path.join(local, server)
        if os.path.exists(local):
                f = open(local, 'r')
                data = f.read()
                searches = json.loads(unicode(data.decode('utf-8', 'ignore')))
                f.close()
        if search in searches:
                searches.remove(search)
        searches.insert(0, search)
        remove = len(searches) - maximum
        if remove > 0:
                for i in range(remove):
                        searches.pop()
        f = open(local, 'w')
        f.write(json.dumps(searches, ensure_ascii=True))
        f.close()

# source from xbmc_doplnky
def remove_search(addon, server, search):
        local = os.path.join(config.plugins.archivCZSK.dataPath.value, addon.id)
        if not os.path.exists(local):
                return
        local = os.path.join(local, server)
        if os.path.exists(local):
                f = open(local, 'r')
                data = f.read()
                searches = json.loads(unicode(data.decode('utf-8', 'ignore')))
                f.close()
                searches.remove(search)
                f = open(local, 'w')
                f.write(json.dumps(searches, ensure_ascii=True))
                f.close()    


