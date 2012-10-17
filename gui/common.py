'''
Created on 22.5.2012

@author: marko
'''
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard

from Components.Sources.List import List
from Components.Label import Label, MultiColorLabel, LabelConditional
from Components.Pixmap import Pixmap
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, pathExists, fileExists
from Plugins.Extensions.archivCZSK.resources.tools.task import callFromThread
from captcha import Captcha
import twisted.internet.defer as defer

from enigma import loadPNG, RT_HALIGN_RIGHT, RT_VALIGN_TOP, eSize, eListbox, ePoint, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListboxPythonMultiContent, gFont, getDesktop, ePicLoad, eServiceCenter, iServiceInformation, eServiceReference, iSeekableService, iPlayableService, iPlayableServicePtr, eTimer


PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/"
PNG_PATH = PLUGIN_PATH + 'gui/icon/'

class PanelList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setItemHeight(26)
        self.l.setFont(0, gFont("Regular", 21))
            
def PanelListEntryHD(name, idx, png=''):
    res = [(name)]
    if fileExists(png):
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(35, 25), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(60, 5), size=(950, 30), font=0, flags=RT_VALIGN_TOP, text=name))
    else:
        res.append(MultiContentEntryText(pos=(5, 5), size=(950, 30), font=0, flags=RT_VALIGN_TOP, text=name))
    return res 

def PanelListEntrySD(name, idx, png=''):
    res = [(name)]
    if fileExists(png):
        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 5), size=(35, 25), png=loadPNG(png)))
        res.append(MultiContentEntryText(pos=(60, 5), size=(550, 30), font=0, flags=RT_VALIGN_TOP, text=name))
    else:
        res.append(MultiContentEntryText(pos=(5, 5), size=(330, 30), font=0, flags=RT_VALIGN_TOP, text=name))
    return res 


class MyConditionalLabel(LabelConditional):
    def __init__(self, text, conditionalFunction):
        LabelConditional.__init__(self, text, withTimer=False)
        self.conditionalFunction = conditionalFunction
        

class TipBar():
    def __init__(self, tip_list=[], startOnShown=False, tip_timer_refresh=10):
        
        self["tip_pixmap"] = Pixmap()
        self["tip_label"] = Label("")
        
        self.tip_list = tip_list
        self.tip_selection = 0
        self.tip_timer_refresh = tip_timer_refresh * 1000
        self.tip_timer = eTimer()
        self.tip_timer_running = False
        self.tip_timer.callback.append(self.changeTip)
        if startOnShown:
            self.onExecBegin.append(self.startTipTimer)
            
        self.onStartWork.append(self.start)
        self.onStopWork.append(self.stop)
        
        self.onClose.append(self.__exit)
        
    def updateTipList(self, tip_list):
        self.tip_list = tip_list
        
    def changeTip(self):
        print "[ArchivCZSK] tip_timer tick"
        if len(self.tip_list) > 0:
            if self.tip_selection + 1 >= len(self.tip_list):
                self.tip_selection = 0
            else: 
                self.tip_selection += 1
            self["tip_pixmap"].instance.setPixmap(self.tip_list[self.tip_selection][0])
            self["tip_label"].setText(self.tip_list[self.tip_selection][1])
        else:
            self["tip_pixmap"].instance.setPixmap(None)
            self["tip_label"].setText("")
            
            
    def stop(self):
        self["tip_pixmap"].hide()
        self["tip_label"].hide()
        self.stopTipTimer()
        
    def start(self):
        self["tip_pixmap"].show()
        self["tip_label"].show()
        self.startTipTimer()
        
    def startTipTimer(self):
        if not self.tip_timer_running:
            self.tip_timer.start(self.tip_timer_refresh)
            self.tip_timer_running = True
        
    def stopTipTimer(self):
        if self.tip_timer_running:
            self.tip_timer.stop()
            self.tip_timer_running = False
            
    def __exit(self):
        self.stopTipTimer()
        del self.tip_timer


class LoadingScreen(Screen):
    skin = """
        <screen position="center,center" size="76,76" flags="wfNoBorder" backgroundColor="background" >
        <eLabel position="2,2" zPosition="1" size="72,72" font="Regular;18" backgroundColor="background"/>
        <widget name="spinner" position="14,14" zPosition="2" size="48,48" alphatest="on" transparent="1" />
        </screen>"""

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)

        self["spinner"] = Pixmap()
        self.curr = 0
        self.__shown = False

        self.timer = eTimer()
        self.timer.callback.append(self.showNextSpinner)

    def start(self):
        self.__shown = True
        self.show()
        self.timer.start(200, False)

    def stop(self):
        self.hide()
        self.timer.stop()
        self.__shown = False

    def isShown(self):
        return self.__shown

    def showNextSpinner(self):
        self.curr += 1
        if self.curr > 10:
            self.curr = 0
        png = LoadPixmap(cached=True, path=PNG_PATH + str(self.curr) + ".png")
        self["spinner"].instance.setPixmap(png)

   
