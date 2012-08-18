# -*- coding: UTF-8 -*-
'''
Created on 22.4.2012

@author: marko
'''
from Screens.Screen import Screen
from Plugins.Extensions.archivCZSK import _
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import *
from Components.ActionMap import ActionMap
from Components.Label import Label
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.AVSwitch import AVSwitch
from enigma import getDesktop
import os
from Components.config import config
from twisted.web.client import downloadPage, getPage
from enigma import ePicLoad, getDesktop
from Components.Pixmap import Pixmap, MovingPixmap
from Plugins.Extensions.archivCZSK.resources.tools.util import PVideo


class Captcha(object):
    def __init__(self, session, captchaCB, captchaS, wf, prmLD, dest='/tmp/captcha.png'):
        self.session = session
        self.captchaCB = captchaCB
        self.captchaS = captchaS
        self.wf = wf
        self.prmLD = prmLD
        # self.item=item
        link = "http://img.uloz.to/captcha/%s.png" % config.plugins.archivCZSK.archives.movielibrary.captcha_id.value
        downloadPage(link, dest).addCallback(self.downloadCaptchaCallback).addErrback(self.downloadCaptchaError)

    def downloadCaptchaError(self, err):
        print "[Captcha] download captcha error:", err
        return

    def downloadCaptchaCallback(self, txt=""):
        print "[Captcha] downloaded successfully:"
        self.session.openWithCallback(self.captchaTextCallback, CaptchaDialog)

    def captchaTextCallback(self, callback=None):
        if callback is not None and len(callback):
            print 'new Captcha value is', callback
            config.plugins.archivCZSK.archives.movielibrary.captcha_text.setValue(callback)
            config.plugins.archivCZSK.archives.movielibrary.captcha_text.save()
            stream = self.captchaCB[0](self.captchaCB[1], self.captchaCB[2], self.captchaCB[3], self.captchaCB[4], self.captchaCB[5])
            if isinstance(stream, basestring):
                it = PVideo()
                it.name = 'Video'
                it.url = stream
                self.prmLD['lst_items'] = [it]
                self.prmLD['date'] = None
                self.captchaS(self.prmLD)
            else:
                Captcha(self.session, self.captchaCB, self.captchaS, self.wf, self.prmLD)

        else:
            self.wf()


class CaptchaDialog(VirtualKeyBoard):
    def __init__(self, session):
        self.skin = """
            <screen position="center,center" size="1100,600" zPosition="99">
                <widget source="Title" render="Label" position=" 50,12" size="1050, 33" halign="center" font="Regular;30" backgroundColor="background" shadowColor="black" shadowOffset="-3,-3" transparent="1"/>
                <eLabel position=" 20,55" size="1080,1" backgroundColor="white"/>
                <widget name="header" position="100,90" size="900,40" font="Regular;30" transparent="1" noWrap="1" />
                <widget name="text" position="114,164" size="872,50" font="Regular;46" transparent="1" noWrap="1" halign="right" valign="center"/>
                <widget name="list" position="22,272" size="1056,225" selectionDisabled="1" transparent="1"/>
                <widget name="captcha" position="450,65" zPosition="-1" size="175,70"  alphatest="on"/>
                <eLabel position="20,555" size="1060,1" backgroundColor="white" />
            </screen> """
        self.skin3 = """
            <screen position="center,center" size="720,576" zPosition="99">
                <widget source="Title" render="Label" position=" 50,12" size="720, 33" halign="center" font="Regular;30" backgroundColor="background" shadowColor="black" shadowOffset="-3,-3" transparent="1"/>
                <eLabel position=" 20,55" size="720,1" backgroundColor="white"/>
                <widget name="header" position="10,90" size="490,40" font="Regular;30" transparent="1" noWrap="1" />
                <widget name="text" position="10,135" size="710,33" font="Regular;30" transparent="1" noWrap="1" halign="right" valign="center"/>
                <widget name="list" position="10,180" size="710,396" selectionDisabled="1" transparent="1"/>
                <widget name="captcha" position="520,90" zPosition="-1" size="175,70"  alphatest="on"/>
            </screen> """
        self.skin2 = """
            <screen name="VirtualKeyBoard" position="center,center" size="560,440" zPosition="99" title="Virtual KeyBoard">
                <widget name="captcha" position="center,10" zPosition="-1" size="175,70"  alphatest="on"/>
                <ePixmap pixmap="skin_default/vkey_text.png" position="9,125" zPosition="-4" size="542,52" alphatest="on" />
                <widget name="header" position="10,10" size="500,70" font="Regular;20" transparent="1" noWrap="1" />
                <widget name="text" position="12,35" size="536,136" font="Regular;46" transparent="1" noWrap="1" halign="right" />
                <widget name="list" position="10,100" size="540,315" selectionDisabled="1" transparent="1" />
            </screen>"""

        VirtualKeyBoard.__init__(self, session, _('Type text of picture'))
        self["captcha"] = Pixmap()
        self.Scale = AVSwitch().getFramebufferScale()
        self.picPath = '/tmp/captcha.png'
        self.picLoad = ePicLoad()
        self.picLoad.PictureData.get().append(self.decodePicture)
        self.onLayoutFinish.append(self.showPicture)

    def showPicture(self):
        self.picLoad.setPara([self["captcha"].instance.size().width(), self["captcha"].instance.size().height(), self.Scale[0], self.Scale[1], 0, 1, "#002C2C39"])
        self.picLoad.startDecode(self.picPath)

    def decodePicture(self, PicInfo=""):
        ptr = self.picLoad.getData()
        self["captcha"].instance.setPixmap(ptr)

    def showPic(self, picInfo=""):
        ptr = self.picLoad.getData()
        if ptr != None:
            self["captcha"].instance.setPixmap(ptr.__deref__())
            self["captcha"].show()
