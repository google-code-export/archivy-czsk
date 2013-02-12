'''
Created on 15.10.2012

@author: marko
'''
import os

from Components.config import config, ConfigSubsection, ConfigSelection, ConfigDirectory, ConfigInteger, ConfigYesNo, ConfigText, configfile, getConfigListEntry
from Components.Language import language
from Plugins.Extensions.archivCZSK import log, _
from engine.player.info import videoPlayerInfo
from engine.tools import stb
SERVICEMP4 = False

try:
    import engine.player.servicemp4
    SERVICEMP4 = True
except ImportError:
    print '[ArchivCZSK] error in importing servicemp4'
    SERVICEMP4 = False
 
LANGUAGE_SETTINGS_ID = language.getLanguage()[:2]
AZBOX = stb.getBoxtype()[0] == 'Azbox'

######### Plugin Paths ##############

PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/"
IMAGE_PATH = os.path.join(PLUGIN_PATH, 'gui/icon')
SKIN_PATH = os.path.join(PLUGIN_PATH, 'gui/skin')
REPOSITORY_PATH = os.path.join(PLUGIN_PATH, 'resources/repositories')
STREAM_PATH = os.path.join(PLUGIN_PATH, 'streams/streams.xml')

############ Updater Paths #############

TMP_PATH = '/tmp/archivCZSK/'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0'

config.plugins.archivCZSK = ConfigSubsection()
config.plugins.archivCZSK.archives = ConfigSubsection()

################## Player config #####################################

config.plugins.archivCZSK.videoPlayer = ConfigSubsection()
playertype = [(videoPlayerInfo.type, videoPlayerInfo.getName())]

config.plugins.archivCZSK.videoPlayer.detectedType = ConfigSelection(choices=playertype)
if videoPlayerInfo.isRTMPSupported():        
    config.plugins.archivCZSK.videoPlayer.seeking = ConfigYesNo(default=True)
else:
    config.plugins.archivCZSK.videoPlayer.seeking = ConfigYesNo(default=False)

choicelist = [('standard', _('standard player')),
              ('custom', _('custom player (subtitle support)'))]
config.plugins.archivCZSK.videoPlayer.type = ConfigSelection(default="custom", choices=choicelist)
config.plugins.archivCZSK.videoPlayer.useVideoController = ConfigYesNo(default=True)             
config.plugins.archivCZSK.videoPlayer.useDefaultSkin = ConfigYesNo(default=True)
config.plugins.archivCZSK.videoPlayer.autoPlay = ConfigYesNo(default=True)

# to use servicemrua instead of servicemp3/servicemp4
config.plugins.archivCZSK.videoPlayer.servicemrua = ConfigYesNo(default=False)

if SERVICEMP4:
    config.plugins.archivCZSK.videoPlayer.servicemp4 = ConfigYesNo(default=True)
else:
    config.plugins.archivCZSK.videoPlayer.servicemp4 = ConfigYesNo(default=False)
    

# downloading flag, headers, userAgent for servicemp4
config.plugins.archivCZSK.videoPlayer.download = ConfigText(default="False")
config.plugins.archivCZSK.videoPlayer.download.setValue("False")
config.plugins.archivCZSK.videoPlayer.download.save()

config.plugins.archivCZSK.videoPlayer.extraHeaders = ConfigText(default="")
config.plugins.archivCZSK.videoPlayer.userAgent = ConfigText(default="")


choicelist=[]
for i in range(5, 120, 1):
    choicelist.append(("%d" % i, "%d s" % i))
config.plugins.archivCZSK.videoPlayer.httpTimeout = ConfigSelection(default="40", choices=choicelist)

choicelist = [("0", _("default")), ("1", _("prefill")), ("2", _("progressive (need HDD)")), ("3", _("manual"))]
config.plugins.archivCZSK.videoPlayer.bufferMode = ConfigSelection(default="0", choices=choicelist)

choicelist = []
for i in range(500, 20000, 500):
    choicelist.append(("%d" % i, "%d KB" % i))
config.plugins.archivCZSK.videoPlayer.bufferSize = ConfigSelection(default="5000", choices=choicelist)

for i in range(1, 100, 1):
    choicelist.append(("%d" % i, "%d MB" % i))
config.plugins.archivCZSK.videoPlayer.downloadBufferSize = ConfigSelection(default="8", choices=choicelist)

choicelist = []
for i in range(1, 50, 1):
    choicelist.append(("%d" % i, "%d s" % i))
config.plugins.archivCZSK.videoPlayer.bufferDuration = ConfigSelection(default="5", choices=choicelist)

choicelist = []
for i in range(5, 250, 1):
    choicelist.append(("%d" % i, "%d s" % i))
config.plugins.archivCZSK.videoPlayer.playDelay = ConfigSelection(default="20", choices=choicelist)

choicelist = []
for i in range(1000, 50000, 1000):
    choicelist.append(("%d" % i, "%d ms" % i))
config.plugins.archivCZSK.videoPlayer.archiveBuffer = ConfigSelection(default="6000", choices=choicelist)

choicelist = []
for i in range(1000, 50000, 1000):
    choicelist.append(("%d" % i, "%d ms" % i))
config.plugins.archivCZSK.videoPlayer.liveBuffer = ConfigSelection(default="6000", choices=choicelist)


############ Main config #################

config.plugins.archivCZSK.main_menu = ConfigYesNo(default=True)
config.plugins.archivCZSK.extensions_menu = ConfigYesNo(default=False)
config.plugins.archivCZSK.autoUpdate = ConfigYesNo(default=True)
config.plugins.archivCZSK.preload = ConfigYesNo(default=True)

choicelist = [('1', _("info")), ('2', _("debug"))]
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

# we dont need linkVerification with gstreamer
if videoPlayerInfo.type == 'gstreamer':
    config.plugins.archivCZSK.linkVerification = ConfigYesNo(default=False)
    config.plugins.archivCZSK.linkVerification.setValue(False)
    config.plugins.archivCZSK.linkVerification.save()
else:
    config.plugins.archivCZSK.linkVerification = ConfigYesNo(default=True)
    

choicelist = []
for i in range(1, 250, 1):
    choicelist.append(("%d" % i, "%d s" % i))
config.plugins.archivCZSK.linkVerificationTimeout = ConfigSelection(default="30", choices=choicelist)



def get_player_settings():
    list = []
    player = config.plugins.archivCZSK.videoPlayer.type.getValue()
    useServiceMP4 = config.plugins.archivCZSK.videoPlayer.servicemp4.getValue()
    useServiceMRUA = config.plugins.archivCZSK.videoPlayer.servicemrua.getValue()
    buffer_mode = config.plugins.archivCZSK.videoPlayer.bufferMode.getValue()
    list.append(getConfigListEntry(_("Detected player"), config.plugins.archivCZSK.videoPlayer.detectedType))
    list.append(getConfigListEntry(_("Video player"), config.plugins.archivCZSK.videoPlayer.type))
    if player == 'custom':
        list.append(getConfigListEntry(_("Use video controller"), config.plugins.archivCZSK.videoPlayer.useVideoController))
        list.append(getConfigListEntry(_("Use default skin"), config.plugins.archivCZSK.videoPlayer.useDefaultSkin))
        if videoPlayerInfo.type == 'gstreamer':
            list.append(getConfigListEntry(_("Buffer size"), config.plugins.archivCZSK.videoPlayer.bufferSize))
            #list.append(getConfigListEntry(_("Video player Buffer Mode"), config.plugins.archivCZSK.videoPlayer.bufferMode))
    if (player == 'standard' and AZBOX) and not useServiceMP4:
        list.append(getConfigListEntry(_("Use servicemrua (AZBOX)"), config.plugins.archivCZSK.videoPlayer.servicemrua))
    if SERVICEMP4 and not useServiceMRUA:
        list.append(getConfigListEntry(_("Use servicemp4"), config.plugins.archivCZSK.videoPlayer.servicemp4))
        if useServiceMP4:
            list.append(getConfigListEntry(_("HTTP Timeout"), config.plugins.archivCZSK.videoPlayer.httpTimeout))
            list.append(getConfigListEntry(_("Buffer Mode"), config.plugins.archivCZSK.videoPlayer.bufferMode))
            list.append(getConfigListEntry(_("Buffer duration"), config.plugins.archivCZSK.videoPlayer.bufferDuration))
            if buffer_mode == "2":
                list.append(getConfigListEntry(_("Buffer size on HDD"), config.plugins.archivCZSK.videoPlayer.downloadBufferSize))
    list.append(getConfigListEntry(_("Video player with RTMP support"), config.plugins.archivCZSK.videoPlayer.seeking))
    list.append(getConfigListEntry(_("TV archive rtmp buffer"), config.plugins.archivCZSK.videoPlayer.archiveBuffer))                                                 
    list.append(getConfigListEntry(_("Default live rtmp streams buffer"), config.plugins.archivCZSK.videoPlayer.liveBuffer))
    #if not (videoPlayerInfo.type == 'gstreamer'):                                
    list.append(getConfigListEntry(_("Play after"), config.plugins.archivCZSK.videoPlayer.playDelay))
    return list
    
def get_main_settings():
    list = []
    list.append(getConfigListEntry(_("Allow auto-update"), config.plugins.archivCZSK.autoUpdate))
    #list.append(getConfigListEntry(_("Preload"), config.plugins.archivCZSK.preload))
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
    if not (videoPlayerInfo.type == 'gstreamer'):
        list.append(getConfigListEntry(_("Use link verification"), config.plugins.archivCZSK.linkVerification))
        if verification:
            list.append(getConfigListEntry(_("Verification timeout"), config.plugins.archivCZSK.linkVerificationTimeout))
    return list
