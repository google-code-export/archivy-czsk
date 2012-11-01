import  mimetypes, sys, urllib2, re
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
    xml = open(xml_file, "r+")
    
    # trying to set encoding utf-8 in xml file with not defined encoding
    if 'encoding' not in xml.readline():
        xml.seek(0)
        xml_string = xml.read()
        xml_string = xml_string.decode('utf-8')
        xml.seek(0)
        xml.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        xml.write(xml_string.encode('utf-8'))
        xml.flush()
    xml.close()
    
    el = ElementTree()
    try:
        el.parse(xml_file)
    except IOError, e:
        print "cannot load %s file I/O error(%d): %s" % (xml_file, e.errno, e.strerror)
        raise
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
    
def decode_string(string):    
    encodings = ['utf-8', 'windows-1250', 'iso-8859-2']
    for encoding in encodings:
        try:
            return string.decode(encoding)
        except Exception:
            if encoding == encodings[-1]:
                return u'cannot_decode'
            else:
                continue
            
def check_version(local, remote):
    local = local.split('.')
    remote = remote.split('.')
    if len(local) < len(remote):
        for i in range(len(local)):
            if int(local[i]) == int(remote[i]):
                continue
            return int(local[i]) < int(remote[i])
        return True
    else:
        for i in range(len(remote)):
            if int(local[i]) == int(remote[i]):
                continue
            return int(local[i]) < int(remote[i])
        return False
    
            

def download_to_file(remote, local):
    try:
        f = urllib2.urlopen(remote)
        print  "downloading " + remote 
        localFile = open(local, "w")
        localFile.write(f.read())
        localFile.close()
    except urllib2.HTTPError, e:
        print "HTTP Error: %s %s" % (e.code, remote)
        raise
    except urllib2.URLError, e:
        print "URL Error: %s %s" % (e.reason, remote)
        raise
    except IOError, e:
        print "I/O error(%d): %s" % (e.errno, e.strerror)
        raise
    else:
        print local + ' succesfully downloaded'            


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
                return unichr(int('0x' + ent, 16))
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
    return True


def BtoKB(self, byte):
        return int(float(byte) / float(1024))
    
def BtoMB(self, byte):
        return int(float(byte) / float(1024 * 1024))
    
def sToHMS(self, sec):
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return h, m, s



class Language(object):
    language_map = {
                'en':'English',
                'sk':'Slovak',
                'cz':'Czech',
                }
    @staticmethod
    def get_language_id(language_name):
        revert_langs = dict(map(lambda item: (item[1], item[0]), Language.language_map.items()))
        if language_name in revert_langs:
            return revert_langs[language_name]
        else:
            return None
    
    @staticmethod    
    def get_language_name(language_id):
        if language_id in Language.language_map:
            return Language.language_map[language_id]
        else:
            return None
