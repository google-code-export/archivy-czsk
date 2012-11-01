'''
Created on 11.8.2012

@author: marko
'''
from Plugins.Extensions.archivCZSK import _
from Components.config import config, ConfigSubsection, ConfigSelection, ConfigYesNo, configfile, getConfigListEntry

#define settings which will apply for every addons
global_archive_settings = [{'label':_('playing'),
                             'subentries':[
                                        {'label':_("seekable"), 'id':'seekable', 'entry':ConfigYesNo(default=True)},
                                        {'label':_("pausable"), 'id':'pausable', 'entry':ConfigYesNo(default=True)}
                                        ]
                            }
                           ]

#globally adding archivCZSK specific options to addons
def add_global_addon_settings(addon_config):
    for category in global_archive_settings:
        for setting in category['subentries']:
            setattr(addon_config, setting['id'], setting['entry'])
            setting['setting_id'] = getattr(addon_config, setting['id'])


#get archive config entries with global addons settings          
def getArchiveConfigList(archive):
    categories = archive.settings.get_configlist_categories()[:]
    for category in global_archive_settings:
        category_init = {'label':category['label'], 'subentries':[]}
        for setting in category['subentries']:
            category_init['subentries'].append(getConfigListEntry(setting['label'], setting['setting_id']))
        categories.append(category_init)
    return categories
            
