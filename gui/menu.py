# -*- coding: UTF-8 -*-
import os
from Screens.Screen import Screen
from Plugins.Extensions.archivCZSK import _
import Plugins.Extensions.archivCZSK.resources.archives.config as archive_conf
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import *
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from Screens.VirtualKeyBoard import VirtualKeyBoard
from enigma import getDesktop
from info import ChangelogScreen
from Components.FileList import FileList
from Components.Sources.StaticText import StaticText

                      
config.plugins.archivCZSK.archives.streamy = ConfigSubsection()
config.plugins.archivCZSK.mipselPlayer = ConfigSubsection()
config.plugins.archivCZSK.mipselPlayer.autoPlay = ConfigYesNo(default=True)
config.plugins.archivCZSK.mipselPlayer.buffer = ConfigInteger(default=8 * 1024 * 1024)

choicelist = [('standard', _('standard player')), ('custom', _('custom player (subtitle support)')), ('mipsel', _('mipsel player'))]   
config.plugins.archivCZSK.player = ConfigSelection(default="custom", choices=choicelist)                   
config.plugins.archivCZSK.seeking = ConfigYesNo(default=False)
config.plugins.archivCZSK.extensions_menu = ConfigYesNo(default=True)
config.plugins.archivCZSK.clearMemory = ConfigYesNo(default=False)
config.plugins.archivCZSK.autoUpdate = ConfigYesNo(default=False)
config.plugins.archivCZSK.debug = ConfigYesNo(default=False) 
config.plugins.archivCZSK.dataPath = ConfigDirectory(default="/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/resources/data")
config.plugins.archivCZSK.downloadsPath = ConfigDirectory(default="/media/hdd")
config.plugins.archivCZSK.subtitlesPath = ConfigDirectory(default="/tmp")

choicelist = []
for i in range(5, 250, 1):
    choicelist.append(("%d" % i, "%d s" % i))
config.plugins.archivCZSK.playDelay = Config = ConfigSelection(default="7", choices=choicelist)

choicelist = []
for i in range(1000, 20000, 1000):
    choicelist.append(("%d" % i, "%d ms" % i))
config.plugins.archivCZSK.archiveBuffer = ConfigSelection(default="3000", choices=choicelist)

choicelist = []
for i in range(1000, 20000, 1000):
    choicelist.append(("%d" % i, "%d ms" % i))
config.plugins.archivCZSK.liveBuffer = ConfigSelection(default="3000", choices=choicelist)




class ArchiveCZSKConfigScreen(Screen, ConfigListScreen):
    try:
		sz_w = getDesktop(0).size().width()
		if sz_w == 1280:
			HDSkn = True
		else:
			HDSkn = False
    except:
		HDSkn = False
    
    
    if HDSkn:
        skin = """
            <screen position="335,140" size="610,435" >
                <widget name="key_red" position="10,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="160,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="310,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="460,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <eLabel position="-1,55" size="612,1" backgroundColor="#999999" />
                <widget name="config" position="0,55" size="610,350" scrollbarMode="showOnDemand" />
            </screen>"""
    else:
        skin = """
            <screen position="170,120" size="381,320" >
                <widget name="key_red" position="3,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="98,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="193,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="288,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <eLabel position="-1,45" size="383,1" backgroundColor="#999999" />
                <widget name="config" position="0,45" size="390,245" scrollbarMode="showOnDemand" />
            </screen>"""
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.onChangedEntry = [ ]
        self.list = [ ]
        ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)
        self.setup_title = _("Configuration of Archiv CZSK")
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "green": self.keySave,
                "ok": self.keyOk,
                "red": self.keyCancel,
            }, -2)
        self["key_yellow"] = Label("")
        self["key_green"] = Label(_("Save"))
        self["key_red"] = Label(_("Cancel"))
        self["key_blue"] = Label("")
        self.buildMenu()
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_("Configuration of ArchivCZSK"))

    def buildMenu(self):
        self.list = []
        self.list.append(getConfigListEntry(_("Video player"), config.plugins.archivCZSK.player))
        if config.plugins.archivCZSK.player.getValue() == 'mipsel':
            self.list.append(getConfigListEntry(_("Video player Buffer"), config.plugins.archivCZSK.mipselPlayer.buffer))
            self.list.append(getConfigListEntry(_("AutoPlay"), config.plugins.archivCZSK.mipselPlayer.autoPlay))
        self.list.append(getConfigListEntry(_("Video player with RTMP support"), config.plugins.archivCZSK.seeking))
        self.list.append(getConfigListEntry(_("TV archive rtmp buffer"), config.plugins.archivCZSK.archiveBuffer))                                                 
        self.list.append(getConfigListEntry(_("Live rtmp streams buffer"), config.plugins.archivCZSK.liveBuffer))                                
        self.list.append(getConfigListEntry(_("Play after"), config.plugins.archivCZSK.playDelay))
        self.list.append(getConfigListEntry(_("Data path"), config.plugins.archivCZSK.dataPath))
        self.list.append(getConfigListEntry(_("Downloads path"), config.plugins.archivCZSK.downloadsPath))
        self.list.append(getConfigListEntry(_("Subtitles path"), config.plugins.archivCZSK.subtitlesPath))
        self.list.append(getConfigListEntry(_("Allow auto-update"), config.plugins.archivCZSK.autoUpdate))
        self.list.append(getConfigListEntry(_("Debug mode"), config.plugins.archivCZSK.debug))
        self.list.append(getConfigListEntry(_("Free memory after exit"), config.plugins.archivCZSK.clearMemory))
        self.list.append(getConfigListEntry(_("Add to extensions menu"), config.plugins.archivCZSK.extensions_menu))

        self["config"].list = self.list
        self["config"].setList(self.list)
    
    def keyOk(self):
        current = self["config"].getCurrent()[1]
        if current == config.plugins.archivCZSK.subtitlesPath:
            self.session.openWithCallback(self.pathSelectedSubtitles, SelectPath, config.plugins.archivCZSK.subtitlesPath.value)
        if current == config.plugins.archivCZSK.dataPath:
            self.session.openWithCallback(self.pathSelectedData, SelectPath, config.plugins.archivCZSK.dataPath.value)
        if current == config.plugins.archivCZSK.downloadsPath:
            self.session.openWithCallback(self.pathSelectedDownloads, SelectPath, config.plugins.archivCZSK.downloadsPath.value)
        pass
    
    def pathSelectedSubtitles(self, res):
        if res is not None:
            config.plugins.archivCZSK.subtitlesPath.value = res
    
    def pathSelectedData(self, res):
        if res is not None:
            config.plugins.archivCZSK.dataPath.value = res
    
    def pathSelectedDownloads(self, res):
        if res is not None:
            config.plugins.archivCZSK.downloadsPath.value = res

    def keySave(self):
        for x in self["config"].list:
            x[1].save()
        configfile.save()
        self.close()

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()

    def keyLeft(self):
        ConfigListScreen.keyLeft(self) 
        if self["config"].getCurrent()[1] == config.plugins.archivCZSK.player:
            self.buildMenu()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        if self["config"].getCurrent()[1] == config.plugins.archivCZSK.player:
            self.buildMenu()

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()
          
        
 
class ArchiveConfigScreen(Screen, ConfigListScreen):
    try:
		sz_w = getDesktop(0).size().width()
		if sz_w == 1280:
			HDSkn = True
		else:
			HDSkn = False
    except:
		HDSkn = False
    
    
    if HDSkn:
        skin = """
            <screen position="335,140" size="610,435" >
                <widget name="key_red" position="10,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="160,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="310,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="460,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <eLabel position="-1,55" size="612,1" backgroundColor="#999999" />
                <widget name="config" position="0,55" size="610,350" scrollbarMode="showOnDemand" />
            </screen>"""
    else:
        skin = """
            <screen position="170,120" size="381,320" >
                <widget name="key_red" position="3,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="98,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="193,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="288,0" zPosition="1" size="90,40" font="Regular;17" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <eLabel position="-1,45" size="383,1" backgroundColor="#999999" />
                <widget name="config" position="0,45" size="390,245" scrollbarMode="showOnDemand" />
            </screen>"""
    
    def __init__(self, session, archive):
        Screen.__init__(self, session)
        self.session = session
        self.archive = archive
        self.onChangedEntry = [ ]
        self.list = [ ]
        ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)
        self.setup_title = _("Settings of ") + archive.name.encode('utf-8')
        self.archive_conf = getattr(config.plugins.archivCZSK.archives, archive.id)
            
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "green": self.keySave,
                "ok": self.keyOk,
                "red": self.keyCancel,
                "blue": self.changelog
            }, -2)
        self["key_yellow"] = Label("")
        self["key_green"] = Label(_("Save"))
        self["key_red"] = Label(_("Cancel"))
        self["key_blue"] = Label("Changelog")
        self.buildMenu()
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_("Settings of") + ' ' + self.archive.name.encode('utf-8'))
            
    
    def changelog(self):
        self.session.open(ChangelogScreen, self.archive)
        
    def buildMenu(self):
        self.list = archive_conf.getArchiveConfigListEntries(self.archive)
        self["config"].list = self.list
        self["config"].setList(self.list)  
        
    def keyOk(self):
        if len(self.list) > 0:
            current = self["config"].getCurrent()[1]
            if current == config.plugins.archivCZSK.archives.voyo.password:
                self.session.openWithCallback(lambda x : self.VirtualKeyBoardCallback(x, 'password'), VirtualKeyBoard, title=(_("Enter the password:")), text=config.plugins.archivCZSK.archives.voyo.password.value)
            elif current == config.plugins.archivCZSK.archives.stream.username:
                self.session.openWithCallback(lambda x : self.VirtualKeyBoardCallback(x, 'username'), VirtualKeyBoard, title=(_("Enter the username:")), text=config.plugins.archivCZSK.archives.stream.username.value)    	
            else:
                pass
        else:
            pass		    
    
    def keySave(self):
        for x in self["config"].list:
            x[1].save()
        configfile.save()
        self.close()

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()

    def keyLeft(self):
        ConfigListScreen.keyLeft(self) 

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()    
            
    def VirtualKeyBoardCallback(self, callback=None, entry=None):
        if callback is not None and len(callback) and entry is not None and len(entry):
            if entry == 'password':
                config.plugins.archivCZSK.archives.voyo.password.setValue(callback)
            if entry == 'username':
                config.plugins.archivCZSK.archives.stream.username.setValue(callback)



class SelectPath(Screen):
    skin = """<screen name="SelectPath" position="center,center" size="560,320">
            <ePixmap pixmap="skin_default/buttons/red.png" position="0,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="140,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" zPosition="0" size="140,40" transparent="1" alphatest="on" />
            <widget name="target" position="0,60" size="540,22" valign="center" font="Regular;22" />
            <widget name="filelist" position="0,100" zPosition="1" size="560,220" scrollbarMode="showOnDemand"/>
            <widget render="Label" source="key_red" position="0,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
            <widget render="Label" source="key_green" position="140,0" size="140,40" zPosition="5" valign="center" halign="center" backgroundColor="red" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />
        </screen>"""
    def __init__(self, session, initDir):
        Screen.__init__(self, session)
        inhibitDirs = ["/bin", "/boot", "/dev", "/etc", "/lib", "/proc", "/sbin", "/sys", "/usr", "/var"]
        inhibitMounts = []
        self["filelist"] = FileList(initDir, showDirectories=True, showFiles=False, inhibitMounts=inhibitMounts, inhibitDirs=inhibitDirs)
        self["target"] = Label()
        self["actions"] = ActionMap(["WizardActions", "DirectionActions", "ColorActions", "EPGSelectActions"],
        {
            "back": self.cancel,
            "left": self.left,
            "right": self.right,
            "up": self.up,
            "down": self.down,
            "ok": self.ok,
            "green": self.green,
            "red": self.cancel
            
        }, -1)
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("OK"))
        self.onShown.append(self.setWindowTitle)
        
    def setWindowTitle(self):
        self.setTitle(_("Select directory"))

    def cancel(self):
        self.close(None)

    def green(self):
        self.close(self["filelist"].getSelection()[0])

    def up(self):
        self["filelist"].up()
        self.updateTarget()

    def down(self):
        self["filelist"].down()
        self.updateTarget()

    def left(self):
        self["filelist"].pageUp()
        self.updateTarget()

    def right(self):
        self["filelist"].pageDown()
        self.updateTarget()

    def ok(self):
        if self["filelist"].canDescent():
            self["filelist"].descent()
            self.updateTarget()

    def updateTarget(self):
        currFolder = self["filelist"].getSelection()[0]
        if currFolder is not None:
            self["target"].setText(currFolder)
        else:
            self["target"].setText(_("Invalid Location"))

