'''
Created on 25.6.2012

@author: marko
'''

from xml.etree.cElementTree import ElementTree
import urllib2
import os, shutil

from Components.config import config

from tools import unzip, util, parser
from Plugins.Extensions.archivCZSK import settings
from exceptions import archiveException as archiveException

GUI_CB = None

def debug(text):
    text = '[archivCZSK [update] ] %s' % text
    if GUI_CB is not None:
        GUI_CB(text)
    if config.plugins.archivCZSK.debug.value:
        print text
    
def removePyOC(pyfile):
    if os.path.isfile(pyfile + 'c'):
        debug('removing %s' % (pyfile + 'c'))
        os.remove(pyfile + 'c')
    elif os.path.isfile(pyfile + 'o'):
        debug('removing %s' % (pyfile + 'o'))
        os.remove(pyfile + 'o')

def removeFiles(files):
    for f in files:
        if os.path.isfile(f):
            os.remove(f) 
                     
def download(remote, local):
    try:
        f = urllib2.urlopen(remote, timeout=15)
        debug("downloading " + remote) 
    except urllib2.HTTPError, e:
        debug("HTTP Error: %s %s" % (e.code, remote))
        raise
    except urllib2.URLError, e:
        debug("URL Error: %s %s" % (e.reason, remote))
        raise
    except IOError, e:
        debug("I/O error(%d): %s" % (e.errno, e.strerror))
        raise
    else:
        debug(local + ' succesfully downloaded')
        return f
    
    
class Updater(object):
    """Updater for updating addons in repository, every repository has its own updater"""
    
    def __init__(self, repository):
        self.repository = repository
        self.update_xml = None
        self.update_xml_url = repository.update_xml_url
        self.remote_addons_dict = {}
        
        self.tmp_path = os.path.join(settings.TMP_PATH, repository.id)
        self.remote_path = repository.update_datadir_url
        self.local_path = repository.path
        
    def check_addon(self, addon):
        """check if addon needs update"""
        
        self._get_server_addon(addon, reload=True)
        
        remote_version = self.server_addons_dict[addon.id]['version']
        local_version = addon.version
        
        return util.check_version(local_version, remote_version)
          
    def update_addon(self, addon):
        """updates addon"""
        self._get_server_addon(addon)
    
        tmp_base = os.path.join(self.tmp_path, addon.relative_path)
        local_base = os.path.join(self.local_path, addon.relative_path)
        
        zip_file = self._download(addon)
        
        if zip_file and os.path.isfile(zip_file):
            shutil.rmtree(local_base)
            os.makedirs(local_base)
            
            unzipper = unzip.unzip()
            unzipper.extract(zip_file, local_base)
            
            addon._update_needed = False
            return True
        return False
    
    
    def check_addons(self):
        """checks every addon in repository, and update its state accordingly"""
        debug('checking addons')
        update_needed = []
        self._get_server_addons()
        for remote_addon in self.remote_addons_dict.keys():
            if remote_addon['id'] in [addon.id for addon in self.repository.addons]:
                if addon.check_update():
                    update_needed.append(addon)
            else:
                new_archive_addon = DummyAddon(self.repository, self.remote_addon['id'], self.remote_addon['name'], self.remote_addon['version'])
                self.repository.addons.append(new_archive_addon)
                update_needed.append(addon)
        return update_needed        
            
            
    def update_addons(self):
        """update addons in repository, according to their state"""
        debug('updating addons')
        update_success = []
        for addon in self.repository:
            if addon.need_update():
                if addon.update():
                    update_success.append(update_success)
        return update_success
                    
                
                
    def _get_server_addons(self):
        """loads info actual info of addons from remote repository to remote_addons_dict"""
        if self.update_xml is None:
            self._download_update_xml()
            
        pars = parser.XBMCMultiAddonXMLParser(self.update_xml_url)
        self.remote_addons_dict = pars.read_addons()
            

    def _get_server_addon(self, addon, reload=False):
        """load info about addon from remote repository"""
        
        if self.update_xml is None or reload:
            self._download_update_xml()
            
        if addon.id not in self.server_addons_dict:
            pars = parser.XBMCMultiAddonXMLParser(self.update_xml_url)
            addon_el = pars.find_addon(addon.id)
            self.remote_addons_dict[addon.id] = pars.parse(addon_el)
        
    
    def _download(self, addon):
        """downloads addon zipfile to tmp"""
        zip_filename = addon.id + self.remote_addons_dict[addon.id]['version'] + '.zip'
        
        remote_base = self.remote_path + '/' + addon.relative_path 
        tmp_base = os.path.join(self.tmp_path, addon.relative_path)
        
        local_file = os.path.join(tmp_base, zip_filename)
        remote_file = remote_base + '/' + zip_filename
        
        
        if not os.path.isdir(tmp_base):
            os.makedirs(tmp_base) 
        try:
            util.download_to_file(remote_file, local_file)
        except:
            shutil.rmtree(tmp_base)
            return None
        return local_file      
            
            
    def _download_update_xml(self):
        """downloads update xml of repository"""
        try:
            self.update_xml = download(self.update_xml_url)
        except Exception:
            raise archiveException.UpdateXMLVersionException()
        

class DummyAddon(object):
    """to add new addon to repository"""
    def __init__(self, repository, id, name, version):
        self.name = name
        self.id = id
        self.relative_path = '/archive/' + self.id
        self.path = os.path.join(repository.path, self.relative_path)
        self._needed_update = True
        
    def need_update(self):
        return True
    
    def update(self):
        self.repository._updater.update_addon(self)

