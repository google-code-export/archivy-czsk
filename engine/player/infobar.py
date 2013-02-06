'''
Created on 25.9.2012

@author: marko
'''
from Components.ProgressBar import ProgressBar
from Components.Label import Label
from Components.config import config
from Plugins.Extensions.archivCZSK import _

def BtoKB(byte):
    return int(float(byte) / float(1024))
    
def BtoMB(byte):
    return float(float(byte) / float(1024 * 1024))

class ArchivCZSKMoviePlayerInfobar(object):
    def __init__(self):
        self["buffer_slider"] = ProgressBar()
        self["buffer_size_label"] = Label(_("Buffer size"))
        self["buffer_size"] = Label(_("0"))
        self["buffer_label"] = Label("Buffer")
        self["buffer_state"] = Label(_("N/A"))
        self["download_label"] = Label(_("Speed"))
        self["download_speed"] = Label(_("N/A"))
        self["bitrate_label"] = Label(_("Bitrate"))
        self["bitrate"] = Label("")
        self.onFirstExecBegin.append(self.__resetBufferSlider) 
        
    def __resetBufferSlider(self):
        self["buffer_slider"].setValue(0)    
        
    def setBufferSliderRange(self, video_length):
        #doesnt work
        self["buffer_slider"].setRange([(0), (video_length)])
        
    def __updateBufferSecondsLeft(self, seconds, limit=20):
        if seconds <= limit:
            self['buffer_state'].setText("%ss" % seconds)
        else:
            self['buffer_state'].setText(">%ss" % limit)
        
    def __updateBufferPercent(self, percent):
        self['buffer_state'].setText("%s%%" % percent)
        
    def __updateBufferSize(self, size):
        self['buffer_size'].setText("%d KB" % size)
        
    def __updateBufferSlider(self, percent):
        self["buffer_slider"].setValue(percent)
        
    def __updateBitrate(self, value):
        self["bitrate"].setText("%d KB/s" % BtoKB(value))
        
    def __updateDownloadSpeed(self, speed):
        speedKB = BtoKB(speed)
        if speedKB <= 1000 and speedKB > 0:
            self['download_speed'].setText(("%d KB/s" % speedKB))
        elif speedKB > 1000:
            self['download_speed'].setText(("%.2f MB/s" % BtoMB(speed)))
        else:
            self['download_speed'].setText(("%d KB/s" % 0))
        
    def updateInfobar(self, info, bufferStateMode=0, limit=50):
        if bufferStateMode == 0:
            self.__updateBufferPercent(info['buffer_percent'])
        else:
            self.__updateBufferSecondsLeft(info['buffer_secondsleft'], limit)
        self.__updateBufferSize(info['buffer_size'])
        self.__updateDownloadSpeed(info['download_speed'])
        self.__updateBitrate(info['bitrate'])
        self.__updateBufferSlider(info['buffer_slider'])
