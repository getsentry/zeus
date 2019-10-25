from ..adapter import Adapter
from ..exceptions import UnknownTask


class SyncAdapter(Adapter):
    def create_queue(self, name):
        return self

    def enqueue(self, task, kwargs=None, context=None):
        if isinstance(task, str):
            try:
                task = self.task_registry[task]
            except KeyError:
                raise UnknownTask(task)
        task.call(context=context, kwargs=kwargs)
