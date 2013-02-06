'''
Created on 22.12.2012

@author: marko
'''
import os

GSTREAMER_PATH = '/usr/lib/gstreamer-0.10'
EPLAYER2_PATH = '/lib/libeplayer2.so'
EPLAYER3_PATH = '/lib/libeplayer3.so'


class VideoPlayerInfo(object):
    def __init__(self):
        self.type = 'gstreamer'
        self.version = 0
        if os.path.isdir(GSTREAMER_PATH):
            print 'found gstreamer'
            self.type = 'gstreamer'
        elif os.path.isfile(EPLAYER3_PATH):
            print 'found eplayer3'
            self.type = 'eplayer3'
        elif os.path.isfile(EPLAYER2_PATH):
            print 'found eplayer2'
            self.type = 'eplayer2'
            
    def isRTMPSupported(self):
        """
        @return: True if its 100% supported
        @return: None may be supported
        @return: False not supported
        """
        
        if self.type == 'gstreamer':
            rtmplib = os.path.join(GSTREAMER_PATH, 'libgstrtmp.so')
            # flv is very common file container used in rtmp 
            flvlib = os.path.join(GSTREAMER_PATH, 'libgstflv.so')
            if os.path.isfile(rtmplib):
                if os.path.isfile(flvlib):
                    return True
                return None
            
        elif self.type == 'eplayer2':
            # dont know any eplayer2 which supports rtmp
            # also not used anymore so setting to false
            return False
        elif self.type == 'eplayer3':
            rtmplib = '/usr/lib/librtmp.so'
            if os.path.isfile(rtmplib):
                # some older e2 images not support rtmp
                # even if there is this library
                return None
    def getName(self):
        if self.type == 'gstreamer':
            return 'GStreamer'
        if self.type == 'eplayer3':
            return 'EPlayer3'
        if self.type == 'eplayer2':
            return 'Eplayer2'
        
videoPlayerInfo = VideoPlayerInfo()
            
            
