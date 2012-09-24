'''
Created on 8.5.2012

@author: marko
'''
import os, time, sys, mimetypes
from subprocess import Popen
from twisted.python import failure
from twisted.internet import reactor
from twisted.web import client
from twisted.internet import reactor, protocol, defer
import urlparse, urllib2
try:
    from enigma import eConsoleAppContainer
except ImportError:
    pass

rtmpdump_path = '/usr/bin/rtmpdump'
wget_path = 'wget'
user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1'
#rtmpdump_path = 'd:/rtpmp/rtmpdump.exe'
#wget_path = 'd:/rtpmp/wget.exe'
video_extensions = ('.avi', '.flv', '.mp4', '.mkv', '.mpeg', '.asf', '.wmv', '.divx')

class DownloadInfo():
    def __init__(self, download, refreshTime):
        self.download = download
        self.refreshTime = refreshTime
        self.tempLength = download.tempLength 
        self.speed = 0
        self.speedKB = 0
        self.speedMB = 0
        self.eta = -1
        self.etaM = -1
        self.etaMS = (-1, -1)
        self.etaHMS = (-1, -1, -1)
        
    def updateInfo(self):
        totalLength = self.download.totalLength
        tempLength = self.download.tempLength
        speedB = 0
        if os.path.isfile(self.download.local):
            currentLength = os.path.getsize(self.download.local)
            if tempLength == 0:
                speedB = currentLength / self.refreshTime
            elif tempLength > 0:
                speedB = (tempLength - currentLength) / self.refreshTime
            if speedB > 0:
                self.speed = speedB
                self.speedKB = self.speed / 1024
                self.speedMB = self.speedKB / 1024
                if totalLength > 0:
                    self.eta = (totalLength - currentLength) / speedB
                    self.etaM = self.eta / 60
                    self.etaMS = (self.etaM, self.eta)
                    self.etaHMS = (self.etaM / 60, self.etaM, self.eta)
            self.download.tempLength = currentLength


class DownloadManager(object):
    instance = None

    @staticmethod
    def getInstance():
        return DownloadManager.instance

    def __init__(self, download_lst):
        print 'initializing downloadManager'
        DownloadManager.instance = self
        self.download_lst = download_lst

    def addDownload(self, download, overrideCB=None):
        if not download.url in [down.url for down in self.download_lst]:
                self.download_lst.append(download)
                download.start()
        else:
            if overrideCB is not None:
                overrideCB(download)

    def cancelDownload(self, download):
        if download.running:
            download.cancel()

    def removeDownload(self, download):
        if download.running:
            if download.e2download:
                download.pp.appClosed.append(download.remove)
            else:
                download.finishDeffer.addCallback(download.remove)
            download.cancel()
            self.download_lst.remove(download)
        else:
            download.remove()
            self.download_lst.remove(download)

    def findDownloadByIT(self, it):
        for download in self.download_lst:
            if it.url == download.local:
                return download
        return None
    
    def createDownload(self, name, url, destination, filename=None, live=False, startCB=None, finishCB=None, e2download=True, quite=False, playDownload=False):
        d = None
        if not os.path.exists(destination):
            os.makedirs(destination)

        if url[0:4] == 'rtmp':
            url = url.split()
            url = ' --'.join(url[0:])
            if e2download:
                d = RTMPDownloadE2(url=url, name=name, destDir=destination, live=live, quite=quite)
                d.startCB = startCB
                d.finishCB = finishCB
                d.e2download = e2download
            else:
                d = RTMPDownloadTW(url=url, name=name, destDir=destination, live=live, quite=quite)
                if startCB is not None:
                    d.startDeffer.addCallback(startCB)
                if finishCB is not None:
                    d.finishDeffer.addCallback(finishCB)
            return d

        elif url[0:4] == 'http':
            req = urllib2.Request(url)
            resp = urllib2.urlopen(req)
            exttype = resp.info().get('Content-Type')
            length = resp.info().get('Content-Length')
            resp.close()
            if filename is not None:
                if os.path.splitext(filename)[1] in video_extensions:
                    pass
                else:
                    ext = mimetypes.guess_extension(exttype)
                    if ext is not None:
                        filename = filename + ext
                filename = filename.replace(' ', '_')
            else:
                path = urlparse.urlparse(url).path
                filename = os.path.basename(path)
                
            if os.path.splitext(filename)[1] == '.avi' and playDownload:
                d = HTTPDownloadTwisted(name=filename, url=url, filename=filename, destDir=destination, quite=quite)
                d.startCB = startCB
                d.finishCB = finishCB
                d.e2download = False

            elif e2download:
                d = HTTPDownloadE2(name=filename, url=url, filename=filename, destDir=destination, quite=quite)
                d.startCB = startCB
                d.finishCB = finishCB
                d.e2download = e2download
            else:
                d = HTTPDownloadTW(name=filename, url=url, filename=filename, destDir=destination, quite=quite)
                if startCB is not None:
                    d.startDeffer.addCallback(startCB)
                if finishCB is not None:
                    d.finishDeffer.addCallback(finishCB)
            
            d.totalLength = length
            return d
            
        else:
            print 'Cannot download file', url, 'not supported protocol'
            return None


class Download(object):
    def __init__(self, name, url, destDir, filename, quite):
        self.init_time = time.time()
        self.finish_time = None
        self.url = url
        self.name = name
        self.filename = filename.encode('ascii', 'ignore')
        self.destDir = destDir.encode('ascii', 'ignore')
        self.local = os.path.join(destDir, filename).encode('ascii', 'ignore')
        self.quite = quite
        self.running = False
        self.killed = False
        self.paused = False
        self.downloaded = False
        self.showOutput = False
        self.outputCB = None
        self.totalLength = 0
        self.pp = None
        self.startCB = None
        self.finishCB = None
        self.e2download = False

    def remove(self, callback=None):
        """removes download"""
        if not self.running and os.path.isfile(self.local):
            print 'removing', self.filename
            os.remove(self.local)

    def start(self):
        """Starts downloading file"""
        pass

    def stop(self):
        """Stops downloading file"""
        pass

    def resume(self):
        """Resumes downloading file"""
        pass

    def cancel(self):
        """Kills downloading process"""
        pass


class RTMPDownloadE2(Download):
    def __init__(self, name, url, destDir, filename=None, live=False, quite=False):
        self.e2download = True
        if not filename:
            filename = name + '.flv'
            filename = filename.replace(' ', '_')
            filename = filename.replace('/', '')
            filename = filename.replace('(', '')
            filename = filename.replace(')', '')
        Download.__init__(self, name, url, destDir, filename, quite)
        self.pp = eConsoleAppContainer()
        #self.pp.dataAvail.append(self.__startCB)
        self.pp.appClosed.append(self.__finishCB)
        self.pp.stderrAvail.append(self.__outputCB)
        self.live = live

    def __startCB(self):
        self.running = True
        if self.startCB is not None:
            self.startCB(self)

    def __finishCB(self, retval):
        print 'e2rtmpdownload finished with', str(retval)
        self.running = False
        self.finish_time = time.time()
        if retval == 0 and not self.killed:
            self.downloaded = True
        else:
            self.downloaded = False
        if self.finishCB is not None:
            self.finishCB(self)


    def __outputCB(self, data):
        if self.showOutput and self.outputCB is not None:
            self.outputCB(data)

    def start(self):
        cmd = rtmpdump_path + ' -r ' + self.url + ' -o ' + '"' + self.local + '"'
        cmd = cmd.encode('utf-8')
        print cmd
        if self.quite:
            cmd += ' -q '
        if self.live:
            cmd += ' -v'
        print '[RTMPDownloadE2] starting downloading', self.url, 'to', self.local
        self.__startCB()
        self.pp.execute(cmd)

    def cancel(self):
        if self.pp.running():
            self.killed = True
            self.downloaded = False
            self.pp.sendCtrlC()


class HTTPDownloadE2(Download):
    def __init__(self, name, url, destDir, filename=None, quite=False):
        self.e2download = True
        if filename is None:
            path = urlparse.urlparse(url).path
            filename = os.path.basename(path)
        Download.__init__(self, name, url, destDir, filename, quite)
        self.pp = eConsoleAppContainer()
        #self.pp.dataAvail.append(self.__startCB)
        self.pp.stderrAvail.append(self.__outputCB)
        self.pp.appClosed.append(self.__finishCB)

    def __startCB(self):
        self.running = True
        if self.startCB is not None:
            self.startCB(self)

    def __finishCB(self, retval):
        print 'e2httpdownload finished with', str(retval)
        self.running = False
        self.finish_time = time.time()
        if retval == 0 and not self.killed:
            self.downloaded = True
        else:
            self.downloaded = False
        if self.finishCB is not None:
            self.finishCB(self)

    def __outputCB(self, data):
        if self.showOutput and self.outputCB is not None:
            self.outputCB(data)

    def kill(self):
        if self.pp.running():
            self.pp.kill()

    def start(self):
        cmd = wget_path + ' "' + self.url + '"' + ' -O ' + '"' + self.local + '"' ' -U ' + '"' + user_agent + '"'
        cmd = cmd.encode('utf-8')
        print cmd
        if self.quite:
            cmd += ' -q'
        print '[HTTPDownloadE2] starting downloading', self.url
        self.__startCB()
        self.pp.execute(cmd)

    def cancel(self):
        if self.pp.running():
            self.killed = True
            self.pp.sendCtrlC()


class RTMPDownloadTW(Download):
    """Downloads rtmp stream with rtmpdump, using Twisted as process controler and creator""" 
    def __init__(self, name, url, destDir, filename=None, live=False, quite=False):
        if not filename:
            filename = name + '.flv'
            filename = filename.replace(' ', '_')
            filename = filename.replace('/', '')
            filename = filename.replace('(', '')
            filename = filename.replace(')', '')
        Download.__init__(self, name, url, destDir, filename, quite)
        self.startDeffer = defer.Deferred()
        self.finishDeffer = defer.Deferred()
        self.pp = RTMPDumpProcessProtocol(self)
        self.live = live

    def start(self):
        cmd = rtmpdump_path + ' -r ' + self.url + ' -o ' + self.local
        cmd = cmd.encode('utf-8')
        print cmd
        cmd = cmd.split()
        if self.quite:
            cmd.append('-q')
        if self.live:
            cmd.append('-v')
        print '[RTMPDownloadTW] starting downloading', self.url, 'to', self.local
        reactor.spawnProcess(self.pp, cmd[0], cmd)

    def cancel(self):
        if self.running:
            self.pp.kill()


class RTMPDumpProcessProtocol(protocol.ProcessProtocol):
    def __init__(self, download):
        self.download = download

    def connectionMade(self):
        print '[RTMPDumpProcessProtocol] connectionMade', self.download.name.encode('utf-8')
        self.download.running = True
        self.download.startDeffer.callback(self.download)

    def processEnded(self, reason):
        print '[RTMPDumpProcessProtocol] processEnded', self.download.name.encode('utf-8'), reason.value.exitCode
        self.download.running = False
        self.download.finish_time = time.time()

        if reason.value.exitCode == 0:
            self.download.downloaded = True
            self.download.totalLength = os.path.getsize(self.download.local)
        else:
            self.download.downloaded = False
        self.download.finishDeffer.callback(self.download)

    def errReceived(self, data):
        if self.download.showOutput:
            if self.download.outputCB:
                self.download.outputCB(data)

    def kill(self):
        self.transport.signalProcess('KILL')


class HTTPDownloadTW(Download):
    """Downloads http stream with wget, using Twisted as process controller and creator""" 
    def __init__(self, name, url, destDir, filename=None, quite=False):
        if filename is None:
            path = urlparse.urlparse(url).path
            filename = os.path.basename(path)
        Download.__init__(self, name, url, destDir, filename, quite)
        self.startDeffer = defer.Deferred()
        self.finishDeffer = defer.Deferred()
        self.pp = wgetProcessProtocol(self)

    def start(self):
        cmd = wget_path + ' -c ' + self.url + ' -O ' + self.local #+ ' -U ' + '"' + user_agent + '"'
        cmd = cmd.encode('utf-8')
        print cmd
        cmd = cmd.split()
        if self.quite:
            cmd.append('-q')
        print '[HTTPDownloadTW] starting downloading', self.url
        reactor.spawnProcess(self.pp, cmd[0], cmd)

    def cancel(self):
        if self.running:
            self.pp.kill()
        #self.removeDownload()


class wgetProcessProtocol(protocol.ProcessProtocol):
    def __init__(self, download):
        self.download = download

    def connectionMade(self):
        print '[wgetProcessProtocol] connectionMade', self.download.name.encode('utf-8')
        self.download.running = True
        self.download.startDeffer.callback(self.download)

    def processEnded(self, reason):
        print '[wgetProcessProtocol] processEnded', self.download.name.encode('utf-8'), reason.value.exitCode
        self.download.running = False
        self.download.finish_time = time.time()

        if reason.value.exitCode == 0:
            self.download.downloaded = True
            self.download.totalLength = os.path.getsize(self.download.local)
        else:
            self.download.downloaded = False
        self.download.finishDeffer.callback(self.download)

    def errReceived(self, data):
        if self.download.showOutput:
            if self.download.outputCB:
                self.download.outputCB(data)

    def kill(self):
        self.transport.signalProcess('KILL')
        
class HTTPProgressDownloader(client.HTTPDownloader):
    
    def __init__(self, url, fileOrName, writeToEmptyFile=False, outputCB=None, *args, **kwargs):
        self.writeToEmptyFile = writeToEmptyFile
        self.outputCB = outputCB
        self.totalLength = 0
        client.HTTPDownloader.__init__(self, url, fileOrName, *args, **kwargs)
        

    def gotHeaders(self, headers):
        print 'gotHeaders'
        if self.status == '200': # page data is on the way
            if headers.has_key('content-length'):
                self.totalLength = int(headers['content-length'][0])
                print self.totalLength
            else:
                self.totalLength = 0
            self.currentLength = 0.0
            print ''
        return client.HTTPDownloader.gotHeaders(self, headers)
    
    def pageStart(self, partialContent):
        """Called on page download start.

        @param partialContent: tells us if the download is partial download we requested.
        """
        if partialContent and not self.requestedPartial:
            raise ValueError, "we shouldn't get partial content response if we didn't want it!"
        if self.waiting:
            try:
                if not self.file:
                    self.file = self.openFile(partialContent)
            except IOError:
                #raise
                self.deferred.errback(failure.Failure())

    def pagePart(self, data):
        if self.status == '200':
            self.currentLength += len(data)
            if self.totalLength:
                percent = "%i%%" % ((self.currentLength / self.totalLength) * 100)
                outputstr = "%.3f/%.3f MB %s percent" % (float(self.currentLength / (1024 * 1024)), float(self.totalLength / (1024 * 1024)), percent)
                self.outputCB(outputstr)
                #print "3[1FProgress: " + percent
               # log.msg("3[1FProgress: " + percent)
            else:
                percent = '%dK' % (self.currentLength / 1000)
                outputstr = "%d/%i MB %d percent" % (self.currentLength, percent)
                self.outputCB(outputstr)
        return client.HTTPDownloader.pagePart(self, data)
    
    def createEmptyFile(self, size):
        print 'createemptyfile'
        f = open(self.fileName, "wb")
        f.seek((size) - 1)
        f.write("\0")
        f.close()

    
    def openFile(self, partialContent):
        #download avi files to existing file with full length of file which will be downloaded
        if self.writeToEmptyFile:
            self.createEmptyFile(self.totalLength)
            file = open(self.fileName, 'rb+')
            return file
        else:
            return client.HTTPDownloader.openFile(self, partialContent)



class HTTPDownloadTwisted(Download):
    def __init__(self, name, url, destDir, filename=None, quite=False):
        if filename is None:
            path = urlparse.urlparse(url).path
            filename = os.path.basename(path)
        Download.__init__(self, name, url, destDir, filename, quite)
        self.connector = None

    def __startCB(self):
        self.running = True
        if self.startCB is not None:
            self.startCB(self)

    def __finishCB(self, retval):
        self.running = False
        self.finish_time = time.time()
        self.downloaded = True
        if self.finishCB is not None:
            self.finishCB(self)

    def __outputCB(self, data):
        if self.showOutput and self.outputCB is not None:
            self.outputCB(data)

    def start(self):
        self.__startCB()
        self.defer = self.downloadWithProgress(self.url, self.local, writeToEmptyFile=True, outputCB=self.__outputCB).addCallback(self.__finishCB).addErrback(self.downloadError)

    def cancel(self):
        if self.running and self.connector is not None:
            self.downloaded = False
            self.running = False
            self.connector.disconnect()
    
    def downloadWithProgress(self, url, file, contextFactory=None, *args, **kwargs):
        print 'downloadWithProgress'
        scheme, host, port, path = client._parse(url)
        factory = HTTPProgressDownloader(url, file, *args, **kwargs)
        if scheme == 'https':
            from twisted.internet import ssl
            if contextFactory is None:
                contextFactory = ssl.ClientContextFactory()
            self.connector = reactor.connectSSL(host, port, factory, contextFactory)
        else:
            self.connector = reactor.connectTCP(host, port, factory)
        return factory.deferred
    
    def downloadError(self, failure):
        self.downloaded = False
        self.running = False
        print "Error:", failure.getErrorMessage()
        if self.finishCB is not None:
            self.finishCB(self)
