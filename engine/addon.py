'''
Created on 21.10.2012

@author: marko
'''
import os, traceback, sys, imp

from Tools.LoadPixmap import LoadPixmap
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigYesNo, ConfigText, configfile, getConfigListEntry

from tools import util, parser
from Plugins.Extensions.archivCZSK import settings
from Plugins.Extensions.archivCZSK.resources.repositories import config as addon_config
from Plugins.Extensions.archivCZSK.gui import menu
from Plugins.Extensions.archivCZSK.gui import info
from Plugins.Extensions.archivCZSK.gui import shortcuts
from Plugins.Extensions.archivCZSK.gui import download
from contentprovider import AddonContentProvider


def debug(text):
    if config.plugins.archivCZSK.debug.value:
        print '[ArchivCZSK] Addon', text.encode('utf-8')


class Addon(object):
    
    def __init__(self, info, repository):
        self.repository = repository
        self.info = info
        
        self.id = info.id
        self.name = info.name
        self.version = info.version
        self.author = info.author
        self.description = info.description
        self.changelog = info.changelog
        self.path = info.path
        self.relative_path = os.path.relpath(self.path, repository.path)
        
        debug("initializing %s" % self)

        self._updater = repository._updater
        self._update_needed = False
        
        # load languages
        self.language = AddonLanguage(self, os.path.join(self.path, self.repository.addon_languages_relpath))
        
        if self.language.has_language(settings.LANGUAGE_SETTINGS_ID):
            self.language.set_language(settings.LANGUAGE_SETTINGS_ID)
        else:
            #fix to use czech language instead of slovak language when slovak is not available
            if settings.LANGUAGE_SETTINGS_ID == 'sk' and self.language.has_language('cs'):
                self.language.set_language('cs')
            else:
                self.language.set_language('en')
        
        # load settings
        self.settings = AddonSettings(self, os.path.join(self.path, self.repository.addon_settings_relpath))
        self.settings.initialize()
        
        # loader to handle addon imports    
        self.loader = AddonLoader(self)
    
    def __repr__(self):
        return "%s(%s %s)" % (self.__class__.__name__, self.name, self.version)
        
    def update_needed(self):
        return self._update_needed
        
    def check_update(self):
        self._update_needed = self._updater.check_version(self)
        
    def update(self):
        if self._update_needed:
            self._updater.update(self)
        else:
            debug("%s is up to date" % self)
            
    
    def get_localized_string(self, id_language):
        return self.language.get_localized_string(id_language)
    
    def get_setting(self, setting):
        try:
            setting = getattr(self.settings.main, '%s' % setting)
        except Exception, e:
            debug('%s cannot retrieve setting %s\nreason %s' % (self,setting, str(e)))
        else:
            return getattr(setting, 'value', setting)
    
    def get_info(self, info):
        try:
            atr = getattr(self.info, '%s' % info)
        except Exception:
            debug("get_info cannot retrieve info")
            return None
        else:
            return atr
        
    def open_settings(self, session, cb=None):
        menu.openAddonMenu(session, self, cb)
        
    def open_changelog(self, session):
        info.showChangelog(session, self.name, self.changelog)
        
        
    def include(self):
        self.loader.add_importer()
        
    def deinclude(self):
        self.loader.remove_importer()
        
        
        
class XBMCAddon(Addon):
    def getLocalizedString(self,id_language):
        return self.get_localized_string(id_language)
    
    def getAddonInfo(self,inf):
        return self.get_info(info)
    
    def getSetting(self,setting):
            val= self.get_setting(setting)
            if isinstance(val,bool):
                if val:
                    return 'false'
                else:
                    return 'true'
            return val
        
        
                 
class ToolsAddon(Addon):
    def __init__(self, info, repository):
        Addon.__init__(self, info, repository)
        self.library = self.info.library
        debug('%s successfully loaded' % self)
        
        lib_path = os.path.join(self.path, self.library)
        self.loader.add_path(lib_path)

class VideoAddon(Addon):
        
    def __init__(self, info, repository):
        Addon.__init__(self, info, repository)
        self.script = info.script
        self.requires = info.requires
        if self.script == '':
            raise Exception("'%s entry point missing in addon.xml' % self")
        # content provider
        downloads_path = os.path.join(config.plugins.archivCZSK.downloadsPath.value, self.id)
        shortcuts_path = os.path.join(config.plugins.archivCZSK.dataPath.value,self.id)
        self.provider = AddonContentProvider(self, downloads_path,shortcuts_path)
            
        debug('%s successfully loaded' % self)
    
  
    def open_shortcuts(self, session, cb):
        shortcuts.openShortcuts(session, self, cb)
        
    def open_downloads(self, session, cb):
        download.openAddonDownloads(session, self, cb)

        

class AddonLanguage(object):
    """Loading xml language file"""
    
    language_map = {
                    'en':'English',
                    'sk':'Slovak',
                    'cs':'Czech',
                    }

    def __init__(self, addon, languages_dir):
        
        self.addon = addon
        self._language_filename = 'strings.xml'
        self.current_language = {}
        self.default_language_id = 'en'
        self.current_language_id = 'en'
        self.languages = {}
        debug("initializing languages of %s" % addon)
        
        if not os.path.isdir(languages_dir):
            debug("%s cannot load languages, missing %s directory" % (self, os.path.basename(languages_dir)))
            return
    
        for language_dir in os.listdir(languages_dir):
            language_id = self.get_language_id(language_dir)
            if language_id is None:
                debug("%s unknown language %s, you need to update Language map to use it" % self, language_dir)
                debug("skipping language %s" % language_dir)
                continue
            language_dir_path = os.path.join(languages_dir, language_dir)
            language_file_path = os.path.join(language_dir_path, self._language_filename)
            if os.path.isfile(language_file_path):
                try:
                    el = util.load_xml(language_file_path)
                except Exception:
                    debug("skipping language %s" % language_dir)
                else:
                    language = {}
                    strings = el.getroot()
                    for string in strings.findall('string'):
                        string_id = int(string.attrib.get('id'))
                        text = string.text
                        language[string_id] = text
                    self.languages[language_id] = language
                    debug("%s language %s was successfully loaded" % (self, language_dir))
                    el = None
            else:
                debug("%s cannot find language file %s" % (self, language_file_path))
                debug("skipping language %s" % language_dir)
                
    def __repr__(self):
        return "%s Language" % self.addon
                  
    def get_language_id(self, language_name):
        revert_langs = dict(map(lambda item: (item[1], item[0]), self.language_map.items()))
        if language_name in revert_langs:
            return revert_langs[language_name]
        else:
            return None
        
    def get_language_name(self, language_id):
        if language_id in self.language_map:
            return self.language_map[language_id]
        else:
            return None

    def get_localized_string(self, string_id):
        if string_id in self.current_language:
            return self.current_language[string_id]
        else:
            debug("%s cannot find language id %s in %s language of %s\n returning id of language" % (self, string_id, self.current_language_id))
            return str(string_id)
        
    
    def has_language(self, language_id):
        return language_id in self.languages   
        
    def set_language(self, language_id):
        if self.has_language(language_id):
            debug("setting current language %s to %s" % (self.current_language_id, language_id))
            self.current_language_id = language_id
            self.current_language = self.languages[language_id]
        else:
            debug("%s cannot set language %s, language is not available" % (self, language_id))
            
    def get_language(self):
        return self.current_language_id
                    
     
     
class AddonSettings(object):
    
    def __init__(self, addon, settings_file):
        debug("initializing settings of addon %s" % addon.name)
        setattr(config.plugins.archivCZSK.archives, addon.id, ConfigSubsection())
        self.main = getattr(config.plugins.archivCZSK.archives, addon.id)
        addon_config.add_global_addon_settings(self.main)
        
        self.addon = addon
        self.entries = []
        self.categories = []
        try:
            el = util.load_xml(settings_file)
        except Exception:
            debug("cannot load %s"%self)
            el=None
        if el is not None:
            settings = el.getroot()
            main_category = {'label':'general', 'subentries':[]}
            
            for category in settings.findall('category'):
                entry = {'label':category.attrib.get('label'), 'subentries':[]}
                for setting in category.findall('setting'):
                    entry['subentries'].append(self.get_setting_entry(setting))
                self.entries.append(entry)
                
            for setting in settings.findall('setting'):
                main_category['subentries'].append(self.get_setting_entry(setting))
            
            self.entries.append(main_category)
            el = None
            
    def __repr__(self):
        return "%s Settings" % self.addon
            
    
    def initialize(self):
        for entry in self.entries:
            if entry['label'] == 'general': 
                if len(entry['subentries']) == 0 :
                    continue
                else:
                    category = {'label':'general', 'subentries':[]}
            else:
                category = {'label':self.get_label(entry['label']), 'subentries':[]}
                
            for subentry in entry['subentries']:
                self.initialize_entry(self.main, subentry)
                category['subentries'].append(getConfigListEntry(self.get_label(subentry['label']).encode('utf-8'), subentry['setting_id']))
            debug("initialized category %s" % str(category))
            self.categories.append(category)                                      

                            
    def get_configlist_categories(self):
        return self.categories
             
       
    def get_setting_entry(self, setting):
        entry = {}
        entry['label'] = setting.attrib.get('label')
        entry['id'] = setting.attrib.get('id')
        entry['type'] = setting.attrib.get('type')
        entry['default'] = setting.attrib.get('default')
        if entry['type'] == 'enum':
            entry['lvalues'] = setting.attrib.get('lvalues')
        if entry['type'] == 'labelenum':
            entry['values'] = setting.attrib.get('values')
            
        debug("getting entry from xml %s" % str(entry))
        return entry
    
    def get_label(self, label):
        debug('resolving label: %s' % label)
        try:
            string_id = int(label)
        except ValueError:
            debug("isstring")
            if isinstance(label, unicode):
                debug("isunicode %s" % label)
                return label
            else:
                label = util.decode_string(label)
                debug('decoded label: %s' % label)
                return label
        else:
            label = self.addon.get_localized_string(string_id)
            return label
            
    
    def initialize_entry(self, setting, entry):
        if entry['type'] == 'bool':
            setattr(setting, entry['id'], ConfigYesNo(default=(entry['default'] == 'true')))
            entry['setting_id'] = getattr(setting, entry['id'])
            
        elif entry['type'] == 'text':
            setattr(setting, entry['id'], ConfigText(default=entry['default'], fixed_size=False))
            entry['setting_id'] = getattr(setting, entry['id'])
            
        elif entry['type'] == 'enum':
            choicelist = [(str(idx), self.get_label(e).encode('utf-8')) for idx, e in enumerate(entry['lvalues'].split("|"))]
            setattr(setting, entry['id'], ConfigSelection(default=entry['default'], choices=choicelist))
            entry['setting_id'] = getattr(setting, entry['id'])
            
        elif entry['type'] == 'labelenum':
            choicelist = [(self.get_label(e).encode('utf-8'), self.get_label(e).encode('utf-8')) for e in entry['values'].split("|")]
            setattr(setting, entry['id'], ConfigSelection(default=entry['default'], choices=choicelist))
            entry['setting_id'] = getattr(setting, entry['id'])
        else:
            debug('%s cannot initialize unknown entry %s' % (self, entry['type']))


class AddonInfo(object):
    
    def __init__(self, info_file):
        debug("initializing info of addon from %s" % info_file)
        
        pars = parser.XBMCAddonXMLParser(info_file)
        addon_dict = pars.parse()
        
        
        self.id = addon_dict['id']
        self.name = addon_dict['name']
        self.version = addon_dict['version']
        self.author = addon_dict['author']
        self.type = addon_dict['type']
        self.broken = addon_dict['broken']
        self.path = os.path.split(info_file)[0]
        self.description = u''
        self.library = addon_dict['library']
        self.script = addon_dict['script']
        
        if settings.LANGUAGE_SETTINGS_ID in addon_dict['description']:
            self.description = addon_dict['description'][settings.LANGUAGE_SETTINGS_ID]
        elif settings.LANGUAGE_SETTINGS_ID == 'sk' and 'cs' in addon_dict['description']:
            self.description = addon_dict['description']['cs']
        else:
            if not 'en' in addon_dict['description']:
                self.description = u''
            else:
                self.description = addon_dict['description']['en']
                
        self.requires = addon_dict['requires']
        
        self.image = LoadPixmap(cached=True, path=os.path.join(self.path, 'icon.png'))

        #changelog
        changelog_path = None
        if os.path.isfile(os.path.join(self.path, 'changelog.txt')):
            changelog_path = os.path.join(self.path, 'changelog.txt')
            
        elif os.path.isfile(os.path.join(self.path, 'Changelog.txt')):
            changelog_path = os.path.join(self.path, 'Changelog.txt')
            
        else:
            changelog_path = None
            
        if changelog_path is not None:
            with open(changelog_path, 'r') as f:
                text = f.read()
                f.close()
            try:
                self.changelog = text.decode('windows-1250')
            except Exception:
                debug('cannot decode c[C]angleog.txt')
                self.changelog = u''
                pass
        else:
            debug('c[C]hangelog.txt missing')
            self.changelog = u''
                
                
    def get_changelog(self):
        return self.changelog
    
    
class AddonLoader():    
    def __init__(self, addon):
        self.addon = addon
        self.__importer = AddonImporter(addon.id)
        
    def add_path(self, path):
        self.__importer.add_path(path)
    
    def add_importer(self):
        debug("%s adding importer" % self.addon)
        sys.meta_path.append(self.__importer)
        
    def remove_importer(self):
        debug("%s removing importer" % self.addon)
        sys.meta_path.remove(self.__importer)
        
        


class AddonImporter:
    """Used to avoid name collisions in sys.modules"""
    def __init__(self, name, lib_path=''):
        self.name = name
        self.path = [lib_path]
        self.modules = {}
        
    def add_path(self, path):
        if not path in self.path:
            self.path.append(path)
      
    def __repr__(self):
        return "[%s-importer] " % self.name               

    def find_module(self, fullname, path):
        debug("%s import '%s'" % (self, fullname))
        
        if fullname in sys.modules:
            debug("%s found '%s' in sys.modules\nUsing python standard importer" % self, fullname)
            return None
        
        if fullname in self.modules:
            debug("%s found '%s' in modules" % (self, fullname))
            return self
        try:
            path = self.path
            debug("%s finding modul '%s' in %s" % (self, fullname, path))
            self.f, self.filename, self.description = imp.find_module(fullname, path)
            debug("%s found modul '%s' <filename:%s description:%s>" % (self, fullname, self.filename, self.description))
        except ImportError:
            debug("%s cannot found modul %s" % (self, fullname))
            return None
        if self.f is None:
            debug("%s cannot import package '%s', try to append it to sys.path" % (self, fullname))
            raise ImportError
        debug("%s trying to load module '%s'" % (self, fullname))
        return self
    
    def load_module(self, fullname):
        if fullname in self.modules:
            return self.modules[fullname]
        try:
            code = self.f.read()
        except Exception:
            if self.f: self.f.close()
            return 
        else: self.f.close()
        debug("%s importing modul '%s'" % (self, fullname))
        mod = self.modules[fullname] = imp.new_module(fullname)
        mod.__file__ = self.filename
        mod.__loader__ = self
        del self.filename
        del self.description
        del self.f
        try:
            exec code in mod.__dict__
            debug("%s imported modul '%s'"  % (self,fullname))
        except Exception:
            del self.modules[fullname]
            raise
        return mod
        
