from flask import current_app
from typing import Callable, List, Mapping, Type


def generate_task_name(func):
    return "{}.{}".format(func.__module__, func.__name__)


def run_task(
    task_name: str, task_args: list, task_kwargs: dict, task_context: dict = None
):
    """
    Generic task running function which is picked up by underlying queue frameworks
    to avoid serialization complexity.

    This let's us keep our own task registry and also ensure that tasks are executed
    under the circumstances we define (such as retry behavior).

    Lastly it enforces permanent "task name" structures in a standardized way that
    also works with our scheduler.
    """
    from zeus.config import queue

    if task_context is None:
        task_context = {}

    task_context.setdefault("attempts", 0)
    task_context["attempts"] += 1

    return queue.task_registry[task_name].call(
        context=task_context, args=task_args, kwargs=task_kwargs
    )


class Task(object):
    def __init__(
        self,
        func: Callable,
        name: str = None,
        max_retries: int = 0,
        autoretry_for: List[Type] = (),
    ):
        self.func = func
        self.name = name or generate_task_name(func)

        self.max_retries = max_retries
        self.autoretry_for = autoretry_for

    def __call__(self, *args, **kwargs):
        return self.call(args=args, kwargs=kwargs, context={})

    def descriptor(self, args, kwargs):
        if args and kwargs:
            return "%s(%s, %s)" % (
                self.name,
                ",".join(repr(k) for k in args),
                ", ".join("%s=%r" % (k, v) for k, v in kwargs.items()),
            )
        elif kwargs:
            return "%s(%s)" % (
                self.name,
                ", ".join("%s=%r" % (k, v) for k, v in kwargs.items()),
            )
        elif args:
            return "%s(%s, %s)" % (self.name, ",".join(repr(k) for k in args))
        return "%s()" % (self.name,)

    def call(self, context: Mapping, args: List, kwargs: Mapping):
        try:
            return self.func(*args, **kwargs)
        except self.autoretry_for:
            current_attempts = context["attempts"]
            if current_attempts < self.max_retries + 1:
                current_app.logger.exception(
                    "task %s failed, retrying", self.descriptor(args, kwargs)
                )
                self.enqueue_call(args=args, kwargs=kwargs, context=context)
            else:
                raise

    def enqueue(self, *args, **kwargs):
        from zeus.config import queue

        queue.enqueue(self, args=args, kwargs=kwargs)

    # compat with previous celery usage
    delay = enqueue

    def enqueue_call(self, **kwargs):
        from zeus.config import queue

        queue.enqueue(self, **kwargs)
