import rq

from flask import current_app

from zeus.config import redis

from ..adapter import Adapter
from ..worker import Worker


class RqWorker(Worker):
    def listen(self):
        current_app.logger.info("Listening for tasks, press Ctrl+C to exit.")
        with rq.Connection():
            worker = rq.Worker([self.queue_name])
            worker.log = current_app.logger
            try:
                worker.work()
            except KeyboardInterrupt:
                current_app.logger.info("Stopped listening for tasks.")


class RqAdapter(Adapter):
    worker_class = RqWorker

    def create_queue(self, name):
        return rq.Queue(connection=redis)
