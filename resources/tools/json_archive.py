# -*- coding: utf-8 -*-
'''
Created on 17.4.2012

@author: marko
'''

import datetime
import os
import util
import Plugins.Extensions.archivCZSK.resources.archives.simplejson as json
from downloader import HTTPDownloadTW, RTMPDownloadTW
from Components.config import config
_dataPath = config.plugins.archivCZSK.dataPath.value  

class mainJSON(object):
    
    def __init__(self, name):
        self.filename = name + '.json'
        self.data = None 
        self.changed = False
        self.fileExist = self.openArchiveFile()  
     
    def createJSONArchive(self):
        pass
         
    def openArchiveFile(self):
        try:
            f = open(os.path.join(_dataPath, self.filename), 'r')
            data = f.read()
            self.data = json.loads(unicode(data.decode('utf-8', 'ignore')))
            f.close()    
        except:
            return False
        return True

    
    def writeArchiveFile(self):    
        print 'writing json file'
        self.changed = True
        if self.changed:
            f = open(os.path.join(_dataPath, self.filename), 'w')
            f.write(json.dumps(self.data, ensure_ascii=True))
            f.close() 
        else:
            pass
        
        
class downloadJSON(mainJSON):
    def __init__(self, destDir):
        name = 'downloads'
        mainJSON.__init__(self, name)
        if not self.fileExist:
            self.createJSONArchive()
            
    def createJSONArchive(self):
        self.data = {}
        
    def getDownloads(self):
        dld_list = []
        for key in self.data.keys():
            dld = self.data[key][0]
            if dld['url'][0:4] == 'http':
                download = HTTPDownloadTW(url=dld['url'], name=dld['name'], filename=dld['filename'], destDir=dld['destDir'], quite=dld['quite'])
            elif download['url'][0:4] == 'rtmp':
                download = RTMPDownloadTW(url=dld['url'], name=dld['name'], filename=dld['filename'], destDir=dld['destDir'], quite=dld['quite'], live=dld['live'])
            download.running = dld['running']
            download.downloaded = dld['downloaded']
            download.paused = dld['paused']
            download.local = dld['local']
            dld_list.append(download)
        return dld_list
    
    def addDownload(self, download):
        count = 0
        if isinstance(download, HTTPDownloadTW):
            count += 1
            self.data[download.url] = [{'url':download.url, 'name':download.name, 'filename':download.filename, 'destDir':download.destDir, 'quite':download.quite, 'running':download.running, 'paused':download.paused, 'downloaded':download.downloaded, 'local':download.local}]
        elif isinstance(download, RTMPDownloadTW):
            count += 1
            self.data[download.url] = [{'url':download.url, 'name':download.name, 'filename':download.filename, 'destDir':download.destDir, 'quite':download.quite, 'running':download.running, 'paused':download.paused, 'downloaded':download.downloaded, 'local':download.local, 'live':download.live}]
        return count
    
    def removeDownload(self, url):
        del self.data[url]
        
        
    
class archiveJSON(mainJSON):
    def __init__(self, name):
        #super(mainXML, self).__init__(name)
        mainJSON.__init__(self, name)
        if not self.fileExist:
            self.createJSONArchive()
        


    def createJSONArchive(self):
        self.data = {}
        self.data['root'] = [{'date':str(datetime.datetime.now()), 'items':[]}]

    def equal(self, elem, it):
        id = it.url_text + it.mode_text
        if self.data.has_key(id):
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
            main_show = self.data['root'][0]
        else:
            id = it.url_text + it.mode_text
            main_show = self.data[id][0] 
        item_lst = []
        date = main_show['date']
        items = main_show['items']
        
        for show_id in items:
            show = self.data[show_id][0]
            it = util.PItem()
            it.name = show['name'].encode('utf-8')
            it.mode_text = str(show['mode'])
            it.url_text = str(show['url'])
            it.folder = show['folder'] == 'True'
            it.image = str(show['image'])
            if it.mode_text == '':
                it.url = {it.mode_text:it.url_text}
            else:
                try:
                    it.mode = int(it.mode_text)
                    it.url = it.url_text
                except:
                    it.url = {it.mode_text:it.url_text}
            it.info = show['info']
            if it.info:
                it.info = it.info.encode('utf-8')
            if show.has_key('kanal'):
                it.kanal = show['kanal'] 
            if show.has_key('page'):
                it.kanal = show['page']  
            item_lst.append(it)
            
        if len(item_lst) == 0:
            return None, None
        else:
            return item_lst, date
                    
        return None, None
    
    
    def updateShowList(self, item_lst, id_show=None):
        if item_lst is None:
            pass
        else:
            if item_lst[0].folder: #ak su to videa tak nerob nic
                if id_show is None:
                    show = self.data['root'][0]
                else:
                    if id_show in self.data.keys():
                        show = self.data[id_show][0]
                    else :
                        show = self.data['root'][0]
                self.createShowList(show, item_lst)
            else: 
                pass
                     
    
               
    def createShowList(self, show, item_lst):
        it = item_lst
        data = self.data
        date = str(datetime.datetime.now())
        show['date'] = date 
        forbid, remove = self.exist(show['items'], item_lst)
        for el in remove:
            del data[el]
            show['items'].remove(el)
        for it in item_lst:
            if it in forbid:
                continue
            else:
                item = [{'url':it.url_text, 'name':it.name, 'mode':it.mode_text, 'image':str(it.image), 'info':it.info, 'folder':str(it.folder), 'items':[], 'date':''}]
                if it.page:
                    item[0]['page'] = it.page
                if it.kanal:
                    item[0]['kanal'] = it.kanal
                id = it.url_text + it.mode_text
                show['items'].append(id)
                data[id] = item

