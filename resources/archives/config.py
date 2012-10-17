'''
Created on 11.8.2012

@author: marko
'''
#Main archives config
import os
import Plugins.Extensions.archivCZSK.resources.tools.util2 as util

from Plugins.Extensions.archivCZSK import _
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigYesNo, configfile, getConfigListEntry

class Repository():
    def __init__(self, name, config_file):
        self.name = name
        self.archives = []
       # self.path = REPOSITORY_PATH
        #self.tools_path = os.path.join(REPOSITORY_PATH,'tools')
        
        el=util.load_xml(config_file)
        if el is not None:
            root = el.getroot()
            
        
# plugin paths
PLUGIN_PATH = "/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/"
IMAGE_PATH = os.path.join(PLUGIN_PATH, 'gui/icon')
SKIN_PATH = os.path.join(PLUGIN_PATH, 'gui/skin')
ARCHIVES_PATH = os.path.join(PLUGIN_PATH, 'resources/archives')
CONFIG_ARCHIVES_PATH = os.path.join(ARCHIVES_PATH, 'config.py')

# define repo paths and their tools path
DMD_PATH = os.path.join(ARCHIVES_PATH, 'dmd_czech')
DMD_TOOLS_PATH = 'resources/archives/dmd_czech/tools'
DMD_TOOLS_NAME = 'dmd_czech_tools'
DMD_ARCHIVE_FILES = ['default.py', 'cp.py', 'addon.xml', 'settings.xml', 'changelog.txt', 'icon.png']

DOPLNKY_PATH = os.path.join(ARCHIVES_PATH, 'xbmc_doplnky')
DOPLNKY_TOOLS_PATH = 'resources/archives/xbmc_doplnky/tools'
DOPLNKY_TOOLS_NAME = 'xbmc_doplnky_tools'
DOPLNKY_ARCHIVE_FILES = ['default.py', 'addon.xml', 'changelog.txt', 'settings.xml', 'icon.png']

OTHER = os.path.join(ARCHIVES_PATH, 'other')



archives = [DMD_PATH, DOPLNKY_PATH, OTHER]
tools = [(DMD_TOOLS_NAME, DMD_TOOLS_PATH), (DOPLNKY_TOOLS_NAME, DOPLNKY_TOOLS_PATH)]

doplnky = ('movielibrary', 'koukni', 'videacesky', 'bezvadata', 'pohadkar', 'replay', 'serialycz', 'eserial', 'onlinefiles','playserial','hejbejse','rajfilmy')
dmd = ('muvi', 'filmyczcom', 'stream', 'markiza', 'joj', 'btv', 'voyo', 'ivysilani', 'stv', 'metropol', 'prima', 'huste')



#define in which category archive belong
video_archives = (
                  'movielibrary',
                  'koukni',
                  'muvi',
                  'filmyczcom',
                  'videacesky',
                  'stream',
                  'bezvadata',
                  'pohadkar',
                  'replay',
                  'serialycz',
                  'eserial',
                  'nastojaka',
                  'playserial',
                  'zkouknito',
                  'onlinefiles',
                  'hejbejse',
                  'rajfilmy'
                   )

tv_archives = (
               'markiza',
               'joj',
               'btv',
               'voyo',
               'ivysilani',
               'stv',
               'metropol',
               'prima',
               'huste'
               )

streamy = 'streamy'
config.plugins.archivCZSK.archives.streamy = ConfigSubsection()

#define settings which will apply for every archive
global_archive_settings = [{'label':_('playing'),
                             'subentries':[
                                        {'label':_("seekable"), 'id':'seekable', 'entry':ConfigYesNo(default=True)},
                                        {'label':_("pausable"), 'id':'pausable', 'entry':ConfigYesNo(default=True)}
                                        ]
                            }
                           ]


#creating config for every archive
for archs_dir in archives:
    for module in os.listdir(archs_dir):
        if module in ['tools', 'init.py','init.pyc','init.pyo']:
            continue
        setattr(config.plugins.archivCZSK.archives, module, ConfigSubsection())
        
        #globally adding archivCZSK specific options to archives
        archive_conf = getattr(config.plugins.archivCZSK.archives, module)
        for category in global_archive_settings:
            for setting in category['subentries']:
                setattr(archive_conf, setting['id'], setting['entry'])
                setting['setting_id'] = getattr(archive_conf, setting['id'])


#get archive config entries with global archive settings          
def getArchiveConfigList(archive):
    categories = archive.settings.get_configlist_categories()[:]
    for category in global_archive_settings:
        category_init = {'label':category['label'], 'subentries':[]}
        for setting in category['subentries']:
            category_init['subentries'].append(getConfigListEntry(setting['label'], setting['setting_id']))
        categories.append(category_init)
    return categories
            
