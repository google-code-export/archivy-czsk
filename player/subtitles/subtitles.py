# -*- coding: UTF-8 -*-
#################################################################################
#
#    Subtitles library 0.2 for Dreambox-Enigma2
#    Coded by mx3L (c)2012
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#################################################################################

import re
import urllib2
import os
from string import split
from time import sleep
from copy import copy
from re import compile as re_compile
from os import path as os_path, listdir


from enigma import  RT_HALIGN_RIGHT, RT_VALIGN_TOP, eSize, ePoint, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont, getDesktop, eServiceCenter, iServiceInformation, eServiceReference, iSeekableService, iPlayableService, iPlayableServicePtr, eTimer, addFont, gFont
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Language import language
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import ConfigSubsection, ConfigSelection, ConfigYesNo, configfile, getConfigListEntry
from Components.Harddisk import harddiskmanager
from Components.Label import Label, MultiColorLabel
from Components.ActionMap import ActionMap, NumberActionMap
from Components.FileList import FileList
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.config import config
from Tools.Directories import SCOPE_SKIN_IMAGE, SCOPE_PLUGINS, resolveFilename, SCOPE_LANGUAGE
from Tools.LoadPixmap import LoadPixmap

# import localization function if you want
from Plugins.Extensions.archivCZSK import _

# set the name of plugin in which this library belongs 
PLUGIN_NAME = 'archivCZSK'

# set supported encodings, you have to make sure, that you have corresponding python
# libraries in %PYTHON_PATH%/encodings/ (ie. iso-8859-2 requires iso_8859_2.py library)

# to choose encodings for region you want visit:
# http://docs.python.org/release/2.4.4/lib/standard-encodings.html

#Common central European encodings
CENTRAL_EUROPE_ENCODINGS = ['utf-8', 'iso-8859-2', 'windows-1250', 'maclatin2', 'IBM852']


ENCODINGS = {_("Central Europe"):CENTRAL_EUROPE_ENCODINGS}

FONT_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/player/subtitles/fonts/"

# set your fonts
FONT = {
        "Ubuntu":({"regular":"Ubuntu-M.ttf",
                    "italic":"Ubuntu-MI.ttf",
                    "bold":"Ubuntu-B.ttf"}),
        
        
        "Default": ({"regular":"Regular",
                     "italic":"Regular",
                     "bold":"Regular"})
        }

#initializing fonts
for f in FONT.iterkeys():
    if f == 'Default':
        continue
    
    regular = FONT[f]['regular']
    italic = FONT[f]['italic']
    bold = FONT[f]['bold']
    
    if os.path.isfile(FONT_PATH + regular) and os.path.isfile(FONT_PATH + italic) and os.path.isfile(FONT_PATH + bold):
        addFont(FONT_PATH + regular, regular, 100, False)
        addFont(FONT_PATH + italic, italic, 100, False)
        addFont(FONT_PATH + bold, bold, 100, False)
    else:
        del FONT[f]

#initializing settings
plugin_settings = getattr(config.plugins, PLUGIN_NAME)
setattr(plugin_settings, 'subtitles', ConfigSubsection())
subtitles_settings = getattr(plugin_settings, 'subtitles')

subtitles_settings.showSubtitles = ConfigYesNo(default=True)
subtitles_settings.autoLoad = ConfigYesNo(default=True)

choicelist = []
for e in ENCODINGS.iterkeys():
    choicelist.append(e)
subtitles_settings.encodingsGroup = ConfigSelection(default=_("Central Europe"), choices=choicelist)

choicelist = []
for f in FONT.iterkeys():
    choicelist.append(f)
subtitles_settings.fontType = ConfigSelection(default="Default", choices=choicelist)

choicelist = []
for i in range(10, 60, 1):
    choicelist.append(("%d" % i, "%d" % i))
    
# set default font size of subtitles
subtitles_settings.fontSize = ConfigSelection(default="35", choices=choicelist)

choicelist = []
for i in range(0, 101, 2):
    choicelist.append(("%d" % i, "%d" % i))
# set default position of subtitles (0-100) 0-top ,100-bottom
subtitles_settings.position = ConfigSelection(default="94", choices=choicelist)

# set available colors for subtitles
choicelist = []
choicelist.append(("red", _("red")))
#choicelist.append(("#dcfcfc", _("grey")))
choicelist.append(("#00ff00", _("green")))
choicelist.append(("#ff00ff", _("purple")))
choicelist.append(("yellow", _("yellow")))
choicelist.append(("white", _("white")))
choicelist.append(("#00ffff", _("blue")))

subtitles_settings.color = ConfigSelection(default="white", choices=choicelist) 


class SubsScreen(Screen):
        
    def __init__(self, session):
        desktop = getDesktop(0)
        size = desktop.size()
        sc_width = size.width()
        sc_height = size.height()
        fontSize = int(subtitles_settings.fontSize.getValue())
        fontType = subtitles_settings.fontType.getValue()
        
        self.font = {"regular":gFont(FONT[fontType]['regular'], fontSize),
                     "italic":gFont(FONT[fontType]['italic'], fontSize),
                     "bold":gFont(FONT[fontType]['bold'], fontSize)}
        
        self.selected_font = "regular"
        
        position = int(subtitles_settings.position.getValue())
        vSize = fontSize * 3 + 10 # 3 rows + reserve
        color = subtitles_settings.color.getValue()
        position = int(position * (float(sc_height - vSize) / 100)) 
        
        self.skin = """
            <screen name="SubtitleDisplay" position="0,0" size="%s,%s" zPosition="-1" backgroundColor="transparent" flags="wfNoBorder">
                    <widget name="subtitles" position="0,%s" size="%s,%s" valign="center" halign="center" font="%s;%s" transparent="1" foregroundColor="%s" shadowColor="#40101010" shadowOffset="3,3" />
            </screen>""" % (str(sc_width), str(sc_height), str(position), str(sc_width), str(vSize), str(FONT[fontType]['regular']), str(fontSize), color)
            
        Screen.__init__(self, session)
        self.stand_alone = True
        print 'initializing subtitle display'
        self["subtitles"] = Label("")
        
    def setSubtitle(self, sub):
        if sub['style'] != self.selected_font:
            self.selected_font = sub['style']
            self['subtitles'].instance.setFont(self.font[sub['style']])
            
        self["subtitles"].setText(sub['text'].encode('utf-8'))
    
    def hideSubtitle(self):
        self["subtitles"].setText("")
         

              
class Subtitles(object):
    def __init__(self, session, subPath=None, defaultPath=None, forceDefaultPath=False):
        self.session = session
        self.subsScreen = None
        self.subsEngine = None
        self.subDict = None
        self.loaded = False
        self.subPath = None
        self.subDir = None
        self.subEnc = None
        self.defaultPath = None
        self.forceDefaultPath = forceDefaultPath
        self.encodings = ENCODINGS[subtitles_settings.encodingsGroup.getValue()][:]
        
        if defaultPath is not None and os.path.isdir(defaultPath):
            self.defaultPath = defaultPath
            self.subDir = defaultPath
        if subPath is not None:
            self.load(subPath)
            
    def reset(self, enc=True):
        self.encodings = ENCODINGS[subtitles_settings.encodingsGroup.getValue()][:]
        self.subsEngine.pause()
        self.subsEngine.exit()
        self.subsEngine = None
        self.session.deleteDialog(self.subsScreen)
        if enc:
            self.subEnc = None
        self.subsScreen = None
        self.subPath = None
        self.subDict = None
        self.loaded = False
    
    def resetSubsScreen(self):
        self.pause()
        self.hideDialog()
        self.session.deleteDialog(self.subsScreen)
        self.subsScreen = self.session.instantiateDialog(SubsScreen)
        self.subsEngine.subsScreen = self.subsScreen
        self.resume()  
    
    def load(self, filePath):
        self.subPath = None
        if self.defaultPath is not None:
            self.subDir = self.defaultPath
        else:
            self.subDir = None

        if filePath is not None:
            if filePath.startswith('http'):
                self.subPath = filePath
            else:
                if self.defaultPath is not None and self.forceDefaultPath:
                        self.subDir = self.defaultPath
                else:
                    if os.path.isdir(os.path.split(filePath)[0]):
                        self.subDir = os.path.split(filePath)[0]
                    else:
                        self.subDir = self.defaultPath
                if os.path.isfile(filePath):
                    self.subPath = filePath
            
            if self.subPath is not None:

                # decoding text to unicode
                spp = SubProcessPath(self.subPath, self.encodings, self.subEnc)
                subText, self.subEnc = spp.text, spp.encoding
                # parsing subtitles to dict
                srt = srtParser(subText)
                subDict = srt.parse()
                
                ## removing tags and adding style
                ss = SubStyler(subDict)
                self.subDict = ss.subDict 
                
            if self.subDict is not None:
                self.loaded = True
                self.subsScreen = self.session.instantiateDialog(SubsScreen)
                self.subsEngine = SubsEngine(self.session, self.subsScreen, self.subDict)
                return True
            else:
                return False
        return False
           
    def pause(self):
        if self.loaded:
            print '[Subtitles] pausing subtitles'
            self.subsEngine.pause()
    
    def play(self):
        if self.loaded:
            if subtitles_settings.showSubtitles.value:
                self.showDialog() 
            else:
                self.hideDialog()
            self.subsEngine.play()
            
    def playAfterSeek(self):
        if self.loaded:
            if subtitles_settings.showSubtitles.value:
                self.showDialog() 
            else:
                self.hideDialog()
            self.subsEngine.playAfterSeek()
       
    def resume(self):
        if self.loaded:
            print '[Subtitles] resuming subtitles'
            self.play()   
        
    def showDialog(self):
        if self.loaded:
            print '[Subtitles] show dialog'   
            self.subsScreen.show()
    
    def hideDialog(self):
        if self.loaded:
            print '[Subtitles] hide dialog' 
            self.subsScreen.hide()
        
    def setup(self):
        self.session.openWithCallback(self.subsMenuCB, SubsMenu, self.subPath, self.subDir, self.subEnc)
    
    def subsMenuCB(self, subfile, settings_changed, change_encoding=False):
        # subtitles loaded and changed settings
        if self.loaded and (self.subPath == subfile) and settings_changed and not change_encoding:
            print 'resetsubscreen' 
            self.resetSubsScreen()
                
        elif change_encoding:
            print 'changed encoding'
            if self.loaded:
                self.reset(False)
            self.load(subfile)
            self.resume()   
        
        elif subfile != self.subPath:
            print 'changed file'
            if self.loaded:
                self.reset(True)
            self.load(subfile)
            self.resume()
                
    def exit(self):
            
        self.hideDialog()
        
        if self.subsEngine:
            self.subsEngine.exit()
            del self.subsEngine
            self.subsEngine = None
        
        if self.subsScreen:
            self.session.deleteDialog(self.subsScreen)
            del self.subsScreen
            self.subsScreen = None
        
        del self.subDict
        self.subDict = None
        
        subtitles_settings.showSubtitles.setValue(True)
        subtitles_settings.showSubtitles.save()
        print '[Subtitles] closing subtitleDisplay'
    
    
    
class SubsEngine(object):

    def __init__(self, session, subsScreen, srtDict):
        self.subsScreen = subsScreen
        self.session = session
        self.srtsub = srtDict
        self.pos = 0
        self.service = None
        self.playPts = None
        self.oldPlayPts = None
        self.actsub = None
        self.showSubs = False
        self.timer1 = eTimer()
        self.timer1.callback.append(self.wait)
        self.timer1_running = False
        self.timer2 = eTimer()
        self.timer2.callback.append(self.hide)
        self.timer2_running = False
        self.seek_timer = eTimer()
        self.seek_timer.callback.append(self.setPlayPts)
        self.seek_timer.callback.append(self.doPlayAfterSeek)
        self.seek_timer_running = False
        
        
    def reset(self):
        self.timer1.stop()
        self.timer1_running = False
        self.timer2.stop()
        self.timer2_running = False
        self.actsub = None
        self.loaded = False
        self.srtsub = None
        self.playPts = None
        self.pos = 0
        
    def wait(self):
        self.timer1.stop()
        self.timer1_running = False      
        self.playPts = self.getPlayPts()
        while self.playPts is None:
            self.playPts = self.getPlayPts()
              
        if self.playPts < self.actsub['start']:
            diff = self.actsub['start'] - self.playPts
            diff = diff / 90
            if diff > 1:
                if not self.timer1_running and not self.timer2_running:                   
                    self.timer1.start(diff)
                    self.timer1_running = True
                else:
                    self.wait()
            else:
                self.show()
        else:
            if self.actsub['start'] - self.playPts < -90000:
                self.pos = self.pos + 1
                self.play()
            else:
                self.delay = (self.actsub['start'] - self.playPts) / 90
                self.show()
                                                    
        
    def play(self):   
        if self.pos == 0:
            while self.service is None:
                self.service = self.session.nav.getCurrentService()
            self.seek = self.service.seek()   
            sub = self.srtsub[0]
            self.actsub = sub
            self.wait()
                   
        if self.pos > 0 and self.pos < len(self.srtsub):
            sub = self.srtsub[self.pos]
            self.actsub = sub
            self.wait()
                
    def pause(self):
        self.subsScreen.hideSubtitle()
        self.timer1.stop()
        self.timer1_running = False
        self.timer2.stop()
        self.timer2_running = False
        
    
    def playAfterSeek(self):
        self.seek_timer.start(1000)
                    
    def doPlayAfterSeek(self):
        self.seek_timer.stop()
        self.pause()
        ptsBefore = self.oldPlayPts        
        if self.playPts < ptsBefore: #seek backward
            while self.srtsub[self.pos]['start'] > self.playPts and self.pos > 0:
                self.pos = self.pos - 1
        else: #seek forward
            while self.srtsub[self.pos]['start'] < self.playPts and self.pos < len(self.srtsub) - 1:
                self.pos = self.pos + 1
        self.play()
                      
    def show(self):
        self.showSubs = True
        duration = int(self.actsub['duration'])#+self.delay
        self.subsScreen.setSubtitle(self.actsub)
        if not self.timer1_running and not self.timer2_running:
            self.timer2.start(duration)
            self.timer2_running = True
            
            
    def hide(self):
        self.timer2.stop()
        self.timer2_running = False
        self.showSubs = False
        self.subsScreen.hideSubtitle()
        if len(self.srtsub) <= self.pos + 1:
            self.pause()
        else:
            self.pos = self.pos + 1
            self.play()
    
    def showDialog(self):
        #print '[SubsEngine] show dialog'   
        self.subsScreen.show()
    
    def hideDialog(self): 
        #print '[SubsEngine] hide dialog' 
        self.subsScreen.hide()            
                             
    def getPlayPts(self):
        r = self.seek.getPlayPosition()
        if r[0]:
            return None
        return long(r[1])
    
    def setPlayPts(self):
        self.oldPlayPts = copy(self.playPts)
        self.playPts = self.getPlayPts()
    
    def exit(self):
        self.pause()
        del self.timer1
        del self.timer2
        del self.seek_timer
        
class PanelList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setItemHeight(35)
        self.l.setFont(0, gFont("Regular", 22))
            
def PanelListEntry(name, idx, png=''):
    res = [(name)]
    res.append(MultiContentEntryText(pos=(5, 5), size=(330, 30), font=0, flags=RT_VALIGN_TOP, text=name))
    return res        
        
        
class SubsMenu(Screen):
    skin = """
        <screen position="center,center" size="500,400" title="Main Menu" >
            <widget name="info_sub" position="0,5" size="500,40" valign="center" halign="center" font="Regular;25" transparent="1" foregroundColor="white" />
            <widget name="info_subfile" position="0,55" size="500,40" valign="center" halign="center" font="Regular;22" transparent="1" foregroundColor="#DAA520" />
            <widget name="enc_sub" position="0,90" size="80,25" valign="center" halign="left" font="Regular;16" transparent="1" foregroundColor="white" />
            <widget name="enc_subfile" position="100,90" size="200,25" valign="center" halign="left" font="Regular;16" transparent="1" foregroundColor="#DAA520" />
            <widget name="menu" position="0,125" size="500,275" transparent="1" scrollbarMode="showOnDemand" />
        </screen>"""

    def __init__(self, session, subfile=None, subdir=None, encoding=None):
        Screen.__init__(self, session)
        
        self["menu"] = PanelList([])
        self["info_sub"] = Label(_("Currently choosed subtitles"))
        self["info_subfile"] = Label("")
        self["enc_sub"] = Label("")
        self["enc_subfile"] = Label("")
        
        if subfile is not None:
            self["info_subfile"].setText(os.path.split(subfile)[1].encode('utf-8'))
            self["enc_sub"].setText(_("encoding"))
            self["enc_subfile"].setText(encoding.encode('utf-8'))
        else:
            self["info_subfile"].setText(_("None"))
        
        self.title = _('Subtitles')
        self.lst = [unicode(_('Choose subtitles'), 'utf-8'),
                    unicode(_('Subtitles settings'), 'utf-8')]
        if subfile is not None:
            self.lst.append(_('Change encoding'))
        self.subfile = subfile
        self.subdir = subdir
        self.change_encoding = False
        self.changed_settings = False
        self.working = False
        
        self.onShown.append(self.setWindowTitle)

        self["actions"] = NumberActionMap(["SetupActions", "DirectionActions"],
            {
                "ok": self.okClicked,
                "cancel": self.exit,
                "up": self.up,
                "down": self.down,
            }, -2)          
        self.onLayoutFinish.append(self.createMenu)
        
    def setWindowTitle(self):
        self.setTitle(self.title)
        
    def createMenu(self):
        lst = self.lst
        self.working = True
            
        self.menu_main = []
        for x in self.menu_main:
            del self.menu_main[0]
            
        list = []
        idx = 0
        for x in lst:
            list.append(PanelListEntry(x.encode('utf-8'), idx))
            self.menu_main.append(x)
            idx += 1        
        self["menu"].setList(list)
        self.working = False
        
    def okClicked(self):
        if not self.working:
            self.working = True
            if self["menu"].getSelectedIndex() == 0:
                self.session.openWithCallback(self.fileChooserCB, SubsFileChooser, self.subdir)
                
            elif self["menu"].getSelectedIndex() == 1:
                self.session.openWithCallback(self.subsSetupCB, SubsSetup)
            elif self["menu"].getSelectedIndex() == 2:
                self.change_encoding = True
                self.working = False
                self.exit()
            
    def up(self):
        if not self.working:
            self["menu"].up()

    def down(self):
        if not self.working:
            self["menu"].down()
            
    def fileChooserCB(self, file=None):
        if file is not None:
            if self.subfile is not None and self.subfile == file:
                pass
            else: 
                self.subfile = file
                self.subdir = os.path.split(self.subfile)[0]
                self["info_subfile"].setText(os.path.split(self.subfile)[1].encode('utf-8'))
                self["enc_sub"].setText("")
                self["enc_subfile"].setText("")
        self.working = False
            
    def subsSetupCB(self, changed=False, changedEncodingGroup=False):
        if changed:
            self.changed_settings = True
        if changedEncodingGroup:
            self.change_encoding = True
        self.working = False
        
    def exit(self):
        if not self.working:
            self.close(self.subfile, self.changed_settings, self.change_encoding)     


class SubsSetup(Screen, ConfigListScreen):
    skin = """
            <screen position="center,center" size="610,435" >
                <widget name="key_red" position="10,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_green" position="160,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_yellow" position="310,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" shadowOffset="-2,-2" shadowColor="black" />
                <widget name="key_blue" position="460,5" zPosition="1" size="140,45" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" shadowOffset="-2,-2" shadowColor="black" />
                <eLabel position="-1,55" size="612,1" backgroundColor="#999999" />
                <widget name="config" position="0,75" size="610,360" scrollbarMode="showOnDemand" />
            </screen>"""

    
    def __init__(self, session):
        Screen.__init__(self, session)

        self.onChangedEntry = [ ]
        self.list = [ ]
        self.currentEncodingGroup = subtitles_settings.encodingsGroup.getValue()
        ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)
        self.setup_title = _("Subtitles setting")
        
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "green": self.keySave,
                "ok": self.keyOk,
                "red": self.keyCancel,
            }, -2)

        self["key_green"] = Label(_("Save"))
        self["key_red"] = Label(_("Cancel"))
        self["key_blue"] = Label("")
        self["key_yellow"] = Label("")
        
        self.buildMenu()
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_("Subtitles setting"))

    def buildMenu(self):
        del self.list[:]       
        self.list.append(getConfigListEntry(_("Show subtitles"), subtitles_settings.showSubtitles))
        self.list.append(getConfigListEntry(_("Font type"), subtitles_settings.fontType))
        self.list.append(getConfigListEntry(_("Font size"), subtitles_settings.fontSize))
        self.list.append(getConfigListEntry(_("Position"), subtitles_settings.position))                                                 
        self.list.append(getConfigListEntry(_("Color"), subtitles_settings.color))
        self.list.append(getConfigListEntry(_("Encoding"), subtitles_settings.encodingsGroup))
        self["config"].list = self.list
        self["config"].setList(self.list)

    def keyOk(self):
        current = self["config"].getCurrent()[1]
        pass
    
    def keySave(self):
        for x in self["config"].list:
            x[1].save()
        configfile.save()
        if self.currentEncodingGroup != subtitles_settings.encodingsGroup.getValue():
            self.close(True, True)
        self.close(True, False)

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close(False, False)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)  

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()



def FileEntryComponent(name, absolute=None, isDir=False):
        res = [ (absolute, isDir) ]
        res.append((eListboxPythonMultiContent.TYPE_TEXT, 35, 1, 470, 20, 0, RT_HALIGN_LEFT, name))
        if isDir:
            png = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "extensions/directory.png"))
        else:
            png = LoadPixmap(resolveFilename(SCOPE_PLUGINS, 'Extensions/MediaPlayer2/subtitles.png'))
        if png is not None:
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 10, 2, 20, 20, png))
        return res
    


class SubFileList(FileList):
    def __init__(self, defaultDir):
        FileList.__init__(self, defaultDir, matchingPattern="(?i)^.*\.(srt)", useServiceRef=False)
        
    def changeDir(self, directory, select=None):
        self.list = []
        # if we are just entering from the list of mount points:
        if self.current_directory is None:
            if directory and self.showMountpoints:
                self.current_mountpoint = self.getMountpointLink(directory)
            else:
                self.current_mountpoint = None
        self.current_directory = directory
        directories = []
        files = []

        if directory is None and self.showMountpoints: # present available mountpoints
            for p in harddiskmanager.getMountedPartitions():
                path = os_path.join(p.mountpoint, "")
                if path not in self.inhibitMounts and not self.inParentDirs(path, self.inhibitDirs):
                    self.list.append(FileEntryComponent(name=p.description, absolute=path, isDir=True))
            files = [ ]
            directories = [ ]
        elif directory is None:
            files = [ ]
            directories = [ ]
        elif self.useServiceRef:
            root = eServiceReference("2:0:1:0:0:0:0:0:0:0:" + directory)
            if self.additional_extensions:
                root.setName(self.additional_extensions)
            serviceHandler = eServiceCenter.getInstance()
            list = serviceHandler.list(root)

            while 1:
                s = list.getNext()
                if not s.valid():
                    del list
                    break
                if s.flags & s.mustDescent:
                    directories.append(s.getPath())
                else:
                    files.append(s)
            directories.sort()
            files.sort()
        else:
            if os_path.exists(directory):
                files = listdir(directory)
                files.sort()
                tmpfiles = files[:]
                for x in tmpfiles:
                    if os_path.isdir(directory + x):
                        directories.append(directory + x + "/")
                        files.remove(x)

        if directory is not None and self.showDirectories and not self.isTop:
            if directory == self.current_mountpoint and self.showMountpoints:
                self.list.append(FileEntryComponent(name="<" + _("List of Storage Devices") + ">", absolute=None, isDir=True))
            elif (directory != "/") and not (self.inhibitMounts and self.getMountpoint(directory) in self.inhibitMounts):
                self.list.append(FileEntryComponent(name="<" + _("Parent Directory") + ">", absolute='/'.join(directory.split('/')[:-2]) + '/', isDir=True))

        if self.showDirectories:
            for x in directories:
                if not (self.inhibitMounts and self.getMountpoint(x) in self.inhibitMounts) and not self.inParentDirs(x, self.inhibitDirs):
                    name = x.split('/')[-2]
                    self.list.append(FileEntryComponent(name=name, absolute=x, isDir=True))

        if self.showFiles:
            for x in files:
                if self.useServiceRef:
                    path = x.getPath()
                    name = path.split('/')[-1]
                else:
                    path = directory + x
                    name = x

                if (self.matchingPattern is None) or re_compile(self.matchingPattern).search(path):
                    self.list.append(FileEntryComponent(name=name, absolute=x , isDir=False))

        self.l.setList(self.list)

        if select is not None:
            i = 0
            self.moveToIndex(0)
            for x in self.list:
                p = x[0][0]
                
                if isinstance(p, eServiceReference):
                    p = p.getPath()
                
                if p == select:
                    self.moveToIndex(i)
                i += 1
    
class SubsFileChooser(Screen):
    skin = """
        <screen position="center,center" size="610,435" >
            <widget name="filelist" position="0,55" size="610,350" scrollbarMode="showOnDemand" />
        </screen>
        """
            
    def __init__(self, session, subdir=None):
        Screen.__init__(self, session)
        self.session = session
        defaultDir = subdir + '/'
        print '[SubsFileChooser] defaultdir', defaultDir
        self.filelist = SubFileList(defaultDir)
        self["filelist"] = self.filelist
        
        self["actions"] = NumberActionMap(["OkCancelActions", "DirectionActions"],
            {
                "ok": self.okClicked,
                "cancel": self.close,
                "up": self.up,
                "down": self.down,
            }, -2)    
        
        self.onLayoutFinish.append(self.layoutFinished)
        
    def layoutFinished(self):
        self.setTitle(_("Choose Subtitles"))
        
    def okClicked(self):
        if self.filelist.canDescent():
            self.filelist.descent()
        else:
            filePath = os.path.join(self.filelist.current_directory, self.filelist.getFilename())
            print '[SubsFileChooser]' , filePath 
            self.close(filePath)
            
    def up(self):
        self['filelist'].up()

    def down(self):
        self['filelist'].down()


class SubProcessPath(object):
    def __init__(self, subfile, encodings, current_encoding=None):
        self.subfile = subfile
        
        self.text = None
        self.encoding = None
        self.encodings = encodings
        self.current_encoding = current_encoding
        
        if subfile[0:4] == 'http':
            try:
                text = self.request(subfile)
            except Exception:
                print "[Subtitles] cannot download subtitles %s" % subfile
                
            self.text, self.encoding = self.decode(text) 
        else:
            try:
                f = open(subfile, 'r')
            except IOError:
                print '[srtParser] cannot open subtitle file %s' % subfile
                self.text = None
            else:
                text = f.read()
                f.close()
                self.text, self.encoding = self.decode(text)
                      
    
    def decode(self, text):
        utext = None
        used_encoding = None
        idx = 0
        if self.current_encoding is not None:
            idx = self.encodings.index(self.current_encoding)
        for enc in self.encodings[idx:]:
            #trying another encodings
            if self.current_encoding is not None and enc == self.current_encoding:
                continue
            try:
                utext = text.decode(enc)
                used_encoding = enc
                break
            except Exception:
                if enc == self.encodings[-1]:
                    if self.current_encoding is not None:
                        utext = text.decode(self.current_encoding)
                        used_encoding = self.current_encoding   
                    print '[Subtitles] cannot decode file'
                continue
        return utext, used_encoding
    
    
    def request(self, url):
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        data = response.read()
        response.close()
        return data   
            
        
class SubStyler(object):
    def __init__(self, subDict):
        self.subDict = subDict
        self.addStyle()

        
    def removeTags(self, text):
        text = text.replace('<i>', '')
        text = text.replace('</i>', '')
        text = text.replace('<I>', '')
        text = text.replace('</I>', '')
        text = text.replace('<b>', '')
        text = text.replace('</b>', '')
        text = text.replace('<B>', '')
        text = text.replace('</B>', '')
        text = text.replace('<u>', '')
        text = text.replace('</u>', '')
        text = text.replace('<U>', '')
        text = text.replace('</U>', '')
        return text
        
            
    def addStyle(self):
        """adds style to subtitles using tags"""  
        for sub in self.subDict:
            sub['style'] = 'regular'
            if sub['text'].find('<i>') != -1 or sub['text'].find('<I>') != -1:
                sub['style'] = 'italic'
                sub['text'] = self.removeTags(sub['text'])
            
            elif sub['text'].find('<b>') != -1 or sub['text'].find('<B>') != -1:
                sub['style'] = 'bold'
                sub['text'] = self.removeTags(sub['text'])
                
            elif sub['text'].find('<u>') != -1 or sub['text'].find('<U>') != -1:
                sub['style'] = 'regular'
                sub['text'] = self.removeTags(sub['text'])
                
                

class Parser():
    def __init__(self, text):
        self.text = text
        self.subdict = None
        
    def parse(self):
        pass
            

class srtParser(Parser):

    def parse(self):
        try:
            self.subdict = self.srt_to_dict(self.text)
        except Exception:
            print '[srtParser] cannot load srt subtitles'
            self.subdict = None
        return self.subdict
        
        
       
    def srt_time_to_pts(self, time):
        split_time = time.split(',')
        major, minor = (split_time[0].split(':'), split_time[1])
        return long((int(major[0]) * 3600 + int(major[1]) * 60 + int(major[2])) * 1000 + int(minor)) * 90

    def srt_to_dict(self, srtText):
        subs = []
        for s in re.sub('\s*\n\n\n*', '\n\n', re.sub('\r\n', '\n', srtText)).split('\n\n'):
            st = s.split('\n')
            if len(st) >= 3:
                split = st[1].split(' --> ')
                startTime = self.srt_time_to_pts(split[0].strip())
                endTime = self.srt_time_to_pts(split[1].strip())
                subs.append({'start': startTime,
                             'end': endTime,
                             'duration': (endTime - startTime) / 90,
                             'text': '\n'.join(j for j in st[2:len(st)])
                            })
        return subs


