try:
    # python 2.x
    import Queue
except ImportError:
    # python 3.x
    import queue as Queue
#import pyspi.worker as worker
import worker
import requests
import os
import logging

def conf_from_env(name, default=None):
    """
    gets configuration from the environment
    """
    if name in os.environ:
        return os.environ(name)
    else:
        return default


class ParallelDownloader(object):
    """
    this class downloads in parallel a list of urls given as a tuple (key, url), and creates a dict
    that contains the resulting object
    """
    _TP = [] # the thread pool container
    
    def __init__(self, thread_pool_size):
        """
        We set up the queues and the thread pool
        """
        #TODO: move the thread pool to __new__ method, and make it common for all instances?
        self._download_queue = Queue.Queue()
        self._out_queue = Queue.Queue()
        self._tp_size = thread_pool_size
        for i in xrange(thread_pool_size):
            w = worker.Download(self._download_queue, self._out_queue)
            w.daemon = True
            w.start()
            self._TP.append(w)

    def add(self, key, url, payload=None, timeout=None):
        """
        adds a url to the download queue
        """
        self._download_queue.put((key, url, payload, timeout))
    
    def fetch(self):
        """
        Fetches results for all urls
        """
        #wait for all resources to be downloaded
        results = {}
        self._download_queue.join()
        while not self._out_queue.empty():
            (key,obj) = self._out_queue.get(True)
            self._out_queue.task_done()
            results[key] = obj
        return results


class SPI(ParallelDownloader):
    def __init__(self, service):
        raise NotImplementedError
        
if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(message)s')
    logging.warning("Download Starting")
    p = ParallelDownloader(4)
    for i in xrange(8):
        p.add(i, "https://github.com/timeline.json")
    p.fetch()
    logging.warning("Download Finished")
    
