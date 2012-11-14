'''
Created on 11.8.2012

@author: marko
'''
from Plugins.Extensions.archivCZSK import _
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigYesNo, ConfigDirectory, configfile, getConfigListEntry

import os

#define settings which will apply for every addon
global_addon_settings = [{'label':_('playing'),
                             'subentries':[
                                        {'label':_("seekable"), 'id':'seekable', 'entry':ConfigYesNo(default=True)},
                                        {'label':_("pausable"), 'id':'pausable', 'entry':ConfigYesNo(default=True)}
                                        ]
                            },
                           {'label':_('download'),
                             'subentries':[
                                        {'label':_("download path"), 'id':'download_path'},
                                        ]
                            }
                           ]


def add_global_addon_specific_setting(addon, addon_config, setting):
    
    if setting['id'] == 'download_path':
        download_path = os.path.join(config.plugins.archivCZSK.downloadsPath.getValue(), addon.id)
        print '[ArchivCZSK] adding download_path %s to %s' % (download_path, addon.id)
        setattr(addon_config, setting['id'], ConfigDirectory(default=download_path))
        

#globally adding archivCZSK specific options to addons
def add_global_addon_settings(addon, addon_config):
    for category in global_addon_settings:
        for setting in category['subentries']:
            if 'entry' not in setting:
                add_global_addon_specific_setting(addon, addon_config, setting)
            else: 
                setattr(addon_config, setting['id'], setting['entry'])
                setting['setting_id'] = getattr(addon_config, setting['id'])


#get addon config entries with global addons settings          
def getArchiveConfigList(addon):
    categories = addon.settings.get_configlist_categories()[:]
    for category in global_addon_settings:
        category_init = {'label':category['label'], 'subentries':[]}
        for setting in category['subentries']:
            if 'setting_id' not in setting:
                category_init['subentries'].append(getConfigListEntry(setting['label'], getattr(addon.settings.main, setting['id'])))
            else:
                category_init['subentries'].append(getConfigListEntry(setting['label'], setting['setting_id']))
        categories.append(category_init)
    return categories
            
