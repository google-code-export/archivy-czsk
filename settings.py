'''
Created on 15.10.2012

@author: marko
'''
import os

from Components.config import config, ConfigSubsection, ConfigSelection, ConfigDirectory, ConfigInteger, ConfigYesNo, ConfigText, configfile, getConfigListEntry
from Components.Language import language
from Plugins.Extensions.archivCZSK import _


LANGUAGE_SETTINGS_ID = language.getLanguage()[:2]

######### Plugin Paths ##############
PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/"
IMAGE_PATH = os.path.join(PLUGIN_PATH, 'gui/icon')
SKIN_PATH = os.path.join(PLUGIN_PATH, 'gui/skin')
REPOSITORY_PATH = os.path.join(PLUGIN_PATH, 'resources/repositories')
STREAM_PATH = os.path.join(PLUGIN_PATH, 'streams/streams.xml')

############ Updater Paths #############
TMP_PATH = '/tmp/archivCZSK/'


config.plugins.archivCZSK = ConfigSubsection()
config.plugins.archivCZSK.archives = ConfigSubsection()

################## Player config #####################################
config.plugins.archivCZSK.videoPlayer = ConfigSubsection()
choicelist = [('standard', _('standard player')), ('custom', _('custom player (subtitle support)')), ('mipsel', _('mipsel player'))]   
config.plugins.archivCZSK.videoPlayer.type = ConfigSelection(default="custom", choices=choicelist)
config.plugins.archivCZSK.videoPlayer.useVideoController = ConfigYesNo(default=True)             
config.plugins.archivCZSK.videoPlayer.seeking = ConfigYesNo(default=False)
config.plugins.archivCZSK.videoPlayer.useDefaultSkin = ConfigYesNo(default=False)
config.plugins.archivCZSK.videoPlayer.mipselPlayer = ConfigSubsection()
config.plugins.archivCZSK.videoPlayer.mipselPlayer.autoPlay = ConfigYesNo(default=True)
config.plugins.archivCZSK.videoPlayer.mipselPlayer.buffer = ConfigInteger(default=8 * 1024 * 1024)


choicelist = []
for i in range(5, 250, 1):
    choicelist.append(("%d" % i, "%d s" % i))
config.plugins.archivCZSK.videoPlayer.playDelay = Config = ConfigSelection(default="20", choices=choicelist)

choicelist = []
for i in range(1000, 50000, 1000):
    choicelist.append(("%d" % i, "%d ms" % i))
config.plugins.archivCZSK.videoPlayer.archiveBuffer = ConfigSelection(default="14000", choices=choicelist)

choicelist = []
for i in range(1000, 50000, 1000):
    choicelist.append(("%d" % i, "%d ms" % i))
config.plugins.archivCZSK.videoPlayer.liveBuffer = ConfigSelection(default="14000", choices=choicelist)


############ Main config #################

config.plugins.archivCZSK.main_menu = ConfigYesNo(default=True)
config.plugins.archivCZSK.extensions_menu = ConfigYesNo(default=False)
config.plugins.archivCZSK.clearMemory = ConfigYesNo(default=False)
config.plugins.archivCZSK.autoUpdate = ConfigYesNo(default=False)
config.plugins.archivCZSK.debug = ConfigYesNo(default=False)
config.plugins.archivCZSK.convertPNG = ConfigYesNo(default=False)

############ Paths ####################### 

config.plugins.archivCZSK.dataPath = ConfigDirectory(default="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/resources/data")
config.plugins.archivCZSK.downloadsPath = ConfigDirectory(default="/media/hdd")
config.plugins.archivCZSK.subtitlesPath = ConfigDirectory(default="/tmp")


def get_player_settings():
    list = []
    player = config.plugins.archivCZSK.videoPlayer.type.getValue()
    list.append(getConfigListEntry(_("Video player"), config.plugins.archivCZSK.videoPlayer.type))
    if player == 'mipsel' or player == 'custom':
        list.append(getConfigListEntry(_("Use video controller"), config.plugins.archivCZSK.videoPlayer.useVideoController))
    if player == 'mipsel':
        list.append(getConfigListEntry(_("Video player Buffer"), config.plugins.archivCZSK.videoPlayer.mipselPlayer.buffer))
        list.append(getConfigListEntry(_("AutoPlay"), config.plugins.archivCZSK.videoPlayer.mipselPlayer.autoPlay))
    list.append(getConfigListEntry(_("Video player with RTMP support"), config.plugins.archivCZSK.videoPlayer.seeking))
    list.append(getConfigListEntry(_("TV archive rtmp buffer"), config.plugins.archivCZSK.videoPlayer.archiveBuffer))                                                 
    list.append(getConfigListEntry(_("Default live rtmp streams buffer"), config.plugins.archivCZSK.videoPlayer.liveBuffer))                                
    list.append(getConfigListEntry(_("Play after"), config.plugins.archivCZSK.videoPlayer.playDelay))
    list.append(getConfigListEntry(_("Use default skin"), config.plugins.archivCZSK.videoPlayer.useDefaultSkin))
    return list
    
def get_main_settings():
    list = []
    list.append(getConfigListEntry(_("Allow auto-update"), config.plugins.archivCZSK.autoUpdate))
    list.append(getConfigListEntry(_("Debug mode"), config.plugins.archivCZSK.debug))
    list.append(getConfigListEntry(_("Add to extensions menu"), config.plugins.archivCZSK.extensions_menu))
    list.append(getConfigListEntry(_("Add to main menu"), config.plugins.archivCZSK.main_menu))
    return list
    
def get_path_settings():
    list = []
    list.append(getConfigListEntry(_("Data path"), config.plugins.archivCZSK.dataPath))
    list.append(getConfigListEntry(_("Downloads path"), config.plugins.archivCZSK.downloadsPath))
    list.append(getConfigListEntry(_("Subtitles path"), config.plugins.archivCZSK.subtitlesPath))
    return list

def get_misc_settings():
    list = []
    list.append(getConfigListEntry(_("Convert captcha images to 8bit"), config.plugins.archivCZSK.convertPNG))
    list.append(getConfigListEntry(_("Free memory after exit"), config.plugins.archivCZSK.clearMemory))
    return list
    





