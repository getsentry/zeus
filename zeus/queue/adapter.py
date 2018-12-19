from .exceptions import UnknownTask
from .scheduler import Scheduler
from .worker import Worker
from .task import run_task


class Adapter(object):
    scheduler_class = Scheduler
    worker_class = Worker

    def __init__(self, task_registry):
        self.queues = {}
        self.task_registry = task_registry

    def get_queue(self, name):
        if name not in self.queues:
            self.queues[name] = self.create_queue(name)
        return self.queues[name]

    def create_queue(self, name):
        raise NotImplementedError

    def enqueue(self, task, args=None, kwargs=None, context=None):
        if isinstance(task, str):
            try:
                task = self.task_registry[task]
            except KeyError:
                raise UnknownTask(task)
        return self.get_queue("default").enqueue_call(
            run_task,
            kwargs={
                "task_name": task.name,
                "task_args": args,
                "task_kwargs": kwargs,
                "task_context": context or {},
            },
        )

    def get_worker(self, queue_name="default"):
        return self.worker_class(adapter=self, queue_name=queue_name)

    def get_scheduler(self, **kwargs):
        return self.scheduler_class(adapter=self, **kwargs)
