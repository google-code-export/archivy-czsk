'''
Created on 21.10.2012

@author: marko
'''

from Screens.MessageBox import MessageBox
from Components.config import config

from . import _
from gui.content import VideoAddonsContentScreen
import engine.exceptions.archiveException as archiveException
from engine.items import PVideoAddon
from engine.addon import VideoAddon

nova = 'plugin.video.dmd-czech.voyo'
btv = 'plugin.video.dmd-czech.btv'
huste = 'plugin.video.dmd-czech.huste'
ct = 'plugin.video.dmd-czech.ivysilani'
metropol = 'plugin.video.dmd-czech.metropol'
muvi = 'plugin.video.dmd-czech.muvi'
joj = 'plugin.video.dmd-czech.joj'
prima = 'plugin.video.dmd-czech.prima'
stream = 'plugin.video.dmd-czech.stream'
stv = 'plugin.video.dmd-czech.stv'
markiza = 'plugin.video.dmd-czech.markiza'

tv_archives = [stv, joj, ct, prima, nova, huste, metropol, btv, markiza, stream]



class ArchivCZSK():
    
    __need_restart = False
    
    __repositories = {}
    __addons = {}
    
    @staticmethod
    def get_repository(repository_id):
        return ArchivCZSK.__repositories[repository_id]
    
    @staticmethod
    def add_repository(repository_id, repository):
        ArchivCZSK.__repositories[repository_id] = repository
    
    @staticmethod
    def get_addon(addon_id):
        return ArchivCZSK.__addons[addon_id]
    
    @staticmethod
    def has_addon(addon_id):
        return addon_id in ArchivCZSK.__addons
    
    @staticmethod
    def add_addon(addon_id, addon):
        ArchivCZSK.__addons[addon_id] = addon
        
    
    def __init__(self, session):
        self.session = session
        self.update_addons = []
        self.updated_addons = []
    
        update_string = ''
        if self.__need_restart:
            self.ask_restart_e2()
        
        elif config.plugins.archivCZSK.autoUpdate.value:
            update_string = self.check_addon_updates()
            if update_string != '':
                self.ask_update_addons(update_string)
            else:
                self.open_archive_screen()
        else:
            self.open_archive_screen()

    def check_addon_updates(self):
        for repo_key in self.__repositories.keys():
            repository = self.__repositories[repo_key]
            try:
                self.update_addons += repository.check_updates()
            except archiveException.UpdateXMLVersionException:
                self.show_error(_("Cannot retrieve update xml for repository") + " [%s]" % repository.name.encode('utf-8'))
                continue
            except Exception:
                self.show_error(_("Error when checking updates of repository") + " [%s]" % repository.name.encode('utf-8'))
                continue
        return ' '.join(addon.name for addon in self.update_addons)
            
    
    
    def ask_update_addons(self, update_string):
        self.session.openWithCallback(self.update_addons,
                                      MessageBox, _("Do you want to update") + update_string.encode('utf-8') + " " + _("addons"),
                                      type=MessageBox.TYPE_YESNO)
        
    
    def update_addons(self, callback=None):
        if callback is not None:
            updated_string = self._update_addons()
            if updated_string != '':
                self.session.openWithCallback(self.ask_restart_e2,
                                              MessageBox,
                                              _("Following addons were updated") + ' ' + updated_string.encode('utf-8'),
                                              type=MessageBox.TYPE_YESNO)
            else:
                self.open_archive_screen()
        else:
            self.open_archive_screen()
        
            
    def _update_addons(self):
        for repo_key in self.__repositories.keys():
            repository = self.__repositories[repo_key]
            try:
                self.updated_addons += repository.update_addons()
            except Exception:
                self.show_error(_("Error when updating repository") + " [%s]" % repository.name)
                continue
        return ' '.join(addon.name for addon in self.updated_addons)
            
    
    def ask_restart_e2(self):
        self.__need_restart = True
        self.session.openWithCallback(self.restart_e2, MessageBox, _("You need to restart E2. Do you want to restart it now?"))        
            
    
    def restart_e2(self, callback=None):
        if callback:
            from Screens.Standby import TryQuitMainloop
            self.session.open(TryQuitMainloop, 3)
        
    
    
    def open_archive_screen(self):
        tv_video_addon = []
        video_addon = []
        for key in ArchivCZSK.__addons.keys():
            addon = ArchivCZSK.get_addon(key)
            if not isinstance(addon, VideoAddon):
                continue
            if key in tv_archives:
                tv_video_addon.append(PVideoAddon(addon))
                print '[ArchivCZSK] adding %s addon to tv group' % key
            else:
                video_addon.append(PVideoAddon(addon))
                print '[ArchivCZSK] adding %s addon to video group' % key
                
            tv_video_addon.sort(cmp=None, key=None, reverse=False)
            video_addon.sort(cmp=None, key=None, reverse=False)
                
        self.session.open(VideoAddonsContentScreen, tv_video_addon, video_addon)
        
    def show_error(self, info):
        self.session.open(MessageBox, info, type=MessageBox.TYPE_ERROR, timeout=1)
        
        
