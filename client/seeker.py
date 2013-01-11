'''
Created on 11.1.2013

@author: marko
'''
#from Plugins.Plugin import PluginDescriptor

import traceback
from Screens.MessageBox import MessageBox    

#    Napriklad:
#   
#    search_exp = u'Matrix'
#    search(session, search_exp, 'plugin.video.online-files')
 
def search(session, search_exp, addon_id, mode=None):
    """
    Vyhlada v archivCZSK hladany vyraz prostrednictvom addonu s addon_id s modom vyhladavania mode
    @param : session - aktivna session
    @param : search_exp - hladany vyraz
    @param : addon_id - id addonu v ktorom chceme vyhladavat
    @param : mode - mod vyhladavania podporovany addonom
    """
    archivCZSKSeeker = ArchivCZSKSeeker.getInstance(session)
    if archivCZSKSeeker is not None:
        archivCZSKSeeker.search(search_exp, addon_id, mode)
    
def searchClose():
    """
    Uvolni pamat po unkonceni prace s vyhladavacom
    """
    if ArchivCZSKSeeker.instance is not None:
        ArchivCZSKSeeker.instance.close()
        

def isArchivCZSKRunning(session):
    for dialog in session.dialog_stack:
        # csfd plugin sa da otvorit len z ContentScreen    
        if dialog.__class__.__name__ == 'ContentScreen':
            return True
    return False
    
def getArchivCZSK():
    from Plugins.Extensions.archivCZSK.archivczsk import ArchivCZSK
    from Plugins.Extensions.archivCZSK.gui.content import ContentScreen
    from Plugins.Extensions.archivCZSK.engine.tools.task import Task
    return ArchivCZSK, ContentScreen, Task

class ArchivCZSKSeeker():
    instance = None
    
    @staticmethod
    def getInstance(session):
        if ArchivCZSKSeeker.instance is None:
            try:
                return ArchivCZSKSeeker(session)
            except ImportError:
                showInfoMessage(session, _('Cannot search, archivCZSK is not installed'), 5)
                print 'cannot found archivCZSK'
                return None
            except Exception:
                traceback.print_exc()
                showErrorMessage(session, _('unknown error'), 5)
                return None
        return ArchivCZSKSeeker.instance
    
    def __init__(self, session):
        self.session = session
        self.archivCZSK, self.contentScreen, self.task = getArchivCZSK() 
        self.searcher = None
        self.addon = None
        self.searching = False
        if not isArchivCZSKRunning(session):
            self.task.startWorkerThread()
        ArchivCZSKSeeker.instance = self
        
    def __repr__(self):
        return '[ArchivCZSKSeeker]'
            
    def _successSearch(self, content):
        (searchItems, command, args) = content
        self.session.openWithCallback(self._contentScreenCB, self.contentScreen, self.addon, searchItems)
        
        
    def _errorSearch(self, failure):
        showErrorMessage(self.session, _('Error while trying to retrieve search list'), 5) 
        if self.searcher is not None:
            self.searcher.close()
            self.searcher = None
        self.searching = False
        self.addon = None
        
    def _contentScreenCB(self, cp):
        if self.searcher is not None:
            self.searcher.close()
            self.searcher = None
        self.searching = False
        self.addon = None           

        
    def search(self, search_exp, addon_id, mode=None):
        if self.searching:
            showInfoMessage(_("You cannot search, archivCZSK Search is already running"))
            print "%s cannot search, searching is not finished" % self
            return
        searcher = getSearcher(self.session, addon_id, self.archivCZSK, self._successSearch, self._errorSearch)
        if searcher is not None:
            self.searcher = searcher
            self.searching = True
            self.addon = searcher.addon
            searcher.search(search_exp, mode)
        else:
            showInfoMessage(_("Cannot find searcher") + ' ' + addon_id.encode('utf-8'))
            
    def close(self):
        if self.searching:
            print '%s cannot close, searching is not finished yet' % self
            return False
        if not isArchivCZSKRunning(self.session):
            self.task.stopWorkerThread()
        ArchivCZSKSeeker.instance = None
        return True
        
        
def getSearcher(session, addon_name, archivczsk, succ_cb, err_cb):
    if addon_name == 'plugin.video.online-files':
        return OnlineFilesSearch(session, archivczsk, succ_cb, err_cb)
    else:
        return None
            

class Search(object):
    def __init__(self, session, archivczsk, succ_cb, err_cb):
        self.session = session
        self.addon = archivczsk.get_addon(self.addon_id)
        self.provider = self.addon.provider
        self.succ_cb = succ_cb
        self.err_cb = err_cb
        
    def search(self, search_exp, mode=None):
        """search according to search_exp and choosen mode"""
        pass
    
    def close(self):
        """releases resources"""
        self.provider.release_dependencies()


class OnlineFilesSearch(Search):
    addon_id = 'plugin.video.online-files'
    
    def search(self, search_exp, mode='all'):
        if mode == 'all':
            self.search_all(search_exp)
        elif mode == 'bezvadata.cz':
            self.bezvadata_search(search_exp)
        elif mode == 'ulozto.cz':
            self.ulozto_search(search_exp)
        elif mode == 'hellspy.cz':
            self.hellspy_search(search_exp)
        else:
            self.search_all(search_exp)
    
    def search_all(self, search_exp):
        params = {'search':search_exp, 'search-no-history':True}
        self.provider.get_content(self.session, params, self.succ_cb, self.err_cb)

    def ulozto_search(self, search_exp):
        params = {'cp':'ulozto.cz', 'search':search_exp, 'search-no-history':True}
        self.provider.get_content(self.session, params, self.succ_cb, self.err_cb)

    def bezvadata_search(self, search_exp):
        params = {'cp':'bezvadata.cz', 'search':search_exp, 'search-no-history':True}
        self.provider.get_content(self.session, params, self.succ_cb, self.err_cb) 
 
    def hellspy_search(self, search_exp, succ_cb, err_cb):
        params = {'cp':'hellspy.cz', 'search':search_exp, 'search-no-history':True}
        self.provider.get_content(self.session, params, self.succ_cb, self.err_cb)

            
            



def showInfoMessage(session, message, timeout=3, cb=None):
    if cb is not None:
        session.openWithCallback(cb, MessageBox, text=message, timeout=timeout, type=MessageBox.TYPE_INFO)
    else:
        session.open(MessageBox, text=message, timeout=timeout, type=MessageBox.TYPE_INFO)

def showWarningMessage(session, message, timeout=3, cb=None):
    if cb is not None:
        session.openWithCallback(cb, MessageBox, text=message, timeout=timeout, type=MessageBox.TYPE_WARNING)
    else:
        session.open(MessageBox, text=message, timeout=timeout, type=MessageBox.TYPE_WARNING)    

def showErrorMessage(session, message, timeout=3, cb=None):
    if cb is not None:
        session.openWithCallback(cb, MessageBox, text=message, timeout=timeout, type=MessageBox.TYPE_ERROR)
    else:
        session.open(MessageBox, text=message, timeout=timeout, type=MessageBox.TYPE_ERROR)


#def main(session, **kwargs):
#    search_exp = u'Matrix'
#    search(session, search_exp, 'plugin.video.online-files')

 
#def Plugins(**kwargs):
#    return [PluginDescriptor(name='Test_Plugin', description='', where=PluginDescriptor.WHERE_PLUGINMENU, icon="plugin.png", fnc=main)]

