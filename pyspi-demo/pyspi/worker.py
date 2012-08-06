import threading
import requests

class Download(threading.Thread):
    def __init__(self, queue, out_queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.out_queue = out_queue

    @staticmethod
    def check_response(r):
        if r.status_code == 200:
            return
        raise ValueError(r.status_code)
        
        

    def run(self):
        while True:
            #grabs data from queue
            (key, url, payload, timeout) = self.queue.get()

            #grabs urls of hosts and then grabs chunk of webpage
            try:
                if not payload:
                    r = requests.get(url, timeout=timeout)
                else:
                    r = requests.post(url, data=payload, timeout=timeout)
            except requests.exceptions.Timeout:
                # We use code 1000 for timeouts
                self.out_queue.put( (key, {'is_error': True, 'error_code': 1000}) )
                self.queue.task_done()
                return

            #Now let's check the http response code
            try:
                Download.check_response(r)
            except ValueError, e:
                self.out_queue.put( (key, {'is_error': True, 'error_code': e}) )
                self. queue.task_done()
                return
            self.out_queue.put((key, r.json))
            self.queue.task_done()
