# -*- coding: UTF-8 -*-
'''
Created on 28.4.2012

@author: marko
'''
from Components.ActionMap import ActionMap, NumberActionMap

from base import  BaseArchivCZSKMenuListScreen
from common import PanelList, PanelListEntryHD

PanelListEntry = PanelListEntryHD    

def showContextMenu(session, context_items, cb):
    session.openWithCallback(cb, ContextMenuScreen, context_items)

class ContextMenuScreen(BaseArchivCZSKMenuListScreen):  
        def __init__(self, session, context_items):
            BaseArchivCZSKMenuListScreen.__init__(self, session)
            
            self.context_items = context_items
        
            self["menu"] = PanelList([])
            self["actions"] = NumberActionMap(["archivCZSKActions"],
                {
                "ok": self.ok,
                "cancel": self.cancel,
                "up": self.up,
                "down": self.down,
                }, -2)
            
            self.onShown.append(self.setWindowTitle)

        def setWindowTitle(self):
            self.setTitle('Menu')
                
        def updateMenuList(self):
            self.menu_list[:]
            list = []
            for idx, menu_item in enumerate(self.context_items):
                list.append(PanelListEntry(menu_item.name, idx))
                            
            self["menu"].setList(list)      
                     
         
        def ok(self):
            if not self.working:
                self.close(self['menu'].getSelectedIndex())
                
        def cancel(self):
            self.close(None)
                
    
