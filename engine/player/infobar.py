'''
Created on 25.9.2012

@author: marko
'''
from Components.ProgressBar import ProgressBar
from Components.Label import Label
from Components.config import config
from Plugins.Extensions.archivCZSK import _

def debug(data):
    if config.plugins.archivCZSK.debug.getValue():
        print '[ArchivCZSK] Infobar:', data.encode('utf-8')

class CustomPlayerInfobar(object):
    def __init__(self):
        self["buffer_slider"] = ProgressBar()
        self["buffer_percent"] = Label(_("N/A"))
        self["buffer_label"] = Label("Buffer")
        self["download_label"] = Label(_("Speed"))
        self["download_speed"] = Label(_("N/A"))
        self.onFirstExecBegin.append(self.resetBufferSlider) 
        #self.onExecBegin.append(self.resetBufferSlider)
        
    def resetBufferSlider(self):
        debug("reseting buffer slider")
        self["buffer_slider"].setValue(0)    
        
    def setBufferSliderRange(self, video_length):
        debug('setting buffer slider range to 0-%lu' % video_length)
        
        #doesnt work
        self.bufferSlider.setRange([(0), (video_length)])
        
        
    def BtoKB(self, byte):
        return int(float(byte) / float(1024))
    
    def BtoMB(self, byte):
        return int(float(byte) / float(1024 * 1024))
        
    def updateInfobar(self, downloading=False, download_speed=0, buffering=False, buffered_length=0, buffer_percent=0):
            print self["buffer_slider"].getRange(), self["buffer_slider"].getValue()
            debug("buffering: %s buffered %d buffered_video_length %lu downloading %s download_speed %lu" % \
               (str(buffering), buffer_percent, buffered_length, str(downloading), download_speed))
            if downloading:
                self["download_label"].setText(_("Downloading"))
                self["download_speed"].setText("%d KB/s" % self.BtoKB(download_speed))
                buff = int(float(buffered_length) / float(self.video_length) * 100)
                self["buffer_slider"].setValue(buff)
            else:
                self["download_label"].setText("")
                self["download_speed"].setText("")
    
            self["buffer_percent"].setText("%s %%" % buffer_percent)
