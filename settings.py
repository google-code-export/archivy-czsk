'''
Created on 15.10.2012

@author: marko
'''
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigDirectory, ConfigInteger, ConfigYesNo, ConfigText, configfile, getConfigListEntry
import os
from Plugins.Extensions.archivCZSK import _

PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/"
IMAGE_PATH = os.path.join(PLUGIN_PATH, 'gui/icon')
SKIN_PATH = os.path.join(PLUGIN_PATH, 'gui/skin')
REPOSITORY_PATH = os.path.join(PLUGIN_PATH, 'resources/archives')


config.plugins.archivCZSK = ConfigSubsection()
config.plugins.archivCZSK.archives = ConfigSubsection()

################## Player config #####################################

choicelist = [('standard', _('standard player')), ('custom', _('custom player (subtitle support)')), ('mipsel', _('mipsel player'))]   
config.plugins.archivCZSK.player = ConfigSelection(default="custom", choices=choicelist)
config.plugins.archivCZSK.useVideoController = ConfigYesNo(default=False)             
config.plugins.archivCZSK.seeking = ConfigYesNo(default=False)
config.plugins.archivCZSK.mipselPlayer = ConfigSubsection()
config.plugins.archivCZSK.mipselPlayer.autoPlay = ConfigYesNo(default=True)
config.plugins.archivCZSK.mipselPlayer.buffer = ConfigInteger(default=8 * 1024 * 1024)

choicelist = []
for i in range(5, 250, 1):
    choicelist.append(("%d" % i, "%d s" % i))
config.plugins.archivCZSK.playDelay = Config = ConfigSelection(default="10", choices=choicelist)

choicelist = []
for i in range(1000, 20000, 1000):
    choicelist.append(("%d" % i, "%d ms" % i))
config.plugins.archivCZSK.archiveBuffer = ConfigSelection(default="3000", choices=choicelist)

choicelist = []
for i in range(1000, 20000, 1000):
    choicelist.append(("%d" % i, "%d ms" % i))
config.plugins.archivCZSK.liveBuffer = ConfigSelection(default="3000", choices=choicelist)


############ Main config #################

config.plugins.archivCZSK.main_menu = ConfigYesNo(default=True)
config.plugins.archivCZSK.extensions_menu = ConfigYesNo(default=False)
config.plugins.archivCZSK.clearMemory = ConfigYesNo(default=False)
config.plugins.archivCZSK.autoUpdate = ConfigYesNo(default=False)
config.plugins.archivCZSK.debug = ConfigYesNo(default=False)


############ Paths ####################### 

config.plugins.archivCZSK.dataPath = ConfigDirectory(default="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/resources/data")
config.plugins.archivCZSK.downloadsPath = ConfigDirectory(default="/media/hdd")
config.plugins.archivCZSK.subtitlesPath = ConfigDirectory(default="/tmp")


def get_player_settings():
    list = []
    list.append(getConfigListEntry(_("Video player"), config.plugins.archivCZSK.player))
    list.append(getConfigListEntry(_("Use video controller"), config.plugins.archivCZSK.useVideoController))
    if config.plugins.archivCZSK.player.getValue() == 'mipsel':
        list.append(getConfigListEntry(_("Video player Buffer"), config.plugins.archivCZSK.mipselPlayer.buffer))
        list.append(getConfigListEntry(_("AutoPlay"), config.plugins.archivCZSK.mipselPlayer.autoPlay))
    list.append(getConfigListEntry(_("Video player with RTMP support"), config.plugins.archivCZSK.seeking))
    list.append(getConfigListEntry(_("TV archive rtmp buffer"), config.plugins.archivCZSK.archiveBuffer))                                                 
    list.append(getConfigListEntry(_("Default live rtmp streams buffer"), config.plugins.archivCZSK.liveBuffer))                                
    list.append(getConfigListEntry(_("Play after"), config.plugins.archivCZSK.playDelay))
    return list
    
def get_main_settings():
    list = []
    #list.append(getConfigListEntry(_("Allow auto-update"), config.plugins.archivCZSK.autoUpdate))
    list.append(getConfigListEntry(_("Debug mode"), config.plugins.archivCZSK.debug))
    list.append(getConfigListEntry(_("Free memory after exit"), config.plugins.archivCZSK.clearMemory))
    list.append(getConfigListEntry(_("Add to extensions menu"), config.plugins.archivCZSK.extensions_menu))
    list.append(getConfigListEntry(_("Add to main menu"), config.plugins.archivCZSK.main_menu))
    return list
    
def get_path_settings():
    list = []
    list.append(getConfigListEntry(_("Data path"), config.plugins.archivCZSK.dataPath))
    list.append(getConfigListEntry(_("Downloads path"), config.plugins.archivCZSK.downloadsPath))
    list.append(getConfigListEntry(_("Subtitles path"), config.plugins.archivCZSK.subtitlesPath))
    return list
    





