# -*- coding: UTF-8 -*-
#################################################################################
#
#    Plugin for Dreambox-Enigma2
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

from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import *
from Screens.Screen import Screen
from Components.Label import Label, MultiColorLabel
from Components.ActionMap import ActionMap, NumberActionMap
from Components.FileList import FileList, EXTENSIONS
from Tools.Directories import SCOPE_SKIN_IMAGE, SCOPE_PLUGINS, resolveFilename
from Components.config import config
from Screens.MessageBox import MessageBox
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Plugins.Extensions.archivCZSK import _

from enigma import  RT_HALIGN_RIGHT, RT_VALIGN_TOP, eSize, ePoint, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont, getDesktop, eServiceCenter, iServiceInformation, eServiceReference, iSeekableService, iPlayableService, iPlayableServicePtr, eTimer
from string import split
from time import sleep
from copy import copy
import re
import sys
import urllib2
import os

#EXTENSIONS['srt'] = 'subtitle.png'

config.plugins.subsSRT = ConfigSubsection()
config.plugins.subsSRT.showSubtitles = ConfigYesNo(default=True)

choicelist = []
for i in range(10, 60, 1):
    choicelist.append(("%d" % i, "%d" % i))
config.plugins.subsSRT.fontSize = ConfigSelection(default="35", choices=choicelist)

choicelist = []
for i in range(0, 101, 2):
    choicelist.append(("%d" % i, "%d" % i))
config.plugins.subsSRT.position = ConfigSelection(default="94", choices=choicelist)

choicelist = []
choicelist.append(("red", _("red")))
choicelist.append(("#00ff00", _("green")))
choicelist.append(("#ff00ff", _("purple")))
choicelist.append(("yellow", _("yellow")))
choicelist.append(("white", _("white")))
choicelist.append(("#00ffff", _("blue")))

config.plugins.subsSRT.color = ConfigSelection(default="white", choices=choicelist)

class PanelList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setItemHeight(35)
        self.l.setFont(0, gFont("Regular", 22))
            
def PanelListEntry(name, idx, png=''):
    res = [(name)]
    res.append(MultiContentEntryText(pos=(5, 5), size=(330, 30), font=0, flags=RT_VALIGN_TOP, text=name))
    return res    


class SubsScreen(Screen):    
    def __init__(self, session):
        desktop = getDesktop(0)
        size = desktop.size()
        sc_width = size.width()
        sc_height = size.height()
        
        position = int(config.plugins.subsSRT.position.value)
        fontSize = int(config.plugins.subsSRT.fontSize.value)
        vSize = fontSize * 3 + 10 # 3 rows + reserve
        color = config.plugins.subsSRT.color.value
        position = int(position * (float(sc_height - vSize) / 100)) 
        
        print position, fontSize, vSize, color
        self.skin = """
            <screen name="SubtitleDisplay" position="0,0" size="%s,%s" zPosition="-1" backgroundColor="transparent" flags="wfNoBorder">
                    <widget name="subtitles" position="0,%s" size="%s,%s" valign="center" halign="center" font="Regular;%s" transparent="1" foregroundColor="%s" shadowColor="#40101010" shadowOffset="3,3" />
            </screen>""" % (str(sc_width), str(sc_height), str(position), str(sc_width), str(vSize), str(fontSize), color)
            
            
        Screen.__init__(self, session)
        self.stand_alone = True
        print 'initializing subtitle display'
        self["subtitles"] = Label("")
        
    def setText(self, text):
        self["subtitles"].setText(text)
    
    def hideText(self):
        self["subtitles"].setText("") 
            
            
            
class Subtitles(object):
    def __init__(self, session, subpath=None):
        self.session = session
        self.subsScreen = None
        self.subsEngine = None
        self.srtsub = None
        self.session = session
        self.loaded = False
        self.subPath = None
        if subpath is not None:
            if not os.path.isfile(subpath):
                self.subPath = subpath
        if self.subPath is not None:
                self.load(self.subPath)
            
    def reset(self):
        if self.loaded:
            self.subsEngine.pause()
            self.subsEngine.exit()
            self.subsEngine = None
            self.session.deleteDialog(self.subsScreen)
            del self.subsScreen
            self.subsScreen = None
            self.subPath = None
        self.loaded = False
    
    def resetSubsScreen(self):
        self.pause()
        self.hideDialog()
        self.session.deleteDialog(self.subsScreen)
        del self.subsScreen
        self.subsScreen = self.session.instantiateDialog(SubsScreen)
        self.subsEngine.subsScreen = self.subsScreen
        self.resume()  
    
    def load(self, filename):
        self.subPath = filename
        srt = srtParser(filename)
        self.srtsub = srt.srtDict
        if self.srtsub is not None:
            self.loaded = True
            self.subsScreen = self.session.instantiateDialog(SubsScreen)
            self.subsEngine = SubsEngine(self.session, self.subsScreen, self.srtsub)
            return True
        else:
            return False
           
    def pause(self):
        if self.loaded:
            print '[Subtitles] pausing subtitles'
            self.subsEngine.pause()
    
    def play(self):
        if self.loaded:
            if config.plugins.subsSRT.showSubtitles.value:
                self.showDialog() 
            else:
                self.hideDialog()
            self.subsEngine.play()
            
    def playAfterRewind(self):
        if self.loaded:
            if config.plugins.subsSRT.showSubtitles.value:
                self.showDialog() 
            else:
                self.hideDialog()
            self.subsEngine.playAfterRewind()
       
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
        self.session.openWithCallback(self.subsMenuCB, SubsMenu, self.subPath)
    
    def subsMenuCB(self, subfile, settings_changed):
        if self.loaded and (self.subPath == subfile) and settings_changed:
                self.resetSubsScreen()
        elif subfile != self.subPath:
            if self.loaded:
                self.reset()
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
        
        del self.srtsub
        self.srtsub = None
        
        config.plugins.subsSRT.showSubtitles.setValue(True)
        config.plugins.subsSRT.showSubtitles.save()
        print '[Subtitles] closing subtitleDisplay'
    
    
    
class SubsEngine(object):

    def __init__(self, session, subsScreen, srtDict):
        self.subsScreen = subsScreen
        self.session = session
        self.srtsub = srtDict
        self.pos = 0
        self.service = None
        self.playPts = None
        self.actsub = None
        self.showSubs = False
        self.timer1 = eTimer()
        self.timer1.callback.append(self.wait)
        self.timer1_running = False
        self.timer2 = eTimer()
        self.timer2.callback.append(self.hide)
        self.timer2_running = False
        
        
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
        self.subsScreen.hideText()
        self.timer1.stop()
        self.timer1_running = False
        self.timer2.stop()
        self.timer2_running = False
                    
    def playAfterRewind(self):
        self.pause()
        ptsBefore = copy(self.playPts)
        self.subsScreen.hideText()
        sleep(1)#pockame pre korektne nacitanie PTS
        #while self.playPts == self.getPlayPts():
        # pass
        self.playPts = self.getPlayPts()
               
        if self.playPts < ptsBefore: #rewind backward
            while self.srtsub[self.pos]['start'] > self.playPts and self.pos > 0:
                self.pos = self.pos - 1
        else: #rewind forward
            while self.srtsub[self.pos]['start'] < self.playPts and self.pos < len(self.srtsub) - 1:
                self.pos = self.pos + 1
        self.play()           
                      
    def show(self):
        self.showSubs = True
        duration = int(self.actsub['duration'])#+self.delay
        self.subsScreen.setText(self.actsub['text'])
        if not self.timer1_running and not self.timer2_running:
            self.timer2.start(duration)
            self.timer2_running = True
            
            
    def hide(self):
        self.timer2.stop()
        self.timer2_running = False
        self.showSubs = False
        self.subsScreen.hideText()
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
    
    def exit(self):
        self.pause()
        del self.timer1
        del self.timer2
        
        
class SubsMenu(Screen):
    skin = """
        <screen position="center,center" size="500,400" title="Main Menu" >
            <widget name="info_sub" position="0,5" size="500,40" valign="center" halign="center" font="Regular;25" transparent="1" foregroundColor="white" />
            <widget name="info_subfile" position="0,55" size="500,40" valign="center" halign="center" font="Regular;25" transparent="1" foregroundColor="#DAA520" />
            <widget name="menu" position="0,105" size="500,295" transparent="1" scrollbarMode="showOnDemand" />
        </screen>"""

    def __init__(self, session, subfile=None):
        Screen.__init__(self, session)
        
        self["menu"] = PanelList([])
        self["info_sub"] = Label(_("Currently choosed subtitles"))
        self["info_subfile"] = Label("")
        if subfile is not None:
            self["info_subfile"].setText(os.path.split(subfile)[1].encode('utf-8'))
        else:
            self["info_subfile"].setText(_("None"))
        
        self.title = _('Subtitles')
        self.lst = [unicode(_('Choose subtitles'), 'utf-8'), unicode(_('Subtitles settings'), 'utf-8')]
        self.subfile = subfile
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
                self.session.openWithCallback(self.fileChooserCB, SubsFileChooser, self.subfile)
            elif self["menu"].getSelectedIndex() == 1:
                self.session.openWithCallback(self.subsSetupCB, SubsSetup)
            
    def up(self):
        if not self.working:
            self.working = True
            self["menu"].up()
            self.working = False

    def down(self):
        if not self.working:
            self.working = True
            self["menu"].down()
            self.working = False
            
    def fileChooserCB(self, file=None):
        if file:
            self.subfile = file
            if self.subfile is not None:
                self["info_subfile"].setText(os.path.split(self.subfile)[1].encode('utf-8'))
            else:
                self["info_subfile"].setText(_("None"))
        self.working = False
            
    def subsSetupCB(self, changed=None):
        if changed:
            self.changed_settings = True
        self.working = False
        
    def exit(self):
        if not self.working:
            self.close(self.subfile, self.changed_settings)     


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
        ConfigListScreen.__init__(self, self.list, session=session, on_change=self.changedEntry)
        self.setup_title = _("Subtitles setting")
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
            {
                "cancel": self.keyCancel,
                "green": self.keySave,
                "blue": self.doNothing,
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
        
    def doNothing(self):
        pass

    def buildMenu(self):
        del self.list[:]       
        self.list.append(getConfigListEntry(_("Show subtitles"), config.plugins.subsSRT.showSubtitles))
        self.list.append(getConfigListEntry(_("Font size"), config.plugins.subsSRT.fontSize))                                    
        self.list.append(getConfigListEntry(_("Position"), config.plugins.subsSRT.position))                                                 
        self.list.append(getConfigListEntry(_("Color"), config.plugins.subsSRT.color))
        self["config"].list = self.list
        self["config"].setList(self.list)

    def keyOk(self):
        current = self["config"].getCurrent()[1]
        pass
    
    def keySave(self):
        for x in self["config"].list:
            x[1].save()
        configfile.save()
        self.close(True)

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close(False)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)  

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()


#def FileEntryComponent(name, absolute=None, isDir=False):
#    res = [ (absolute, isDir) ]
#    res.append((eListboxPythonMultiContent.TYPE_TEXT, 35, 1, 470, 20, 0, RT_HALIGN_LEFT, name))
#    if isDir:
#        png = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, "extensions/directory.png"))
#    else:
#        png = LoadPixmap(resolveFilename(SCOPE_PLUGINS, 'archivCZSK/icon/subtitle.png'))
#    if png is not None:
#        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST, 10, 2, 20, 20, png))
#    return res
    
class SubsFileChooser(Screen):
    skin = """
        <screen position="center,center" size="610,435" >
            <widget name="filelist" position="0,55" size="610,350" scrollbarMode="showOnDemand" />
        </screen>
        """
            
    def __init__(self, session, subFilePath):
        Screen.__init__(self, session)
        self.session = session
        defaultDir = config.plugins.archivCZSK.subtitlesPath.value
        #if subFilePath is not None:
            #if subFilePath[0:4] == 'http' or subFilePath[0:4] == 'rtmp':
                #defaultDir = None
            #else:
                #defaultDir = os.path.split(subFilePath)[0]
        print '[SubsFileChooser] defaultdir', defaultDir
        self.filelist = FileList(defaultDir, matchingPattern="(?i)^.*\.(srt)", useServiceRef=False)
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
        
     

class srtParser(object):
    def __init__(self, subfile):
        
        self.encodings = ('utf-8', 'windows-1250', 'iso-8859-2') #Common Eastern Europe encodings
        
        if subfile[0:4] == 'http':
            self.srtText = self.request(subfile)
            self.srtText = self.encode_utf8(self.srtText)
        else:
            try:
                with open(subfile, 'r') as f:
                    self.srtText = f.read()
                    f.close()
                    self.srtText = self.encode_utf8(self.srtText)
            except Exception:
                print '[srtParser] cannot open subtitle file'
                self.srtDict = None        
        try:
            self.srtDict = self.srt_to_dict(self.srtText)
        except Exception:
            print '[srtParser] cannot load subtitles'
            self.srtDict = None        
      

    def encode_utf8(self, text):
        self.data = None
        for enc in self.encodings:
            try:
                self.data = text.decode(enc)
                break
            except Exception:
                if enc == self.encodings[-1]:
                    print '[srtParser] cannot find file encoding'
                    self.srtDict = None
                continue
        return self.data.encode('utf-8')
    
    def request(self, url):
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        data = response.read()
        response.close()
        return data
       
    def srt_time_to_pts(self, time):
        split_time = time.split(',')
        major, minor = (split_time[0].split(':'), split_time[1])
        return long((int(major[0]) * 3600 + int(major[1]) * 60 + int(major[2])) * 1000 + int(minor)) * 90

    def srt_to_dict(self, srtText):
        subs = []
        for s in re.sub('\n\n\n*', '\n\n', re.sub('\r\n', '\n', srtText)).split('\n\n'):
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
