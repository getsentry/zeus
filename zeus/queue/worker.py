class Worker(object):
    def __init__(self, adapter, queue_name):
        self.queue_name = queue_name
        self.queue = adapter.get_queue(queue_name)

    def listen(self):
        raise NotImplementedError
