from twisted.python import log
from twisted.web import http, proxy
from twisted.internet import reactor,defer,protocol
import sys
running_defered=[]
global_session=None


class Closer:
    counter = 0
    def __init__(self, session, callback=None):
        self.callback = callback
        self.session = session

    def stop(self):
        global running_defered
        for d in running_defered:
            print "[Webinterface] stopping interface on ", d.interface, " with port", d.port
            x = d.stopListening()
            try:
                x.addCallback(self.isDown)
                self.counter += 1
            except AttributeError:
                pass
        running_defered = []
        if self.counter < 1:
            if self.callback is not None:
                self.callback(self.session)

    def isDown(self, s):
        self.counter -= 1
        if self.counter < 1:
            if self.callback is not None:
                self.callback(self.session)


class ProxyServer():
    request=''
    address='127.0.0.1'#config.plugins.archivCZSK.proxy.address.value
    port=80#config.plugins.archivCZSK.proxy.port.value
    enabled=True #config.plugins.archivCZSK.proxy.enabled.value
    instance=None
    
    def __init__(self):
        ProxyServer.instance=self
        
    def restart(self,session=None):
        global running_defered
        if len(running_defered) > 0:
            Closer(session, self.start).stop()
        else:
            self.start(session)
            
    def setRequest(self,request):
        self.request=request

    def start(self,session=None):
        global running_defered
        if self.enabled is not True:
            print "[Proxy] is disabled!"
            return False
        else:
            self.startServerInstance(session,self.port)

    def stop(self,session=None):
        global running_defered
        if len(running_defered) > 0:
            Closer(session).stop()

    def startServerInstance(self,session,port):
        global running_defered
        try:
            d = reactor.listenTCP(self.port, ProxyFactory())
            running_defered.append(d)
            print "[Proxy] started on localhost:%i" %  port
        except Exception, e:
            print "[Webinterface] starting FAILED on localhost:%i!" % (port), e
            #session.open(MessageBox, 'starting FAILED on localhost:%i!\n\n%s' % (port, str(e)), MessageBox.TYPE_ERROR)

class ProxyClient(proxy.ProxyClient):
    i=0
    buf=0
    """Mange returned header, content here.

    Use `self.father` methods to modify request directly.
    """
    
    def connectionMade(self):
         print "Command",self.command,self.rest
         print "Father",self.father
         proxy.ProxyClient.connectionMade(self)
         
    def handleHeader(self, key, value):
        # change response header here
        log.msg("Header: %s: %s" % (key, value))
        proxy.ProxyClient.handleHeader(self, key, value)

    def handleResponsePart(self, buffer):
        self.i+=1
        self.buf+=len(buffer)
        log.msg("Part %i - downloaded %f KB, Total download %f KB"% (self.i,float(len(buffer)/1024),float(self.buf/1024)))
        # change response part here
        #log.msg("Content: %s" % (buffer[:50],))
        #log.msg("Buffer: %i"% len(buffer))
        # make all content upper case
        proxy.ProxyClient.handleResponsePart(self, buffer)

class ProxyClientFactory(proxy.ProxyClientFactory):
    protocol = ProxyClient

class ProxyRequest(proxy.ProxyRequest):
    protocols = dict(http=ProxyClientFactory)
    
    
    def process(self):
        ##self.uri='http://www.dsl.sk'
        #print self.uri
        proxy.ProxyRequest.process(self)
        

class Proxy(proxy.Proxy):
    def lineReceived(self, line):
        if line[:4]=='Host':
            pass
        else:
            if line[:3]=='GET':
                #pass
                line=ProxyServer.request
            log.msg("line",line)
            proxy.Proxy.lineReceived(self,line)
    requestFactory = ProxyRequest

class ProxyFactory(http.HTTPFactory):
    protocol = Proxy
    
    
def stop():
    d=defer.Deferred()
    d.addCallback(stopReactor)
    d.callback(None)
    
class MyPP(protocol.ProcessProtocol):
    def processExited(self, reason):
        print "processExited, status %s" % (reason.value.exitCode,)
    
def spawnProc(name):
    pp=MyPP()
    reactor.spawnProcess(pp,name)

def stopReactor(callback=None):
    reactor.stop()
    
#log.startLogging(sys.stdout)
#reactor.callLater(2,ProxyServer().start)
#reactor.callLater(3,ProxyServer.instance.request= 'GET http://o-o.preferred.energotel-bts1.v3.lscache7.c.youtube.com/videoplayback?upn=Silbq_09AvQ&sparams=cp%2Cid%2Cip%2Cipbits%2Citag%2Cratebypass%2Csource%2Cupn%2Cexpire&fexp=901801%2C911203%2C900222%2C907217%2C907335%2C921602%2C919306%2C919316%2C912804%2C913542%2C919324%2C912706&ms=au&itag=18&ip=91.0.0.0&signature=AD1CF0AF61F174B9926A1AE022EC43748A09E699.2500423FB8D4B4ED5128C3E24EE78670B8C2AA0C&sver=3&mt=1339487714&ratebypass=yes&source=youtube&expire=1339512968&key=yt1&ipbits=8&cp=U0hSTlVMUF9LUkNOMl9NRlRKOnhaVUtJamVkcjNn&id=b4077f0e1e1cb614&title=Lionel%20Messi%20vs%20Ecuador HTTP/1.1')
#eactor.callLater(3,ProxyServer().stop)
#reactor.callLater(4,ProxyServer().start)

#reactor.callLater(1,spawnProc,'telnet')
#reactor.callLater(3,stop)
#Proxy.getRequest='GET http://koukni.cz/MP4/31423144.mp4 HTTP/1.1'
#reactor.run()


#def Plugins(**kwargs):
 #   return [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart),
  #          PluginDescriptor(where=[PluginDescriptor.WHERE_NETWORKCONFIG_READ], fnc=networkstart),
   #         PluginDescriptor(name=_("Webinterface"), description=_("Configuration for the Webinterface"),
    #                        where=[PluginDescriptor.WHERE_PLUGINMENU], icon="plugin.png", fnc=openconfig)]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  