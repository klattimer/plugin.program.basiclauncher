from queue import Queue
from threading import Thread
import requests
import time


class Downloader(Thread):
    def __init__(self, base_url, limit_size=-1, limit_expires=-1, limit_interval=1):
        super().__init__()
        self.base_url = base_url
        self.last_endpoint_hit = -1
        self.limit_size = limit_size
        self.limit_expires = limit_expires
        self.limit_interval = limit_interval
        self.queue = Queue()
        self.completed = Queue()
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            while self.queue.empty() is False:
                self.__download_next()

    def close(self):
        if self.queue.empty() is False:
            print("Downloader queue not empty, will exit when it is.")
        self.running = False

    def add_item(
                self,
                url,
                method='get',
                params={},
                destination=None,
                callback=None,
                headers=[],
                content=None,
                asynchronous=True,
                userdata=None
            ):
        if asynchronous is True:
            self.queue.put({
                'url': url,
                'method': method,
                'params': params,
                'destination': destination,
                'callback': callback,
                'headers': headers,
                'content': content,
                'userdata': userdata,
                'async': asynchronous
            })
        else:
            return self.__download_item({
                'url': url,
                'method': method,
                'params': params,
                'destination': destination,
                'callback': callback,
                'headers': headers,
                'content': content,
                'userdata': userdata,
                'async': asynchronous
            })

    def __download_next(self):
        try:
            item = self.queue.get(timeout=5)
        except:
            return

        if item is None:
            return
        try:
            self.__download_item(item)
            self.queue.task_done()
        except Exception as e:
            print ("Task caused a dead letter: " + str(e))
            sys.exit(1)

    def __download_item(self, item):
        # Check the time interval since last hit
        now = time.time()
        if self.last_endpoint_hit > 0 and self.last_endpoint_hit + self.limit_interval < now:
            v = now - (self.last_endpoint_hit + self.limit_interval)
            time.sleep(v)
        self.last_endpoint_hit = now

        # Do the download
        if item['method'] == 'get':
            response = requests.get(
                self.base_url + item['url'],
                params=item['params']
            )
        elif item['method'] == 'post':
            response = requests.post(
                self.base_url + item['url'],
                params=item['params'],
                data=item['content']
            )
        else:
            raise Exception("Unsupported HTTP method")

        if response.status_code != requests.codes.ok:
            raise Exception("Item download failed %d: " % response.status_code)

        if response.headers['content-type'] == "application/json":
            data = response.json()
            raw = response.text
            mode = 'wt'
        elif response.headers['content-type'].endswith("text"):
            data = response.text
            raw = response.text
            mode = 'wt'
        else:
            data = response.content
            raw = response.content
            mode = 'wb'

        if item.get('callback'):
            item.get('callback')(data, item['userdata'])

        if item.get('destination'):
            with open(item.get('destination'), mode) as f:
                f.write(raw)

        self.completed.put((item, response))
        return data
