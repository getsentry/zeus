
import threading

from zeus.utils.imports import import_string

from .signals import task_postrun, task_prerun
from .task import Task


class Queue(object):
    def __init__(self, app=None):
        self.app = None
        self.adapter = None
        self.task_registry = {}
        self._lock = threading.Lock()
        if app:
            self.init_app(app)

    def __getattr__(self, name):
        assert self.adapter
        return getattr(self.adapter, name)

    def init_app(self, app):
        self.app = app

        adapter_cls = import_string(
            app.config.get("QUEUE_ADAPTER", "zeus.queue.adapters.rq.RqAdapter")
        )

        self.adapter = adapter_cls(
            task_registry=self.task_registry, **app.config.get("QUEUE_OPTIONS", {})
        )

        # worker_process_init.connect(self._worker_process_init)

        task_postrun.connect(self._task_postrun)
        task_prerun.connect(self._task_prerun)

    def task(self, **kwargs):
        def wrapper(task):
            with self._lock:
                if not isinstance(task, Task):
                    task = Task(func=task, **kwargs)
                self.task_registry[task.name] = task
            return task

        return wrapper

    # def _worker_process_init(self, *args, **kwargs):
    #     self.app.app_context().push()

    def _task_prerun(self, task, *args, **kwargs):
        if self.app is None:
            return

        context = task._flask_context = [
            self.app.app_context(),
            self.app.test_request_context(),
        ]
        for ctx in context:
            ctx.push()

    def _task_postrun(self, task, *args, **kwargs):
        try:
            context = task._flask_context
        except AttributeError:
            return

        for ctx in context:
            ctx.pop()
