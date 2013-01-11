'''
Created on 15.10.2012

@author: marko
'''
import os

from Components.config import config, ConfigSubsection, ConfigSelection, ConfigDirectory, ConfigInteger, ConfigYesNo, ConfigText, configfile, getConfigListEntry
from Components.Language import language
from Plugins.Extensions.archivCZSK import log, _
from engine.player.info import VideoPlayerInfo


PLAYER = VideoPlayerInfo()
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
choicelist = [('standard', _('standard player')),
                ('custom', _('custom player (subtitle support)'))]
playertype = [(PLAYER.type, PLAYER.getPlayerName())]

config.plugins.archivCZSK.videoPlayer.detectedType = ConfigSelection(choices=playertype)
if PLAYER.isRTMPSupported():        
    config.plugins.archivCZSK.videoPlayer.seeking = ConfigYesNo(default=True)
else:
    config.plugins.archivCZSK.videoPlayer.seeking = ConfigYesNo(default=False)
config.plugins.archivCZSK.videoPlayer.type = ConfigSelection(default="custom", choices=choicelist)
config.plugins.archivCZSK.videoPlayer.useVideoController = ConfigYesNo(default=True)             
config.plugins.archivCZSK.videoPlayer.useDefaultSkin = ConfigYesNo(default=False)
config.plugins.archivCZSK.videoPlayer.autoPlay = ConfigYesNo(default=True)

choicelist = [("0", _("default")), ("1", _("prefill")), ("2", _("progressive (need HDD)")), ("3", _("manual"))]
config.plugins.archivCZSK.videoPlayer.bufferMode = ConfigSelection(default="0", choices=choicelist)

choicelist = []
for i in range(500, 20000, 500):
    choicelist.append(("%d" % i, "%d KB" % i))
    choicelist.insert(("0", _("Default")))
config.plugins.archivCZSK.videoPlayer.bufferSize = ConfigSelection(default="0", choices=choicelist)

choicelist = []
for i in range(5, 250, 1):
    choicelist.append(("%d" % i, "%d s" % i))
config.plugins.archivCZSK.videoPlayer.playDelay = ConfigSelection(default="20", choices=choicelist)

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
config.plugins.archivCZSK.autoUpdate = ConfigYesNo(default=True)
config.plugins.archivCZSK.preload = ConfigYesNo(default=True)

choicelist = [('1', _("Info")), ('2', _("Debug"))]
config.plugins.archivCZSK.debugMode = ConfigSelection(default='1', choices=choicelist)

def changeLogMode(configElement):
    log.changeMode(int(configElement.value))
    
config.plugins.archivCZSK.debugMode.addNotifier(changeLogMode)

############ Paths ####################### 

config.plugins.archivCZSK.dataPath = ConfigDirectory(default="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/resources/data")
config.plugins.archivCZSK.downloadsPath = ConfigDirectory(default="/media/hdd")
config.plugins.archivCZSK.subtitlesPath = ConfigDirectory(default="/tmp")

########### Misc #########################

config.plugins.archivCZSK.convertPNG = ConfigYesNo(default=True)
config.plugins.archivCZSK.clearMemory = ConfigYesNo(default=False)
config.plugins.archivCZSK.linkVerification = ConfigYesNo(default=True)

choicelist = []
for i in range(1, 250, 1):
    choicelist.append(("%d" % i, "%d s" % i))
config.plugins.archivCZSK.linkVerificationTimeout = ConfigSelection(default="30", choices=choicelist)



def get_player_settings():
    list = []
    player = config.plugins.archivCZSK.videoPlayer.type.getValue()
    list.append(getConfigListEntry(_("Detected player"), config.plugins.archivCZSK.videoPlayer.detectedType))
    list.append(getConfigListEntry(_("Video player"), config.plugins.archivCZSK.videoPlayer.type))
    if player == 'custom':
        list.append(getConfigListEntry(_("Use video controller"), config.plugins.archivCZSK.videoPlayer.useVideoController))
        list.append(getConfigListEntry(_("Use default skin"), config.plugins.archivCZSK.videoPlayer.useDefaultSkin))
        if PLAYER.type == 'gstreamer':
            list.append(getConfigListEntry(_("Video player Buffer"), config.plugins.archivCZSK.videoPlayer.bufferSize))
            list.append(getConfigListEntry(_("Video player Buffer Mode"), config.plugins.archivCZSK.videoPlayer.bufferMode))
    if not PLAYER.isRTMPSupported():
        list.append(getConfigListEntry(_("Video player with RTMP support"), config.plugins.archivCZSK.videoPlayer.seeking))
    list.append(getConfigListEntry(_("TV archive rtmp buffer"), config.plugins.archivCZSK.videoPlayer.archiveBuffer))                                                 
    list.append(getConfigListEntry(_("Default live rtmp streams buffer"), config.plugins.archivCZSK.videoPlayer.liveBuffer))                                
    list.append(getConfigListEntry(_("Play after"), config.plugins.archivCZSK.videoPlayer.playDelay))
    return list
    
def get_main_settings():
    list = []
    list.append(getConfigListEntry(_("Allow auto-update"), config.plugins.archivCZSK.autoUpdate))
    list.append(getConfigListEntry(_("Preload"), config.plugins.archivCZSK.preload))
    list.append(getConfigListEntry(_("Debug mode"), config.plugins.archivCZSK.debugMode))
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
    verification = config.plugins.archivCZSK.linkVerification.getValue()
    list.append(getConfigListEntry(_("Use link verification"), config.plugins.archivCZSK.linkVerification))
    if verification:
        list.append(getConfigListEntry(_("Verification timeout"), config.plugins.archivCZSK.linkVerificationTimeout))
    return list
