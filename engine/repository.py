'''
Created on 21.10.2012

@author: marko
'''
import os, traceback
from Components.config import config

from Plugins.Extensions.archivCZSK import settings
from Plugins.Extensions.archivCZSK import archivczsk
from addon import AddonInfo, ToolsAddon, VideoAddon
from tools import parser
import updater


def debug(text):
    if config.plugins.archivCZSK.debug.value:
        print '[ArchivCZSK] Repository', text.encode('utf-8')

class Repository():
    
    """
        Loads installed repository and its addons, 
        can check and retrieve updates/downloads to addons in local repository 
        from remote repository
         
    """
    SUPPORTED_ADDONS = ['video', 'tools']
        
    def __init__(self, config_file):
        debug("initializing repository from %s" % config_file)
        pars = parser.XBMCAddonXMLParser(config_file)
        repo_dict = pars.parse()
        
        self.id = repo_dict['id']
        self.name = repo_dict['name']
        self.author = repo_dict['author']
        self.version = repo_dict['version']
        self.description = repo_dict['description']
        self.update_xml_url = repo_dict['repo_addons_url']
        self.update_datadir_url = repo_dict['repo_datadir_url']
        
        self.path = os.path.split(config_file)[0]
        self.addons_path = self.path#os.path.join(self.path, "addons")
        
        # every repository should have its update xml, to check versions and update/download addons
        self.update_xml_url = settings.UPDATE_REPOSITORY_PATH + self.id + '/addon.xml'
        
        # addon.xml which describes addon
        self.addon_xml_relpath = 'addon.xml'
        
        # icon for addon size 256x256
        self.addon_icon_relpath = 'icon.png'
        
        self.addon_resources_relpath = 'resources' 
        
        # default language,settings and libraries path of addon
        self.addon_languages_relpath = self.addon_resources_relpath + '/language'
        self.addon_settings_relpath = self.addon_resources_relpath + '/settings.xml'
        self.addon_libraries_relpath = self.addon_resources_relpath + '/lib' 

        self.addons = []
        
        #create updater for repository
        self._updater = updater.Updater(self)
        
        # load installed addons in repository
        for addon_dir in os.listdir(self.addons_path):
            addon_path = os.path.join(self.addons_path, addon_dir)
            if os.path.isfile(addon_path):
                continue
            
            addon_info = AddonInfo(os.path.join(addon_path, self.addon_xml_relpath))
            if addon_info.type not in Repository.SUPPORTED_ADDONS:
                raise Exception("%s '%s' addon not in supported type of addons %s " % (self, addon_info.type,Repository.SUPPORTED_ADDONS))
            if addon_info.type == 'video':
                try:
                    addon = VideoAddon(addon_info, self)
                except Exception:
                    traceback.print_exc()
                    debug("%s cannot load video addon %s" % (self, addon_dir))
                    debug("skipping")
                    continue
                else:
                    archivczsk.ArchivCZSK.add_addon(addon.id, addon)

                    self.addons.append(addon)
            
            elif addon_info.type == 'tools':
                # load tools addons
                try:
                    tools = ToolsAddon(addon_info, self)
                except Exception:
                    traceback.print_exc()
                    debug("%s cannot load tools addon %s" % (self, addon_dir))
                    debug("skipping")
                    continue
                else:
                    archivczsk.ArchivCZSK.add_addon(tools.id, tools)
                    self.addons.append(tools)
        debug("%s successfully loaded" % self)
                
     
    def __repr__(self):
        return "%s" % self.name
            
    def check_updates(self):
        self._updater.check_updates()
        
    def update(self):
        self._updater.update()
