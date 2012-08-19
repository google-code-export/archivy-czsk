'''
Created on 25.6.2012

@author: marko
'''

from xml.etree.cElementTree import ElementTree
import urllib2
import os, shutil
from Plugins.Extensions.archivCZSK.resources.archives import config as archive_cfg

GUI_CB = None
_DEBUG = True
_tmpPath = '/tmp/archivCZSKupdate/'
_tmpPathTools = '/tmp/archivCZSKupdate/tools/'
_baseUpdateURL = 'http://skuskaupdate.googlecode.com/svn/trunk/'
_versionURL = _baseUpdateURL + '/version2.xml'
_pluginPath = "/usr/lib/enigma2/python/Plugins/Extensions/archivCZSK/"
_relArchivesPath = 'resources/archives/'
_archivesPath = archive_cfg.ARCHIVES_PATH
_configRelPath = archive_cfg.CONFIG_ARCHIVES_PATH
archiveFiles = ['default.py', 'addon.xml', 'changelog.txt', '__init__.py', 'icon.png']
#_dmdTools = ('dmd_tools', 'resources/archives/dmd_czech/tools')
#_doplnkyTools = ('doplnky_tools', 'resources/archives/xbmc_doplnky/tools')
archiveTools = archive_cfg.tools
#archiveTools = [_dmdTools, _doplnkyTools]

def debug(text):
    text = '[archivCZSK [update] ] %s' % text
    if GUI_CB is not None:
        GUI_CB(text)
    if _DEBUG:
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
        f = urllib2.urlopen(remote)
        debug("downloading " + remote) 
        localFile = open(local, "w")
        localFile.write(f.read())
        localFile.close()
    except urllib2.HTTPError, e:
        debug("HTTP Error: %s %s" % (e.code, remote))
        raise
    except urllib2.URLError, e:
        debug("URL Error: %s %s" % (e.reason, remote))
        raise
    except IOError, e:
        debug('cannot open archive file')
        raise
    else:
        debug(local + ' succesfully downloaded')


def updateNeeded(local, remote):
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
    
def downloadArchive(archive, directory=_tmpPath):
    if archive.id == 'movielibrary':
        archiveFiles.append('ulozto.py')
    for archiveFile in archiveFiles:    
        url = _baseUpdateURL + archive.relDir + '/' + archiveFile
        local = os.path.join(directory, archiveFile)
        try:
            download(url, local)
        except urllib2.HTTPError, e:
            if url.split('/')[-1] == 'changelog.txt':
                try:
                    download(_baseUpdateURL + archive.relDir + '/Changelog.txt')
                except:
                    removeFiles(archiveFiles)
                else:
                    continue
            else:
                removeFiles(archiveFiles)
                return None
        except:
            removeFiles(archiveFiles)
            return None
    return archiveFiles

def downloadTool(tool, remoteBase, tmpBase):
    #download tool directories and their files 
    if not os.path.isdir(tmpBase):
        os.makedirs(tmpBase)
    for dir in tool.keys():
        if dir in ['name', 'root', 'path']:
            continue
        tmpDir = os.path.join(tmpBase, dir)
        remoteDir = remoteBase + '/' + dir
        if not os.path.isdir(tmpDir):
            os.makedirs(tmpDir)
        for f in tool[dir]:
            remote = remoteDir + '/' + f
            local = os.path.join(tmpDir, f)
            try:
                download(remote, local)
            except:
                shutil.rmtree(tmpBase)
                return None
            
    #download root directory files        
    for f in tool['root']:
        remote = remoteBase + '/' + f
        local = os.path.join(tmpBase, f)
        try:
            download(remote, local)
        except:
            shutil.rmtree(tmpBase)
            return None
    return True
             

def downloadConfig(archive, directory=_tmpPath):
    remote = _baseUpdateURL + _configRelPath
    local = os.path.join(_pluginPath, _configRelPath)
    try:
        download(remote, local)
    except:
        pass
    else:
        removePyOC(local)
                
                
def findLocalTools():
    global archiveTools
    for repository in os.listdir(_archivesPath):
        repositoryPath = os.path.join(_archivesPath, repository)
        toolsPath = os.path.join(repositoryPath, 'tools')
        if os.path.isdir(toolsPath):
            archiveTools.append(repository + '_tools', toolsPath)
            
            
def updateArchiveTools(tools):
    success = []
    for tool in tools:
        remoteBase = _baseUpdateURL + tool['path']
        tmpBase = os.path.join(_tmpPathTools, tool['name'])
        localBase = os.path.join(_pluginPath, tool['path'])
        
        ret = downloadTool(tool, remoteBase, tmpBase)
        #download to tmp was successfull, copy all contents from tmp directory to archive directory
        if ret is not None and os.path.isdir(tmpBase):
            success.append(tool['name'])
            for dir in tool.keys():
                if dir in ['name', 'root', 'path']:
                    continue
                tmpDir = os.path.join(tmpBase, dir)
                localDir = os.path.join(localBase, dir)
                if not os.path.isdir(localDir):
                    os.makedirs(localDir)
                for f in tool[dir]: 
                    print f, '   ', tmpDir
                    shutil.copy(os.path.join(tmpDir, f), os.path.join(localDir, f))                                                           
                    if os.path.splitext(f)[1] == '.py':
                        removePyOC(f)                                                                                                                                                                            
            for f in tool['root']:
                shutil.copy(os.path.join(tmpBase, f), os.path.join(localBase, f))
                if os.path.splitext(f)[1] == '.py':
                    removePyOC(f)        
    return ' '.join(success)
        
def updateArchives(archives):
    if not os.path.isdir(_tmpPath):
        os.makedirs(_tmpPath)
    success = []
    for archLocal in archives:
        if archLocal.needUpdate:
            files = downloadArchive(archLocal, _tmpPath)
            if files is not None:
                localBase = os.path.join(_pluginPath, archLocal.relDir)
                if not os.path.isdir(localBase):
                    os.makedirs(localBase)
                for f in files:
                    tmpfile = os.path.join(_tmpPath, f)
                    localfile = os.path.join(localBase, f)
                    print tmpfile, localfile
                    shutil.copy(tmpfile, localfile)
                    if os.path.splitext(f)[1] == '.py':
                        removePyOC(localfile)
                debug("update %s was successfull" % (archLocal.name))
                archLocal.needUpdate = False
                success.append(archLocal.name)
            else:
                debug("update %s was not successfull" % (archLocal.name))
                
    if len(success) > 0:
            remote = _baseUpdateURL + _configRelPath
            local = os.path.join(_pluginPath, _configRelPath)
            try:
                download(remote, local)
            except:
                pass
            else:
                removePyOC(local)
            
    return ' '.join(success)

def checkArchiveToolVersion(archRemote, name, version, repository):
    archiveTool = {}
    
    def createTool(tool, archRemote, name):
        debug('Tool to update' + name)
        archiveTool['root'] = []
        for info in archRemote.findall('extension'):
            if info.attrib.get('point') == 'xbmc.addon.metadata':
                tools = info.find('tools')
                for dir in tools.findall('directory'):
                    dirName = dir.attrib.get('name')
                    archiveTool[dirName] = []
                    for f in dir.findall('file'):
                        archiveTool[dirName].append(f.text)         
                for f in tools.findall('file'):
                    #debug('rootfile ' + f.text)
                    archiveTool['root'].append(f.text)
            archiveTool['name'] = name
            archiveTool['path'] = tool[1]
            
    if name in [tool[0] for tool in archiveTools]:
        for tool in archiveTools:
            if tool[0] == name:
                el = ElementTree()
                toolDir = os.path.join(_pluginPath, tool[1])
                try:
                    el.parse(os.path.join(toolDir, 'addon.xml'))
                except IOError:
                    debug('addon.xml doesnt exist in ' + toolDir)
                    return {}   
                addon = el.getroot()
                localVersion = addon.attrib.get('version')
                if updateNeeded(localVersion, version):
                    debug('tools %s < %s' % (localVersion, version))
                    createTool(tool, archRemote, name)
    elif name.find('tools') != -1:
        tool = (name, os.path.join(os.path.join(_archivesPath, repository), 'tools'))
        createTool(tool, archRemote, name)
    return archiveTool


def checkArchiveVersions(archives):
    tools = []
    needUpdate = []
    newArchives = []
    try:
        xml = urllib2.urlopen(_versionURL, timeout=15.0)
    except:
        debug("Errors apeared while retrieving " + _versionURL)
        return '', [], []
    el = ElementTree()
    el.parse(xml)
    for archRemote in el.findall('addon'):
        id_a = archRemote.attrib.get("id")
        name = archRemote.attrib.get("name")
        version = archRemote.attrib.get('version')
        repository = archRemote.attrib.get('repository')
        if name not in [archLocal.name for archLocal in archives]:
            if name.find('tools') == -1:
                debug("found new archive " + name)
                newArchives.append(PArchiveDummy(id_a, name, repository))
            else:
                tool = checkArchiveToolVersion(archRemote, name, version, repository)
                if len(tool) > 0:
                    tools.append(tool)

        #print 'remote', name, version        
        for archLocal in archives:
            #print 'local', archLocal.name, archLocal.version
            if name == archLocal.name and updateNeeded(archLocal.version, version):
                debug("%s > %s" % (version, archLocal.version))
                needUpdate.append(archLocal)
                archLocal.needUpdate = True
            
    
    return needUpdate, tools, newArchives



def updatePlugin():
    pass

def checkPluginVersion():
    pass


class PArchiveDummy(object):
    """Dummy PArchive class for downloading new archives"""
    def __init__(self, id, name, repository):
        self.name = name
        self.id = id.split('.')[-2] if id.split('.')[-1] == 'cz' else id.split('.')[-1]
        self.relDir = _relArchivesPath + repository + '/' + self.id
        self.dir = os.path.join(_pluginPath, self.relDir)
        self.needUpdate = True


#findLocalTools()
#archives = [PArchive('ct', 3), PArchive('stv', 3)]
#print checkArchiveVersions(archives)
#needUpdate=checkVersions()
#if len(needUpdate)>0:
#    print 'Update is needed for: ' + needUpdate+' archives'
#    print update()
#else:
#    print 'Not need to update'
