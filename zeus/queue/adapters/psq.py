from flask import current_app
from google.cloud import pubsub_v1
import psq

from ..adapter import Adapter
from ..worker import Worker


class PsqWorker(Worker):
    def listen(self):
        future = None

        try:
            future = self.queue.listen(self.run_task)
            current_app.logger.info("Listening for tasks, press Ctrl+C to exit.")
            future.result()

        except KeyboardInterrupt:
            if future is not None:
                future.cancel()
            current_app.logger.info("Stopped listening for tasks.")

        finally:
            self.queue.cleanup()

    def run_task(self, task):
        current_app.logger.info("Received task {}".format(task.id))
        with self.queue.queue_context():
            task.execute(self.queue)


class PsqAdapter(Adapter):
    worker_cls = PsqWorker

    def __init__(self, project, **kwargs):
        self.project = project
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        super().__init__(**kwargs)

    def create_queue(self, name):
        return psq.Queue(
            publisher=self.publisher,
            subscriber=self.subscriber,
            project=self.project,
            name=name,
            extra_context=current_app.app_context,
        )
