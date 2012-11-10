import  mimetypes, sys, urllib2, re
import md5
import htmlentitydefs
import os.path
import imp
import traceback
from xml.etree.cElementTree import ElementTree, fromstring
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


def load_xml_string(xml_string):
    try:
        root = fromstring(xml_string)
    except Exception, er:
        print "cannot parse xml string", er
        raise
    else:
        return root
        

def load_xml(xml_file):
    xml = None
    try:
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
    except IOError, e:
        print "I/O error(%d): %s" % (e.errno, e.strerror)
        pass
    finally:
        if xml:xml.close()
        
    
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
    if isinstance(string,unicode):
        return string    
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
    

def make_path(p):
    '''Makes sure directory components of p exist.'''
    try:
        os.makedirs(p)
    except OSError:
        pass
    
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None
            

def download_to_file(remote, local, mode='wb', debugfnc=None):
    try:
        if debugfnc:
            debugfnc("downloading %s to %s" % (remote, local))
        else:
            print  "downloading %s to %s" % (remote, local) 
        f = urllib2.urlopen(remote)
        make_path(os.path.dirname(local))
        localFile = open(local, mode)
        localFile.write(f.read())
    except urllib2.HTTPError, e:
        if debugfnc:
            debugfnc("HTTP Error: %s %s" % (e.code, remote))
        else:
            print "HTTP Error: %s %s" % (e.code, remote)
        raise
    except urllib2.URLError, e:
        if debugfnc:
            debugfnc("URL Error: %s %s" % (e.reason, remote))
        else:
            print "URL Error: %s %s" % (e.reason, remote)
        raise
    except IOError, e:
        if debugfnc:
            debugfnc("I/O error(%d): %s" % (e.errno, e.strerror))
        else:
            print "I/O error(%d): %s" % (e.errno, e.strerror)
        raise
    else:
        if debugfnc:
            debugfnc('%s succesfully downloaded' % local)
        else:
            print local, 'succesfully downloaded'
    finally:
        if f:f.close()
        if localFile:localFile.close()            


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

def unescapeHTML(s):
    """
    @param s a string (of type unicode)
    """
    assert type(s) == type(u'')

    result = re.sub(ur'(?u)&(.+?);', htmlentity_transform, s)
    return result

def clean_html(html):
    """Clean an HTML snippet into a readable string"""
    # Newline vs <br />
    html = html.replace('\n', ' ')
    html = re.sub('\s*<\s*br\s*/?\s*>\s*', '\n', html)
    # Strip html tags
    html = re.sub('<.*?>', '', html)
    # Replace html entities
    html = unescapeHTML(html)
    return html

def encodeFilename(s):
    """
    @param s The name of the file (of type unicode)
    """

    assert type(s) == type(u'')

    if sys.platform == 'win32' and sys.getwindowsversion()[0] >= 5:
        # Pass u'' directly to use Unicode APIs on Windows 2000 and up
        # (Detecting Windows NT 4 is tricky because 'major >= 4' would
        # match Windows 9x series as well. Besides, NT 4 is obsolete.)
        return s
    else:
        return s.encode(sys.getfilesystemencoding(), 'ignore')

def sanitize_filename(s):
    """Sanitizes a string so it could be used as part of a filename."""
    def replace_insane(char):
        if char == '?' or ord(char) < 32 or ord(char) == 127:
            return ''
        elif char == '"':
            return '\''
        elif char == ':':
            return ' -'
        elif char in '\\/|*<>':
            return '-'
        return char

    result = u''.join(map(replace_insane, s))
    while '--' in result:
        result = result.replace('--', '-')
    return result.strip('-')

def htmlentity_transform(matchobj):
    """Transforms an HTML entity to a Unicode character.

    This function receives a match object and is intended to be used with
    the re.sub() function.
    """
    entity = matchobj.group(1)

    # Known non-numeric HTML entity
    if entity in htmlentitydefs.name2codepoint:
        return unichr(htmlentitydefs.name2codepoint[entity])

    # Unicode character
    mobj = re.match(ur'(?u)#(x?\d+)', entity)
    if mobj is not None:
        numstr = mobj.group(1)
        if numstr.startswith(u'x'):
            base = 16
            numstr = u'0%s' % numstr
        else:
            base = 10
        return unichr(long(numstr, base))

    # Unknown entity in name, return its literal representation
    return (u'&%s;' % entity)



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
