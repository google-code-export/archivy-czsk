'''
Created on 11.8.2012

@author: marko
'''
#Main config for all archives

import os
from Plugins.Extensions.archivCZSK import _
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import *

PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/"
ARCHIVES_PATH = os.path.join(PLUGIN_PATH, 'resources/archives')
CONFIG_ARCHIVES_PATH = os.path.join(ARCHIVES_PATH, 'config.py')

#define repo paths and their tools path
DMD_PATH = os.path.join(ARCHIVES_PATH, 'dmd_czech')
DMD_TOOLS_PATH = 'resources/archives/dmd_czech/tools'
DMD_TOOLS_NAME = 'dmd_czech_tools'

DOPLNKY_PATH = os.path.join(ARCHIVES_PATH, 'xbmc_doplnky')
DOPLNKY_TOOLS_PATH = 'resources/archives/xbmc_doplnky/tools'
DOPLNKY_TOOLS_NAME = 'xbmc_doplnky_tools'

OTHER = os.path.join(ARCHIVES_PATH, 'other')

archives = [DMD_PATH, DOPLNKY_PATH, OTHER]
tools = [(DMD_TOOLS_NAME, DMD_TOOLS_PATH), (DOPLNKY_TOOLS_NAME, DOPLNKY_TOOLS_PATH)]

dmd = ['movielibrary', 'koukni', 'videacesky', 'bezvadata', 'pohadkar', 'replay', 'serialycz', 'eserialcz']
doplnky = ['muvi', 'filmyczcom', 'stream', 'markiza', 'joj', 'btv', 'voyo', 'ivysilani', 'stv', 'metropol', 'prima', 'huste']



#define in which category archive belong
video_archives = ['movielibrary', 'koukni', 'muvi', 'filmyczcom', 'videacesky', 'stream', 'bezvadata', 'pohadkar', 'replay', 'serialycz', 'eserialcz', 'nastojaka']
tv_archives = ['markiza', 'joj', 'btv', 'voyo', 'ivysilani', 'stv', 'metropol', 'prima', 'huste']
streamy = 'streamy'

config.plugins.archivCZSK = ConfigSubsection()
config.plugins.archivCZSK.archives = ConfigSubsection()


#creating config for every archive
for archs_dir in archives:
    for module in os.listdir(archs_dir):
        if module in ['tools', 'init.py']:
            continue
        setattr(config.plugins.archivCZSK.archives, module, ConfigSubsection())
        archive_conf = getattr(config.plugins.archivCZSK.archives, module)
        archive_conf.enabled = ConfigYesNo(default=True)
        #archive_conf.xml = ConfigYesNo(default=False)

#tv archives
        if module in tv_archives:
            
            if module == 'ivysilani':
                choicelist = [('0', '0'), ('1', '1'), ('2', '2'), ('3', '3'), ('4', _('Infinity'))]
                archive_conf.listings = ConfigSelection(default="0", choices=choicelist)
                
            if module == 'voyo':
                archive_conf.password = ConfigText(default="")
                
            if module == 'joj':
                archive_conf.server = ConfigYesNo(default=False)
                
#video_archives
        elif module in video_archives:
            
            if module == 'koukni':
                choicelist = []
                for i in range(0, 40, 1):
                    choicelist.append(("%d" % i, "%d %s" % (i, _('items'))))
                    archive_conf.keep_searches = ConfigSelection(default="20", choices=choicelist)
                    
            if module == 'nastojaka':
                choicelist = []
                for i in range(0, 40, 1):
                    choicelist.append(("%d" % i, "%d %s" % (i, _('items'))))
                    archive_conf.keep_searches = ConfigSelection(default="20", choices=choicelist)
            
            if module == 'movielibrary':
                choicelist = []
                for i in range(0, 40, 1):
                    choicelist.append(("%d" % i, "%d %s" % (i, _('items'))))
                    archive_conf.keep_searches = ConfigSelection(default="20", choices=choicelist)
                archive_conf.captcha_text = ConfigText(default="abcd")
                archive_conf.captcha_id = ConfigText(default="3333")
                choicelist = [('0', _('name')), ('1', _('year')), ('2', _('date')), ('3', _('rating'))]
                archive_conf.lang_filter = ConfigText(default="")
                archive_conf.lang_filter_include = ConfigYesNo(default=True)
                archive_conf.order = ConfigSelection(default="2", choices=choicelist)
                    
            if module == 'stream':
                archive_conf.username = ConfigText(default="")
                
            if module == 'bezvadata':
                archive_conf.adult = ConfigYesNo(default=False)
#streamy   
        elif module == 'streamy':
            pass
                
            
            
#create config entries           
def getArchiveConfigListEntries(archive):
    archive_conf = archive.config
    list = []
    module = archive.id           
    if module == 'voyo':
        list.append(getConfigListEntry(_("Password"), archive_conf.password))
                
    if module == 'joj':
        list.append(getConfigListEntry(_("Use alternate stream server?"), archive_conf.server))
        
    if module == 'nastojaka':
        list.append(getConfigListEntry(_("Search history"), archive_conf.keep_searches))
                
    if module == 'koukni':
        list.append(getConfigListEntry(_("Search history"), archive_conf.keep_searches))
                
    if module == 'movielibrary':
        list.append(getConfigListEntry(_("Search history"), archive_conf.keep_searches))
        list.append(getConfigListEntry(_("Order by"), archive_conf.order))
        list.append(getConfigListEntry(_("Filter languages - comma-separated e.g.: cz,sk"), archive_conf.lang_filter))
        list.append(getConfigListEntry(_("Include movies without language when filtering"), archive_conf.lang_filter_include))
                
    if module == 'stream':
        list.append(getConfigListEntry(_("User name"), archive_conf.username)) 
                
    if module == 'bezvadata':
        list.append(getConfigListEntry(_("Show 18+ content"), archive_conf.adult))
                
    if module == 'ivysilani':
        list.append(getConfigListEntry(_("Listings"), archive_conf.listings))
    return list
            
