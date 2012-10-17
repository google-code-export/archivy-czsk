# -*- coding: utf-8 -*-
'''
Created on 20.3.2012

@author: marko
'''
from  xml.etree.cElementTree import ElementTree, Element, SubElement, Comment, tostring
import datetime
import os
import items as util
from Components.config import config
_dataPath = config.plugins.archivCZSK.dataPath.value
    

class mainXML(object):
    
    def __init__(self, name):
        self.filename = os.path.join(name, 'shortcuts.xml')
        self.xmlTree = None
        self.xmlRootElement = None
        self.fileExist = self.openArchiveFile()
            
     
    def createXMLArchive(self):
	pass
	     
    def openArchiveFile(self):
        try:
            self.xmlTree = ElementTree()
            self.xmlTree.parse(os.path.join(_dataPath, self.filename))
            self.xmlRootElement = self.xmlTree.getroot()
        except:
            return False
        return True

    def indent(self, elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for e in elem:
                self.indent(e, level + 1)
                if not e.tail or not e.tail.strip():
                    e.tail = i + "  "
            if not e.tail or not e.tail.strip():
                e.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
	
    def writeArchiveFile(self):    
        print 'writing xml file'
        #self.indent(self.xmlRootElement)
        pth=os.path.dirname((os.path.join(_dataPath, self.filename)))
        if not os.path.exists(pth):
            os.makedirs(pth)
        self.xmlTree = ElementTree(self.xmlRootElement).write(os.path.join(_dataPath, self.filename))
    

class archiveXML(mainXML):
    def __init__(self, name):
		#super(mainXML, self).__init__(name)
		mainXML.__init__(self, name)
		if not self.fileExist:
			self.createXMLArchive()


    def createXMLArchive(self):
        self.xmlRootElement = Element('root')
        items = SubElement(self.xmlRootElement, 'items')
        items.set('date', str(datetime.datetime.now()))
       
    def equal(self, elem, it):
        id = it.url_text + it.mode_text
        if elem.attrib.get("id") == id:
            return True
        return False
    
    def exist(self, el_list, it_list):
        exist = False
        item_exist = []
        el_remove = []
        for el in el_list:  
            for it in it_list:			
                    existtmp = self.equal(el, it)
                    exist = exist or existtmp
                    if existtmp:
                        item_exist.append(it)
                        break
            if not exist:
                el_remove.append(el)
                #el_list.remove(el_list[i])
                print 'remove'
            exist = False
        return item_exist, el_remove 

        
           
        
    def getContent(self, it):
        if it is None:
            parentEl = self.xmlRootElement
        else:
            id = it.url_text + it.mode_text
            parentEl = self.findShowById(id)
                
        if parentEl is not None:   
                date = None   
                item_lst = []
                items = parentEl.find('items')
                print items.tag, items.attrib.get('date')
                date = items.attrib.get('date')
                for show in items.findall('item'):
                    it = util.PItem()
                    it.name = show.findtext('name')
                    it.url_text = show.findtext('url')
                    it.mode_text = show.findtext('mode')
                    
                    if it.mode_text == '':
                        it.url = {it.mode_text:it.url_text}						
                    else:
                        try:
                            it.mode = int(it.mode_text)
                            it.url = it.url_text
                        except:
                            it.url = {it.mode_text:it.url_text}
                            
                    it.image = show.findtext('img')
                    it.info = show.findtext('info')
                    if it.info:
						it.info = it.info
                    it.page = show.findtext('page')
                    it.kanal = show.findtext('kanal')           
                    it.folder = show.findtext('dir') == 'True'
                    item_lst.append(it)
                    
                if len(item_lst) == 0:
			       return None, None
                else:
				   return item_lst, date
					
        return None, None
    
    def findShowById(self, id_show):
		allcases = self.xmlRootElement.findall(".//item")
		for c in allcases:
			if c.get('id') == str(id_show):
				return c
		return None

        #return self.xmlRootElement.find(".//item[@id='%s']" % id_show)
    
    #def findShowsById(self,id):
    
    def updateShowList(self, item_lst, url=None):
		if item_lst is None:
			pass
		else:
			if item_lst[0].folder: #ak su to videa tak nerob nic
				if url is None:
					parent = self.xmlRootElement
				else:
					parent = self.findShowById(url)
					if parent is None:
						parent = self.xmlRootElement
                              
				self.createShowList(parent, item_lst)
			else: 
				pass
                     
    
               
    def createShowList(self, parentEl, item_lst):
        #print parentEl.tag
        #it = item_lst
        for child in parentEl:
            print child.tag
        items = parentEl.find('items')
        items.set('date', str(datetime.datetime.now())) 
        forbid, remove = self.exist(items, item_lst)
        for el in remove:
            items.remove(el)
        for it in item_lst:
                if it in forbid:
                    continue
                else: 
                    print 'newitem'
                    show = Element('item')
                    id = it.url_text + it.mode_text
                    show.set('id', id)
                    name = SubElement(show, 'name')
                    name.text = it.name
                    url = SubElement(show, 'url')
                    url.text = it.url_text
                    mode = SubElement(show, 'mode')
                    mode.text = it.mode_text
                    img = SubElement(show, 'img')
                    img.text = it.image
                    info = SubElement(show, 'info')
                    info.text = it.info
                    dir = SubElement(show, 'dir')
                    dir.text = str(it.folder)
                    if it.page:
                        page = SubElement(show, 'page')
                        page.text = str(it.page)
                    if it.kanal:
                        kanal = SubElement(show, 'kanal')
                        kanal.text = str(it.kanal)
                    SubElement(show, 'items')
                    items.append(show) 

class shortcutXML(mainXML):
    def __init__(self, name):
		mainXML.__init__(self, name)
		#super( mainXML, self ).__init__(name)
		if not self.fileExist:
			self.createXMLArchive()

    def createXMLArchive(self):
        self.xmlRootElement = Element('root')
        SubElement(self.xmlRootElement, 'shortcuts')

    def createShortcut(self, shortcut_it):
        shortcuts = self.xmlRootElement.find('shortcuts')
        id_sc = shortcut_it.url_text + shortcut_it.mode_text
        if self.findShortcutById(id_sc) is not None:
            return False
        else:
            shortcut = Element('shortcut')
            shortcut.set('id', id_sc)
            name = SubElement(shortcut, 'name')
            name.text = shortcut_it.name
            url = SubElement(shortcut, 'url')
            url.text = str(shortcut_it.url_text)
            #info = SubElement(shortcut, 'info')
            #info.text = str(shortcut_it.info)
            mode = SubElement(shortcut, 'mode')
            mode.text = str(shortcut_it.mode_text)
            img = SubElement(shortcut, 'img')
            img.text = shortcut_it.image
            dir = SubElement(shortcut, 'dir')
            dir.text = str(shortcut_it.folder)
            #parent = SubElement(shortcut, 'parent')
            #parent.text = str(shortcut_it.parent)
            if shortcut_it.page:
                page = SubElement(shortcut, 'page')
                page.text = str(shortcut_it.page)
            if shortcut_it.kanal:
                kanal = SubElement(shortcut, 'kanal')
                kanal.text = str(shortcut_it.kanal)
            shortcuts.append(shortcut)
        return True

    def getShortcuts(self):
        shortcut_lst = []
        parentEl = self.xmlRootElement
        shortcuts = parentEl.find('shortcuts')
        for shortcut in shortcuts.findall('shortcut'):
            
            it = util.PFolder()
            it.name = shortcut.findtext('name')
            it.url_text = shortcut.findtext('url')
            #parent = shortcut.findtext('parent')
            it.mode_text = shortcut.findtext('mode')
            if it.mode_text == '':
                it.url = {it.mode_text:it.url_text}
            else:
                try:
                    it.mode = int(it.mode_text)
                    it.url = it.url_text
                except:
                    it.url = {it.mode_text:it.url_text}
                    
            it.image = shortcut.findtext('img')
            #it.info = shortcut.findtext('info')
            #if it.info:
             #   it.info=it.info.encode('utf-8')
            it.page = shortcut.findtext('page')
            it.kanal = shortcut.findtext('kanal')   
            it.folder = shortcut.findtext('dir') == 'True'
            shortcut_lst.append(it)
                    
        if len(shortcut_lst) == 0:
            return None
        else:
            return shortcut_lst	
            
        
    def removeShortcut(self, shortcut_id):
        shortcuts = self.xmlRootElement.find('shortcuts')
        shortcut = self.findShortcutById(shortcut_id)
        shortcuts.remove(shortcut)  

    def findShortcutById(self, id_shortcut):
        allcases = self.xmlRootElement.findall(".//shortcut")
        for c in allcases:
            if c.get('id') == str(id_shortcut):
                return c
        return None
  

