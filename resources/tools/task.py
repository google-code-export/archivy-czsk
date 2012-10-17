'''
Created on 10.9.2012

@author: marko
'''
import Queue
import threading
from twisted.internet import defer
from twisted.python import log, context, failure

from enigma import eTimer
import Plugins.Extensions.archivCZSK.resources.exceptions.archiveException as exceptions

DEBUG = True

def debug(info):
    if DEBUG:
        print '[ArchivCZSK] Task ', info.encode('utf-8')
        
# object for stopping workerThread        
WorkerStop = object()

# queue for function to be executed in workerThread
fnc_queue = Queue.Queue()

# input queue to send results from reactor thread to running function in workerThread
fnc_in_queue = Queue.Queue()

#output queue to send function decorated by callFromThread from workerThread to reactor thread and run it there
fnc_out_queue = Queue.Queue()


def callFromThread(func):
    """calls function from child thread in main(reactor) thread, and wait(in child thread) for result. Used mainly for GUI calls"""
    def wrapped(*args, **kwargs):
        
        def _callFromThread():
            debug("_callFromThread")
            result = defer.maybeDeferred(func, *args, **kwargs)
            result.addBoth(fnc_in_queue.put)
            
        fnc_out_queue.put(_callFromThread)
        result = fnc_in_queue.get()
        debug("result is %s" % str(result))
        if isinstance(result, failure.Failure):
            result.raiseException()
        return result
    return wrapped



class WorkerThread(threading.Thread):
    """WorkerThread for running user tasks"""
    def __init__(self, fnc_queue):
        threading.Thread.__init__(self)
        self.q = fnc_queue

    def run(self):
        debug("WorkerThread, waiting for function to execute")
        o = self.q.get()
        debug("getting function")
        while o is not WorkerStop:
            ctx, function, args, kwargs, onResult = o
            del o
            try:
                result = context.call(ctx, function, *args, **kwargs)
                success = True
            except:
                success = False
                if onResult is None:
                    context.call(ctx, log.err)
                    result = None
                else:
                    result = failure.Failure()

            del function, args, kwargs

            if onResult is not None:
                try:
                    context.call(ctx, onResult, success, result)
                except:
                    context.call(ctx, log.err)

            del ctx, onResult, result

            o = self.q.get()
        debug("working thread stopped")
            
    def stop(self):
        debug("stopping working thread")
        self.q.put(WorkerStop)
        self.join()        
        
        
        
        

class Task():
    """Class for running single python task at time in worker thread"""
    instance = None
    worker_thread = None
    polling_interval = 1000#ms
    
    @staticmethod
    def getInstance():
        return Task.instance
    
    @staticmethod
    def startWorkerThread():
        debug("starting workerThread")
        Task.worker_thread = WorkerThread(fnc_queue)
        Task.worker_thread.start()
        
    @staticmethod   
    def stopWorkerThread():
        debug("stopping workerThread")
        Task.worker_thread.stop()
        Task.worker_thread = None
        
    @staticmethod     
    def setPollingInterval(self, interval):
        self.polling_interval = interval
        
    
    def __init__(self, callback, fnc, *args, **kwargs):
        debug('initializing')
        Task.instance = self
        self.running = False
        self._aborted = False
        self.callback = callback
        self.fnc = fnc
        self.args = args
        self.kwargs = kwargs
        self.timer = eTimer()
        self.timer.callback.append(self.check_fnc_callback)
        
          
    def run(self):
        debug('running')
        self.running = True
        self._aborted = False
        
        ctx = context.theContextTracker.currentContext().contexts[-1]
        o = (ctx, self.fnc, self.args, self.kwargs, self.onComplete)
        fnc_queue.put(o)
        self.timer.start(self.polling_interval) 
        self.check_fnc_callback()
        
    #poll this function in reactor thread
    def check_fnc_callback(self):
        """check non-blockingly in reactor thread if function executed in workerThread 
            didnt send function which wants to call in reactor thread. 
            If there is an function, than call it.
        """
        if self.running:
            debug("checking function in thread callback")
            try:
                return fnc_out_queue.get(block=False)()
            except Exception:
                debug("nothing in queue")
        else:
            self.timer.stop()    
        
    def setResume(self):
        debug("resuming")
        self._aborted = False
    
    def setCancel(self):
        """setting flag to abort executing compatible task(ie. controlling this flag in task execution)"""
        debug('cancelling...')
        self._aborted = True
            
    def isCancelling(self):
        return self._aborted

    def onComplete(self, success, result):
        self.running = False
        if success:
            debug('completed with success')
        else:
            debug('completed with failure')
        #To make sure that, when we abort processing of task, that its always the same type of failure
        if self._aborted:
            success = False
            result = failure.Failure(exceptions.ArchiveThreadException())
        self.finish(success, result)
    
            
    def onCompleteSuccess(self, result):
        debug('completed with success')
        self.finish(True, result)
            
    def onCompleteFailure(self, failure):
        self.finish(False, failure)
        debug('completed with failure')
            
    def finish(self, success, result):
        Task.instance = None
        self.callback(success, result)
            
    

