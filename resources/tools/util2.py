import os, mimetypes, sys, traceback, urllib2, urlparse, re
import md5
import os.path
import imp
import traceback
from xml.etree.cElementTree import ElementTree
from htmlentitydefs import name2codepoint as n2cp
supported_video_extensions = ('.avi', '.mp4', '.mkv', '.mpeg', '.mpg')





def load_module(code_path):
    try:
        try:
            code_dir = os.path.dirname(code_path)
            code_file = os.path.basename(code_path)

            fin = open(code_path, 'rb')

            return  imp.load_source(md5.new(code_path).hexdigest(), code_path, fin)
        finally:
            try: fin.close()
            except: pass
    except ImportError, x:
        traceback.print_exc(file=sys.stderr)
        raise
    except:
        traceback.print_exc(file=sys.stderr)
        raise

def load_xml(xml_file):
    el = ElementTree()
    try:
        el.parse(xml_file)
    except IOError, e:
        print "cannot load %s file I/O error(%d): %s" % (xml_file, e.errno, e.strerror)
        return None
    else:
        return el
    
#source from xbmc_doplnky
def decode_html(data):
    try:
        if not type(data) == unicode:
            data = unicode(data, 'utf-8', errors='ignore')
            entity_re = re.compile(r'&(#?)(x?)(\w+);')
            return entity_re.subn(_substitute_entity, data)[0]
    except:
        traceback.print_exc()
        print [data]
        return data

#source from xbmc_doplnky 
def _substitute_entity(match):
        ent = match.group(3)
        if match.group(1) == '#':
            # decoding by number
            if match.group(2) == '':
                # number is in decimal
                return unichr(int(ent))
            elif match.group(2) == 'x':
                # number is in hex
                return unichr(int('0x'+ent, 16))
        else:
            # they were using a name
            cp = n2cp.get(ent)
            if cp: return unichr(cp)
            else: return match.group()
        


def isSupportedVideo(url):
    if url.startswith('rtmp'):
        return True
    if os.path.splitext(url)[1] != '':
        if os.path.splitext(url)[1] in supported_video_extensions:
            return True
        else:
            return False
    else:
        req = urllib2.Request(url)
        resp = urllib2.urlopen(req)
        exttype = resp.info().get('Content-Type')
        resp.close()
        ext = mimetypes.guess_extension(exttype)
        if ext in supported_video_extensions:
            return True
        else:
            return False
    return False


def BtoKB(self, byte):
        return int(float(byte) / float(1024))
    
def BtoMB(self, byte):
        return int(float(byte) / float(1024 * 1024))
    
def sToHMS(self, sec):
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return h, m, s
 

search = [_('Search'), _('New search')]  




